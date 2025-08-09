#!/usr/bin/env python3
r"""
Conan Exiles Moon Tuner

Adjusts Conan Exiles server settings based on the real-world moon cycle.

Behavior
- Uses a simple astronomically-reasonable model of the synodic month to compute
  the current lunar illumination fraction in [0.0, 1.0].
- Maps illumination fraction to configured min/max multipliers via linear interpolation.
- Updates keys inside [ServerSettings] of ServerSettings.ini:
  - HarvestAmountMultiplier
  - NPCDamageMultiplier
  - NPCHealthMultiplier
- Creates a timestamped backup beside the INI before writing.
- Optional restart command to apply changes immediately.

Usage examples
  python3 conan_moon_tuner.py \
    --ini-path /path/to/ConanSandbox/Saved/Config/LinuxServer/ServerSettings.ini \
    --event-file /path/to/MoonTide/events.json \
    --restart-cmd "systemctl restart conanexiles"

  python3 conan_moon_tuner.py \
    --ini-path "C:/ConanServer/ConanSandbox/Saved/Config/WindowsServer/ServerSettings.ini" \
    --event-file "C:/ConanServer/MoonTide/events.json" \
    --restart-cmd "powershell -NoProfile -Command \"Restart-Service -Name 'ConanExiles'\""

Notes
- Typical INI paths:
  - Linux:   ConanSandbox/Saved/Config/LinuxServer/ServerSettings.ini
- Windows: ConanSandbox\\Saved\\Config\\WindowsServer\\ServerSettings.ini
- Schedule daily (e.g., midnight UTC) to track the moon smoothly.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import urllib.request
import urllib.error
import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union


# ------------------------------
# Lunar computation
# ------------------------------

def compute_lunar_state(timestamp_utc: dt.datetime) -> Tuple[float, float, float]:
    """Return (illumination_fraction, phase_days, synodic_days).

    - Illumination in [0, 1]
    - phase_days in [0, synodic_days)
    - synodic_days ~ 29.53
    """

    if timestamp_utc.tzinfo is None:
        timestamp_utc = timestamp_utc.replace(tzinfo=dt.timezone.utc)
    else:
        timestamp_utc = timestamp_utc.astimezone(dt.timezone.utc)

    reference_new_moon = dt.datetime(2000, 1, 6, 18, 14, tzinfo=dt.timezone.utc)
    synodic_days = 29.53058867

    delta_days = (timestamp_utc - reference_new_moon).total_seconds() / 86400.0
    phase_days = delta_days % synodic_days
    phase_angle = 2.0 * math.pi * (phase_days / synodic_days)

    illumination = 0.5 * (1.0 - math.cos(phase_angle))
    illumination = max(0.0, min(1.0, illumination))
    return illumination, phase_days, synodic_days


def reference_new_moon_datetime() -> dt.datetime:
    return dt.datetime(2000, 1, 6, 18, 14, tzinfo=dt.timezone.utc)


def timestamp_for_phase_day(day_index: int) -> dt.datetime:
    """Return a synthetic UTC timestamp corresponding to a given phase day.

    Places the time near midday UTC for stability.
    """
    base = reference_new_moon_datetime()
    return base + dt.timedelta(days=day_index, hours=12)


def categorize_moon_phase(
    illumination_fraction: float,
    phase_days: float,
    synodic_days: float,
    new_threshold: float = 0.06,
    full_threshold: float = 0.94,
) -> str:
    if illumination_fraction <= new_threshold:
        return "new"
    if illumination_fraction >= full_threshold:
        return "full"
    half = synodic_days / 2.0
    return "waxing" if phase_days < half else "waning"


def categorize_phase_bucket_by_day(phase_days: float) -> str:
    """Return granular phase bucket based on integer day index since new moon.

    Buckets:
      - new: day 0 or 29
      - waxing_crescent: 1-5
      - first_quarter: 6-9
      - waxing_gibbous: 10-14
      - full: 15-16
      - waning_gibbous: 17-20
      - last_quarter: 21-23
      - waning_crescent: 24-28
    """
    day = int(math.floor(phase_days))
    if day == 0 or day == 29:
        return "new"
    if 1 <= day <= 5:
        return "waxing_crescent"
    if 6 <= day <= 9:
        return "first_quarter"
    if 10 <= day <= 14:
        return "waxing_gibbous"
    if 15 <= day <= 16:
        return "full"
    if 17 <= day <= 20:
        return "waning_gibbous"
    if 21 <= day <= 23:
        return "last_quarter"
    if 24 <= day <= 28:
        return "waning_crescent"
    # Fallback
    return "new"


def nearest_full_moon_datetime(
    now_utc: dt.datetime,
    reference_new_moon: dt.datetime = dt.datetime(2000, 1, 6, 18, 14, tzinfo=dt.timezone.utc),
    synodic_days: float = 29.53058867,
) -> dt.datetime:
    # full moons occur approximately every synodic_days, offset by 0.5 cycle from new moon
    delta_days = (now_utc - reference_new_moon).total_seconds() / 86400.0
    n = round(delta_days / synodic_days)
    full_days = (n + 0.5) * synodic_days
    return reference_new_moon + dt.timedelta(days=full_days)


def parse_hhmm_to_minutes(hhmm: str) -> int:
    h, m = hhmm.strip().split(":")
    return int(h) * 60 + int(m)


WEEKDAY_TO_INT = {
    "mon": 0, "monday": 0,
    "tue": 1, "tuesday": 1,
    "wed": 2, "wednesday": 2,
    "thu": 3, "thursday": 3,
    "fri": 4, "friday": 4,
    "sat": 5, "saturday": 5,
    "sun": 6, "sunday": 6,
}


def parse_weektime(s: str) -> Tuple[int, int]:
    # e.g., "Fri 18:00"
    parts = s.strip().split()
    if len(parts) != 2:
        raise ValueError(f"Invalid weektime: {s}")
    wd = WEEKDAY_TO_INT[parts[0].lower()]
    mins = parse_hhmm_to_minutes(parts[1])
    return wd, mins


def is_in_week_window(now_local: dt.datetime, start_spec: str, end_spec: str) -> bool:
    start_wd, start_min = parse_weektime(start_spec)
    end_wd, end_min = parse_weektime(end_spec)

    now_idx = now_local.weekday() * 1440 + now_local.hour * 60 + now_local.minute
    start_idx = start_wd * 1440 + start_min
    end_idx = end_wd * 1440 + end_min

    if start_idx <= end_idx:
        return start_idx <= now_idx <= end_idx
    # wraps across week boundary
    return now_idx >= start_idx or now_idx <= end_idx


def is_in_time_window(now_local: dt.datetime, start_hhmm: str, end_hhmm: str) -> bool:
    now_min = now_local.hour * 60 + now_local.minute
    start_min = parse_hhmm_to_minutes(start_hhmm)
    end_min = parse_hhmm_to_minutes(end_hhmm)
    if start_min <= end_min:
        return start_min <= now_min <= end_min
    # crosses midnight
    return now_min >= start_min or now_min <= end_min


def get_local_time(now_utc: dt.datetime, cfg: Dict[str, Union[int, float]], override: Optional[Dict[str, Union[int, float]]] = None) -> dt.datetime:
    offset = 0.0
    if cfg is not None:
        offset = float(cfg.get("timezone_offset_hours", 0.0))
    if override is not None:
        offset = float(override.get("timezone_offset_hours", offset))
    return now_utc + dt.timedelta(hours=offset)


def is_trigger_active(
    trigger: Dict[str, Union[str, int, float, bool, List, Dict]],
    now_utc: dt.datetime,
    illumination_fraction: float,
    phase_days: float,
    synodic_days: float,
    root_config: Dict[str, Union[str, int, float, bool, List, Dict]],
) -> bool:
    ttype = str(trigger.get("type", "")).lower()
    local_now = get_local_time(now_utc, root_config or {}, trigger)

    if ttype == "astronomical":
        event = str(trigger.get("event", "")).lower()
        window_hours = float(trigger.get("window_hours", 24))
        half = synodic_days / 2.0
        diff_days = abs(phase_days - half)
        diff_days = min(diff_days, synodic_days - diff_days)
        diff_hours = diff_days * 24.0

        if event == "full_moon":
            within_window = diff_hours <= (window_hours / 2.0)
            if not within_window:
                return False
            if bool(trigger.get("nearest_weekend", False)):
                return local_now.weekday() in (4, 5)  # Fri, Sat
            return True

        if event == "blue_moon":
            # Near a full moon and that full moon is the 2nd in month
            if diff_hours > (window_hours / 2.0):
                return False
            ref_new = dt.datetime(2000, 1, 6, 18, 14, tzinfo=dt.timezone.utc)
            cur_full = nearest_full_moon_datetime(now_utc, ref_new, synodic_days)
            prev_full = cur_full - dt.timedelta(days=synodic_days)
            if cur_full.month == prev_full.month and cur_full.year == prev_full.year:
                # Optional weekly activation window like ["Fri 18:00","Sun 23:59"]
                win = trigger.get("activate_window")
                if isinstance(win, list) and len(win) == 2:
                    return is_in_week_window(local_now, str(win[0]), str(win[1]))
                return True
            return False

        return False

    if ttype == "seasonal_window":
        months = trigger.get("months", [])
        if isinstance(months, list) and months and local_now.month not in [int(m) for m in months]:
            return False
        daily = trigger.get("daily_window")
        if isinstance(daily, list) and len(daily) == 2:
            return is_in_time_window(local_now, str(daily[0]), str(daily[1]))
        return True

    if ttype == "date_window":
        start = str(trigger.get("start", "01-01"))  # MM-DD
        end = str(trigger.get("end", "12-31"))
        sm, sd = [int(x) for x in start.split("-")]
        em, ed = [int(x) for x in end.split("-")]

        def monthday_index(m: int, d: int) -> int:
            return m * 31 + d

        now_idx = monthday_index(local_now.month, local_now.day)
        start_idx = monthday_index(sm, sd)
        end_idx = monthday_index(em, ed)
        in_range = start_idx <= now_idx <= end_idx if start_idx <= end_idx else (now_idx >= start_idx or now_idx <= end_idx)
        if not in_range:
            return False
        night = trigger.get("night_window") or trigger.get("time_window")
        if isinstance(night, list) and len(night) == 2:
            return is_in_time_window(local_now, str(night[0]), str(night[1]))
        return True

    if ttype == "weather":
        # Stub: not implemented until a weather API is configured
        return False

    # Unknown trigger type -> not active
    return False


def interpolate(min_value: float, max_value: float, t: float) -> float:
    """Linear interpolation between min_value and max_value using t in [0, 1]."""
    return min_value + (max_value - min_value) * t


def compute_scaled_values(
    illumination_fraction: float,
    minmax_by_key: Dict[str, Dict[str, float]],
    gamma: float = 1.0,
) -> Dict[str, float]:
    """Compute scaled values for arbitrary INI keys.

    minmax_by_key: { INI_KEY: {"min": float, "max": float } }
    gamma shapes the curve: t' = t ** gamma
    """
    t = illumination_fraction
    if gamma > 0:
        try:
            t = max(0.0, min(1.0, t ** gamma))
        except Exception:
            t = illumination_fraction

    result: Dict[str, float] = {}
    for ini_key, rng in minmax_by_key.items():
        vmin = float(rng.get("min", 1.0))
        vmax = float(rng.get("max", 1.0))
        result[ini_key] = interpolate(vmin, vmax, t)
    return result


# ------------------------------
# INI editing
# ------------------------------

SERVER_SETTINGS_SECTION = "ServerSettings"


class BackupManager:
    def __init__(self, ini_path: str, backup_dir: Optional[str], keep: int, one_backup_per_run: bool = True) -> None:
        self.ini_path = os.path.abspath(ini_path)
        self.ini_basename = os.path.basename(self.ini_path)
        self.keep = max(1, int(keep))
        self.one_backup_per_run = bool(one_backup_per_run)
        default_dir = os.path.join(os.path.dirname(self.ini_path), "backups")
        self.backup_dir = os.path.abspath(backup_dir) if backup_dir else default_dir
        self._made_backup = False

    def ensure_backup(self) -> Optional[str]:
        if self.one_backup_per_run and self._made_backup:
            return None
        os.makedirs(self.backup_dir, exist_ok=True)
        timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_name = f"{self.ini_basename}.bak.{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        shutil.copy2(self.ini_path, backup_path)
        self._made_backup = True
        self._prune_old_backups()
        return backup_path

    def _prune_old_backups(self) -> None:
        try:
            candidates = []
            for name in os.listdir(self.backup_dir):
                if name.startswith(self.ini_basename + ".bak."):
                    full = os.path.join(self.backup_dir, name)
                    if os.path.isfile(full):
                        candidates.append((full, os.path.getmtime(full)))
            candidates.sort(key=lambda x: x[1], reverse=True)
            for full, _ in candidates[self.keep:]:
                try:
                    os.remove(full)
                except OSError:
                    pass
        except FileNotFoundError:
            pass


def read_text_lines(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def write_text_lines(path: str, lines: List[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def find_section_ranges(lines: List[str]) -> Dict[str, Tuple[int, int]]:
    section_header_pattern = re.compile(r"^\s*\[(?P<name>[^\]]+)\]\s*$")
    sections: Dict[str, Tuple[int, int]] = {}
    current_name: Optional[str] = None
    current_start = -1

    for idx, line in enumerate(lines):
        match = section_header_pattern.match(line)
        if match:
            if current_name is not None:
                sections[current_name] = (current_start, idx)
            current_name = match.group("name").strip()
            current_start = idx

    if current_name is not None:
        sections[current_name] = (current_start, len(lines))

    return sections


def upsert_key_in_section(
    lines: List[str], section_name: str, key: str, value_str: str
) -> Tuple[List[str], bool]:
    key_pattern = re.compile(rf"^\s*{re.escape(key)}\s*=\s*.*$")
    updated = False

    sections = find_section_ranges(lines)
    if section_name in sections:
        start, end = sections[section_name]
        for i in range(start + 1, end):
            if key_pattern.match(lines[i]):
                lines[i] = f"{key}={value_str}"
                updated = True
                break
        if not updated:
            insertion_index = end
            lines.insert(insertion_index, f"{key}={value_str}")
            updated = True
    else:
        if lines and lines[-1].strip() != "":
            lines.append("")
        lines.append(f"[{section_name}]")
        lines.append(f"{key}={value_str}")
        updated = True

    return lines, updated


def key_exists_in_section(lines: List[str], section_name: str, key: str) -> bool:
    sections = find_section_ranges(lines)
    if section_name not in sections:
        return False
    start, end = sections[section_name]
    key_pattern = re.compile(rf"^\s*{re.escape(key)}\s*=\s*.*$")
    for i in range(start + 1, end):
        if key_pattern.match(lines[i]):
            return True
    return False


def apply_settings(
    ini_path: str,
    harvest_amount: float,
    npc_damage: float,
    npc_health: float,
    dry_run: bool,
    backup_manager: BackupManager,
) -> Tuple[bool, List[str]]:
    changes: List[str] = []
    lines = read_text_lines(ini_path)

    def set_key(k: str, v: float) -> None:
        nonlocal lines
        old_lines = list(lines)
        lines, _ = upsert_key_in_section(lines, SERVER_SETTINGS_SECTION, k, f"{v:.6f}")
        if lines != old_lines:
            changes.append(f"{k} -> {v:.6f}")

    set_key("HarvestAmountMultiplier", harvest_amount)
    set_key("NPCDamageMultiplier", npc_damage)
    set_key("NPCHealthMultiplier", npc_health)

    if not changes:
        return False, []

    if dry_run:
        return True, changes

    backup_path = backup_manager.ensure_backup()
    write_text_lines(ini_path, lines)
    result_msgs = changes if backup_path is None else [f"Backup: {backup_path}"] + changes
    return True, result_msgs


def format_value(value: Union[int, float, str], precision: int) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) or (isinstance(value, float) and float(value).is_integer()):
        return f"{int(value)}"
    return f"{float(value):.{precision}f}"


def _post_discord_summary(
    webhook_url: str,
    phase_name: str,
    phase_bucket: str,
    illumination: float,
    events_applied: List[str],
    motd: str,
) -> None:
    content = (
        f"**MoonTide** — phase: `{phase_name}` bucket: `{phase_bucket}` illum: `{illumination:.3f}`\n"
        f"Events: {', '.join(events_applied) if events_applied else 'none'}\n\n"
        f"MOTD:\n{motd}"
    )
    payload = {"content": content}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as _resp:
            return
    except Exception as exc:
        # Fallback: try curl (helps when local Python certs are misconfigured)
        try:
            import shutil as _shutil
            if _shutil.which("curl") is None:
                raise
            payload_str = json.dumps(payload, ensure_ascii=False)
            subprocess.run(
                [
                    "curl",
                    "-sS",
                    "-X",
                    "POST",
                    "-H",
                    "Content-Type: application/json",
                    "-d",
                    payload_str,
                    webhook_url,
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        except Exception:
            raise exc


def apply_settings_map(
    ini_path: str,
    settings: Dict[str, Union[int, float, str, bool]],
    dry_run: bool,
    precision: int,
    insert_missing_keys: bool,
    backup_manager: BackupManager,
) -> Tuple[bool, List[str]]:
    changes: List[str] = []
    lines = read_text_lines(ini_path)

    for key, raw_value in settings.items():
        value_str = format_value(raw_value, precision)
        old_lines = list(lines)
        if insert_missing_keys or key_exists_in_section(lines, SERVER_SETTINGS_SECTION, key):
            lines, _ = upsert_key_in_section(lines, SERVER_SETTINGS_SECTION, key, value_str)
            if lines != old_lines:
                changes.append(f"{key} -> {value_str}")
        else:
            # Skip keys that don't already exist in the INI
            changes.append(f"(skipped) {key} not present in [{SERVER_SETTINGS_SECTION}]")

    if not changes:
        return False, []

    if dry_run:
        return True, changes

    backup_path = backup_manager.ensure_backup()
    write_text_lines(ini_path, lines)
    result_msgs = changes if backup_path is None else [f"Backup: {backup_path}"] + changes
    return True, result_msgs


def is_numeric_value(value: Union[int, float, str, bool]) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool))


def is_string_value(value: Union[int, float, str, bool]) -> bool:
    return isinstance(value, str)


def merge_settings_additive(
    maps: List[Dict[str, Union[int, float, str, bool]]],
    append_string_keys: Optional[List[str]] = None,
    string_joiner: str = " <BR> ",
    merge_rules: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Union[int, float, str, bool]]:
    """Merge settings across multiple maps.

    Strategies:
      - Default numeric: add
      - multiplicative_keys: multiply numeric values
      - min_keys / max_keys: take min/max of numeric
      - append_string_keys: append strings using joiner
      - Otherwise last value wins
    """
    append_set = set(append_string_keys or [])
    multiplicative = set((merge_rules or {}).get("multiplicative_keys", []))
    min_keys = set((merge_rules or {}).get("min_keys", []))
    max_keys = set((merge_rules or {}).get("max_keys", []))

    merged: Dict[str, Union[int, float, str, bool]] = {}
    for m in maps:
        for k, v in m.items():
            if is_numeric_value(v) and k in merged and is_numeric_value(merged[k]):
                cur = float(merged[k])  # type: ignore[arg-type]
                val = float(v)
                if k in multiplicative:
                    merged[k] = cur * val
                elif k in min_keys:
                    merged[k] = min(cur, val)
                elif k in max_keys:
                    merged[k] = max(cur, val)
                else:
                    merged[k] = cur + val
                continue

                
            if k in merged and k in append_set and is_string_value(merged[k]) and is_string_value(v):
                left = str(merged[k])
                right = str(v)
                if right and right not in left:
                    merged[k] = (left + string_joiner + right) if left else right
                continue
            merged[k] = v
    return merged


def apply_caps(
    settings: Dict[str, Union[int, float, str, bool]],
    caps: Dict[str, Dict[str, Union[int, float]]],
) -> Dict[str, Union[int, float, str, bool]]:
    """Clamp numeric values according to per-key caps: { key: {min, max} }"""
    if not isinstance(caps, dict) or not caps:
        return settings
    clamped: Dict[str, Union[int, float, str, bool]] = {}
    for k, v in settings.items():
        if is_numeric_value(v) and isinstance(caps.get(k), dict):
            cap = caps[k]
            vmin = cap.get("min")
            vmax = cap.get("max")
            val = float(v)  # type: ignore[arg-type]
            if isinstance(vmin, (int, float)):
                val = max(float(vmin), val)
            if isinstance(vmax, (int, float)):
                val = min(float(vmax), val)
            clamped[k] = val
        else:
            clamped[k] = v
    return clamped


# ------------------------------
# CLI and orchestration
# ------------------------------


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Adjust Conan Exiles server settings based on real-world moon phase",
    )
    parser.add_argument(
        "--ini-path",
        required=True,
        help="Absolute path to ServerSettings.ini",
    )
    parser.add_argument(
        "--event-file",
        required=True,
        help="Path to JSON file describing moon-phase mapping, events, and restart policy",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and show changes without writing to disk",
    )
    parser.add_argument(
        "--restart-cmd",
        default=None,
        help="Optional shell command to restart the server after writing",
    )
    parser.add_argument(
        "--precision",
        type=int,
        default=6,
        help="Decimal precision when writing values",
    )
    parser.add_argument(
        "--now",
        default=None,
        help="Override current time (ISO 8601, e.g., 2025-08-01T00:00:00Z)",
    )
    parser.add_argument(
        "--phase-day",
        type=int,
        default=None,
        help="Override using a synthetic timestamp for the given lunar day index (0..29)",
    )
    parser.add_argument(
        "--json-summary",
        action="store_true",
        help="Emit a JSON summary of computed values and applied settings to stdout",
    )
    parser.add_argument(
        "--discord-post",
        action="store_true",
        help="If set, post a summary to Discord via webhook",
    )
    parser.add_argument(
        "--discord-webhook-url",
        default=None,
        help="Discord webhook URL (if omitted, reads DISCORD_WEBHOOK_URL env)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    ini_path = os.path.abspath(args.ini_path)
    if not os.path.isfile(ini_path):
        print(f"ERROR: INI not found: {ini_path}", file=sys.stderr)
        return 2

    event_file_path = os.path.abspath(args.event_file)
    if not os.path.isfile(event_file_path):
        print(f"ERROR: Event file not found: {event_file_path}", file=sys.stderr)
        return 2

    # Load event configuration
    try:
        with open(event_file_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as exc:
        print(f"ERROR: Failed to parse event file: {exc}", file=sys.stderr)
        return 2

    # Precision override from file if present, else CLI arg
    precision = int(config.get("precision", args.precision))

    # Decide behavior: phase mapping and/or discrete events
    # Time override handling for tests
    if args.phase_day is not None:
        if args.phase_day < 0 or args.phase_day > 29:
            print("ERROR: --phase-day must be between 0 and 29", file=sys.stderr)
            return 2
        now_utc = timestamp_for_phase_day(args.phase_day)
    elif args.now:
        raw = str(args.now).strip()
        # Accept 'Z' suffix
        if raw.endswith('Z'):
            raw = raw[:-1] + '+00:00'
        try:
            parsed = dt.datetime.fromisoformat(raw)
        except Exception as exc:
            print(f"ERROR: Failed to parse --now: {exc}", file=sys.stderr)
            return 2
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        now_utc = parsed.astimezone(dt.timezone.utc)
    else:
        now_utc = dt.datetime.now(dt.timezone.utc)
    illumination_fraction, phase_days, synodic_days = compute_lunar_state(now_utc)
    phase_name = categorize_moon_phase(illumination_fraction, phase_days, synodic_days)
    phase_bucket = categorize_phase_bucket_by_day(phase_days)

    # Backup configuration
    backup_cfg = (config or {}).get("backup", {})
    backup_dir = backup_cfg.get("dir") if isinstance(backup_cfg, dict) else None
    backup_keep = int(backup_cfg.get("keep", 10)) if isinstance(backup_cfg, dict) else 10
    backup_one = bool(backup_cfg.get("one_backup_per_run", True)) if isinstance(backup_cfg, dict) else True
    backup_manager = BackupManager(
        ini_path=ini_path,
        backup_dir=backup_dir,
        keep=backup_keep,
        one_backup_per_run=backup_one,
    )

    # Prepare JSON summary (filled progressively if requested)
    summary: Dict[str, Union[str, int, float, Dict, List]] = {}
    last_event_motd: str = ""

    # Track keys set during this run (for default reversion later)
    set_keys_current_run: set = set()

    # 1) Apply continuous moon-phase mapping, if enabled
    moon_cfg = (config or {}).get("moon_phase", {})
    any_changes = False
    change_msgs: List[str] = []
    if moon_cfg.get("enabled", True):
        mapping = moon_cfg.get("mapping", {})
        gamma = float(moon_cfg.get("gamma", 1.0))

        # Allow mapping keys to be explicit INI keys, and provide defaults for common ones
        # If user uses shorthand keys, translate to INI keys
        translation = {
            "harvest": "HarvestAmountMultiplier",
            "npc_damage": "NPCDamageMultiplier",
            "npc_health": "NPCHealthMultiplier",
        }
        minmax_by_key: Dict[str, Dict[str, float]] = {}
        for k, v in mapping.items():
            if not isinstance(v, dict):
                continue
            ini_key = translation.get(k, k)
            minmax_by_key[ini_key] = {"min": float(v.get("min", 1.0)), "max": float(v.get("max", 1.0))}

        scaled_values = compute_scaled_values(
            illumination_fraction=illumination_fraction,
            minmax_by_key=minmax_by_key,
            gamma=gamma,
        )
        caps_cfg = (config or {}).get("caps", {})
        if isinstance(caps_cfg, dict):
            scaled_values = apply_caps(scaled_values, caps_cfg)

        print(
            f"UTC: {now_utc.isoformat()} | Illumination: {illumination_fraction:.4f} | Phase: {phase_name} | Bucket: {phase_bucket}"
        )
        if scaled_values:
            pretty = ", ".join(f"{k}: {v:.3f}" for k, v in scaled_values.items())
            print(f"Continuous scaled -> {pretty}")

        if args.json_summary:
            summary.update({
                "timestamp_utc": now_utc.isoformat(),
                "phase_day": int(math.floor(phase_days)),
                "illumination": illumination_fraction,
                "phase_name": phase_name,
                "phase_bucket": phase_bucket,
                "gamma": gamma,
                "mapping": minmax_by_key,
                "caps": caps_cfg if isinstance(caps_cfg, dict) else {},
                "scaled_values": scaled_values,
            })

        if scaled_values:
            set_keys_current_run.update(scaled_values.keys())
            changed, msgs = apply_settings_map(
                ini_path=ini_path,
                settings=scaled_values,
                dry_run=args.dry_run,
                precision=precision,
                insert_missing_keys=bool(config.get("insert_missing_keys", False)),
                backup_manager=backup_manager,
            )
            any_changes = any_changes or changed
            change_msgs.extend(msgs)

    # 2) Apply discrete event presets, if any are active
    events_cfg = (config or {}).get("events", {})
    active_events: List[Dict[str, Union[str, Dict[str, Union[int, float, str, bool]]]]] = []

    # Phase-based event activation
    phase_events = events_cfg.get("phases", {}) if isinstance(events_cfg.get("phases", {}), dict) else {}
    selected_phase_event = phase_events.get(phase_name) or phase_events.get(phase_bucket)
    if isinstance(selected_phase_event, dict) and selected_phase_event.get("enabled", True):
        active_events.append(selected_phase_event)

    # Additional event categories: calendar, weather, custom
    for key in ["calendar", "weather", "custom"]:
        lst = events_cfg.get(key, [])
        if isinstance(lst, list):
            for evt in lst:
                if isinstance(evt, dict) and evt.get("enabled", False):
                    active_events.append(evt)

    # Collect and merge active events first, then apply once additively
    merged_event_settings: List[Dict[str, Union[int, float, str, bool]]] = []
    applied_event_names: List[str] = []
    for evt in active_events:
        name = str(evt.get("name", "event"))
        settings = evt.get("settings", {})
        if not isinstance(settings, dict):
            continue
        trigger = evt.get("trigger")
        should_apply = True
        if isinstance(trigger, dict):
            should_apply = is_trigger_active(
                trigger=trigger,
                now_utc=now_utc,
                illumination_fraction=illumination_fraction,
                phase_days=phase_days,
                synodic_days=synodic_days,
                root_config=config,
            )
        if not should_apply:
            continue
        merged_event_settings.append(settings)
        applied_event_names.append(name)

    if merged_event_settings:
        append_keys = []
        try:
            append_keys = list((config or {}).get("string_append_keys", []))
        except Exception:
            append_keys = []
        merge_rules = {}
        try:
            cfg_rules = (config or {}).get("merge", {})
            if isinstance(cfg_rules, dict):
                merge_rules = {
                    "multiplicative_keys": list(cfg_rules.get("multiplicative_keys", [])),
                    "min_keys": list(cfg_rules.get("min_keys", [])),
                    "max_keys": list(cfg_rules.get("max_keys", [])),
                }
        except Exception:
            merge_rules = {}

        additive_settings = merge_settings_additive(
            merged_event_settings,
            append_string_keys=append_keys,
            string_joiner=str((config or {}).get("string_append_joiner", " <BR> ")),
            merge_rules=merge_rules,
        )
        # Optional MOTD header/footer
        motd_cfg = (config or {}).get("motd", {})
        if isinstance(motd_cfg, dict):
            header = str(motd_cfg.get("header", ""))
            footer = str(motd_cfg.get("footer", ""))
            always = bool(motd_cfg.get("always_include", False))
            joiner = str((config or {}).get("string_append_joiner", " <BR> "))
            has_motd = "ServerMessageOfTheDay" in additive_settings and isinstance(additive_settings["ServerMessageOfTheDay"], str)
            if (header or footer) and (has_motd or always):
                base = str(additive_settings.get("ServerMessageOfTheDay", ""))
                parts = []
                if header:
                    parts.append(header)
                if base:
                    parts.append(base)
                if footer:
                    parts.append(footer)
                additive_settings["ServerMessageOfTheDay"] = joiner.join([p for p in parts if p])
        caps_cfg = (config or {}).get("caps", {})
        if isinstance(caps_cfg, dict):
            additive_settings = apply_caps(additive_settings, caps_cfg)  
        pretty = ", ".join(f"{k}: {v}" for k, v in additive_settings.items())
        print(f"Applying merged events: {', '.join(applied_event_names)} -> {pretty}")
        if args.json_summary:
            summary["events_applied"] = applied_event_names
            summary["additive_event_settings"] = additive_settings
        # Track keys set via events
        set_keys_current_run.update(additive_settings.keys())
        # Capture MOTD if present for Discord summary
        if isinstance(additive_settings.get("ServerMessageOfTheDay"), str):
            last_event_motd = str(additive_settings.get("ServerMessageOfTheDay"))
        changed, msgs = apply_settings_map(
            ini_path=ini_path,
            settings=additive_settings, 
            dry_run=args.dry_run,
            precision=precision,
            insert_missing_keys=bool(config.get("insert_missing_keys", False)),
            backup_manager=backup_manager,
        )
        any_changes = any_changes or changed
        for name in applied_event_names:
            change_msgs.extend([f"[{name}] {m}" for m in msgs])

    # 3) Revert managed keys not set this run back to defaults
    managed_keys = []
    try:
        managed_keys = list((config or {}).get("managed_keys", []))
    except Exception:
        managed_keys = []
    defaults_map = {}
    try:
        defaults_cfg = (config or {}).get("defaults", {})
        if isinstance(defaults_cfg, dict):
            defaults_map = defaults_cfg
    except Exception:
        defaults_map = {}

    if managed_keys and defaults_map:
        revert_settings = {}
        for k in managed_keys:
            if k not in set_keys_current_run and k in defaults_map:
                revert_settings[k] = defaults_map[k]
        if revert_settings:
            print(
                "Reverting unmanaged keys to defaults: "
                + ", ".join(f"{k}={v}" for k, v in revert_settings.items())
            )
            changed, msgs = apply_settings_map(
                ini_path=ini_path,
                settings=revert_settings,
                dry_run=args.dry_run,
                precision=precision,
                insert_missing_keys=bool(config.get("insert_missing_keys", False)),
                backup_manager=backup_manager,
            )
            any_changes = any_changes or changed
            change_msgs.extend([f"[defaults] {m}" for m in msgs])

    if args.json_summary and summary:
        try:
            print(json.dumps(summary))
        except Exception:
            pass

    if not any_changes:
        if args.discord_post:
            webhook = args.discord_webhook_url or os.environ.get("DISCORD_WEBHOOK_URL")
            if webhook:
                try:
                    _post_discord_summary(
                        webhook,
                        phase_name,
                        phase_bucket,
                        illumination_fraction,
                        applied_event_names,
                        last_event_motd,
                    )
                    print("Posted summary to Discord.")
                except Exception as _exc:
                    print("WARNING: Failed to post Discord summary.")
        print("No changes necessary (already up to date).")
        return 0

    print("Changes:")
    for msg in change_msgs:
        print(f" - {msg}")

    # Optionally post to Discord (allowed in dry-run for preview/testing)
    if args.discord_post:
        webhook = args.discord_webhook_url or os.environ.get("DISCORD_WEBHOOK_URL")
        if webhook:
            try:
                _post_discord_summary(webhook, phase_name, phase_bucket, illumination_fraction, applied_event_names, last_event_motd)
                print("Posted summary to Discord.")
            except Exception as _exc:
                print("WARNING: Failed to post Discord summary.")

    if args.dry_run:
        return 0

    # Determine restart command: CLI override > event file > none
    restart_cfg = (config or {}).get("restart", {})
    restart_cmd = args.restart_cmd or restart_cfg.get("command")
    if restart_cmd:
        print(f"Restarting server: {restart_cmd}")
        try:
            completed = subprocess.run(
                restart_cmd, shell=True, check=True, capture_output=True, text=True
            )
            if completed.stdout:
                print(completed.stdout.strip())
            if completed.stderr:
                print(completed.stderr.strip())
        except subprocess.CalledProcessError as exc:
            print(
                f"WARNING: Restart command failed with exit code {exc.returncode}.",
                file=sys.stderr,
            )
            if exc.stdout:
                print(exc.stdout)
            if exc.stderr:
                print(exc.stderr, file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


