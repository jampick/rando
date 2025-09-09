#!/usr/bin/env bash
set -euo pipefail

# Test Blood Moon and Blue Moon trigger logic
# Usage: test_blood_blue_moon_triggers.sh /abs/path/to/ServerSettings.ini /abs/path/to/events.json

INI_PATH=${1:-}
EVENT_FILE=${2:-}

if [[ -z "$INI_PATH" || -z "$EVENT_FILE" ]]; then
  echo "Usage: $0 /abs/path/to/ServerSettings.ini /abs/path/to/events.json" >&2
  exit 2
fi

if [[ ! -f "$INI_PATH" ]]; then echo "INI not found: $INI_PATH" >&2; exit 2; fi
if [[ ! -f "$EVENT_FILE" ]]; then echo "Event file not found: $EVENT_FILE" >&2; exit 2; fi

SCRIPT_DIR=$(cd "$(dirname "$0")/.." && pwd)
PY=${PYTHON:-python3}

echo "Testing Blood Moon and Blue Moon trigger logic..."
echo

# Test cases for Blood Moon (should only trigger on weekends near full moon)
echo "[1/4] Testing Blood Moon trigger logic..."

# Test Blood Moon on Friday (day 15 = full moon, Friday)
echo "  - Blood Moon on Friday (full moon):"
if "$PY" "$SCRIPT_DIR/wrath_manager.py" \
  --ini-path "$INI_PATH" \
  --event-file "$EVENT_FILE" \
  --phase-day 15 \
  --dry-run --json-summary 2>/dev/null | grep -q "Blood Moon"; then
  echo "    PASS - Blood Moon detected on Friday full moon"
else
  echo "    FAIL - Blood Moon not detected on Friday full moon" >&2
fi

# Test Blood Moon on Saturday (day 15 = full moon, Saturday) 
echo "  - Blood Moon on Saturday (full moon):"
if "$PY" "$SCRIPT_DIR/wrath_manager.py" \
  --ini-path "$INI_PATH" \
  --event-file "$EVENT_FILE" \
  --phase-day 15 \
  --dry-run --json-summary 2>/dev/null | grep -q "Blood Moon"; then
  echo "    PASS - Blood Moon detected on Saturday full moon"
else
  echo "    FAIL - Blood Moon not detected on Saturday full moon" >&2
fi

# Test Blood Moon on Tuesday (day 15 = full moon, Tuesday - should NOT trigger)
echo "  - Blood Moon on Tuesday (full moon - should NOT trigger):"
if "$PY" "$SCRIPT_DIR/wrath_manager.py" \
  --ini-path "$INI_PATH" \
  --event-file "$EVENT_FILE" \
  --phase-day 15 \
  --dry-run --json-summary 2>/dev/null | grep -q "Blood Moon"; then
  echo "    FAIL - Blood Moon incorrectly detected on Tuesday full moon" >&2
else
  echo "    PASS - Blood Moon correctly NOT detected on Tuesday full moon"
fi

# Test Blood Moon on Friday but far from full moon (should NOT trigger)
echo "  - Blood Moon on Friday but far from full moon (should NOT trigger):"
if "$PY" "$SCRIPT_DIR/wrath_manager.py" \
  --ini-path "$INI_PATH" \
  --event-file "$EVENT_FILE" \
  --phase-day 5 \
  --dry-run --json-summary 2>/dev/null | grep -q "Blood Moon"; then
  echo "    FAIL - Blood Moon incorrectly detected far from full moon" >&2
else
  echo "    PASS - Blood Moon correctly NOT detected far from full moon"
fi

echo

# Test Blue Moon trigger logic
echo "[2/4] Testing Blue Moon trigger logic..."

# Test Blue Moon during second full moon in month (Friday-Sunday window)
echo "  - Blue Moon during weekend window:"
if "$PY" "$SCRIPT_DIR/wrath_manager.py" \
  --ini-path "$INI_PATH" \
  --event-file "$EVENT_FILE" \
  --phase-day 15 \
  --dry-run --json-summary 2>/dev/null | grep -q "Blue Moon"; then
  echo "    PASS - Blue Moon detected during weekend window"
else
  echo "    FAIL - Blue Moon not detected during weekend window" >&2
fi

echo

# Test event settings are applied correctly
echo "[3/4] Testing Blood Moon settings application..."

TMP_OUT=$(mktemp)
"$PY" "$SCRIPT_DIR/wrath_manager.py" \
  --ini-path "$INI_PATH" \
  --event-file "$EVENT_FILE" \
  --phase-day 15 \
  --dry-run --json-summary > "$TMP_OUT" 2>/dev/null

# Check for Blood Moon specific settings
if grep -q "NPCHealthMultiplier.*2.5" "$TMP_OUT"; then
  echo "  PASS - Blood Moon NPCHealthMultiplier=2.5 applied"
else
  echo "  FAIL - Blood Moon NPCHealthMultiplier not applied" >&2
fi

if grep -q "PurgeLevel.*6" "$TMP_OUT"; then
  echo "  PASS - Blood Moon PurgeLevel=6 applied"
else
  echo "  FAIL - Blood Moon PurgeLevel not applied" >&2
fi

if grep -q "StormEnabled.*true" "$TMP_OUT"; then
  echo "  PASS - Blood Moon StormEnabled=true applied"
else
  echo "  FAIL - Blood Moon StormEnabled not applied" >&2
fi

rm -f "$TMP_OUT"

echo

# Test Blue Moon settings
echo "[4/4] Testing Blue Moon settings application..."

TMP_OUT=$(mktemp)
"$PY" "$SCRIPT_DIR/wrath_manager.py" \
  --ini-path "$INI_PATH" \
  --event-file "$EVENT_FILE" \
  --phase-day 15 \
  --dry-run --json-summary > "$TMP_OUT" 2>/dev/null

# Check for Blue Moon specific settings
if grep -q "PlayerXPTimeMultiplier.*2.0" "$TMP_OUT"; then
  echo "  PASS - Blue Moon PlayerXPTimeMultiplier=2.0 applied"
else
  echo "  FAIL - Blue Moon PlayerXPTimeMultiplier not applied" >&2
fi

if grep -q "PlayerXPRateMultiplier.*4.0" "$TMP_OUT"; then
  echo "  PASS - Blue Moon PlayerXPRateMultiplier=4.0 applied"
else
  echo "  FAIL - Blue Moon PlayerXPRateMultiplier not applied" >&2
fi

rm -f "$TMP_OUT"

echo
echo "Blood Moon and Blue Moon trigger tests completed!"
