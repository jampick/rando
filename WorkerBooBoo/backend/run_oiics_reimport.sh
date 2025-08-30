#!/bin/bash

echo "========================================"
echo "   OIICS Data Reimport and Validation"
echo "========================================"
echo ""
echo "This script will:"
echo "1. Reimport existing data with OIICS fields"
echo "2. Run validation tests"
echo "3. Display results"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

# Check if virtual environment exists
if [ -f "../../.venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source ../../.venv/bin/activate
else
    echo "No virtual environment found, using system Python"
fi

echo ""
echo "Step 1: Running OIICS data reimport..."
python3 reimport_with_oiics.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Reimport failed! Check the logs above."
    exit 1
fi

echo ""
echo "Step 2: Running validation tests..."
python3 test_oiics_validation.py

if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: Some validation tests failed! Review the results above."
else
    echo ""
    echo "SUCCESS: All validation tests passed!"
fi

echo ""
echo "Process completed! Check the logs above for details."
