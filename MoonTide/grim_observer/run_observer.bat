@echo off
setlocal ENABLEDELAYEDEXPANSION

REM ================================================
REM  Grim Observer - Conan Exiles Log Monitor
REM  Simple Windows batch wrapper
REM  Version: 1.0.0
REM  Date: 2025-08-09
REM ================================================

echo [DEBUG] Starting run_observer.bat v1.0.0
echo [DEBUG] Arguments: %*

set "SCRIPT_DIR=%~dp0"
set "GRIM_SCRIPT=%SCRIPT_DIR%grim_observer.py"
set "MAP=exiled"
set "MODE=scan-monitor"

echo [DEBUG] SCRIPT_DIR=%SCRIPT_DIR%
echo [DEBUG] GRIM_SCRIPT=%GRIM_SCRIPT%

REM Parse arguments
echo [DEBUG] About to check argument 1: "%~1"
echo [DEBUG] Argument 1 content: [%~1]
echo [DEBUG] Argument 2 content: [%~2]

REM More robust argument checking
set "ARG1=%~1"
set "ARG2=%~2"
echo [DEBUG] ARG1 variable set to: [%ARG1%]
echo [DEBUG] ARG2 variable set to: [%ARG2%]

REM Alternative argument checking method
echo [DEBUG] Testing alternative argument check...
if defined ARG1 (
    echo [DEBUG] ARG1 is defined
    if not "%ARG1%"=="" (
        echo [DEBUG] ARG1 is not empty
        goto :args_ok
    ) else (
        echo [DEBUG] ARG1 is empty string
    )
) else (
    echo [DEBUG] ARG1 is not defined
)

echo [DEBUG] ARGUMENT CHECK FAILED: ARG1 is empty or undefined
echo Usage: run_observer.bat [exiled^|siptah] [scan^|monitor^|scan-monitor]
echo.
echo Examples:
echo   run_observer.bat exiled
echo   run_observer.bat siptah
echo   run_observer.bat exiled monitor
echo   run_observer.bat siptah scan
echo   run_observer.bat exiled scan-monitor
echo.
echo Modes:
echo   scan        - Process entire log file once, then exit
echo   monitor     - Monitor for new events only (no historical)
echo   scan-monitor - Process entire log, then monitor new events (default)
echo.
echo Note: Auto-detection is now enabled by default. The system will
echo automatically find and monitor the most recent ConanSandbox.log file
echo in the specified log directory.
echo.
echo [DEBUG] Exiting with code 1: No arguments provided
pause
exit /b 1

:args_ok
echo [DEBUG] ARGUMENT CHECK PASSED: ARG1 is NOT empty
echo [DEBUG] Testing argument parsing...
echo [DEBUG] ARG1 equals siptah: %ARG1%==siptah
echo [DEBUG] ARG2 equals monitor: %ARG2%==monitor

set "MAP=%ARG1%"
echo [DEBUG] MAP set to: %MAP%

REM Parse mode argument (optional, defaults to scan-monitor)
if not "%ARG2%"=="" (
    set "MODE=%ARG2%"
    echo [DEBUG] MODE set to: %MODE%
) else (
    echo [DEBUG] No mode specified, using default: %MODE%
)

REM Validate mode
echo [DEBUG] Validating mode: %MODE%
if not "%MODE%"=="scan" if not "%MODE%"=="monitor" if not "%MODE%"=="scan-monitor" (
    echo Error: Invalid mode '%MODE%'. Use scan, monitor, or scan-monitor
    echo [DEBUG] Exiting with code 2: Invalid mode specified
    pause
    exit /b 2
)
echo [DEBUG] Mode validation passed

REM Check if Python is available
echo [DEBUG] Checking Python availability...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.6+ and try again
    echo [DEBUG] Exiting with code 3: Python not available
    pause
    exit /b 3
)
echo [DEBUG] Python check passed

REM Load map-specific secrets
set "SECRETS_FILE=%SCRIPT_DIR%secrets\secrets.%MAP%.bat"
echo [DEBUG] Looking for secrets file: %SECRETS_FILE%
if exist "%SECRETS_FILE%" (
    echo Loading secrets for %MAP% map...
    echo [DEBUG] Secrets file exists, calling it...
    call "%SECRETS_FILE%"
    echo [DEBUG] Secrets file loaded
    echo [DEBUG] DISCORD_WEBHOOK_URL=%DISCORD_WEBHOOK_URL%
    echo [DEBUG] LOG_FILE_PATH=%LOG_FILE_PATH%
) else (
    echo Error: Secrets file not found: %SECRETS_FILE%
    echo.
    echo To fix this:
    echo 1. Copy secrets.%MAP%.bat.rename to secrets.%MAP%.bat
    echo 2. Edit secrets.%MAP%.bat with your actual Discord webhook and log file path
    echo.
    echo Example:
    echo   copy secrets.exiled.bat.rename secrets.exiled.bat
    echo   copy secrets.siptah.bat.rename secrets.siptah.bat
    echo.
    echo [DEBUG] Exiting with code 4: Secrets file not found
    pause
    exit /b 4
)

REM Check if required secrets are loaded
echo [DEBUG] Checking if DISCORD_WEBHOOK_URL is defined...
if not defined DISCORD_WEBHOOK_URL (
    echo Error: DISCORD_WEBHOOK_URL not found in secrets
    echo [DEBUG] DISCORD_WEBHOOK_URL is not defined
    echo [DEBUG] Exiting with code 5: DISCORD_WEBHOOK_URL not defined
    pause
    exit /b 5
)
echo [DEBUG] DISCORD_WEBHOOK_URL check passed

echo [DEBUG] Checking if LOG_FILE_PATH is defined...
if not defined LOG_FILE_PATH (
    echo Error: LOG_FILE_PATH not found in secrets
    echo [DEBUG] LOG_FILE_PATH is not defined
    echo [DEBUG] Exiting with code 6: LOG_FILE_PATH not defined
    pause
    exit /b 6
)
echo [DEBUG] LOG_FILE_PATH check passed

REM Run the observer with selected mode
echo.
echo [DEBUG] All checks passed, starting Grim Observer...
echo Starting Grim Observer for %MAP% map in %MODE% mode...
echo Log directory: %LOG_FILE_PATH%
echo Auto-detection: ENABLED
echo Press Ctrl+C to stop
echo.

echo [DEBUG] Running command: python "%GRIM_SCRIPT%" %MODE% "%LOG_FILE_PATH%" --map %MAP% --discord --force-curl --auto-detect-log
python "%GRIM_SCRIPT%" %MODE% "%LOG_FILE_PATH%" --map %MAP% --discord --force-curl --auto-detect-log

echo.
echo [DEBUG] Python script finished
echo Observer stopped.
echo [DEBUG] Exiting with code 0: Success
pause
exit /b 0
