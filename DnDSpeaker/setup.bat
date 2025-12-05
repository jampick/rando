@echo off
REM Setup script for DnD Speaker - installs dependencies (Windows)

echo === DnD Speaker Setup ===
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Check if venv exists
if exist "venv" (
    echo Virtual environment already exists.
    set /p RECREATE="Recreate venv? (y/N): "
    if /i "%RECREATE%"=="y" (
        echo Removing existing venv...
        rmdir /s /q venv
        set CREATE_VENV=1
    ) else (
        set CREATE_VENV=0
    )
) else (
    set CREATE_VENV=1
)

REM Create venv if needed
if "%CREATE_VENV%"=="1" (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded
echo.

REM Install Python dependencies
echo Installing Python dependencies from requirements.txt...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Some dependencies failed to install
    echo.
    echo Troubleshooting:
    echo   - Make sure you have Visual C++ Build Tools installed
    echo   - For pyaudio issues, try: pip install pipwin
    echo   - Then: pipwin install pyaudio
    pause
    exit /b 1
)

echo [OK] All dependencies installed successfully
echo.
echo === Setup Complete ===
echo.
echo To run DnD Speaker:
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate
echo.
echo   2. Run the application:
echo      python main.py
echo.
echo Or use the convenience script:
echo    start.bat
echo.
pause

