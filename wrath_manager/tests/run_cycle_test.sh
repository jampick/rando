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
pass=0
fail=0
tmp_out=$(mktemp)
tmp_json=$(mktemp)
for d in $(seq 0 29); do
  echo "--- phase-day=$d ---"
  if "$PY" "$SCRIPT_DIR/wrath_manager.py" \
    --ini-path "$INI_PATH" \
    --event-file "$EVENT_FILE" \
    --phase-day "$d" \
    --dry-run --json-summary > "$tmp_out"; then
    # Extract JSON summary line(s) from mixed output
    grep -E "^\{" "$tmp_out" | tail -n 1 > "$tmp_json" || true
    # Basic assertion: scaled values should exist for continuous mapping keys
    if [[ -s "$tmp_json" ]] && jq -e '.scaled_values | has("HarvestAmountMultiplier")' "$tmp_json" >/dev/null 2>&1; then
      ((pass++))
    else
      echo "[WARN] Missing scaled HarvestAmountMultiplier in summary for day $d" >&2
      ((fail++))
    fi
  else
    echo "[FAIL] Script error on day $d" >&2
    ((fail++))
  fi
done
rm -f "$tmp_out" "$tmp_json"
echo "Done. Pass: $pass  Fail: $fail  Total: $((pass+fail))"
test $fail -eq 0


