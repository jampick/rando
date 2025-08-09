#!/usr/bin/env bash
set -euo pipefail

# Example: run one phase update, write a temp updated INI, and verify only expected keys changed

ROOT=$(cd "$(dirname "$0")/.." && pwd)
INI_ORIG="$ROOT/tests/ServerSettings.test.ini"
EVENTS="$ROOT/events.json"
INI_TMP=$(mktemp)
OUT_JSON=$(mktemp)
OUT_RAW=$(mktemp)

cp "$INI_ORIG" "$INI_TMP"

python3 "$ROOT/conan_moon_tuner.py" \
  --ini-path "$INI_TMP" \
  --event-file "$EVENTS" \
  --phase-day 15 \
  --json-summary > "$OUT_RAW"

# Extract JSON from mixed output
grep -E '^\{' "$OUT_RAW" | tail -n 1 > "$OUT_JSON" || true

python3 "$ROOT/tests/verify_update.py" "$INI_ORIG" "$INI_TMP" "$OUT_JSON"

rm -f "$INI_TMP" "$OUT_JSON" "$OUT_RAW"
echo "Verification complete"


