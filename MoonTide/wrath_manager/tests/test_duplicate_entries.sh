#!/usr/bin/env bash
set -euo pipefail

# Test script for duplicate entries bug fix
# This test verifies that wrath_manager properly removes duplicate settings

SCRIPT_DIR=$(cd "$(dirname "$0")/.." && pwd)
ROOT="$SCRIPT_DIR"
TEST_SCRIPT="$ROOT/tests/test_duplicate_entries.py"

if [[ ! -f "$TEST_SCRIPT" ]]; then
  echo "Test script not found: $TEST_SCRIPT" >&2
  exit 2
fi

echo "Running duplicate entries test..."
python3 "$TEST_SCRIPT"

exit $?

