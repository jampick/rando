@echo off
rem ================================================
rem  Grim Observer - Run All Tests
rem  Comprehensive test suite for grim_observer
rem ================================================

echo.
echo 🚀 Grim Observer - Running Comprehensive Test Suite
echo ================================================
echo.

rem Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.7+ and try again.
    echo.
    pause
    exit /b 1
)

rem Check if grim_observer.py exists
if not exist "grim_observer.py" (
    echo ❌ grim_observer.py not found in current directory.
    echo Please run this script from the grim_observer folder.
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
echo ✅ grim_observer.py found
echo.
echo 🧪 Starting test suite...
echo.

rem Run the comprehensive test suite
python run_all_tests.py

rem Capture the exit code
set TEST_EXIT_CODE=%errorlevel%

echo.
echo ================================================
if %TEST_EXIT_CODE%==0 (
    echo 🎉 All tests completed successfully!
) else (
    echo ⚠️  Some tests failed. Check the output above.
)
echo ================================================
echo.

pause
exit /b %TEST_EXIT_CODE%
