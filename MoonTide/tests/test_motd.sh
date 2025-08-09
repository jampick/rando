#!/usr/bin/env bash
set -euo pipefail

# Usage: test_motd.sh /abs/path/to/ServerSettings.ini /abs/path/to/events.json

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

pass=0
fail=0
tmp_out=$(mktemp)
tmp_json=$(mktemp)

echo "[1/2] Checking MOTD exists for all phase days (0..29)"
for d in $(seq 0 29); do
  if "$PY" "$SCRIPT_DIR/conan_moon_tuner.py" \
      --ini-path "$INI_PATH" \
      --event-file "$EVENT_FILE" \
      --phase-day "$d" \
      --dry-run --json-summary > "$tmp_out"; then
    grep -E "^\{" "$tmp_out" | tail -n 1 > "$tmp_json" || true
    if [[ -s "$tmp_json" ]] && jq -e '(.additive_event_settings // {}) | has("ServerMessageOfTheDay") and (.ServerMessageOfTheDay|type=="string") and (.ServerMessageOfTheDay|length>0)' "$tmp_json" >/dev/null 2>&1; then
      ((pass++))
    else
      echo "[FAIL] No MOTD for phase-day=$d" >&2
      ((fail++))
    fi
  else
    echo "[FAIL] Script error for phase-day=$d" >&2
    ((fail++))
  fi
done

echo "[2/2] Checking MOTD appends when multiple events are active (Full Moon + calendar)"
tmp_events=$(mktemp)
jq '.events.calendar += [{"enabled":true,"name":"Test Calendar","trigger":{"type":"date_window","start":"01-01","end":"12-31"},"settings":{"ServerMessageOfTheDay":"Calendar MOTD"}}]' "$EVENT_FILE" > "$tmp_events"
if "$PY" "$SCRIPT_DIR/conan_moon_tuner.py" \
      --ini-path "$INI_PATH" \
      --event-file "$tmp_events" \
      --phase-day 15 \
      --dry-run --json-summary > "$tmp_out"; then
  grep -E "^\{" "$tmp_out" | tail -n 1 > "$tmp_json" || true
  motd=$(jq -r '(.additive_event_settings // {}).ServerMessageOfTheDay // empty' "$tmp_json")
  if [[ -n "$motd" ]] && [[ "$motd" == *"Full Moon"* ]] && [[ "$motd" == *"Calendar MOTD"* ]] && [[ "$motd" == *" <BR> "* ]]; then
    ((pass++))
  else
    echo "[FAIL] MOTD did not append as expected on Full Moon + calendar: $motd" >&2
    ((fail++))
  fi
else
  echo "[FAIL] Script error during append test" >&2
  ((fail++))
fi

rm -f "$tmp_out" "$tmp_json" "$tmp_events"
echo "Done. Pass: $pass  Fail: $fail  Total: $((pass+fail))"
test $fail -eq 0


