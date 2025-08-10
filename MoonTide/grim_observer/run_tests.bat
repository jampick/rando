@echo off
echo Running Grim Observer Test Suite...
echo.

python3 run_tests.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All tests passed successfully!
    pause
) else (
    echo.
    echo Some tests failed. Check the output above.
    pause
)
