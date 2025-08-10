# Grim Observer - Conan Exiles Log Monitor
# PowerShell script to run the observer

param(
    [Parameter(Mandatory=$true)]
    [string]$LogFilePath,
    
    [string]$OutputFile = "grim_events.json",
    [switch]$Verbose,
    [double]$Interval = 1.0
)

Write-Host "Starting Grim Observer..." -ForegroundColor Green
Write-Host ""

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

# Check if log file exists
if (-not (Test-Path $LogFilePath)) {
    Write-Host "Error: Log file not found: $LogFilePath" -ForegroundColor Red
    Write-Host "Please provide a valid path to ConanSandbox.log" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Build command arguments
$args = @("grim_observer.py", "--log-file", "`"$LogFilePath`"")
if ($OutputFile) {
    $args += @("--output", "`"$OutputFile`"")
}
if ($Verbose) {
    $args += @("--verbose")
}
$args += @("--interval", $Interval)

Write-Host "Monitoring log file: $LogFilePath" -ForegroundColor Cyan
Write-Host "Output file: $OutputFile" -ForegroundColor Cyan
Write-Host "Check interval: $Interval seconds" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
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
