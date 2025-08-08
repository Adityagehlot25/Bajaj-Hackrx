# 🔧 Git Repository Setup Commands

## PowerShell Commands for Windows

### Step 1: Initialize Git Repository
```powershell
# Navigate to your project directory
cd "e:\final try"

# Initialize git repository
git init

# Check git status
git status
```

### Step 2: Add All Files
```powershell
# Add all files to staging area
git add .

# Verify files are staged
git status
```

### Step 3: Create Initial Commit
```powershell
# Create initial commit with descriptive message
git commit -m "Initial commit: HackRX FastAPI app with comprehensive error handling and deployment files"

# Verify commit was created
git log --oneline
```

### Step 4: Set Main Branch
```powershell
# Rename default branch to main (if not already)
git branch -M main

# Verify current branch
git branch
```

### Step 5: Add Remote Repository
```powershell
# Add remote origin (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/hackrx-fastapi-app.git

# Verify remote was added
git remote -v
```

### Step 6: Push to GitHub
```powershell
# Push to GitHub main branch
git push -u origin main

# Verify push was successful
git status
```

---

## 🚀 Complete Command Sequence (Copy & Paste)

```powershell
# Complete setup in one go
cd "e:\final try"
git init
git add .
git commit -m "Initial commit: HackRX FastAPI app with comprehensive error handling and deployment files"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/hackrx-fastapi-app.git
git push -u origin main
```

---

## 📋 Pre-Setup Checklist

Before running these commands, ensure:

### 1. GitHub Repository Created
- ✅ Go to [GitHub.com](https://github.com)
- ✅ Click "+" → "New repository"
- ✅ Repository name: `hackrx-fastapi-app`
- ✅ Description: `HackRX Document Q&A API with Gemini 2.0 Flash`
- ✅ Set to **Public** (required for free deployment)
- ✅ **Do NOT initialize** with README (you already have files)
- ✅ Click "Create repository"
- ✅ Copy the repository URL: `https://github.com/YOUR_USERNAME/hackrx-fastapi-app.git`

### 2. Git Configuration (First Time Setup)
```powershell
# Configure your name and email (replace with your info)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify configuration
git config --global --list
```

### 3. Files to be Committed
Your repository will include:
- ✅ `hackrx_api_fixed.py` - Main FastAPI application
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Deployment startup command
- ✅ `runtime.txt` - Python version specification
- ✅ `vercel.json` - Vercel deployment config
- ✅ `DEPLOYMENT_GUIDE.md` - Complete deployment instructions
- ✅ `.gitignore` - Files to exclude from version control
- ✅ All other project files and documentation

---

## 🔍 Troubleshooting Common Issues

### Issue 1: Git Not Installed
```powershell
# Check if Git is installed
git --version

# If not installed, download from: https://git-scm.com/download/win
```

### Issue 2: Permission Denied
```powershell
# If you get permission errors, try:
git config --global credential.helper manager-core

# Or use GitHub CLI for authentication:
# Install: https://cli.github.com/
gh auth login
```

### Issue 3: Repository Already Has Files
```powershell
# If GitHub repo already has README or other files:
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Issue 4: Large File Warnings
```powershell
# If you get warnings about large files:
git rm --cached large-file.pdf
echo "*.pdf" >> .gitignore
git add .gitignore
git commit -m "Add .gitignore for large files"
git push origin main
```

---

## ✅ Verification Steps

After pushing to GitHub, verify:

### 1. Check GitHub Repository
```powershell
# Your repository should be visible at:
# https://github.com/YOUR_USERNAME/hackrx-fastapi-app
```

### 2. Verify Files Are Present
- ✅ `hackrx_api_fixed.py` visible in repository
- ✅ `requirements.txt` with all dependencies
- ✅ `DEPLOYMENT_GUIDE.md` with full instructions
- ✅ All deployment configuration files

### 3. Test Clone (Optional)
```powershell
# Test by cloning in a different directory
cd C:\temp
git clone https://github.com/YOUR_USERNAME/hackrx-fastapi-app.git
cd hackrx-fastapi-app
ls
```

---

## 🎯 Next Steps After Git Push

Once your code is on GitHub:

1. **Deploy to Render:**
   - Go to [Render.com](https://render.com)
   - Connect your GitHub repository
   - Follow deployment steps in `DEPLOYMENT_GUIDE.md`

2. **Deploy to Railway:**
   - Go to [Railway.app](https://railway.app)
   - Connect your GitHub repository
   - Configure environment variables

3. **Deploy to Vercel:**
   - Install Vercel CLI: `npm i -g vercel`
   - Run: `vercel --prod`
   - Follow prompts

---

## 📝 Sample Commands with Your Repository

Replace `YOUR_USERNAME` with your actual GitHub username:

```powershell
# Example with actual repository URL
cd "e:\final try"
git init
git add .
git commit -m "Initial commit: HackRX FastAPI app with comprehensive error handling and deployment files"
git branch -M main
git remote add origin https://github.com/johndoe/hackrx-fastapi-app.git
git push -u origin main
```

**Your FastAPI HackRX application is now ready to be pushed to GitHub and deployed to production!** 🚀✨
