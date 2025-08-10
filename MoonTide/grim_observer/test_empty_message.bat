@echo off
echo Testing Empty Server Discord Messages
echo ====================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.7+ and try again.
    pause
    exit /b 1
)

REM Run the test script
echo Running test script...
python test_empty_message.py

echo.
echo Test completed! Check the generated JSON files and CURL commands above.
pause
