@echo off
setlocal ENABLEDELAYEDEXPANSION

rem ================================================
rem  Grim Observer - Conan Exiles Log Monitor
rem  Supports map-based secrets loading:
rem    --map <exiled|siptah>     (OPTIONAL; selects secrets)
rem ================================================

set "SCRIPT_DIR=%~dp0"
set "GRIM_SCRIPT=%SCRIPT_DIR%grim_observer.py"
set "LOG_FILE="
set "MODE="
set "EXTRA_ARGS="
set "MAP=exiled"
set "CLI_LOG=0"

rem ---- Parse args ----
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
if /I "%~1"=="--mode" (
  set "MODE=%~2"
  shift
  shift
  goto parse_args
)
rem pass-through any other args
set "EXTRA_ARGS=%EXTRA_ARGS% %~1"
shift
goto parse_args

:done_parse

rem ---- Secrets and defaults by map ----
set "SECRETS_FILE=%SCRIPT_DIR%secrets\secrets.%MAP%.bat"
if exist "%SECRETS_FILE%" (
  call "%SECRETS_FILE%"
  echo [GrimObserver][INFO] Loaded secrets from %SECRETS_FILE%
) else (
  echo [GrimObserver][WARN] Secrets file not found: %SECRETS_FILE%
)

rem Check if log file was provided
if not defined LOG_FILE (
  echo [GrimObserver][ERROR] Missing required log file path
  echo Usage: %~nx0 [--map exiled^|siptah] [--log-file "C:\path\to\ConanSandbox.log] [--mode scan^|monitor^|scan-monitor] [other grim_observer args]
  echo.
  echo Examples:
  echo   %~nx0 --map exiled --mode scan "C:\Conan\ConanSandbox\Saved\Logs\ConanSandbox.log"
  echo   %~nx0 --map siptah --mode monitor "C:\Conan\ConanSandbox\Saved\Logs\ConanSandbox.log"
  echo   %~nx0 --mode scan "C:\Conan\ConanSandbox\Saved\Logs\ConanSandbox.log" --webhook-only
  exit /b 2
)

rem Check if mode was provided
if not defined MODE (
  echo [GrimObserver][ERROR] Missing required mode
  echo Usage: %~nx0 [--map exiled^|siptah] [--log-file "C:\path\to\ConanSandbox.log] [--mode scan^|monitor^|scan-monitor] [other grim_observer args]
  echo.
  echo Modes:
  echo   scan         - Scan entire log file and exit
  echo   monitor      - Monitor log file for new events
  echo   scan-monitor - Scan entire log file then monitor for new events
  exit /b 2
)

if not exist "%LOG_FILE%" (
  echo [GrimObserver][ERROR] Log file not found: %LOG_FILE%
  exit /b 2
)

if not exist "%GRIM_SCRIPT%" (
  echo [GrimObserver][ERROR] Script not found: %GRIM_SCRIPT%
  exit /b 2
)

rem ---- Locate Python ----
set "PYTHON_EXE=python"
where python >nul 2>&1 || set "PYTHON_EXE=py"
set "PY_ARGS="
if /I "%PYTHON_EXE%"=="py" set "PY_ARGS=-3"

echo [GrimObserver] Running log observer
echo    MODE:   %MODE%
echo    LOG:    %LOG_FILE%
echo    MAP:    %MAP%
echo    EXTRA:  %EXTRA_ARGS%

rem Pass the mode, log file, and map parameter to grim_observer for secrets loading
"%PYTHON_EXE%" %PY_ARGS% "%GRIM_SCRIPT%" %MODE% "%LOG_FILE%" %EXTRA_ARGS% --map %MAP%
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo [GrimObserver][WARN] Observer exited with code %RC%
)

endlocal & exit /b %RC%
