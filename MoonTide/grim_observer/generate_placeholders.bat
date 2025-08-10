@echo off
echo Generating placeholder images for Discord embeds...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.7+ and try again.
    pause
    exit /b 1
)

REM Check if Pillow is installed
python -c "from PIL import Image" >nul 2>&1
if errorlevel 1 (
    echo Installing Pillow (PIL)...
    pip install Pillow
    if errorlevel 1 (
        echo ERROR: Failed to install Pillow. Please install manually: pip install Pillow
        pause
        exit /b 1
    )
)

REM Generate the images
echo.
echo Running image generation script...
python placeholder_images.py

echo.
echo Done! Check the 'placeholder_images' folder for your images.
echo.
pause
