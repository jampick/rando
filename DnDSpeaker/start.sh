#!/bin/bash
# Linux/macOS startup script for DnD Speaker

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if venv exists and activate it
if [ -d "venv" ]; then
    source venv/bin/activate
    # Verify we're actually using the venv's Python
    if [[ "$VIRTUAL_ENV" != *"DnDSpeaker"* ]] && [[ "$(which python3)" != *"DnDSpeaker/venv"* ]]; then
        echo "⚠ Warning: Virtual environment activation may have failed"
        echo "  Current Python: $(which python3)"
    fi
    echo "✓ Using DnDSpeaker virtual environment"
else
    echo "⚠ DnDSpeaker virtual environment not found."
    echo ""
    echo "Please run setup first:"
    echo "  ./setup.sh"
    echo ""
    echo "Or create venv manually:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    exit 1
fi

# Verify required dependencies are installed
echo "Checking dependencies..."
MISSING_DEPS=()

python3 -c "import keyboard" 2>/dev/null || MISSING_DEPS+=("keyboard")
python3 -c "import numpy" 2>/dev/null || MISSING_DEPS+=("numpy")
python3 -c "import scipy" 2>/dev/null || MISSING_DEPS+=("scipy")
python3 -c "import pyaudio" 2>/dev/null || MISSING_DEPS+=("pyaudio")
# tkinter is a system package, check separately
python3 -c "import tkinter" 2>/dev/null || {
    # tkinter might be available but with different import name
    python3 -c "import _tkinter" 2>/dev/null || MISSING_DEPS+=("tkinter")
}

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "❌ Missing dependencies: ${MISSING_DEPS[*]}"
    echo ""
    
    # Check if tkinter is the only missing dependency
    if [ ${#MISSING_DEPS[@]} -eq 1 ] && [[ "${MISSING_DEPS[0]}" == "tkinter" ]]; then
        echo "⚠ tkinter is a system-level dependency (not installable via pip)"
        echo ""
        
        # Check if system Python has tkinter
        if /usr/bin/python3 -c "import tkinter" 2>/dev/null; then
            echo "✓ System Python has tkinter available"
            echo ""
            echo "Solution: Recreate venv using system Python:"
            echo "  rm -rf venv"
            echo "  /usr/bin/python3 -m venv venv"
            echo "  source venv/bin/activate"
            echo "  pip install -r requirements.txt"
            echo ""
            echo "Or run setup with system Python:"
            echo "  rm -rf venv"
            echo "  /usr/bin/python3 -m venv venv"
            echo "  source venv/bin/activate"
            echo "  ./setup.sh"
        else
            echo "On macOS with Homebrew Python, tkinter is not included by default."
            echo ""
            echo "Solutions:"
            echo "  1. Install Python from python.org (includes tkinter)"
            echo "  2. Try: brew install python-tk@3.13 (may not be available)"
            echo "  3. Use system Python: /usr/bin/python3 -m venv venv"
        fi
        echo ""
        exit 1
    else
        echo "Please install dependencies:"
        echo "  pip install -r requirements.txt"
        echo ""
        echo "Or run setup:"
        echo "  ./setup.sh"
        echo ""
        
        # Special note for tkinter
        if [[ " ${MISSING_DEPS[@]} " =~ " tkinter " ]]; then
            echo "Note: tkinter requires system-level installation (see above)"
            echo ""
        fi
        
        exit 1
    fi
fi

echo "✓ All dependencies available"
echo ""

# Run the application
python3 main.py

