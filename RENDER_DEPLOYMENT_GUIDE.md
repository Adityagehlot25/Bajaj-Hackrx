# 🚀 Render Deployment Guide - Step by Step

**Deploy your HackRX FastAPI application to Render in under 10 minutes!**

## 📋 Prerequisites Checklist
- ✅ GitHub repository: https://github.com/Adityagehlot25/Bajaj-Hackrx
- ✅ FastAPI application: `hackrx_api_fixed.py`
- ✅ Dependencies file: `requirements.txt`
- ✅ Deployment files: `Procfile`, `runtime.txt`
- ✅ HackRX team token ready

---

## 🎯 Step 1: Create Render Account

### 1.1 Sign Up
1. **Open browser** and go to **https://render.com**
2. **Click "Get Started for Free"**
3. **Choose "Sign up with GitHub"** (recommended)
   - This allows easy repository connection
   - Click the GitHub button
4. **Authorize Render**
   - Review permissions (repository access)
   - Click "Authorize render"
5. **Complete account setup** if prompted

### 1.2 Verify Account
- Check your email for verification if required
- Complete any additional setup steps

---

## 🔗 Step 2: Connect Your GitHub Repository

### 2.1 Create New Web Service
1. **From Render Dashboard**, click the blue **"New +"** button (top-right)
2. **Select "Web Service"** from the dropdown menu

### 2.2 Connect Repository
1. **If first time connecting GitHub**:
   - Click "Connect GitHub"
   - Click "Install Render" on GitHub
   - Select your GitHub account (`Adityagehlot25`)
   - Click "Install & Authorize"

2. **Select Repository**:
   - Find `Adityagehlot25/Bajaj-Hackrx` in the list
   - Click **"Connect"** button next to it

---

## ⚙️ Step 3: Configure Web Service

### 3.1 Basic Settings
Fill out the configuration form:

**Service Name**: `bajaj-hackrx-api`
- This becomes part of your URL
- Use lowercase, hyphens only
- Example: `bajaj-hackrx-api.onrender.com`

**Region**: `Oregon (US West)`
- Choose closest to your users
- Oregon is good for global access

**Branch**: `main` ✅
- Should auto-detect
- This is your GitHub branch

**Root Directory**: *(leave empty)*
- Your code is in repository root
- No subdirectory needed

### 3.2 Build & Deploy Configuration

**Runtime**: Select **"Python 3"** from dropdown ✅

**Build Command**: 
```bash
pip install -r requirements.txt
```
- This installs all dependencies
- Copy exactly as shown

**Start Command**:
```bash
uvicorn hackrx_api_fixed:app --host 0.0.0.0 --port $PORT
```
- This starts your FastAPI app
- `$PORT` is provided by Render
- Copy exactly as shown

### 3.3 Instance Type

**Plan**: Select **"Free"** ✅
- Perfect for testing and development
- $0/month cost
- 512 MB RAM
- Shared CPU
- 750 hours/month (more than enough)

---

## 🔐 Step 4: Configure Environment Variables

**Critical Step** - Your app won't work without these!

### 4.1 Add Environment Variables During Initial Setup
If you're still on the Web Service creation page:

1. **Scroll down to "Environment Variables" section**
2. **Click "Add Environment Variable"** button
3. **Add each variable below one by one**

### 4.2 Add Environment Variables After Service Creation
If your service is already created:

1. **Go to Render Dashboard** (https://dashboard.render.com)
2. **Find and click your service**: `bajaj-hackrx-api`
3. **In the sidebar, click "Environment"**
4. **Click "+ Add Environment Variable"** button
5. **Add each variable below**

### 4.3 Required Environment Variables

#### Variable 1: Gemini API Key
1. **Click "+ Add Environment Variable"**
2. **Enter**:
   ```
   Key: GEMINI_API_KEY
   Value: AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ
   ```
3. **Click "Add"**

#### Variable 2: HackRX Team Token
1. **Click "+ Add Environment Variable"** again
2. **Enter**:
   ```
   Key: TEAM_TOKEN
   Value: your_hackrx_team_token_here
   ```
   **⚠️ Replace `your_hackrx_team_token_here` with your actual HackRX team token!**
3. **Click "Add"**

#### Variable 3: Default Model
1. **Click "+ Add Environment Variable"** again
2. **Enter**:
   ```
   Key: DEFAULT_EMBEDDING_MODEL
   Value: embedding-001
   ```
3. **Click "Add"**

#### Variable 4: Python Path (Optional)
1. **Click "+ Add Environment Variable"** again
2. **Enter**:
   ```
   Key: PYTHONPATH
   Value: /opt/render/project/src
   ```
3. **Click "Add"**

### 4.4 Save and Apply Changes
1. **After adding all variables**, you'll see them listed
2. **Click "Save Changes"** button (if available)
3. **Your service will automatically redeploy** with new environment variables
4. **Wait for redeployment** to complete (1-2 minutes)

### 4.5 Verify Variables Are Set
1. **Check the Environment tab** shows all 4 variables
2. **Look for deployment logs** showing "Environment variables updated"
3. **Variables should show**:
   - ✅ GEMINI_API_KEY (value hidden for security)
   - ✅ TEAM_TOKEN (value hidden for security)  
   - ✅ DEFAULT_EMBEDDING_MODEL = embedding-001
   - ✅ PYTHONPATH = /opt/render/project/src

### 4.6 Manual Redeploy (If Needed)
If changes don't auto-deploy:
1. **Go to your service dashboard**
2. **Click "Manual Deploy"** button
3. **Select "Deploy latest commit"**
4. **Click "Yes, deploy"**

---

## 🚀 Step 5: Deploy Your Application

### 5.1 Final Review
Before deploying, verify:
- ✅ Service name: `bajaj-hackrx-api`
- ✅ Runtime: Python 3
- ✅ Build command: `pip install -r requirements.txt`
- ✅ Start command: `uvicorn hackrx_api_fixed:app --host 0.0.0.0 --port $PORT`
- ✅ Plan: Free
- ✅ All environment variables set

### 5.2 Create Web Service
1. **Click "Create Web Service"** (blue button at bottom)
2. **Wait for deployment** (2-5 minutes)

### 5.3 Monitor Deployment
Watch the deployment logs in real-time:

```
==> Cloning from https://github.com/Adityagehlot25/Bajaj-Hackrx...
==> Using Python 3.11.6 via runtime.txt
==> Installing dependencies with pip
    Collecting fastapi==0.104.1
    Collecting uvicorn[standard]==0.24.0
    ... (dependencies installing)
==> Starting service with 'uvicorn hackrx_api_fixed:app --host 0.0.0.0 --port $PORT'
==> Your service is live 🎉
```

---

## 🎯 Step 6: Get Your Live URL

### 6.1 Copy Your URL
Once deployment succeeds:
1. **Your app URL** will be shown at the top:
   ```
   https://bajaj-hackrx-api.onrender.com
   ```
2. **Copy this URL** - save it for testing

### 6.2 Important Endpoints
- **Root endpoint**: `https://bajaj-hackrx-api.onrender.com/`
- **API endpoint**: `https://bajaj-hackrx-api.onrender.com/api/v1/hackrx/run`
- **Health check**: `https://bajaj-hackrx-api.onrender.com/health`

---

## ✅ Step 7: Test Your Deployment

### 7.1 Quick Test - Root Endpoint
Open in browser or use curl:
```bash
curl https://bajaj-hackrx-api.onrender.com/
```

**Expected Response**:
```json
{
  "message": "HackRX Document Q&A API (Fixed Version)",
  "version": "1.1.0",
  "status": "operational"
}
```

### 7.2 API Endpoint Test
Test your main API:
```bash
curl -X POST "https://bajaj-hackrx-api.onrender.com/api/v1/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_team_token_here" \
  -d '{
    "document_url": "https://www.archives.gov/founding-docs/constitution-transcript",
    "questions": ["What are the three branches of government?"]
  }'
```

**Expected Response**:
```json
{
  "answers": [
    "The three branches of government are the Legislative, Executive, and Judicial branches..."
  ]
}
```

---

## 🔧 Troubleshooting Common Issues

### Issue 1: Build Failed - Dependencies
**Error**: `ERROR: Could not find a version that satisfies the requirement...`

**Solution**:
- Check `requirements.txt` format
- Ensure no extra characters or spaces
- Verify all package names are correct

### Issue 2: Application Failed to Start
**Error**: `uvicorn: command not found`

**Solution**:
- Verify start command is exactly: `uvicorn hackrx_api_fixed:app --host 0.0.0.0 --port $PORT`
- Check `requirements.txt` includes `uvicorn[standard]`

### Issue 3: Environment Variables Not Loaded
**Error**: `KeyError: 'GEMINI_API_KEY'`

**Solution**:
- Go to Render Dashboard → Your Service → Environment
- Verify all variables are set correctly
- No extra spaces in variable names or values
- Click "Save Changes" after adding variables

### Issue 4: 502 Bad Gateway
**Error**: Service not responding

**Solution**:
- Check deployment logs for Python errors
- Verify your FastAPI app starts locally
- Ensure `--host 0.0.0.0` in start command

---

## 🎉 Success! Your API is Live

### What You've Accomplished:
- ✅ **Deployed FastAPI app** to production
- ✅ **Public HTTPS endpoint** available 24/7  
- ✅ **Environment variables** configured securely
- ✅ **Ready for HackRX competition** use
- ✅ **Auto-deploys** when you push to GitHub

### Your Production URLs:
```
Website: https://bajaj-hackrx-api.onrender.com
API Endpoint: https://bajaj-hackrx-api.onrender.com/api/v1/hackrx/run
```

### Next Steps:
1. **Test thoroughly** with different document types
2. **Monitor performance** in Render dashboard
3. **Update GitHub repository** - auto-deploys
4. **Share API endpoint** for HackRX submission

---

**🏆 Congratulations! Your HackRX FastAPI is now live in production!** 

**Need help?** Check Render's logs in the dashboard or refer to the troubleshooting section above.
