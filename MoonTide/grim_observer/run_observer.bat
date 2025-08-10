@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Grim Observer - Conan Exiles Log Monitor
REM Simple Windows batch wrapper

set "SCRIPT_DIR=%~dp0"
set "GRIM_SCRIPT=%SCRIPT_DIR%grim_observer.py"
set "MAP=exiled"

REM Parse map argument
if "%~1"=="" (
    echo Usage: run_observer.bat [exiled^|siptah]
    echo.
    echo Examples:
    echo   run_observer.bat exiled
    echo   run_observer.bat siptah
    echo.
    pause
    exit /b 1
)

set "MAP=%~1"

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
    echo Please create the secrets file for the %MAP% map
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

REM Run the observer with scan-monitor mode
echo.
echo Starting Grim Observer for %MAP% map...
echo Log file: %LOG_FILE_PATH%
echo Press Ctrl+C to stop
echo.

python "%GRIM_SCRIPT%" scan-monitor "%LOG_FILE_PATH%" --map %MAP% --discord --verbose

echo.
echo Observer stopped.
pause
