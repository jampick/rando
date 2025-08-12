#!/bin/bash
# ================================================
#  Grim Observer - Run All Tests
#  Comprehensive test suite for grim_observer
# ================================================

echo
echo "🚀 Grim Observer - Running Comprehensive Test Suite"
echo "================================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.7+ and try again."
    echo
    exit 1
fi

# Check if grim_observer.py exists
if [ ! -f "grim_observer.py" ]; then
    echo "❌ grim_observer.py not found in current directory."
    echo "Please run this script from the grim_observer folder."
    echo
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo "✅ grim_observer.py found"
echo
echo "🧪 Starting test suite..."
echo

# Run the comprehensive test suite
python3 run_all_tests.py

# Capture the exit code
TEST_EXIT_CODE=$?

echo
echo "================================================"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "🎉 All tests completed successfully!"
else
    echo "⚠️  Some tests failed. Check the output above."
fi
echo "================================================"
echo

exit $TEST_EXIT_CODE
