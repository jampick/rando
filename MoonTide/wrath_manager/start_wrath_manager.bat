@echo off
setlocal ENABLEDELAYEDEXPANSION

rem ================================================
rem  MoonTide Settings Tuner (Windows wrapper)
rem  Supports legacy-style args:
rem    -f <ServerSettings.ini>   (REQUIRED)
rem    -e <events.json>          (OPTIONAL; default: events.json next to this .bat)
rem    -m <ignored>              (IGNORED; for MOTD from older tool)
rem    --dry-run                 (OPTIONAL)
rem ================================================

set "SCRIPT_DIR=%~dp0"
set "MOONTIDE_SCRIPT=%SCRIPT_DIR%wrath_manager.py"
set "EVENT_FILE=%SCRIPT_DIR%events.json"
set "INI_PATH="
set "EXTRA_ARGS="

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
rem pass-through any other args
set "EXTRA_ARGS=%EXTRA_ARGS% %~1"
shift
goto parse_args

:done_parse

if not defined INI_PATH (
  echo [MoonTide][ERROR] Missing required -f ^<ServerSettings.ini^>
  echo Usage: %~nx0 -f "C:\path\to\ServerSettings.ini" [-e "C:\path\to\events.json"] [--dry-run]
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
echo    EXTRA:  %EXTRA_ARGS%

"%PYTHON_EXE%" %PY_ARGS% "%MOONTIDE_SCRIPT%" --ini-path "%INI_PATH%" --event-file "%EVENT_FILE%" %EXTRA_ARGS%
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo [MoonTide][WARN] Tuner exited with code %RC%
)

endlocal & exit /b %RC%

