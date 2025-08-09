#!/usr/bin/env bash
set -euo pipefail

# Unified test runner
# Usage: run_all_tests.sh [/abs/path/to/ServerSettings.ini] [/abs/path/to/events.json]

ROOT=$(cd "$(dirname "$0")/.." && pwd)
INI=${1:-"$ROOT/tests/ServerSettings.test.ini"}
EVENTS=${2:-"$ROOT/events.json"}

if [[ ! -f "$INI" ]]; then echo "INI not found: $INI" >&2; exit 2; fi
if [[ ! -f "$EVENTS" ]]; then echo "Events file not found: $EVENTS" >&2; exit 2; fi

PY=${PYTHON:-python3}

echo "Running MoonTide test suite"
echo "INI:    $INI"
echo "EVENTS: $EVENTS"
echo

overall_pass=0
overall_fail=0

# 1) Cycle test
echo "[1/3] Lunar cycle dry-run test"
set +e
bash "$ROOT/tests/run_cycle_test.sh" "$INI" "$EVENTS" > >(tee /dev/stderr) 2>/dev/null
cycle_status=$?
set -e
if [[ $cycle_status -eq 0 ]]; then
  echo " - cycle: PASS"
  ((overall_pass++))
else
  echo " - cycle: FAIL (see output above)" >&2
  ((overall_fail++))
fi
echo

# 2) MOTD test
echo "[2/3] MOTD presence and append test"
set +e
bash "$ROOT/tests/test_motd.sh" "$INI" "$EVENTS" > >(tee /dev/stderr) 2>/dev/null
motd_status=$?
set -e
if [[ $motd_status -eq 0 ]]; then
  echo " - motd: PASS"
  ((overall_pass++))
else
  echo " - motd: FAIL (see output above)" >&2
  ((overall_fail++))
fi
echo

# 3) Verify actual write deltas on a temp copy (Full Moon example)
echo "[3/3] Verify updated INI only changes expected keys (Full Moon example)"
TMP_INI=$(mktemp)
TMP_RAW=$(mktemp)
TMP_JSON=$(mktemp)
cp "$INI" "$TMP_INI"

set +e
$PY "$ROOT/wrath_manager.py" \
  --ini-path "$TMP_INI" \
  --event-file "$EVENTS" \
  --phase-day 15 \
  --json-summary > "$TMP_RAW" 2>/dev/null
grep -E '^\{' "$TMP_RAW" | tail -n 1 > "$TMP_JSON" || true
$PY "$ROOT/tests/verify_update.py" "$INI" "$TMP_INI" "$TMP_JSON" "$EVENTS" | tee /dev/stderr
verify_status=${PIPESTATUS[0]}
set -e

rm -f "$TMP_INI" "$TMP_RAW" "$TMP_JSON"

if [[ $verify_status -eq 0 ]]; then
  echo " - verify: PASS"
  ((overall_pass++))
else
  echo " - verify: FAIL (see summary above)" >&2
  ((overall_fail++))
fi

echo
echo "Summary: PASS=$overall_pass FAIL=$overall_fail TOTAL=$((overall_pass+overall_fail))"
exit $([[ $overall_fail -eq 0 ]])


