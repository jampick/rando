@echo off
setlocal ENABLEDELAYEDEXPANSION

rem ================================================
rem  MoonTide Settings Tuner (Windows wrapper)
rem  Supports legacy-style args:
rem    -f <ServerSettings.ini>   (REQUIRED)
rem    -e <events.json>          (OPTIONAL; default: events.json next to this .bat)
rem    -m <ignored>              (IGNORED; for MOTD from older tool)
rem    --dry-run                 (OPTIONAL)
rem    --map <exiled|siptah>     (OPTIONAL; selects defaults + secrets)
rem ================================================

set "SCRIPT_DIR=%~dp0"
set "MOONTIDE_SCRIPT=%SCRIPT_DIR%wrath_manager.py"
set "EVENT_FILE=%SCRIPT_DIR%events.json"
set "INI_PATH="
set "EXTRA_ARGS="
set "MAP=exiled"

rem ---- Parse args ----
:parse_args
if "%~1"=="" goto done_parse
if /I "%~1"=="-f" (
  set "INI_PATH=%~2"
  shift
  shift
  goto parse_args
)
if /I "%~1"=="-e" (
  set "EVENT_FILE=%~2"
  shift
  shift
  goto parse_args
)
if /I "%~1"=="-m" (
  rem legacy MOTD file arg - ignored
  shift
  shift
  goto parse_args
)
if /I "%~1"=="--dry-run" (
  set "EXTRA_ARGS=%EXTRA_ARGS% --dry-run"
  shift
  goto parse_args
)
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
rem pass-through any other args
set "EXTRA_ARGS=%EXTRA_ARGS% %~1"
shift
goto parse_args

:done_parse

rem ---- Secrets and defaults by map ----
set "SECRETS_FILE=%SCRIPT_DIR%secrets\secrets.%MAP%.bat"
if exist "%SECRETS_FILE%" (
  call "%SECRETS_FILE%"
) else (
  echo [MoonTide][WARN] Secrets file not found: %SECRETS_FILE%
)

if not defined INI_PATH (
  set "INI_PATH=%SCRIPT_DIR%configs\%MAP%\ServerSettings.ini"
)
if "%EVENT_FILE%"=="%SCRIPT_DIR%events.json" (
  if exist "%SCRIPT_DIR%configs\%MAP%\events.json" set "EVENT_FILE=%SCRIPT_DIR%configs\%MAP%\events.json"
)

if not defined INI_PATH (
  echo [MoonTide][ERROR] Missing required -f ^<ServerSettings.ini^>
  echo Usage: %~nx0 -f "C:\path\to\ServerSettings.ini" [-e "C:\path\to\events.json"] [--dry-run] [--map exiled^|siptah]
  exit /b 2
)

if not exist "%INI_PATH%" (
  echo [MoonTide][ERROR] INI not found: %INI_PATH%
  exit /b 2
)
if not exist "%EVENT_FILE%" (
  echo [MoonTide][WARN] Event file not found at %EVENT_FILE%
  echo [MoonTide][WARN] Create one or pass -e "C:\path\to\events.json"
  exit /b 2
)
if not exist "%MOONTIDE_SCRIPT%" (
  echo [MoonTide][ERROR] Script not found: %MOONTIDE_SCRIPT%
  exit /b 2
)

rem ---- Locate Python ----
set "PYTHON_EXE=python"
where python >nul 2>&1 || set "PYTHON_EXE=py"
set "PY_ARGS="
if /I "%PYTHON_EXE%"=="py" set "PY_ARGS=-3"

echo [MoonTide] Running tuner
echo    INI:    %INI_PATH%
echo    EVENTS: %EVENT_FILE%
echo    MAP:    %MAP%
echo    EXTRA:  %EXTRA_ARGS%

"%PYTHON_EXE%" %PY_ARGS% "%MOONTIDE_SCRIPT%" --ini-path "%INI_PATH%" --event-file "%EVENT_FILE%" %EXTRA_ARGS%
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo [MoonTide][WARN] Tuner exited with code %RC%
)

endlocal & exit /b %RC%

