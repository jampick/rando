@echo off
setlocal ENABLEDELAYEDEXPANSION

rem ================================================
rem  Configure these paths for your Windows server
rem ================================================
set "INI_PATH=C:\ConanServer\ConanSandbox\Saved\Config\WindowsServer\ServerSettings.ini"
set "EVENT_FILE=C:\ConanServer\MoonTide\events.json"
set "MOONTIDE_SCRIPT=C:\ConanServer\MoonTide\conan_moon_tuner.py"

rem Optional: set a backup directory (else events.json controls it)
rem set "BACKUP_DIR=C:\ConanServer\backups"

echo [MoonTide] Preparing to tune settings before server startup...

rem ---- Check required files ----
if not exist "%INI_PATH%" (
  echo [MoonTide][ERROR] INI not found: %INI_PATH%
  exit /b 2
)
if not exist "%EVENT_FILE%" (
  echo [MoonTide][ERROR] Event file not found: %EVENT_FILE%
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

rem ---- Run tuner (no restart; server will start next) ----
echo [MoonTide] Running tuner: %PYTHON_EXE% %PY_ARGS% "%MOONTIDE_SCRIPT%"
"%PYTHON_EXE%" %PY_ARGS% "%MOONTIDE_SCRIPT%" --ini-path "%INI_PATH%" --event-file "%EVENT_FILE%" --no-restart
if errorlevel 1 (
  echo [MoonTide][WARN] Tuner exited with code %ERRORLEVEL%. Continuing to start server.
)
endlocal & exit /b 0

