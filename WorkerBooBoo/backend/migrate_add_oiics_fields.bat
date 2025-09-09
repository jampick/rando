@echo off
echo ========================================
echo   OIICS Fields Database Migration
echo ========================================
echo.
echo This script will add new OIICS fields to your database
echo to provide more detailed incident information.
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found, using system Python
)

echo.
echo Running migration script...
python migrate_add_oiics_fields.py

echo.
echo Migration completed!
echo.
pause

