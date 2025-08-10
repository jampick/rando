#!/bin/bash

# Simple Deployment Script for Rando Project
# This script makes deployment faster and more reliable than zip files

set -e  # Exit on any error

# Configuration - UPDATE THESE VALUES FOR YOUR SERVER
SERVER_USER="your_username"
SERVER_HOST="your_server_ip_or_hostname"
SERVER_PATH="/path/to/your/server/directory"
LOCAL_BRANCH="main"
REMOTE_BRANCH="main"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Rando Project Deployment Script${NC}"
echo "=================================="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    echo "Please run this script from the root of your rando project"
    exit 1
fi

# Check if we have uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}⚠️  Warning: You have uncommitted changes${NC}"
    echo "Current changes:"
    git status --short
    echo ""
    read -p "Do you want to commit these changes before deploying? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}📝 Committing changes...${NC}"
        git add .
        read -p "Enter commit message: " commit_msg
        git commit -m "$commit_msg"
    else
        echo -e "${YELLOW}⚠️  Deploying with uncommitted changes...${NC}"
    fi
fi

# Push to GitHub
echo -e "${BLUE}📤 Pushing to GitHub...${NC}"
git push origin $LOCAL_BRANCH

# Deploy to server
echo -e "${BLUE}🖥️  Deploying to server...${NC}"
echo "Server: $SERVER_USER@$SERVER_HOST"
echo "Path: $SERVER_PATH"

# Create deployment command
deploy_cmd="cd $SERVER_PATH && \
if [ -d '.git' ]; then \
    echo 'Updating existing repository...' && \
    git fetch origin && \
    git reset --hard origin/$REMOTE_BRANCH && \
    echo 'Repository updated successfully'; \
else \
    echo 'Cloning repository...' && \
    git clone https://github.com/jampick/rando.git . && \
    git checkout $REMOTE_BRANCH && \
    echo 'Repository cloned successfully'; \
fi"

# Execute deployment
echo -e "${BLUE}🔄 Executing deployment...${NC}"
ssh $SERVER_USER@$SERVER_HOST "$deploy_cmd"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 What was deployed:${NC}"
    echo "- Latest code from branch: $LOCAL_BRANCH"
    echo "- Server location: $SERVER_PATH"
    echo "- Deployed at: $(date)"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi
