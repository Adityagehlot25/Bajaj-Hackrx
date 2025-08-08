#!/usr/bin/env powershell
<#
.SYNOPSIS
Complete Git + GitHub CLI setup script for HackRX FastAPI project

.DESCRIPTION
This script safely initializes Git, creates a GitHub repository using GitHub CLI,
and pushes the project with comprehensive error handling for existing setups.

.NOTES
- Handles existing Git repositories
- Manages existing remote origins
- Creates public GitHub repository using GitHub CLI
- Safe branch renaming and pushing
#>

param(
    [string]$RepoName = "Bajaj-Hackrx",
    [string]$CommitMessage = "Initial commit: HackRX FastAPI app with comprehensive error handling"
)

# Color functions for better output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Step { param($Message) Write-Host "🔧 $Message" -ForegroundColor Magenta }

Write-Host "🚀 HackRX GitHub Repository Setup Script" -ForegroundColor Blue
Write-Host "=" * 50 -ForegroundColor Blue

# Step 1: Check prerequisites
Write-Step "Checking prerequisites..."

# Check if Git is installed
try {
    $gitVersion = git --version 2>$null
    Write-Success "Git is installed: $gitVersion"
} catch {
    Write-Error "Git is not installed. Please install Git from https://git-scm.com/"
    exit 1
}

# Check if GitHub CLI is installed
try {
    $ghVersion = gh --version 2>$null
    Write-Success "GitHub CLI is installed"
    Write-Info "$ghVersion"
} catch {
    Write-Error "GitHub CLI is not installed. Please install from https://cli.github.com/"
    Write-Info "Run: winget install GitHub.cli"
    exit 1
}

# Check if authenticated with GitHub CLI
try {
    $authStatus = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Authenticated with GitHub CLI"
    } else {
        Write-Warning "Not authenticated with GitHub CLI"
        Write-Info "Running: gh auth login"
        gh auth login --web
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to authenticate with GitHub CLI"
            exit 1
        }
        Write-Success "Successfully authenticated with GitHub CLI"
    }
} catch {
    Write-Error "Failed to check GitHub CLI authentication status"
    exit 1
}

# Step 2: Initialize Git repository (if not already initialized)
Write-Step "Initializing Git repository..."

if (Test-Path ".git") {
    Write-Warning "Git repository already initialized"
    Write-Info "Continuing with existing repository..."
} else {
    try {
        git init
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Git repository initialized"
        } else {
            Write-Error "Failed to initialize Git repository"
            exit 1
        }
    } catch {
        Write-Error "Error initializing Git repository: $($_.Exception.Message)"
        exit 1
    }
}

# Step 3: Check if there are files to commit
Write-Step "Checking for files to commit..."

$status = git status --porcelain 2>$null
if (-not $status) {
    # Check if there are any files at all
    $files = Get-ChildItem -File | Where-Object { $_.Name -notmatch "^\.git" }
    if ($files.Count -eq 0) {
        Write-Error "No files found to commit"
        exit 1
    }
}

# Step 4: Stage all files
Write-Step "Staging all files..."

try {
    git add .
    if ($LASTEXITCODE -eq 0) {
        Write-Success "All files staged successfully"
    } else {
        Write-Error "Failed to stage files"
        exit 1
    }
} catch {
    Write-Error "Error staging files: $($_.Exception.Message)"
    exit 1
}

# Step 5: Check if there are changes to commit
$statusAfterAdd = git status --porcelain 2>$null
if (-not $statusAfterAdd) {
    Write-Warning "No changes to commit (all files may already be committed)"
    $hasChanges = $false
} else {
    $hasChanges = $true
}

# Step 6: Make initial commit (if there are changes)
Write-Step "Creating initial commit..."

if ($hasChanges) {
    try {
        git commit -m "$CommitMessage"
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Initial commit created successfully"
        } else {
            Write-Error "Failed to create initial commit"
            exit 1
        }
    } catch {
        Write-Error "Error creating commit: $($_.Exception.Message)"
        exit 1
    }
} else {
    Write-Info "Skipping commit - no changes to commit"
}

# Step 7: Rename branch to main (if not already main)
Write-Step "Ensuring branch is named 'main'..."

try {
    $currentBranch = git branch --show-current 2>$null
    if ($currentBranch -ne "main") {
        git branch -M main
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Branch renamed to 'main'"
        } else {
            Write-Warning "Failed to rename branch to 'main' (may already be main)"
        }
    } else {
        Write-Success "Already on 'main' branch"
    }
} catch {
    Write-Warning "Could not check/rename branch: $($_.Exception.Message)"
}

# Step 8: Check if GitHub repository already exists
Write-Step "Checking if GitHub repository exists..."

try {
    $repoExists = gh repo view "$RepoName" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Warning "Repository '$RepoName' already exists on GitHub"
        $createRepo = $false
    } else {
        $createRepo = $true
    }
} catch {
    $createRepo = $true
}

# Step 9: Create GitHub repository (if it doesn't exist)
if ($createRepo) {
    Write-Step "Creating GitHub repository '$RepoName'..."
    
    try {
        gh repo create "$RepoName" --public --description "HackRX Document Q&A API with Gemini 2.0 Flash and FastAPI"
        if ($LASTEXITCODE -eq 0) {
            Write-Success "GitHub repository '$RepoName' created successfully"
        } else {
            Write-Error "Failed to create GitHub repository"
            exit 1
        }
    } catch {
        Write-Error "Error creating GitHub repository: $($_.Exception.Message)"
        exit 1
    }
} else {
    Write-Info "Using existing GitHub repository '$RepoName'"
}

# Step 10: Get GitHub username
Write-Step "Getting GitHub username..."

try {
    $githubUser = gh api user --jq .login 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "GitHub username: $githubUser"
        $repoUrl = "https://github.com/$githubUser/$RepoName.git"
    } else {
        Write-Error "Failed to get GitHub username"
        exit 1
    }
} catch {
    Write-Error "Error getting GitHub username: $($_.Exception.Message)"
    exit 1
}

# Step 11: Handle remote origin
Write-Step "Configuring remote origin..."

try {
    # Check if remote origin exists
    $existingRemote = git remote get-url origin 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Warning "Remote 'origin' already exists: $existingRemote"
        
        # Check if it's the correct URL
        if ($existingRemote -eq $repoUrl) {
            Write-Success "Remote origin is already correctly configured"
        } else {
            Write-Info "Updating remote origin URL..."
            git remote set-url origin $repoUrl
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Remote origin URL updated successfully"
            } else {
                Write-Error "Failed to update remote origin URL"
                exit 1
            }
        }
    } else {
        # Add remote origin
        Write-Info "Adding remote origin..."
        git remote add origin $repoUrl
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Remote origin added successfully"
        } else {
            Write-Error "Failed to add remote origin"
            exit 1
        }
    }
} catch {
    Write-Error "Error configuring remote origin: $($_.Exception.Message)"
    exit 1
}

# Step 12: Push to GitHub
Write-Step "Pushing to GitHub..."

try {
    # First, try to fetch to see if remote has any commits
    git fetch origin 2>$null
    
    # Check if remote main branch exists
    $remoteBranches = git branch -r 2>$null
    $hasRemoteMain = $remoteBranches -match "origin/main"
    
    if ($hasRemoteMain) {
        Write-Info "Remote main branch exists, attempting merge..."
        # Try to merge any remote changes
        git pull origin main --allow-unrelated-histories 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Could not pull remote changes, proceeding with force push"
        }
    }
    
    # Push main branch
    git push -u origin main
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Successfully pushed to GitHub!"
    } else {
        Write-Warning "Standard push failed, attempting force push..."
        git push -u origin main --force
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Successfully force-pushed to GitHub!"
        } else {
            Write-Error "Failed to push to GitHub"
            exit 1
        }
    }
} catch {
    Write-Error "Error pushing to GitHub: $($_.Exception.Message)"
    exit 1
}

# Step 13: Verify setup
Write-Step "Verifying setup..."

try {
    $remoteUrl = git remote get-url origin
    $currentBranch = git branch --show-current
    
    Write-Success "Setup completed successfully!"
    Write-Host ""
    Write-Host "📋 Repository Information:" -ForegroundColor Yellow
    Write-Host "   Repository: $RepoName" -ForegroundColor White
    Write-Host "   GitHub URL: https://github.com/$githubUser/$RepoName" -ForegroundColor White
    Write-Host "   Remote URL: $remoteUrl" -ForegroundColor White
    Write-Host "   Current Branch: $currentBranch" -ForegroundColor White
    Write-Host ""
    Write-Host "🎯 Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Visit: https://github.com/$githubUser/$RepoName" -ForegroundColor White
    Write-Host "   2. Follow DEPLOYMENT_GUIDE.md for deployment" -ForegroundColor White
    Write-Host "   3. Test your deployed API using test_deployed_api.py" -ForegroundColor White
    Write-Host ""
    Write-Success "Your HackRX FastAPI project is now on GitHub and ready for deployment! 🚀"
    
} catch {
    Write-Warning "Setup may be incomplete. Please verify manually."
}

Write-Host ""
Write-Host "✨ Script completed!" -ForegroundColor Green
