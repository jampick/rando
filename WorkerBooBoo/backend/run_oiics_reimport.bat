@echo off
echo ========================================
echo   OIICS Data Reimport and Validation
echo ========================================
echo.
echo This script will:
echo 1. Reimport existing data with OIICS fields
echo 2. Run validation tests
echo 3. Display results
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
if exist "..\..\.venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call ..\..\.venv\Scripts\activate.bat
) else (
    echo No virtual environment found, using system Python
)

echo.
echo Step 1: Running OIICS data reimport...
python reimport_with_oiics.py

if errorlevel 1 (
    echo.
    echo ERROR: Reimport failed! Check the logs above.
    pause
    exit /b 1
)

echo.
echo Step 2: Running validation tests...
python test_oiics_validation.py

if errorlevel 1 (
    echo.
    echo WARNING: Some validation tests failed! Review the results above.
) else (
    echo.
    echo SUCCESS: All validation tests passed!
)

echo.
echo Process completed! Check the logs above for details.
pause
