#!/bin/bash

# Improved Deployment Script for Rando Project
# This script makes deployment faster and more reliable than zip files

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Function to load configuration
load_config() {
    local config_file="deploy.config.local"
    
    if [ ! -f "$config_file" ]; then
        print_error "❌ Configuration file not found: $config_file"
        echo ""
        echo "Please copy deploy.config to deploy.config.local and update the values:"
        echo "  cp deploy.config deploy.config.local"
        echo "  # Then edit deploy.config.local with your server details"
        exit 1
    fi
    
    print_status "📋 Loading configuration from $config_file"
    source "$config_file"
    
    # Validate required fields
    if [ -z "$SERVER_USER" ] || [ -z "$SERVER_HOST" ] || [ -z "$SERVER_PATH" ]; then
        print_error "❌ Missing required configuration values"
        echo "Please check: SERVER_USER, SERVER_HOST, SERVER_PATH"
        exit 1
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_status "🔍 Checking prerequisites..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "❌ Error: Not in a git repository"
        echo "Please run this script from the root of your rando project"
        exit 1
    fi
    
    # Check if git remote exists
    if ! git remote get-url origin > /dev/null 2>&1; then
        print_error "❌ Error: No 'origin' remote configured"
        echo "Please add your GitHub repository as origin:"
        echo "  git remote add origin https://github.com/jampick/rando.git"
        exit 1
    fi
    
    # Check if SSH is available
    if ! command -v ssh > /dev/null 2>&1; then
        print_error "❌ Error: SSH client not found"
        echo "Please install SSH client for your system"
        exit 1
    fi
    
    print_success "✅ Prerequisites check passed"
}

# Function to handle uncommitted changes
handle_uncommitted_changes() {
    if ! git diff-index --quiet HEAD --; then
        print_warning "⚠️  You have uncommitted changes"
        echo "Current changes:"
        git status --short
        echo ""
        read -p "Do you want to commit these changes before deploying? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "📝 Committing changes..."
            git add .
            read -p "Enter commit message: " commit_msg
            git commit -m "$commit_msg"
            print_success "✅ Changes committed"
        else
            print_warning "⚠️  Deploying with uncommitted changes..."
        fi
    fi
}

# Function to push to GitHub
push_to_github() {
    print_status "📤 Pushing to GitHub..."
    git push origin ${LOCAL_BRANCH:-main}
    if [ $? -eq 0 ]; then
        print_success "✅ Successfully pushed to GitHub"
    else
        print_error "❌ Failed to push to GitHub"
        exit 1
    fi
}

# Function to deploy to server
deploy_to_server() {
    print_status "🖥️  Deploying to server..."
    echo "Server: $SERVER_USER@$SERVER_HOST"
    echo "Path: $SERVER_PATH"
    
    # Build SSH command with options
    local ssh_cmd="ssh"
    if [ ! -z "$SSH_KEY_PATH" ]; then
        ssh_cmd="$ssh_cmd -i $SSH_KEY_PATH"
    fi
    if [ ! -z "$SSH_OPTIONS" ]; then
        ssh_cmd="$ssh_cmd $SSH_OPTIONS"
    fi
    
    # Create deployment command
    local deploy_cmd="set -e && cd $SERVER_PATH && "
    
    # Add pre-deployment commands if configured
    if [ ! -z "$PRE_DEPLOY_CMD" ]; then
        deploy_cmd="$deploy_cmd echo 'Running pre-deployment commands...' && $PRE_DEPLOY_CMD && "
    fi
    
    # Add main deployment logic
    deploy_cmd="$deploy_cmd if [ -d '.git' ]; then "
    deploy_cmd="$deploy_cmd echo 'Updating existing repository...' && "
    deploy_cmd="$deploy_cmd git fetch origin && "
    deploy_cmd="$deploy_cmd git reset --hard origin/${REMOTE_BRANCH:-main} && "
    deploy_cmd="$deploy_cmd echo 'Repository updated successfully'; "
    deploy_cmd="$deploy_cmd else "
    deploy_cmd="$deploy_cmd echo 'Cloning repository...' && "
    deploy_cmd="$deploy_cmd git clone https://github.com/jampick/rando.git . && "
    deploy_cmd="$deploy_cmd git checkout ${REMOTE_BRANCH:-main} && "
    deploy_cmd="$deploy_cmd echo 'Repository cloned successfully'; "
    deploy_cmd="$deploy_cmd fi"
    
    # Add post-deployment commands if configured
    if [ ! -z "$POST_DEPLOY_CMD" ]; then
        deploy_cmd="$deploy_cmd && echo 'Running post-deployment commands...' && $POST_DEPLOY_CMD"
    fi
    
    # Execute deployment
    print_status "🔄 Executing deployment..."
    $ssh_cmd $SERVER_USER@$SERVER_HOST "$deploy_cmd"
    
    if [ $? -eq 0 ]; then
        print_success "✅ Deployment completed successfully!"
        echo ""
        print_header "📋 Deployment Summary:"
        echo "- Latest code from branch: ${LOCAL_BRANCH:-main}"
        echo "- Server location: $SERVER_PATH"
        echo "- Deployed at: $(date)"
        if [ ! -z "$PRE_DEPLOY_CMD" ]; then
            echo "- Pre-deployment commands executed"
        fi
        if [ ! -z "$POST_DEPLOY_CMD" ]; then
            echo "- Post-deployment commands executed"
        fi
    else
        print_error "❌ Deployment failed"
        exit 1
    fi
}

# Main execution
main() {
    print_header "🚀 Rando Project Deployment Script"
    echo "=========================================="
    
    load_config
    check_prerequisites
    handle_uncommitted_changes
    push_to_github
    deploy_to_server
    
    print_success "🎉 All done! Your server is now running the latest code."
}

# Run main function
main "$@"
