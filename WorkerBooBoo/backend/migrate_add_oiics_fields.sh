#!/bin/bash

echo "========================================"
echo "   OIICS Fields Database Migration"
echo "========================================"
echo ""
echo "This script will add new OIICS fields to your database"
echo "to provide more detailed incident information."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

# Check if virtual environment exists
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "No virtual environment found, using system Python"
fi

echo ""
echo "Running migration script..."
python3 migrate_add_oiics_fields.py

echo ""
echo "Migration completed!"
echo ""
