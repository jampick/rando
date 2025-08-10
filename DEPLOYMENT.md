# 🚀 Deployment Guide for Rando Project

This guide shows you how to deploy your Rando project to your server quickly and reliably, replacing the old zip-and-copy method.

## 🎯 **Why This is Better Than Zip Files**

| Old Method (Zip) | New Method (Git) |
|------------------|------------------|
| ❌ Manual file copying | ✅ Automatic deployment |
| ❌ Risk of missing files | ✅ Complete code sync |
| ❌ No version tracking | ✅ Full git history |
| ❌ Slow and error-prone | ✅ Fast and reliable |
| ❌ Hard to rollback | ✅ Easy rollback with git |

## 🚀 **Quick Start - Choose Your Method**

### **Option A: Remote Deployment (SSH) - 3 Steps**

#### 1. **Setup Configuration**
```bash
# Copy the config template
cp deploy.config deploy.config.local

# Edit with your server details
nano deploy.config.local
```

#### 2. **Update Your Server Details**
```bash
# In deploy.config.local, change these values:
SERVER_USER=your_actual_username
SERVER_HOST=your_server_ip_or_hostname
SERVER_PATH=/path/to/your/server/directory
```

#### 3. **Deploy!**
```bash
# Make the script executable (Linux/Mac)
chmod +x deploy_improved.sh

# Run deployment
./deploy_improved.sh
```

### **Option B: Local Deployment (Windows Server) - 2 Steps**

This option runs directly on your Windows server and uses a **two-step deployment process**:

1. **🔄 Git Sync**: Downloads latest code to a staging area (`GIT_SYNC_PATH`)
2. **📋 Copy to Destination**: Copies files to the actual server location (`DESTINATION_PATH`)

#### 1. **Setup Configuration**
```batch
# Copy the config template
copy deploy_local.config deploy_local.config.local

# Edit with your server details
notepad deploy_local.config.local
```

**Key Configuration Options:**
```bash
# Git sync location (staging area)
GIT_SYNC_PATH=C:\MoonTideTools\git_sync

# Final destination (where code runs)
DESTINATION_PATH=C:\MoonTideTools

# Backup location
BACKUP_PATH=C:\MoonTideTools\backup
```

#### 2. **Deploy!**
```batch
# Run the batch file (double-click or command line)
deploy_local.bat

# OR use PowerShell (more features)
deploy_local.ps1
```

**Advanced Usage:**
```powershell
# Git sync only (don't copy to destination)
.\deploy_local.ps1 -SkipCopy

# Deploy to custom locations
.\deploy_local.ps1 -GitSyncPath "D:\Staging" -DestinationPath "C:\Production"

# Deploy and restart services
.\deploy_local.ps1 -RestartServices

# Preview mode - show what would happen without executing
.\deploy_local.ps1 -Preview
```

## 📋 **What You Need**

- ✅ **SSH access** to your server
- ✅ **Git** installed on both your local machine and server
- ✅ **SSH key** set up (recommended) or password authentication
- ✅ **Server directory** where you want to deploy

## 🔧 **Configuration Options**

### **Basic Configuration** (`deploy.config.local`)
```bash
# Required - Server connection
SERVER_USER=admin
SERVER_HOST=192.168.1.100
SERVER_PATH=/opt/conan-exiles

# Required - Git branches
LOCAL_BRANCH=main
REMOTE_BRANCH=main

# Optional - SSH customization
SSH_KEY_PATH=~/.ssh/my_custom_key
SSH_OPTIONS=-o StrictHostKeyChecking=no

# Optional - Service management
PRE_DEPLOY_CMD="sudo systemctl stop conan-exiles"
POST_DEPLOY_CMD="sudo systemctl start conan-exiles"
```

### **Advanced Options**
- **Custom SSH keys**: Use `SSH_KEY_PATH` for non-standard keys
- **Service management**: Automatically stop/start services during deployment
- **Custom SSH options**: Handle host key verification, timeouts, etc.

## 🎮 **Deployment Process**

The script automatically:

1. **🔍 Checks prerequisites** (git repo, SSH, config)
2. **📝 Handles uncommitted changes** (asks if you want to commit)
3. **📤 Pushes to GitHub** (ensures remote is up-to-date)
4. **🖥️ Deploys to server** (clones or updates repository)
5. **⚙️ Runs post-deployment commands** (if configured)

## 🚨 **Troubleshooting**

### **Common Issues**

| Problem | Solution |
|---------|----------|
| "Configuration file not found" | Run `cp deploy.config deploy.config.local` |
| "Not in a git repository" | Run script from project root directory |
| "SSH connection failed" | Check server details and SSH key setup |
| "Permission denied" | Ensure SSH key has correct permissions (600) |

### **SSH Key Setup**
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Copy to server
ssh-copy-id username@server_ip

# Test connection
ssh username@server_ip
```

## 🔄 **Rollback (If Something Goes Wrong)**

```bash
# On your server, rollback to previous version
cd /path/to/your/server/directory
git log --oneline -5  # See recent commits
git reset --hard HEAD~1  # Go back 1 commit
# OR
git reset --hard <commit_hash>  # Go to specific commit
```

## 📱 **Platform Support**

### **Remote Deployment (SSH)**
- **Linux/Mac**: Use `deploy_improved.sh`
- **Windows**: Use `deploy.bat` (basic version)
- **Cross-platform**: Use `deploy.sh` (basic version)

### **Local Deployment (Windows Server)**
- **Windows Batch**: Use `deploy_local.bat` (simple, works everywhere)
- **Windows PowerShell**: Use `deploy_local.ps1` (advanced features, better error handling)
- **Configuration**: Use `deploy_local.config` for easy customization

## 🎯 **Pro Tips**

### **Two-Step Deployment Benefits**
- **🔄 Staging Area**: Test code in `GIT_SYNC_PATH` before copying to production
- **💾 Safe Updates**: Backup destination before copying new files
- **🔍 Code Review**: Examine changes in staging area before deployment
- **⚡ Fast Rollback**: Quick revert by copying from backup
- **🛡️ Production Safety**: Keep production code separate from Git operations
- **👁️ Preview Mode**: See exactly what commands will run before execution

### **Preview Mode - Safety First!**
The `-Preview` flag lets you see exactly what will happen without making any changes:

**PowerShell:**
```powershell
.\deploy_local.ps1 -Preview
```

**Batch File:**
```batch
deploy_local.bat -preview
```

**What You'll See:**
- 🔍 **Backup commands** that would create backups
- 📋 **Copy commands** that would move files
- 🗑️ **Delete commands** that would remove old directories
- 📊 **Summary** of total files and paths involved

**Perfect for:**
- ✅ **Verification**: Double-check paths and file counts
- ✅ **Documentation**: See exact commands for manual execution
- ✅ **Training**: Understand what the script does
- ✅ **Debugging**: Identify configuration issues before deployment

### **General Tips**
1. **Test first**: Try deployment to a test directory before production
2. **Monitor logs**: Check server logs after deployment
3. **Backup first**: Always backup your server before major deployments
4. **Use branches**: Deploy from feature branches for testing

### **Remote Deployment Tips**
5. **Use SSH keys**: Much more secure and convenient than passwords
6. **Test SSH connection**: Verify you can connect before running deployment

### **Local Deployment Tips**
7. **Run as Administrator**: PowerShell script may need admin rights for service management
8. **Check Git installation**: Ensure Git for Windows is installed and in PATH
9. **Customize service names**: Update service names in config to match your Windows services
10. **Use PowerShell**: More features and better error handling than batch files

## 🆘 **Need Help?**

If you run into issues:

1. **Check the error message** - it usually tells you what's wrong
2. **Verify your config** - ensure server details are correct
3. **Test SSH manually** - try connecting to your server directly
4. **Check permissions** - ensure scripts are executable

## 🎉 **You're All Set!**

With this deployment system, you can now:
- ✅ Deploy in seconds instead of minutes
- ✅ Never worry about missing files
- ✅ Easily rollback if needed
- ✅ Automate service restarts
- ✅ Keep full deployment history

**Happy deploying!** 🚀
