@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Grim Observer - Conan Exiles Log Monitor
REM Simple Windows batch wrapper

set "SCRIPT_DIR=%~dp0"
set "GRIM_SCRIPT=%SCRIPT_DIR%grim_observer.py"
set "MAP=exiled"
set "MODE=scan-monitor"

REM Parse arguments
if "%~1"=="" (
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
    pause
    exit /b 1
)

set "MAP=%~1"

REM Parse mode argument (optional, defaults to scan-monitor)
if not "%~2"=="" (
    set "MODE=%~2"
)

REM Validate mode
if not "%MODE%"=="scan" if not "%MODE%"=="monitor" if not "%MODE%"=="scan-monitor" (
    echo Error: Invalid mode '%MODE%'. Use scan, monitor, or scan-monitor
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.6+ and try again
    pause
    exit /b 1
)

REM Load map-specific secrets
set "SECRETS_FILE=%SCRIPT_DIR%secrets\secrets.%MAP%.bat"
if exist "%SECRETS_FILE%" (
    echo Loading secrets for %MAP% map...
    call "%SECRETS_FILE%"
    echo Secrets loaded from %SECRETS_FILE%
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
    pause
    exit /b 1
)

REM Check if required secrets are loaded
if not defined DISCORD_WEBHOOK_URL (
    echo Error: DISCORD_WEBHOOK_URL not found in secrets
    pause
    exit /b 1
)

if not defined LOG_FILE_PATH (
    echo Error: LOG_FILE_PATH not found in secrets
    pause
    exit /b 1
)

REM Run the observer with selected mode
echo.
echo Starting Grim Observer for %MAP% map in %MODE% mode...
echo Log file: %LOG_FILE_PATH%
echo Press Ctrl+C to stop
echo.

python "%GRIM_SCRIPT%" %MODE% "%LOG_FILE_PATH%" --map %MAP% --discord --verbose

echo.
echo Observer stopped.
pause
