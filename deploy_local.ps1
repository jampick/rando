# Local Deployment Script for Rando Project (Windows Server)
# This PowerShell script runs on your Windows server to pull changes from GitHub

param(
    [string]$Branch = "main",
    [string]$DeployPath = "C:\MoonTideTools",
    [switch]$RestartServices,
    [switch]$Force
)

# Configuration
$GitHubRepo = "https://github.com/jampick/rando.git"
$BackupPath = Join-Path $DeployPath "backup"

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$Magenta = "Magenta"
$White = "White"

# Function to print colored output
function Write-Status { param($Message) Write-Host $Message -ForegroundColor $Blue }
function Write-Success { param($Message) Write-Host $Message -ForegroundColor $Green }
function Write-Warning { param($Message) Write-Host $Message -ForegroundColor $Yellow }
function Write-Error { param($Message) Write-Host $Message -ForegroundColor $Red }
function Write-Header { param($Message) Write-Host $Message -ForegroundColor $Magenta }

# Main deployment function
function Deploy-Project {
    Write-Header "🚀 Rando Project Local Deployment Script"
    Write-Host "========================================" -ForegroundColor $White
    Write-Host ""

    # Check prerequisites
    Write-Status "🔍 Checking prerequisites..."
    
    # Check if Git is available
    try {
        $gitVersion = git --version 2>$null
        if (-not $gitVersion) {
            throw "Git not found"
        }
        Write-Success "✅ Git found: $gitVersion"
    }
    catch {
        Write-Error "❌ Error: Git is not installed or not in PATH"
        Write-Host "Please install Git for Windows from: https://git-scm.com/download/win" -ForegroundColor $White
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Create directories if they don't exist
    if (-not (Test-Path $DeployPath)) {
        Write-Status "📁 Creating deployment directory..."
        New-Item -ItemType Directory -Path $DeployPath -Force | Out-Null
    }

    if (-not (Test-Path $BackupPath)) {
        New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
    }

    # Change to deployment directory
    Set-Location $DeployPath

    # Check if repository exists
    if (Test-Path ".git") {
        Write-Status "📁 Found existing repository, updating..."
        
        # Create backup before updating
        Write-Status "💾 Creating backup..."
        $backupName = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        $backupFullPath = Join-Path $BackupPath $backupName
        
        try {
            Copy-Item -Path $DeployPath -Destination $backupFullPath -Recurse -Force
            Write-Success "✅ Backup created: $backupName"
        }
        catch {
            Write-Warning "⚠️  Warning: Could not create backup: $($_.Exception.Message)"
        }

        # Fetch latest changes
        Write-Status "📥 Fetching latest changes from GitHub..."
        try {
            git fetch origin
            Write-Success "✅ Fetched latest changes"
        }
        catch {
            Write-Error "❌ Failed to fetch from GitHub"
            Read-Host "Press Enter to exit"
            exit 1
        }

        # Check if there are new changes
        $newCommits = git log HEAD..origin/$Branch --oneline 2>$null
        if (-not $newCommits -and -not $Force) {
            Write-Success "✅ Already up to date!"
            Show-Status
            return
        }

        # Reset to latest version
        Write-Status "🔄 Updating to latest version..."
        try {
            git reset --hard origin/$Branch
            Write-Success "✅ Repository updated successfully!"
        }
        catch {
            Write-Error "❌ Failed to update repository"
            Read-Host "Press Enter to exit"
            exit 1
        }

    } else {
        Write-Status "📁 No repository found, cloning from GitHub..."
        
        # Clone the repository
        try {
            git clone $GitHubRepo .
            Write-Success "✅ Repository cloned successfully!"
        }
        catch {
            Write-Error "❌ Failed to clone repository"
            Read-Host "Press Enter to exit"
            exit 1
        }

        # Checkout the correct branch
        try {
            git checkout $Branch
            Write-Success "✅ Checked out branch: $Branch"
        }
        catch {
            Write-Error "❌ Failed to checkout branch $Branch"
            Read-Host "Press Enter to exit"
            exit 1
        }
    }

    # Show deployment summary
    Show-Status

    # Restart services if requested
    if ($RestartServices) {
        Restart-ConanServices
    }
}

# Function to show deployment status
function Show-Status {
    Write-Header "📋 Deployment Summary:"
    Write-Host ""
    Write-Host "- Repository: $GitHubRepo" -ForegroundColor $White
    Write-Host "- Branch: $Branch" -ForegroundColor $White
    Write-Host "- Local Path: $DeployPath" -ForegroundColor $White
    Write-Host "- Deployed at: $(Get-Date)" -ForegroundColor $White
    Write-Host ""

    # Show recent commits
    Write-Status "📝 Recent commits:"
    try {
        git log --oneline -5
    }
    catch {
        Write-Warning "⚠️  Could not show recent commits"
    }

    Write-Host ""
    Write-Success "🎉 Deployment completed successfully!"
    Write-Host ""
    Write-Host "💡 Tip: You can run this script anytime to update to the latest version" -ForegroundColor $White
    Write-Host "💡 Tip: Previous versions are backed up in: $BackupPath" -ForegroundColor $White
    Write-Host ""

    # Ask about service restart if not already specified
    if (-not $RestartServices) {
        $restart = Read-Host "Do you want to restart Conan Exiles services? (y/n)"
        if ($restart -eq "y" -or $restart -eq "Y") {
            Restart-ConanServices
        }
    }
}

# Function to restart Conan Exiles services
function Restart-ConanServices {
    Write-Status "🔄 Restarting Conan Exiles services..."
    
    # Stop services (adjust these for your specific setup)
    $services = @("Conan Exiles", "Conan Exiles Dedicated Server")
    
    foreach ($service in $services) {
        try {
            $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
            if ($svc -and $svc.Status -eq "Running") {
                Write-Status "Stopping $service..."
                Stop-Service -Name $service -Force
                Write-Success "✅ $service stopped"
            }
        }
        catch {
            Write-Warning "⚠️  Could not stop $service (may not be running)"
        }
    }

    # Wait a moment
    Start-Sleep -Seconds 3

    # Start services
    foreach ($service in $services) {
        try {
            $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
            if ($svc) {
                Write-Status "Starting $service..."
                Start-Service -Name $service
                Write-Success "✅ $service started"
            }
        }
        catch {
            Write-Warning "⚠️  Could not start $service"
        }
    }

    Write-Success "✅ Services restarted!"
}

# Function to show help
function Show-Help {
    Write-Header "Usage Examples:"
    Write-Host ""
    Write-Host "Basic deployment:" -ForegroundColor $White
    Write-Host "  .\deploy_local.ps1" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "Deploy specific branch:" -ForegroundColor $White
    Write-Host "  .\deploy_local.ps1 -Branch develop" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "Deploy to custom path:" -ForegroundColor $White
    Write-Host "  .\deploy_local.ps1 -DeployPath D:\MyServer" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "Deploy and restart services:" -ForegroundColor $White
    Write-Host "  .\deploy_local.ps1 -RestartServices" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "Force update (even if no changes):" -ForegroundColor $White
    Write-Host "  .\deploy_local.ps1 -Force" -ForegroundColor $Yellow
    Write-Host ""
}

# Check for help parameter
if ($args -contains "-h" -or $args -contains "--help" -or $args -contains "-?") {
    Show-Help
    exit 0
}

# Run deployment
try {
    Deploy-Project
}
catch {
    Write-Error "❌ Deployment failed: $($_.Exception.Message)"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Success "🎉 All done! Your server is now running the latest code."
Read-Host "Press Enter to exit"
