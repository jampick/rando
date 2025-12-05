#!/bin/bash
# Quick demo setup script

echo "=== DnD Speaker Demo Setup ==="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Check dependencies
echo ""
echo "Checking dependencies..."
python3 -c "import pyaudio" 2>/dev/null && echo "✓ PyAudio installed" || echo "❌ PyAudio missing - run: pip install pyaudio"
python3 -c "import numpy" 2>/dev/null && echo "✓ NumPy installed" || echo "❌ NumPy missing - run: pip install numpy"
python3 -c "import scipy" 2>/dev/null && echo "✓ SciPy installed" || echo "❌ SciPy missing - run: pip install scipy"
python3 -c "import keyboard" 2>/dev/null && echo "✓ Keyboard installed" || echo "❌ Keyboard missing - run: pip install keyboard"

echo ""
echo "=== To install all dependencies, run: ==="
echo "pip install -r requirements.txt"
echo ""
echo "=== Then start the app with: ==="
echo "python3 main.py"
echo ""

