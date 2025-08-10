@echo off
setlocal enabledelayedexpansion

REM Local Deployment Script for Rando Project (Windows Server)
REM This script runs on your Windows server to pull changes from GitHub

echo 🚀 Rando Project Local Deployment Script
echo ========================================
echo.

REM Configuration - UPDATE THESE VALUES FOR YOUR SERVER
set GITHUB_REPO=https://github.com/jampick/rando.git
set LOCAL_BRANCH=main
set REMOTE_BRANCH=main
set DEPLOY_PATH=C:\MoonTideTools
set BACKUP_PATH=C:\MoonTideTools\backup

REM Colors for output (Windows 10+)
if "%TERM%"=="xterm-256color" (
    set RED=[91m
    set GREEN=[92m
    set YELLOW=[93m
    set BLUE=[94m
    set PURPLE=[95m
    set NC=[0m
) else (
    set RED=
    set GREEN=
    set YELLOW=
    set BLUE=
    set PURPLE=
    set NC=
)

REM Function to print colored output
:print_status
echo %BLUE%%~1%NC%
goto :eof

:print_success
echo %GREEN%%~1%NC%
goto :eof

:print_warning
echo %YELLOW%%~1%NC%
goto :eof

:print_error
echo %RED%%~1%NC%
goto :eof

:print_header
echo %PURPLE%%~1%NC%
goto :eof

REM Check if git is available
call :print_status "🔍 Checking prerequisites..."
git --version >nul 2>&1
if errorlevel 1 (
    call :print_error "❌ Error: Git is not installed or not in PATH"
    echo Please install Git for Windows from: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Check if deployment directory exists
if not exist "%DEPLOY_PATH%" (
    call :print_status "📁 Creating deployment directory..."
    mkdir "%DEPLOY_PATH%"
)

REM Create backup directory if it doesn't exist
if not exist "%BACKUP_PATH%" (
    mkdir "%BACKUP_PATH%"
)

REM Check if we're in a git repository
cd /d "%DEPLOY_PATH%"
if exist ".git" (
    call :print_status "📁 Found existing repository, updating..."
    
    REM Create backup before updating
    call :print_status "💾 Creating backup..."
    set BACKUP_NAME=backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    set BACKUP_NAME=!BACKUP_NAME: =0!
    xcopy "%DEPLOY_PATH%" "%BACKUP_PATH%\!BACKUP_NAME!\" /E /I /H /Y >nul 2>&1
    call :print_success "✅ Backup created: !BACKUP_NAME!"
    
    REM Fetch latest changes
    call :print_status "📥 Fetching latest changes from GitHub..."
    git fetch origin
    if errorlevel 1 (
        call :print_error "❌ Failed to fetch from GitHub"
        pause
        exit /b 1
    )
    
    REM Check if there are new changes
    git log HEAD..origin/%REMOTE_BRANCH% --oneline >nul 2>&1
    if errorlevel 1 (
        call :print_success "✅ Already up to date!"
        goto :show_status
    )
    
    REM Reset to latest version
    call :print_status "🔄 Updating to latest version..."
    git reset --hard origin/%REMOTE_BRANCH%
    if errorlevel 1 (
        call :print_error "❌ Failed to update repository"
        pause
        exit /b 1
    )
    
) else (
    call :print_status "📁 No repository found, cloning from GitHub..."
    
    REM Clone the repository
    git clone %GITHUB_REPO% .
    if errorlevel 1 (
        call :print_error "❌ Failed to clone repository"
        pause
        exit /b 1
    )
    
    REM Checkout the correct branch
    git checkout %REMOTE_BRANCH%
    if errorlevel 1 (
        call :print_error "❌ Failed to checkout branch %REMOTE_BRANCH%"
        pause
        exit /b 1
    )
)

call :print_success "✅ Repository updated successfully!"

REM Show what was deployed
:show_status
call :print_header "📋 Deployment Summary:"
echo.
echo - Repository: %GITHUB_REPO%
echo - Branch: %REMOTE_BRANCH%
echo - Local Path: %DEPLOY_PATH%
echo - Deployed at: %date% %time%
echo.

REM Show recent commits
call :print_status "📝 Recent commits:"
git log --oneline -5

echo.
call :print_success "🎉 Deployment completed successfully!"
echo.
echo 💡 Tip: You can run this script anytime to update to the latest version
echo 💡 Tip: Previous versions are backed up in: %BACKUP_PATH%
echo.

REM Optional: Ask if user wants to restart services
set /p RESTART_SERVICES="Do you want to restart Conan Exiles services? (y/n): "
if /i "!RESTART_SERVICES!"=="y" (
    call :print_status "🔄 Restarting Conan Exiles services..."
    
    REM Stop services (adjust these commands for your setup)
    echo Stopping services...
    net stop "Conan Exiles" >nul 2>&1
    net stop "Conan Exiles Dedicated Server" >nul 2>&1
    
    REM Wait a moment
    timeout /t 3 /nobreak >nul
    
    REM Start services
    echo Starting services...
    net start "Conan Exiles" >nul 2>&1
    net start "Conan Exiles Dedicated Server" >nul 2>&1
    
    call :print_success "✅ Services restarted!"
)

pause
