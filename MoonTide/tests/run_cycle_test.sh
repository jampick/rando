#!/usr/bin/env bash
set -euo pipefail

# Usage: run_cycle_test.sh /abs/path/to/ServerSettings.ini /abs/path/to/events.json

INI_PATH=${1:-}
EVENT_FILE=${2:-}

if [[ -z "$INI_PATH" || -z "$EVENT_FILE" ]];
then
  echo "Usage: $0 /abs/path/to/ServerSettings.ini /abs/path/to/events.json" >&2
  exit 2
fi

if [[ ! -f "$INI_PATH" ]]; then echo "INI not found: $INI_PATH" >&2; exit 2; fi
if [[ ! -f "$EVENT_FILE" ]]; then echo "Event file not found: $EVENT_FILE" >&2; exit 2; fi

SCRIPT_DIR=$(cd "$(dirname "$0")/.." && pwd)
PY=${PYTHON:-python3}

echo "Testing full lunar cycle (phase-day 0..29) in dry-run mode..."
for d in $(seq 0 29); do
  echo "--- phase-day=$d ---"
  "$PY" "$SCRIPT_DIR/conan_moon_tuner.py" \
    --ini-path "$INI_PATH" \
    --event-file "$EVENT_FILE" \
    --phase-day "$d" \
    --dry-run
done

echo "Done."


