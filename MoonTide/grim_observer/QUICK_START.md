# Grim Observer - Quick Start Guide

## The Problem
You're getting this error:
```
Error: 'str' object has no attribute 'exists'
```

This happens when the secrets files aren't properly configured.

## Quick Fix

### 1. Set up your secrets file
You need to create a secrets file for your map. For the "exiled" map:

**Windows (Batch):**
```batch
copy "secrets\secrets.exiled.bat.rename" "secrets\secrets.exiled.bat"
notepad "secrets\secrets.exiled.bat"
```

**PowerShell:**
```powershell
Copy-Item "secrets\secrets.exiled.ps1.rename" "secrets\secrets.exiled.ps1"
notepad "secrets\secrets.exiled.ps1"
```

### 2. Edit the secrets file
Update these values in your secrets file:
- `DISCORD_WEBHOOK_URL`: Your actual Discord webhook URL
- `LOG_FILE_PATH`: Path to your Conan Exiles log file

**Example for Windows:**
```batch
set "DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_ACTUAL_WEBHOOK"
set "LOG_FILE_PATH=C:\Conan\ConanSandbox\Saved\Logs\ConanSandbox.log"
```

**Example for PowerShell:**
```powershell
$env:DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_ACTUAL_WEBHOOK"
$env:LOG_FILE_PATH = "C:\Conan\ConanSandbox\Saved\Logs\ConanSandbox.log"
```

### 3. Run the observer

**Windows (Batch):**
```batch
run_observer.bat exiled
```

**PowerShell:**
```powershell
.\run_observer.ps1 exiled
```

## What Each Mode Does

- **scan**: Process entire log file once, then exit
- **monitor**: Monitor for new events only (no historical)
- **scan-monitor**: Process entire log, then monitor new events (default)

## Troubleshooting

1. **"Secrets file not found"**: Make sure you copied the .rename file to remove the extension
2. **"Log file not found"**: Update LOG_FILE_PATH in your secrets file to point to the actual log file
3. **"DISCORD_WEBHOOK_URL not found"**: Make sure your secrets file is properly formatted

## File Locations

- **Log file**: Usually at `C:\Conan\ConanSandbox\Saved\Logs\ConanSandbox.log`
- **Secrets**: In the `secrets\` folder
- **Scripts**: In the main grim_observer folder
