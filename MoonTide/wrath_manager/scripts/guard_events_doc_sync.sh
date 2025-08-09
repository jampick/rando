#!/usr/bin/env bash
set -euo pipefail

# Guard: if MoonTide/events.json changes, require MoonTide/EVENTS_DESIGN.md to change too.

BASE_REF=${1:-}
HEAD_REF=${2:-}

if [[ -z "$BASE_REF" || -z "$HEAD_REF" ]]; then
  # Fallback: compare last commit
  BASE_REF="HEAD~1"
  HEAD_REF="HEAD"
fi

changed=$(git diff --name-only "$BASE_REF" "$HEAD_REF" | tr -d '\r')

requires_doc_update=false
doc_updated=false

if echo "$changed" | grep -q '^MoonTide/events.json$'; then
  requires_doc_update=true
fi
if echo "$changed" | grep -q '^MoonTide/EVENTS_DESIGN.md$'; then
  doc_updated=true
fi

if [[ "$requires_doc_update" == true && "$doc_updated" != true ]]; then
  echo "ERROR: MoonTide/events.json changed without updating MoonTide/EVENTS_DESIGN.md" >&2
  echo "Changed files:" >&2
  echo "$changed" >&2
  exit 1
fi

echo "OK: Event JSON/docs sync check passed"

