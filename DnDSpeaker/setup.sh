#!/bin/bash
# Setup script for DnD Speaker - installs dependencies

set -e  # Exit on error

echo "=== DnD Speaker Setup ==="
echo ""

# Detect OS
OS="$(uname -s)"
echo "Detected OS: $OS"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ Python found: $PYTHON_VERSION"
echo ""

# Check if we should create a venv
CREATE_VENV=true
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
    read -p "Recreate venv? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing venv..."
        rm -rf venv
    else
        CREATE_VENV=false
    fi
fi

# Create venv if needed
if [ "$CREATE_VENV" = true ]; then
    echo "Creating virtual environment..."
    
    # Check if current Python has tkinter (required for GUI)
    if ! python3 -c "import tkinter" 2>/dev/null; then
        echo "⚠ Current Python doesn't have tkinter"
        
        # Check if system Python has tkinter
        if /usr/bin/python3 -c "import tkinter" 2>/dev/null 2>/dev/null; then
            echo "✓ System Python has tkinter - using system Python for venv"
            /usr/bin/python3 -m venv venv
        else
            echo "⚠ System Python also missing tkinter"
            echo "Creating venv with current Python (GUI may not work)"
            python3 -m venv venv
        fi
    else
        python3 -m venv venv
    fi
    echo "✓ Virtual environment created"
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install system dependencies (macOS)
if [ "$OS" = "Darwin" ]; then
    echo "Checking for PortAudio (required for pyaudio)..."
    if ! brew list portaudio &> /dev/null; then
        echo "⚠ PortAudio not found. Installing via Homebrew..."
        if command -v brew &> /dev/null; then
            brew install portaudio
            echo "✓ PortAudio installed"
        else
            echo "⚠ Homebrew not found. Please install PortAudio manually:"
            echo "   brew install portaudio"
            echo "   Or install pyaudio may fail."
        fi
    else
        echo "✓ PortAudio already installed"
    fi
    echo ""
fi

# Install Python dependencies
echo "Installing Python dependencies from requirements.txt..."
if pip install -r requirements.txt; then
    echo "✓ All dependencies installed successfully"
else
    echo "❌ Some dependencies failed to install"
    echo ""
    echo "Troubleshooting:"
    echo "  - If pyaudio fails on macOS, install PortAudio: brew install portaudio"
    echo "  - If pyaudio fails on Linux, install: sudo apt-get install portaudio19-dev"
    echo "  - If tkinter is missing, install: sudo apt-get install python3-tk (Linux)"
    exit 1
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To run DnD Speaker:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     python main.py"
echo ""
echo "Or use the convenience script:"
echo "    ./start.sh"
echo ""

