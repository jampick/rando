#!/usr/bin/env python3
"""
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
    --min-harvest 1.0 --max-harvest 5.0 \
    --min-npc-damage 0.6 --max-npc-damage 2.0 \
    --min-npc-health 0.7 --max-npc-health 2.5 \
    --restart-cmd "systemctl restart conanexiles"

  python3 conan_moon_tuner.py \
    --ini-path "C:/ConanServer/ConanSandbox/Saved/Config/WindowsServer/ServerSettings.ini" \
    --restart-cmd "powershell -NoProfile -Command \"Restart-Service -Name 'ConanExiles'\""

Notes
- Typical INI paths:
  - Linux:   ConanSandbox/Saved/Config/LinuxServer/ServerSettings.ini
  - Windows: ConanSandbox\Saved\Config\WindowsServer\ServerSettings.ini
- Schedule daily (e.g., midnight UTC) to track the moon smoothly.
"""

from __future__ import annotations

import argparse
import datetime as dt
import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# ------------------------------
# Lunar computation
# ------------------------------

def compute_lunar_illumination_fraction(timestamp_utc: dt.datetime) -> float:
    """Return approximate lunar illumination fraction in [0, 1].

    Uses a simple synodic cycle approximation. This is sufficient for gameplay
    tuning and avoids external dependencies.

    Approach
    - Compute days since a known new moon epoch.
    - Reduce by synodic period (29.53058867 days) to get phase age.
    - Illumination fraction is (1 - cos(phase_angle)) / 2.
    """

    if timestamp_utc.tzinfo is None:
        timestamp_utc = timestamp_utc.replace(tzinfo=dt.timezone.utc)
    else:
        timestamp_utc = timestamp_utc.astimezone(dt.timezone.utc)

    # Reference new moon: 2000-01-06 18:14 UTC (approx)
    reference_new_moon = dt.datetime(2000, 1, 6, 18, 14, tzinfo=dt.timezone.utc)
    synodic_days = 29.53058867

    delta_days = (timestamp_utc - reference_new_moon).total_seconds() / 86400.0
    phase_days = delta_days % synodic_days
    phase_angle = 2.0 * math.pi * (phase_days / synodic_days)

    illumination = 0.5 * (1.0 - math.cos(phase_angle))
    # Clamp for numerical safety
    return max(0.0, min(1.0, illumination))


def interpolate(min_value: float, max_value: float, t: float) -> float:
    """Linear interpolation between min_value and max_value using t in [0, 1]."""
    return min_value + (max_value - min_value) * t


@dataclass
class Multipliers:
    harvest_amount: float
    npc_damage: float
    npc_health: float


def compute_multipliers(
    illumination_fraction: float,
    min_harvest: float,
    max_harvest: float,
    min_npc_damage: float,
    max_npc_damage: float,
    min_npc_health: float,
    max_npc_health: float,
) -> Multipliers:
    return Multipliers(
        harvest_amount=interpolate(min_harvest, max_harvest, illumination_fraction),
        npc_damage=interpolate(min_npc_damage, max_npc_damage, illumination_fraction),
        npc_health=interpolate(min_npc_health, max_npc_health, illumination_fraction),
    )


# ------------------------------
# INI editing
# ------------------------------

SERVER_SETTINGS_SECTION = "ServerSettings"


def create_backup(ini_path: str) -> str:
    parent_dir = os.path.dirname(os.path.abspath(ini_path))
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = os.path.join(parent_dir, f"ServerSettings.ini.bak.{timestamp}")
    shutil.copy2(ini_path, backup_path)
    return backup_path


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


def apply_settings(
    ini_path: str,
    harvest_amount: float,
    npc_damage: float,
    npc_health: float,
    dry_run: bool,
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

    backup_path = create_backup(ini_path)
    write_text_lines(ini_path, lines)
    return True, [f"Backup: {backup_path}"] + changes


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
        "--min-harvest",
        type=float,
        default=1.0,
        help="Minimum HarvestAmountMultiplier at new moon",
    )
    parser.add_argument(
        "--max-harvest",
        type=float,
        default=5.0,
        help="Maximum HarvestAmountMultiplier at full moon",
    )
    parser.add_argument(
        "--min-npc-damage",
        type=float,
        default=0.6,
        help="Minimum NPCDamageMultiplier at new moon",
    )
    parser.add_argument(
        "--max-npc-damage",
        type=float,
        default=2.0,
        help="Maximum NPCDamageMultiplier at full moon",
    )
    parser.add_argument(
        "--min-npc-health",
        type=float,
        default=0.7,
        help="Minimum NPCHealthMultiplier at new moon",
    )
    parser.add_argument(
        "--max-npc-health",
        type=float,
        default=2.5,
        help="Maximum NPCHealthMultiplier at full moon",
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
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    ini_path = os.path.abspath(args.ini_path)
    if not os.path.isfile(ini_path):
        print(f"ERROR: INI not found: {ini_path}", file=sys.stderr)
        return 2

    now_utc = dt.datetime.now(dt.timezone.utc)
    illumination_fraction = compute_lunar_illumination_fraction(now_utc)
    multipliers = compute_multipliers(
        illumination_fraction=illumination_fraction,
        min_harvest=args.min_harvest,
        max_harvest=args.max_harvest,
        min_npc_damage=args.min_npc_damage,
        max_npc_damage=args.max_npc_damage,
        min_npc_health=args.min_npc_health,
        max_npc_health=args.max_npc_health,
    )

    print(
        f"UTC: {now_utc.isoformat()} | Moon illumination: {illumination_fraction:.4f}"
    )
    print(
        f"Target multipliers -> Harvest: {multipliers.harvest_amount:.3f}, "
        f"NPC Damage: {multipliers.npc_damage:.3f}, NPC Health: {multipliers.npc_health:.3f}"
    )

    changed, change_msgs = apply_settings(
        ini_path=ini_path,
        harvest_amount=multipliers.harvest_amount,
        npc_damage=multipliers.npc_damage,
        npc_health=multipliers.npc_health,
        dry_run=args.dry_run,
    )

    if not changed:
        print("No changes necessary (already up to date).")
        return 0

    print("Changes:")
    for msg in change_msgs:
        print(f" - {msg}")

    if args.dry_run:
        return 0

    if args.restart_cmd:
        print(f"Restarting server: {args.restart_cmd}")
        try:
            completed = subprocess.run(
                args.restart_cmd, shell=True, check=True, capture_output=True, text=True
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


