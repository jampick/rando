#!/usr/bin/env bash
set -euo pipefail

# Usage: test_bilingual_motd.sh [/abs/path/to/ServerSettings.ini] [/abs/path/to/events.json]

ROOT=$(cd "$(dirname "$0")/.." && pwd)
INI=${1:-"$ROOT/tests/ServerSettings.test.ini"}
EVENTS=${2:-"$ROOT/events.json"}

if [[ ! -f "$INI" ]]; then echo "INI not found: $INI" >&2; exit 2; fi
if [[ ! -f "$EVENTS" ]]; then echo "Events file not found: $EVENTS" >&2; exit 2; fi

PY=${PYTHON:-python3}

TMP_RAW=$(mktemp)
TMP_JSON=$(mktemp)
trap 'rm -f "$TMP_RAW" "$TMP_JSON"' EXIT

set +e
$PY "$ROOT/wrath_manager.py" \
  --ini-path "$INI" \
  --event-file "$EVENTS" \
  --dry-run --phase-day 15 --json-summary > "$TMP_RAW" 2>/dev/null
rc=$?
set -e
if [[ $rc -ne 0 ]]; then echo "Runner failed" >&2; exit 1; fi

grep -E '^\{' "$TMP_RAW" | tail -n 1 > "$TMP_JSON" || true
if ! [[ -s "$TMP_JSON" ]]; then echo "No JSON summary found" >&2; exit 1; fi

MOTD=$(jq -r '.additive_event_settings.ServerMessageOfTheDay' "$TMP_JSON")
if [[ -z "$MOTD" || "$MOTD" == "null" ]]; then echo "No MOTD in summary" >&2; exit 1; fi

# Expected substrings (loosely match events.json content). Adjust if you edit events.json.
# Use resilient anchors to avoid minor spacing/punctuation diffs in pretty output
EN_HDR="Crom cares not"
JA_HDR="クロムはお前の運命に興味はない"
EN_EVT="Full Moon:"
JA_EVT="満月"
EN_FTR="Fight. Build. Bleed."
JA_FTR="戦え。築け。"

idx() { awk -v a="$1" 'BEGIN{print index(ARGV[1],a)}' "$MOTD"; }

order_ok() {
  local first second
  first=$(idx "$1"); second=$(idx "$2")
  [[ "$first" -gt 0 && "$second" -gt 0 && "$first" -lt "$second" ]]
}

order_ok "$EN_HDR" "$JA_HDR" && \
order_ok "$EN_EVT" "$JA_EVT" && \
order_ok "$EN_FTR" "$JA_FTR" || { echo "FAIL: EN->JA order not satisfied" >&2; exit 1; }

echo "bilingual motd: PASS"


