@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Grim Observer - Conan Exiles Log Monitor
REM Windows batch file to run the observer with map support

set "SCRIPT_DIR=%~dp0"
set "GRIM_SCRIPT=%SCRIPT_DIR%grim_observer.py"
set "LOG_FILE="
set "MAP=exiled"
set "CLI_LOG=0"
set "CONFIG_FILE=%SCRIPT_DIR%config.json"

REM ---- Parse args ----
:parse_args
if "%~1"=="" goto done_parse
if /I "%~1"=="--map" (
  set "MAP=%~2"
  shift
  shift
  goto parse_args
)
if /I "%~1"=="-map" (
  set "MAP=%~2"
  shift
  shift
  goto parse_args
)
if /I "%~1"=="--log-file" (
  set "LOG_FILE=%~2"
  set "CLI_LOG=1"
  shift
  shift
  goto parse_args
)
if /I "%~1"=="-f" (
  set "LOG_FILE=%~2"
  set "CLI_LOG=1"
  shift
  shift
  goto parse_args
)
if /I "%~1"=="--config" (
  set "CONFIG_FILE=%~2"
  shift
  shift
  goto parse_args
)
rem pass-through any other args
shift
goto parse_args

:done_parse

echo Starting Grim Observer...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.6+ and try again
    pause
    exit /b 1
)

REM ---- Load secrets by map ----
set "SECRETS_FILE=%SCRIPT_DIR%secrets\secrets.%MAP%.bat"
if exist "%SECRETS_FILE%" (
  echo [GrimObserver][INFO] Loading secrets for %MAP% map...
  call "%SECRETS_FILE%"
  echo [GrimObserver][INFO] Loaded secrets from %SECRETS_FILE%
  
  REM Display loaded environment variables
  if defined DISCORD_WEBHOOK_URL (
    echo [GrimObserver][INFO] Discord webhook configured for %MAP% map
  )
  if defined MAP_NAME (
    echo [GrimObserver][INFO] Map name: %MAP_NAME%
  )
  if defined MAP_DESCRIPTION (
    echo [GrimObserver][INFO] Map description: %MAP_DESCRIPTION%
  )
  
  REM Set default log file from secrets if not provided via CLI
  if not defined LOG_FILE (
    if defined LOG_FILE_PATH (
      set "LOG_FILE=%LOG_FILE_PATH%"
      echo [GrimObserver][INFO] Using default log file from secrets: %LOG_FILE%
    )
  )
) else (
  echo [GrimObserver][WARN] Secrets file not found: %SECRETS_FILE%
  echo [GrimObserver][WARN] Using default configuration
)

REM Check if log file path is available (either from CLI or secrets)
if not defined LOG_FILE (
    echo [GrimObserver][ERROR] Missing log file path
    echo.
    echo Usage: run_observer.bat [--map exiled^|siptah] [--log-file "path\to\ConanSandbox.log"] [--config "path\to\config.json"]
    echo.
    echo Examples:
    echo   run_observer.bat --map exiled
    echo   run_observer.bat --map siptah
    echo   run_observer.bat --map exiled --log-file "C:\Conan\ConanSandbox\Saved\Logs\ConanSandbox.log"
    echo   run_observer.bat --map siptah --log-file "C:\Conan\ConanSandbox\Saved\Logs\ConanSandbox.log" --config "C:\path\to\custom_config.json"
    echo.
    echo Note: If --log-file is not specified, the default path from secrets will be used.
    echo.
    pause
    exit /b 1
)

REM ---- Check for map-specific configs ----
set "MAP_CONFIG_DIR=%SCRIPT_DIR%configs\%MAP%"
if exist "%MAP_CONFIG_DIR%" (
  echo [GrimObserver][INFO] Found map-specific configs directory: %MAP_CONFIG_DIR%
  
  REM Check for map-specific config.json
  if exist "%MAP_CONFIG_DIR%\config.json" (
    if "%CONFIG_FILE%"=="%SCRIPT_DIR%config.json" (
      set "CONFIG_FILE=%MAP_CONFIG_DIR%\config.json"
      echo [GrimObserver][INFO] Using map-specific config: %CONFIG_FILE%
    )
  )
  
  REM Check for map-specific events or other configs
  if exist "%MAP_CONFIG_DIR%\events.json" (
    echo [GrimObserver][INFO] Found map-specific events: %MAP_CONFIG_DIR%\events.json
  )
) else (
  echo [GrimObserver][INFO] No map-specific configs found, using defaults
)

REM Run the observer
echo.
echo [GrimObserver] Running log observer
echo    LOG:    %LOG_FILE%
echo    MAP:    %MAP%
echo    CONFIG: %CONFIG_FILE%
echo    Press Ctrl+C to stop monitoring
echo.

python grim_observer.py --log-file "%LOG_FILE%" --map %MAP% --config "%CONFIG_FILE%" --verbose

echo.
echo Observer stopped.
pause
