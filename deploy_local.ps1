param(
    [string]$Branch = "main",
    [string]$GitSyncPath = "C:\MoonTideTools\git_sync",
    [string]$DestinationPath = "C:\MoonTideTools",
    [string]$LocalSource = "",
    [switch]$RestartServices,
    [switch]$Force,
    [switch]$SkipCopy,
    [switch]$Preview,
    [switch]$MoonTideOnly
)

$GitHubRepo = "https://github.com/jampick/rando.git"
$BackupPath = Join-Path $DestinationPath "backup"
$MoonTideSubfolder = "MoonTide"

function Write-Status { param($Message) Write-Host $Message -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host $Message -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host $Message -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host $Message -ForegroundColor Red }
function Write-Header { param($Message) Write-Host $Message -ForegroundColor Magenta }

function Sync-GitRepository {
    Set-Location $GitSyncPath
    if (Test-Path ".git") {
        Write-Status "Found existing repository, updating..."
        try {
            git fetch origin
            Write-Success "Fetched latest changes"
        }
        catch {
            Write-Error "Failed to fetch from GitHub"
            Read-Host "Press Enter to exit"
            exit 1
        }
        $newCommits = git log HEAD..origin/$Branch --oneline 2>$null
        if (-not $newCommits -and -not $Force) {
            Write-Success "Already up to date!"
            return
        }
        try {
            git reset --hard origin/$Branch
            Write-Success "Repository updated successfully!"
        }
        catch {
            Write-Error "Failed to update repository"
            Read-Host "Press Enter to exit"
            exit 1
        }
    } else {
        Write-Status "No repository found, cloning from GitHub..."
        try {
            git clone $GitHubRepo .
            Write-Success "Repository cloned successfully!"
        }
        catch {
            Write-Error "Failed to clone repository"
            Read-Host "Press Enter to exit"
            exit 1
        }
        try {
            git checkout $Branch
            Write-Success "Checked out branch: $Branch"
        }
        catch {
            Write-Error "Failed to checkout branch $Branch"
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
}

function Preview-CopyCommands {
    Write-Header "PREVIEW MODE - Copy Commands That Would Run:"
    Write-Host ""
    if (Test-Path $DestinationPath) {
        Write-Status "Backup that would be created:"
        $backupName = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        $backupFullPath = Join-Path $BackupPath $backupName
        Write-Host "  Copy-Item -Path '$DestinationPath' -Destination '$backupFullPath' -Recurse -Force" -ForegroundColor Yellow
        Write-Host ""
    }
    Write-Status "Copy commands that would run:"
    try {
        if ($MoonTideOnly) {
            $moonTidePath = Join-Path $GitSyncPath $MoonTideSubfolder
            if (Test-Path $moonTidePath) {
                $itemsToCopy = Get-ChildItem -Path $moonTidePath -Exclude ".git" | Where-Object { $_.Name -ne ".git" }
                Write-Status "MoonTide-only mode: Copying from $MoonTideSubfolder subfolder"
            } else {
                Write-Warning "MoonTide subfolder not found at: $moonTidePath"
                return
            }
        } else {
            $itemsToCopy = Get-ChildItem -Path $GitSyncPath -Exclude ".git" | Where-Object { $_.Name -ne ".git" }
        }
        if ($itemsToCopy.Count -eq 0) {
            Write-Warning "No files found in Git sync location to copy"
            return
        }
        foreach ($item in $itemsToCopy) {
            $destPath = Join-Path $DestinationPath $item.Name
            if ($item.PSIsContainer) {
                if (Test-Path $destPath) {
                    Write-Host "  Remove-Item -Path '$destPath' -Recurse -Force" -ForegroundColor Red
                }
                Write-Host "  Copy-Item -Path '$($item.FullName)' -Destination '$DestinationPath' -Recurse -Force" -ForegroundColor Green
            } else {
                Write-Host "  Copy-Item -Path '$($item.FullName)' -Destination '$DestinationPath' -Force" -ForegroundColor Green
            }
        }
        Write-Host ""
        Write-Success "Preview complete! Run without -Preview to execute these commands."
        Write-Host ""
        Write-Host "Summary:" -ForegroundColor White
        Write-Host "  - Files to copy: $($itemsToCopy.Count)" -ForegroundColor White
        if ($MoonTideOnly) {
            Write-Host "  - Source: $(Join-Path $GitSyncPath $MoonTideSubfolder)" -ForegroundColor White
            Write-Host "  - Mode: MoonTide-only" -ForegroundColor White
        } else {
            Write-Host "  - Source: $GitSyncPath" -ForegroundColor White
            Write-Host "  - Mode: Full repository" -ForegroundColor White
        }
        Write-Host "  - Destination: $DestinationPath" -ForegroundColor White
        Write-Host "  - Backup location: $BackupPath" -ForegroundColor White
    }
    catch {
        Write-Error "Error during preview: $($_.Exception.Message)"
    }
}

function Copy-ToDestination {
    Write-Status "Creating backup of destination..."
    $backupName = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    $backupFullPath = Join-Path $BackupPath $backupName
    try {
        if (Test-Path $DestinationPath) {
            Copy-Item -Path $DestinationPath -Destination $backupFullPath -Recurse -Force
            Write-Success "Backup created: $backupName"
        }
    }
    catch {
        Write-Warning "Warning: Could not create backup: $($_.Exception.Message)"
    }
    Write-Status "Copying files to destination..."
    try {
        if ($MoonTideOnly) {
            $moonTidePath = Join-Path $GitSyncPath $MoonTideSubfolder
            if (Test-Path $moonTidePath) {
                $itemsToCopy = Get-ChildItem -Path $moonTidePath -Exclude ".git" | Where-Object { $_.Name -ne ".git" }
                Write-Status "MoonTide-only mode: Copying from $MoonTideSubfolder subfolder"
            } else {
                Write-Error "MoonTide subfolder not found at: $moonTidePath"
                Read-Host "Press Enter to exit"
                exit 1
            }
        } else {
            $itemsToCopy = Get-ChildItem -Path $GitSyncPath -Exclude ".git" | Where-Object { $_.Name -ne ".git" }
        }
        foreach ($item in $itemsToCopy) {
            $destPath = Join-Path $DestinationPath $item.Name
            if ($item.PSIsContainer) {
                if (Test-Path $destPath) {
                    Remove-Item -Path $destPath -Recurse -Force
                }
                Copy-Item -Path $item.FullName -Destination $DestinationPath -Recurse -Force
            } else {
                Copy-Item -Path $item.FullName -Destination $DestinationPath -Force
            }
        }
        Write-Success "Files copied to destination successfully!"
    }
    catch {
        Write-Error "Failed to copy files to destination: $($_.Exception.Message)"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

function Show-Status {
    Write-Header "Deployment Summary:"
    Write-Host ""
    Write-Host "- Repository: $GitHubRepo" -ForegroundColor White
    Write-Host "- Branch: $Branch" -ForegroundColor White
    Write-Host "- Git Sync Path: $GitSyncPath" -ForegroundColor White
    Write-Host "- Destination Path: $DestinationPath" -ForegroundColor White
    if ($MoonTideOnly) {
        Write-Host "- Mode: MoonTide-only" -ForegroundColor White
    } else {
        Write-Host "- Mode: Full repository" -ForegroundColor White
    }
    Write-Host "- Deployed at: $(Get-Date)" -ForegroundColor White
    Write-Host ""
    Write-Status "Recent commits:"
    try {
        $originalLocation = Get-Location
        Set-Location $GitSyncPath
        git log --oneline -5
        Set-Location $originalLocation
    }
    catch {
        Write-Warning "Could not show recent commits"
    }
    Write-Host ""
    Write-Success "Deployment completed successfully!"
    Write-Host ""
    Write-Host "Tip: You can run this script anytime to update to the latest version" -ForegroundColor White
    Write-Host "Tip: Previous versions are backed up in: $BackupPath" -ForegroundColor White
    Write-Host ""
    if (-not $RestartServices) {
        $restart = Read-Host "Do you want to restart Conan Exiles services? (y/n)"
        if ($restart -eq "y" -or $restart -eq "Y") {
            Restart-ConanServices
        }
    }
}

function Restart-ConanServices {
    Write-Status "Restarting Conan Exiles services..."
    $services = @("Conan Exiles", "Conan Exiles Dedicated Server")
    foreach ($service in $services) {
        try {
            $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
            if ($svc -and $svc.Status -eq "Running") {
                Write-Status "Stopping $service..."
                Stop-Service -Name $service -Force
                Write-Success "$service stopped"
            }
        }
        catch {
            Write-Warning "Could not stop $service (may not be running)"
        }
    }
    Start-Sleep -Seconds 3
    foreach ($service in $services) {
        try {
            $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
            if ($svc) {
                Write-Status "Starting $service..."
                Start-Service -Name $service
                Write-Success "$service started"
            }
        }
        catch {
            Write-Warning "Could not start $service"
        }
    }
    Write-Success "Services restarted!"
}

function Show-Help {
    Write-Header "Usage Examples:"
    Write-Host ""
    Write-Host "Basic deployment:" -ForegroundColor White
    Write-Host "  .\deploy_local.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Deploy specific branch:" -ForegroundColor White
    Write-Host "  .\deploy_local.ps1 -Branch develop" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Deploy to custom path:" -ForegroundColor White
    Write-Host "  .\deploy_local.ps1 -DestinationPath D:\MyServer" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Deploy and restart services:" -ForegroundColor White
    Write-Host "  .\deploy_local.ps1 -RestartServices" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Force update (even if no changes):" -ForegroundColor White
    Write-Host "  .\deploy_local.ps1 -Force" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Deploy only MoonTide folder:" -ForegroundColor White
    Write-Host "  .\deploy_local.ps1 -MoonTideOnly" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Preview mode (show what would happen):" -ForegroundColor White
    Write-Host "  .\deploy_local.ps1 -Preview" -ForegroundColor Yellow
    Write-Host ""
}

function Deploy-Project {
    Write-Header "Rando Project Local Deployment Script"
    Write-Host "========================================" -ForegroundColor White
    Write-Host ""
    Write-Status "Checking prerequisites..."
    try {
        $gitVersion = git --version 2>$null
        if (-not $gitVersion) {
            throw "Git not found"
        }
        Write-Success "Git found: $gitVersion"
    }
    catch {
        Write-Error "Error: Git is not installed or not in PATH"
        Write-Host "Please install Git for Windows from: https://git-scm.com/download/win" -ForegroundColor White
        Read-Host "Press Enter to exit"
        exit 1
    }
    if (-not (Test-Path $GitSyncPath)) {
        Write-Status "Creating Git sync directory..."
        New-Item -ItemType Directory -Path $GitSyncPath -Force | Out-Null
    }
    if (-not (Test-Path $DestinationPath)) {
        Write-Status "Creating destination directory..."
        New-Item -ItemType Directory -Path $DestinationPath -Force | Out-Null
    }
    if (-not (Test-Path $BackupPath)) {
        New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
    }
    if ($LocalSource -and (Test-Path $LocalSource)) {
        Write-Status "Step 1: Using local source folder..."
        Write-Status "Local source: $LocalSource"
        if (Test-Path $GitSyncPath) {
            Remove-Item -Path $GitSyncPath -Recurse -Force
        }
        Copy-Item -Path $LocalSource -Destination $GitSyncPath -Recurse -Force
        Write-Success "Local source copied to sync location"
    } else {
        Write-Status "Step 1: Syncing with GitHub..."
        Sync-GitRepository
    }
    if (-not $SkipCopy) {
        if ($Preview) {
            Write-Status "Step 2: Preview mode - showing copy commands..."
            Preview-CopyCommands
        } else {
            Write-Status "Step 2: Copying to destination..."
            Copy-ToDestination
        }
    } else {
        Write-Warning "Skipping copy to destination (Git sync only)"
    }
    Show-Status
    if ($RestartServices) {
        Restart-ConanServices
    }
}

if ($args -contains "-h" -or $args -contains "--help" -or $args -contains "-?") {
    Show-Help
    exit 0
}

try {
    Deploy-Project
}
catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Success "All done! Your server is now running the latest code."
Read-Host "Press Enter to exit"
