# 🚀 Manual Git + GitHub Setup Commands
# Copy and paste these commands one by one into your terminal

# ============================================
# PREREQUISITES CHECK
# ============================================

# 1. Check if Git is installed
git --version

# 2. Check if GitHub CLI is installed
gh --version

# 3. Authenticate with GitHub CLI (if not already done)
gh auth status
# If not authenticated, run:
# gh auth login --web

# ============================================
# GIT REPOSITORY INITIALIZATION
# ============================================

# 4. Initialize Git repository (if not already done)
# Skip this if .git folder already exists
git init

# 5. Stage all files
git add .

# 6. Create initial commit (if there are changes)
git status
# If there are changes to commit:
git commit -m "Initial commit: HackRX FastAPI app with comprehensive error handling"

# 7. Rename branch to main (if not already main)
git branch --show-current
# If not on main branch:
git branch -M main

# ============================================
# GITHUB REPOSITORY CREATION
# ============================================

# 8. Create GitHub repository (if it doesn't exist)
# Check if repo exists:
gh repo view Bajaj-Hackrx

# If repo doesn't exist, create it:
gh repo create Bajaj-Hackrx --public --description "HackRX Document Q&A API with Gemini 2.0 Flash and FastAPI"

# ============================================
# REMOTE CONFIGURATION & PUSH
# ============================================

# 9. Get your GitHub username
gh api user --jq .login

# 10. Configure remote origin (replace YOUR_USERNAME with your actual username)
# Check current remote:
git remote -v

# If no remote exists, add it:
git remote add origin https://github.com/YOUR_USERNAME/Bajaj-Hackrx.git

# If remote exists but wrong URL, update it:
# git remote set-url origin https://github.com/YOUR_USERNAME/Bajaj-Hackrx.git

# 11. Push to GitHub
git push -u origin main

# If push fails due to conflicts, try:
# git pull origin main --allow-unrelated-histories
# git push -u origin main

# If still fails, force push (CAUTION: overwrites remote):
# git push -u origin main --force

# ============================================
# VERIFICATION
# ============================================

# 12. Verify everything is set up correctly
git remote -v
git branch
git status

# 13. View your repository on GitHub
# Visit: https://github.com/YOUR_USERNAME/Bajaj-Hackrx

echo "✅ Repository setup complete!"
echo "🚀 Ready for deployment following DEPLOYMENT_GUIDE.md"

# ============================================
# COMMON TROUBLESHOOTING
# ============================================

# Problem: "remote origin already exists"
# Solution: git remote set-url origin https://github.com/YOUR_USERNAME/Bajaj-Hackrx.git

# Problem: "failed to push some refs"  
# Solution 1: git pull origin main --allow-unrelated-histories
# Solution 2: git push -u origin main --force

# Problem: "repository not found"
# Solution: Make sure repository name is correct and you have access

# Problem: "authentication failed"
# Solution: gh auth login --web

# Problem: "nothing to commit"
# Solution: Make sure you have files in your directory and they're staged with git add .
