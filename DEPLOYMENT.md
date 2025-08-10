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

## 🚀 **Quick Start (3 Steps)**

### 1. **Setup Configuration**
```bash
# Copy the config template
cp deploy.config deploy.config.local

# Edit with your server details
nano deploy.config.local
```

### 2. **Update Your Server Details**
```bash
# In deploy.config.local, change these values:
SERVER_USER=your_actual_username
SERVER_HOST=your_server_ip_or_hostname
SERVER_PATH=/path/to/your/server/directory
```

### 3. **Deploy!**
```bash
# Make the script executable (Linux/Mac)
chmod +x deploy_improved.sh

# Run deployment
./deploy_improved.sh
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

- **Linux/Mac**: Use `deploy_improved.sh`
- **Windows**: Use `deploy.bat` (basic version)
- **Cross-platform**: Use `deploy.sh` (basic version)

## 🎯 **Pro Tips**

1. **Test first**: Try deployment to a test directory before production
2. **Use SSH keys**: Much more secure and convenient than passwords
3. **Monitor logs**: Check server logs after deployment
4. **Backup first**: Always backup your server before major deployments
5. **Use branches**: Deploy from feature branches for testing

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
