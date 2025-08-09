#!/usr/bin/env bash
set -euo pipefail

# Usage: test_defaults_revert.sh /abs/path/to/ServerSettings.ini [/abs/path/to/events.json]

INI_ORIG=${1:-}
EVENTS_BASE=${2:-}

if [[ -z "$INI_ORIG" ]]; then
  echo "Usage: $0 /abs/path/to/ServerSettings.ini [/abs/path/to/events.json]" >&2
  exit 2
fi

SCRIPT_DIR=$(cd "$(dirname "$0")/.." && pwd)
ROOT="$SCRIPT_DIR"
WRATH="$ROOT/wrath_manager.py"
EVENTS_DEFAULT="$ROOT/events.json"
EVENTS_INPUT="${EVENTS_BASE:-$EVENTS_DEFAULT}"

if [[ ! -f "$INI_ORIG" ]]; then echo "INI not found: $INI_ORIG" >&2; exit 2; fi
if [[ ! -f "$EVENTS_INPUT" ]]; then echo "Events not found: $EVENTS_INPUT" >&2; exit 2; fi

TMP_INI=$(mktemp)
TMP_EVENTS=$(mktemp)
TMP_EVENTS2=$(mktemp)

cp "$INI_ORIG" "$TMP_INI"
cp "$EVENTS_INPUT" "$TMP_EVENTS"

# Append a test calendar event that is always active and sets a managed key
jq '.events.calendar += [{
  "enabled": true,
  "name": "Test Defaults Revert",
  "trigger": {"type":"date_window","start":"01-01","end":"12-31"},
  "settings": {"PlayerSprintSpeedScale": 0.9}
}]' "$TMP_EVENTS" > "$TMP_EVENTS2"
mv "$TMP_EVENTS2" "$TMP_EVENTS"

echo "[1/2] Apply event (sets PlayerSprintSpeedScale=0.9)"
python3 "$WRATH" --ini-path "$TMP_INI" --event-file "$TMP_EVENTS" --phase-day 15 --json-summary >/dev/null

if grep -E '^PlayerSprintSpeedScale=0\.9(0+)?$' "$TMP_INI" >/dev/null; then
  echo " - set check: PASS"
else
  echo " - set check: FAIL (expected PlayerSprintSpeedScale=0.9)" >&2
  sed -n '1,200p' "$TMP_INI" | grep -E '^PlayerSprintSpeedScale='
  exit 1
fi

echo "[2/2] Disable event and ensure default reverts (PlayerSprintSpeedScale=1)"
jq '(.events.calendar[] | select(.name=="Test Defaults Revert").enabled)=false' "$TMP_EVENTS" > "$TMP_EVENTS2"
mv "$TMP_EVENTS2" "$TMP_EVENTS"

python3 "$WRATH" --ini-path "$TMP_INI" --event-file "$TMP_EVENTS" --phase-day 15 --json-summary >/dev/null

if grep -E '^PlayerSprintSpeedScale=1(\.0+)?$' "$TMP_INI" >/dev/null; then
  echo " - revert check: PASS"
else
  echo " - revert check: FAIL (expected PlayerSprintSpeedScale=1)" >&2
  sed -n '1,200p' "$TMP_INI" | grep -E '^PlayerSprintSpeedScale='
  exit 1
fi

rm -f "$TMP_INI" "$TMP_EVENTS" "$TMP_EVENTS2"
echo "Defaults revert test: PASS"
exit 0


