#!/bin/bash

echo "Generating placeholder images for Discord embeds..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.7+ and try again."
    exit 1
fi

# Check if Pillow is installed
if ! python3 -c "from PIL import Image" &> /dev/null; then
    echo "Installing Pillow (PIL)..."
    pip3 install Pillow
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install Pillow. Please install manually: pip3 install Pillow"
        exit 1
    fi
fi

# Generate the images
echo
echo "Running image generation script..."
python3 placeholder_images.py

echo
echo "Done! Check the 'placeholder_images' folder for your images."
echo
