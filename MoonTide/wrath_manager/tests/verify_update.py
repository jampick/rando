#!/usr/bin/env python3
import sys
import json
import re
from typing import Dict, Tuple, Optional


def parse_serversettings_ini(path: str) -> Dict[str, str]:
    section = None
    kv: Dict[str, str] = {}
    keyval_re = re.compile(r"^\s*([^#;\s][^=\s]*)\s*=\s*(.*)\s*$")
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for raw in f.read().splitlines():
            line = raw.strip()
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1].strip()
                continue
            if section != "ServerSettings":
                continue
            m = keyval_re.match(raw)
            if not m:
                # ignore non key=value lines inside section
                continue
            k, v = m.group(1), m.group(2).strip()
            kv[k] = v
    return kv


def as_float_if_possible(s: str):
    try:
        return float(s)
    except Exception:
        return s


def nearly_equal(a, b, tol=1e-5, precision: Optional[int] = None):
    try:
        af = float(a)
        bf = float(b)
        if precision is not None:
            af = round(af, precision)
            bf = round(bf, precision)
            return af == bf
        return abs(af - bf) <= tol
    except Exception:
        return str(a) == str(b)


def main():
    if len(sys.argv) < 4:
        print("Usage: verify_update.py ORIGINAL_INI UPDATED_INI EXPECTED_JSON [EVENTS_JSON]", file=sys.stderr)
        return 2
    orig_ini, upd_ini, expected_json = sys.argv[1:4]
    events_json = sys.argv[4] if len(sys.argv) >= 5 else None
    precision: Optional[int] = None

    orig = parse_serversettings_ini(orig_ini)
    upd = parse_serversettings_ini(upd_ini)

    with open(expected_json, "r", encoding="utf-8") as f:
        expected = json.load(f)

    scaled = expected.get("scaled_values", {}) or {}
    added = expected.get("additive_event_settings", {}) or {}
    expected_map: Dict[str, str] = {}
    for k, v in {**scaled, **added}.items():
        expected_map[k] = str(v)

    # If events.json provided, include default reverts for managed_keys not set this run
    if events_json:
        try:
            with open(events_json, "r", encoding="utf-8") as f:
                ev = json.load(f)
            if isinstance(ev.get("precision"), int):
                precision = int(ev.get("precision"))
            managed = list(ev.get("managed_keys", [])) if isinstance(ev.get("managed_keys", []), list) else []
            defaults = ev.get("defaults", {}) if isinstance(ev.get("defaults", {}), dict) else {}
            for k in managed:
                if k not in expected_map and k in defaults:
                    expected_map[k] = str(defaults[k])
        except Exception:
            pass

    # compute changed keys
    changed = {}
    keys = set(orig.keys()) | set(upd.keys())
    for k in keys:
        if str(orig.get(k, "")) != str(upd.get(k, "")):
            changed[k] = (orig.get(k), upd.get(k))

    expected_keys = set(expected_map.keys())
    unexpected_changes = {k: changed[k] for k in changed.keys() - expected_keys}

    missing_expected = []
    wrong_values = []
    for k in expected_keys:
        if k not in upd:
            missing_expected.append(k)
        else:
            if not nearly_equal(upd[k], expected_map[k], precision=precision):
                wrong_values.append((k, upd[k], expected_map[k]))

    ok = not unexpected_changes and not missing_expected and not wrong_values

    summary = {
        "ok": ok,
        "num_changed": len(changed),
        "expected_keys": sorted(list(expected_keys)),
        "unexpected_changes": unexpected_changes,
        "missing_expected": missing_expected,
        "wrong_values": wrong_values,
    }
    print(json.dumps(summary, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())


