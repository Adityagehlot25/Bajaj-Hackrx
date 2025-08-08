#!/bin/bash

# HackRX GitHub Repository Setup Script
# Handles all edge cases for Git initialization and GitHub repository creation

REPO_NAME="Bajaj-Hackrx"
COMMIT_MESSAGE="Initial commit: HackRX FastAPI app with comprehensive error handling"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Helper functions
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
print_step() { echo -e "${MAGENTA}🔧 $1${NC}"; }

echo -e "${BLUE}🚀 HackRX GitHub Repository Setup Script${NC}"
echo -e "${BLUE}=======================================${NC}"

# Step 1: Check prerequisites
print_step "Checking prerequisites..."

# Check Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    print_success "Git is installed: $GIT_VERSION"
else
    print_error "Git is not installed. Please install Git first."
    exit 1
fi

# Check GitHub CLI
if command -v gh &> /dev/null; then
    print_success "GitHub CLI is installed"
    gh --version
else
    print_error "GitHub CLI is not installed. Please install from https://cli.github.com/"
    print_info "Install with: sudo apt install gh   # or   brew install gh"
    exit 1
fi

# Check GitHub authentication
print_step "Checking GitHub CLI authentication..."
if gh auth status &> /dev/null; then
    print_success "Authenticated with GitHub CLI"
else
    print_warning "Not authenticated with GitHub CLI"
    print_info "Please authenticate..."
    gh auth login --web
    if [ $? -ne 0 ]; then
        print_error "Failed to authenticate with GitHub CLI"
        exit 1
    fi
    print_success "Successfully authenticated with GitHub CLI"
fi

# Step 2: Initialize Git repository
print_step "Initializing Git repository..."

if [ -d ".git" ]; then
    print_warning "Git repository already initialized"
else
    git init
    if [ $? -eq 0 ]; then
        print_success "Git repository initialized"
    else
        print_error "Failed to initialize Git repository"
        exit 1
    fi
fi

# Step 3: Stage all files
print_step "Staging all files..."

git add .
if [ $? -eq 0 ]; then
    print_success "All files staged successfully"
else
    print_error "Failed to stage files"
    exit 1
fi

# Step 4: Check if there are changes to commit
STATUS=$(git status --porcelain)
if [ -z "$STATUS" ]; then
    print_warning "No changes to commit"
    HAS_CHANGES=false
else
    HAS_CHANGES=true
fi

# Step 5: Make initial commit
print_step "Creating initial commit..."

if [ "$HAS_CHANGES" = true ]; then
    git commit -m "$COMMIT_MESSAGE"
    if [ $? -eq 0 ]; then
        print_success "Initial commit created successfully"
    else
        print_error "Failed to create initial commit"
        exit 1
    fi
else
    print_info "Skipping commit - no changes to commit"
fi

# Step 6: Rename branch to main
print_step "Ensuring branch is named 'main'..."

CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
if [ "$CURRENT_BRANCH" != "main" ]; then
    git branch -M main
    if [ $? -eq 0 ]; then
        print_success "Branch renamed to 'main'"
    else
        print_warning "Could not rename branch (may already be main)"
    fi
else
    print_success "Already on 'main' branch"
fi

# Step 7: Check if GitHub repository exists
print_step "Checking if GitHub repository exists..."

if gh repo view "$REPO_NAME" &> /dev/null; then
    print_warning "Repository '$REPO_NAME' already exists on GitHub"
    CREATE_REPO=false
else
    CREATE_REPO=true
fi

# Step 8: Create GitHub repository
if [ "$CREATE_REPO" = true ]; then
    print_step "Creating GitHub repository '$REPO_NAME'..."
    
    gh repo create "$REPO_NAME" --public --description "HackRX Document Q&A API with Gemini 2.0 Flash and FastAPI"
    if [ $? -eq 0 ]; then
        print_success "GitHub repository '$REPO_NAME' created successfully"
    else
        print_error "Failed to create GitHub repository"
        exit 1
    fi
else
    print_info "Using existing GitHub repository '$REPO_NAME'"
fi

# Step 9: Get GitHub username
print_step "Getting GitHub username..."

GITHUB_USER=$(gh api user --jq .login 2>/dev/null)
if [ $? -eq 0 ]; then
    print_success "GitHub username: $GITHUB_USER"
    REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
else
    print_error "Failed to get GitHub username"
    exit 1
fi

# Step 10: Handle remote origin
print_step "Configuring remote origin..."

# Check if remote origin exists
EXISTING_REMOTE=$(git remote get-url origin 2>/dev/null)
if [ $? -eq 0 ]; then
    print_warning "Remote 'origin' already exists: $EXISTING_REMOTE"
    
    # Update remote URL if different
    if [ "$EXISTING_REMOTE" != "$REPO_URL" ]; then
        print_info "Updating remote origin URL..."
        git remote set-url origin "$REPO_URL"
        if [ $? -eq 0 ]; then
            print_success "Remote origin URL updated successfully"
        else
            print_error "Failed to update remote origin URL"
            exit 1
        fi
    else
        print_success "Remote origin is already correctly configured"
    fi
else
    # Add remote origin
    print_info "Adding remote origin..."
    git remote add origin "$REPO_URL"
    if [ $? -eq 0 ]; then
        print_success "Remote origin added successfully"
    else
        print_error "Failed to add remote origin"
        exit 1
    fi
fi

# Step 11: Push to GitHub
print_step "Pushing to GitHub..."

# Fetch first to check remote state
git fetch origin &> /dev/null

# Check if remote main exists
if git ls-remote --heads origin main | grep -q main; then
    print_info "Remote main branch exists, attempting merge..."
    git pull origin main --allow-unrelated-histories &> /dev/null
fi

# Push main branch
git push -u origin main
if [ $? -eq 0 ]; then
    print_success "Successfully pushed to GitHub!"
else
    print_warning "Standard push failed, attempting force push..."
    git push -u origin main --force
    if [ $? -eq 0 ]; then
        print_success "Successfully force-pushed to GitHub!"
    else
        print_error "Failed to push to GitHub"
        exit 1
    fi
fi

# Step 12: Verify and display results
print_step "Verifying setup..."

REMOTE_URL=$(git remote get-url origin)
CURRENT_BRANCH=$(git branch --show-current)

print_success "Setup completed successfully!"
echo ""
echo -e "${YELLOW}📋 Repository Information:${NC}"
echo -e "   Repository: ${WHITE}$REPO_NAME${NC}"
echo -e "   GitHub URL: ${WHITE}https://github.com/$GITHUB_USER/$REPO_NAME${NC}"
echo -e "   Remote URL: ${WHITE}$REMOTE_URL${NC}"
echo -e "   Current Branch: ${WHITE}$CURRENT_BRANCH${NC}"
echo ""
echo -e "${YELLOW}🎯 Next Steps:${NC}"
echo -e "   1. Visit: ${WHITE}https://github.com/$GITHUB_USER/$REPO_NAME${NC}"
echo -e "   2. Follow ${WHITE}DEPLOYMENT_GUIDE.md${NC} for deployment"
echo -e "   3. Test your deployed API using ${WHITE}test_deployed_api.py${NC}"
echo ""
print_success "Your HackRX FastAPI project is now on GitHub and ready for deployment! 🚀"

echo ""
echo -e "${GREEN}✨ Script completed!${NC}"
