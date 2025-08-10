# Grim Observer - Conan Exiles Log Monitor
# PowerShell script to run the observer with map-based secrets

param(
    [Parameter(Mandatory=$true)]
    [string]$Map,
    
    [string]$Mode = "scan-monitor",
    [switch]$Verbose
)

Write-Host "Starting Grim Observer..." -ForegroundColor Green
Write-Host ""

# Set script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$GrimScript = Join-Path $ScriptDir "grim_observer.py"

# Validate mode
$ValidModes = @("scan", "monitor", "scan-monitor")
if ($Mode -notin $ValidModes) {
    Write-Host "Error: Invalid mode '$Mode'. Use scan, monitor, or scan-monitor" -ForegroundColor Red
    Write-Host "Valid modes:" -ForegroundColor Yellow
    Write-Host "  scan         - Process entire log file once, then exit" -ForegroundColor Cyan
    Write-Host "  monitor      - Monitor for new events only (no historical)" -ForegroundColor Cyan
    Write-Host "  scan-monitor - Process entire log, then monitor new events (default)" -ForegroundColor Cyan
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.6+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Load map-specific secrets
$SecretsFile = Join-Path $ScriptDir "secrets\secrets.$Map.ps1"
Write-Host "Looking for secrets file: $SecretsFile" -ForegroundColor Cyan

if (Test-Path $SecretsFile) {
    Write-Host "Loading secrets for $Map map..." -ForegroundColor Green
    & $SecretsFile
    Write-Host "Secrets file loaded" -ForegroundColor Green
} else {
    Write-Host "Error: Secrets file not found: $SecretsFile" -ForegroundColor Red
    Write-Host "" -ForegroundColor Red
    Write-Host "To fix this:" -ForegroundColor Yellow
    Write-Host "1. Copy secrets.$Map.ps1.rename to secrets.$Map.ps1" -ForegroundColor Yellow
    Write-Host "2. Edit secrets.$Map.ps1 with your actual Discord webhook and log file path" -ForegroundColor Yellow
    Write-Host "" -ForegroundColor Yellow
    Write-Host "Example:" -ForegroundColor Yellow
    Write-Host "  Copy-Item 'secrets.$Map.ps1.rename' 'secrets.$Map.ps1'" -ForegroundColor Yellow
    Write-Host "  notepad 'secrets.$Map.ps1'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if required secrets are loaded
if (-not $env:DISCORD_WEBHOOK_URL) {
    Write-Host "Error: DISCORD_WEBHOOK_URL not found in secrets" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not $env:LOG_FILE_PATH) {
    Write-Host "Error: LOG_FILE_PATH not found in secrets" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if log file exists
if (-not (Test-Path $env:LOG_FILE_PATH)) {
    Write-Host "Error: Log file not found: $($env:LOG_FILE_PATH)" -ForegroundColor Red
    Write-Host "Please update the LOG_FILE_PATH in your secrets file" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "All checks passed, starting Grim Observer..." -ForegroundColor Green
Write-Host "Starting Grim Observer for $Map map in $Mode mode..." -ForegroundColor Green
Write-Host "Log file: $($env:LOG_FILE_PATH)" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Build command arguments
$args = @($GrimScript, $Mode, $env:LOG_FILE_PATH, "--map", $Map, "--discord")
if ($Verbose) {
    $args += "--verbose"
}

Write-Host "Running command: python $($args -join ' ')" -ForegroundColor Cyan
Write-Host ""

# Run the observer
try {
    python $args
} catch {
    Write-Host "Observer stopped with error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Observer stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
