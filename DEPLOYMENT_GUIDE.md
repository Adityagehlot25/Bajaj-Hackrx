# 🚀 FastAPI HackRX Deployment Guide

Complete step-by-step guide to deploy your HackRX Document Q&A API to production.

## 📋 Table of Contents
1. [Pre-Deployment Preparation](#pre-deployment-preparation)
2. [GitHub Repository Setup](#github-repository-setup)
3. [Deployment Platform Options](#deployment-platform-options)
4. [Render Deployment (Recommended)](#render-deployment-recommended)
5. [Railway Deployment](#railway-deployment)
6. [Vercel Deployment](#vercel-deployment)
7. [Environment Variables Configuration](#environment-variables-configuration)
8. [Post-Deployment Testing](#post-deployment-testing)
9. [Troubleshooting](#troubleshooting)

## 🛠️ Pre-Deployment Preparation

### 1. Create Requirements File
Create `requirements.txt` with all dependencies:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
aiohttp==3.9.1
python-dotenv==1.0.0
PyMuPDF==1.23.8
pdfplumber==0.10.3
PyPDF2==3.0.1
python-docx==1.1.0
faiss-cpu==1.7.4
tiktoken==0.5.2
requests==2.31.0
numpy==1.24.3
```

### 2. Create Deployment Files

#### `Procfile` (for Render/Railway):
```txt
web: uvicorn hackrx_api_fixed:app --host 0.0.0.0 --port $PORT
```

#### `runtime.txt` (specify Python version):
```txt
python-3.11.6
```

#### `.gitignore`:
```txt
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

.env
.env.local
.env.production
.env.staging
.DS_Store
*.log
temp*
tmp*
*.pdf
*.docx
*.txt
```

## 📚 GitHub Repository Setup

### Step 1: Initialize Git Repository
```bash
# Navigate to your project directory
cd "e:\final try"

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: HackRX FastAPI application with comprehensive error handling"
```

### Step 2: Create GitHub Repository
1. Go to [GitHub](https://github.com) and log in
2. Click "+" → "New repository"
3. Repository name: `hackrx-fastapi-app`
4. Description: `HackRX Document Q&A API with Gemini 2.0 Flash`
5. Set to **Public** (required for free deployment)
6. Don't initialize with README (since you already have files)
7. Click "Create repository"

### Step 3: Push to GitHub
```bash
# Add remote origin (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/hackrx-fastapi-app.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 🎯 Deployment Platform Options

| Platform | Pros | Cons | Best For |
|----------|------|------|----------|
| **Render** | Easy setup, good free tier, auto-deploy from GitHub | Can be slower cold starts | **Recommended** |
| **Railway** | Fast deployment, good performance | Limited free tier | High performance needs |
| **Vercel** | Excellent for static sites | Limited for full APIs | Frontend + serverless functions |

---

## 🟢 Render Deployment (Recommended)

### Step 1: Create Render Account
1. Go to [Render.com](https://render.com)
2. Sign up with GitHub account
3. Authorize Render to access your repositories

### Step 2: Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository: `hackrx-fastapi-app`
3. Configure deployment:

#### Basic Settings:
- **Name**: `hackrx-api-production`
- **Root Directory**: `.` (leave empty if code is in root)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main`

#### Build & Deploy:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn hackrx_api_fixed:app --host 0.0.0.0 --port $PORT`

#### Instance Type:
- **Plan**: `Free` (for testing) or `Starter` (for production)

### Step 3: Configure Environment Variables
In Render dashboard → your service → Environment:

```env
GEMINI_API_KEY=AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ
TEAM_TOKEN=your_team_token_here
DEFAULT_EMBEDDING_MODEL=embedding-001
PYTHONPATH=/opt/render/project/src
```

### Step 4: Deploy
1. Click "Create Web Service"
2. Render will automatically build and deploy
3. Monitor deployment logs for any issues
4. Once deployed, you'll get a URL like: `https://hackrx-api-production.onrender.com`

---

## 🚂 Railway Deployment

### Step 1: Create Railway Account
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub account

### Step 2: Deploy from GitHub
1. Click "Deploy from GitHub repo"
2. Select `hackrx-fastapi-app`
3. Railway auto-detects Python and FastAPI

### Step 3: Configure Settings
#### Variables:
```env
GEMINI_API_KEY=AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ
TEAM_TOKEN=your_team_token_here
DEFAULT_EMBEDDING_MODEL=embedding-001
PORT=8000
```

#### Custom Start Command:
```bash
uvicorn hackrx_api_fixed:app --host 0.0.0.0 --port $PORT
```

### Step 4: Generate Domain
1. Go to Settings → Networking
2. Click "Generate Domain"
3. Get URL like: `https://hackrx-api-production.up.railway.app`

---

## ⚡ Vercel Deployment

### Step 1: Create `vercel.json`
```json
{
  "builds": [
    {
      "src": "hackrx_api_fixed.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "hackrx_api_fixed.py"
    }
  ]
}
```

### Step 2: Deploy to Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel --prod`
3. Follow prompts to deploy

**Note**: Vercel has limitations for long-running processes. Consider Render or Railway for full API deployment.

---

## 🔧 Environment Variables Configuration

### Required Environment Variables:

#### Core API Configuration:
```env
# Google Gemini API (Required)
GEMINI_API_KEY=AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ

# Team Token (Required for HackRX)
TEAM_TOKEN=your_hackrx_team_token_here

# Model Configuration
DEFAULT_EMBEDDING_MODEL=embedding-001

# Optional: Logging Level
LOG_LEVEL=INFO

# Optional: CORS Settings
ALLOWED_ORIGINS=*
```

#### Platform-Specific Variables:

**Render:**
```env
PYTHON_VERSION=3.11.6
PYTHONPATH=/opt/render/project/src
```

**Railway:**
```env
PORT=8000
RAILWAY_STATIC_URL=your-app-url.up.railway.app
```

### Step-by-Step Environment Variable Setup:

#### For Render:
1. Go to Render Dashboard
2. Select your service
3. Click "Environment"
4. Click "Add Environment Variable"
5. Add each variable (key-value pairs)
6. Click "Save Changes"

#### For Railway:
1. Go to Railway Dashboard  
2. Select your project
3. Click "Variables" tab
4. Click "New Variable"
5. Add each variable
6. Deploy automatically updates

---

## 🧪 Post-Deployment Testing

### Step 1: Verify Deployment
Check your deployed URL:
- **Render**: `https://your-app.onrender.com`
- **Railway**: `https://your-app.up.railway.app`
- **Vercel**: `https://your-app.vercel.app`

### Step 2: Test API Endpoints

#### Test Root Endpoint:
```bash
curl https://your-app.onrender.com/
```

Expected response:
```json
{
  "message": "HackRX Document Q&A API (Fixed Version)",
  "version": "1.1.0",
  "status": "operational"
}
```

#### Test Main API Endpoint:
```bash
curl -X POST "https://your-app.onrender.com/api/v1/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_test_token" \
  -d '{
    "document_url": "https://www.archives.gov/founding-docs/constitution-transcript",
    "questions": ["What are the three branches of government?"]
  }'
```

Expected response:
```json
{
  "answers": [
    "The three branches of government are the Legislative branch (Congress), the Executive branch (President), and the Judicial branch (Supreme Court)."
  ]
}
```

### Step 3: Verify HTTPS Access
- ✅ Ensure URL starts with `https://`
- ✅ Test endpoint `/api/v1/hackrx/run` is accessible
- ✅ Verify JSON responses are returned correctly
- ✅ Check error handling with invalid requests

### Step 4: Performance Testing
```bash
# Test with multiple questions
curl -X POST "https://your-app.onrender.com/api/v1/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_test_token" \
  -d '{
    "document_url": "https://example.com/document.pdf",
    "questions": [
      "What is the main topic?",
      "Who are the key people mentioned?",
      "When was this written?"
    ]
  }'
```

---

## 🔍 Troubleshooting

### Common Issues:

#### 1. Build Failures
```bash
# Check requirements.txt format
pip install -r requirements.txt

# Verify Python version compatibility
python --version
```

#### 2. Import Errors
```bash
# Add to environment variables:
PYTHONPATH=/opt/render/project/src
```

#### 3. Port Issues
```bash
# Ensure your app uses the PORT environment variable
uvicorn hackrx_api_fixed:app --host 0.0.0.0 --port $PORT
```

#### 4. Environment Variables Not Loading
```python
# Add to your code:
from dotenv import load_dotenv
load_dotenv()
```

### Monitoring & Logs:

#### Render:
- Go to service → "Logs" tab
- Monitor real-time logs
- Check for startup errors

#### Railway:
- Click on deployment
- View "Deployments" tab for logs
- Monitor performance metrics

### Health Check Endpoint:
Add to your FastAPI app:
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.1.0"
    }
```

---

## 🎯 Final Deployment Checklist

### Pre-Deployment:
- [ ] `requirements.txt` created and tested
- [ ] `Procfile` or start command configured
- [ ] `.gitignore` excludes sensitive files
- [ ] Environment variables prepared
- [ ] Code pushed to GitHub

### During Deployment:
- [ ] Service created on chosen platform
- [ ] Repository connected and deployed
- [ ] Environment variables configured
- [ ] Build completed successfully
- [ ] App is accessible via HTTPS

### Post-Deployment:
- [ ] Root endpoint (`/`) responds correctly
- [ ] API endpoint (`/api/v1/hackrx/run`) works with test data
- [ ] Error handling returns appropriate status codes
- [ ] Performance is acceptable for your use case
- [ ] Monitoring and logging are functional

### Production Readiness:
- [ ] Custom domain configured (optional)
- [ ] SSL certificate verified
- [ ] Rate limiting configured (if needed)
- [ ] Monitoring/alerting set up
- [ ] Backup strategy implemented

---

## 🚀 Your App is Now Live!

Your FastAPI HackRX application is now deployed and accessible via HTTPS at:
- **Production URL**: `https://your-app-name.onrender.com`
- **API Endpoint**: `https://your-app-name.onrender.com/api/v1/hackrx/run`

**Ready for HackRX competition!** 🏆✨

---

## 📞 Support

If you encounter issues:
1. Check deployment logs on your chosen platform
2. Verify all environment variables are set correctly
3. Test API endpoints using curl or Postman
4. Monitor performance and error rates

**Your professional-grade FastAPI application is now deployed and ready for production use!** 🎉
