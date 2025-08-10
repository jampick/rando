@echo off
setlocal enabledelayedexpansion

REM Simple Deployment Script for Rando Project (Windows)
REM This script makes deployment faster and more reliable than zip files

echo 🚀 Rando Project Deployment Script
echo ==================================

REM Configuration - UPDATE THESE VALUES FOR YOUR SERVER
set SERVER_USER=your_username
set SERVER_HOST=your_server_ip_or_hostname
set SERVER_PATH=/path/to/your/server/directory
set LOCAL_BRANCH=main
set REMOTE_BRANCH=main

REM Check if we're in a git repository
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Not in a git repository
    echo Please run this script from the root of your rando project
    pause
    exit /b 1
)

REM Check if we have uncommitted changes
git diff-index --quiet HEAD -- >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Warning: You have uncommitted changes
    echo Current changes:
    git status --short
    echo.
    set /p COMMIT_CHANGES="Do you want to commit these changes before deploying? (y/n): "
    if /i "!COMMIT_CHANGES!"=="y" (
        echo 📝 Committing changes...
        git add .
        set /p COMMIT_MSG="Enter commit message: "
        git commit -m "!COMMIT_MSG!"
    ) else (
        echo ⚠️  Deploying with uncommitted changes...
    )
)

REM Push to GitHub
echo 📤 Pushing to GitHub...
git push origin %LOCAL_BRANCH%
if errorlevel 1 (
    echo ❌ Failed to push to GitHub
    pause
    exit /b 1
)

REM Deploy to server
echo 🖥️  Deploying to server...
echo Server: %SERVER_USER%@%SERVER_HOST%
echo Path: %SERVER_PATH%

REM Create deployment command
set DEPLOY_CMD=cd %SERVER_PATH% ^&^& if [ -d '.git' ]; then echo 'Updating existing repository...' ^&^& git fetch origin ^&^& git reset --hard origin/%REMOTE_BRANCH% ^&^& echo 'Repository updated successfully'; else echo 'Cloning repository...' ^&^& git clone https://github.com/jampick/rando.git . ^&^& git checkout %REMOTE_BRANCH% ^&^& echo 'Repository cloned successfully'; fi

REM Execute deployment
echo 🔄 Executing deployment...
ssh %SERVER_USER%@%SERVER_HOST% "%DEPLOY_CMD%"

if errorlevel 1 (
    echo ❌ Deployment failed
    pause
    exit /b 1
) else (
    echo ✅ Deployment completed successfully!
    echo.
    echo 📋 What was deployed:
    echo - Latest code from branch: %LOCAL_BRANCH%
    echo - Server location: %SERVER_PATH%
    echo - Deployed at: %date% %time%
)

pause
