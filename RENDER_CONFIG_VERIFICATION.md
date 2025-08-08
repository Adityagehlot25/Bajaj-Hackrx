# 🔧 Render Environment Variables Configuration & Verification Guide

## Overview
This guide provides step-by-step instructions for configuring environment variables on Render and verifying your deployment works correctly.

---

## Step 1: Access Environment Settings

### Code Comments for Environment Access:
```python
# RENDER DASHBOARD ACCESS INSTRUCTIONS
# =====================================
# 
# To configure environment variables for your FastAPI deployment:
# 
# 1. Navigate to Render Dashboard
#    - Open your browser and go to: https://dashboard.render.com
#    - Log in with your GitHub account credentials
# 
# 2. Select Your Service
#    - Look for your service name: "bajaj-hackrx-api" (or whatever you named it)
#    - Click on the service name to open the service dashboard
# 
# 3. Access Environment Settings
#    - In the left sidebar, locate and click "Environment"
#    - This opens the Environment Variables configuration page
#    - You'll see a list of current variables (if any) and an "Add" button
```

### Manual Steps:
1. **Open Render Dashboard**
   ```
   URL: https://dashboard.render.com
   Login: Use your GitHub account
   ```

2. **Select Your Service**
   ```
   Service Name: bajaj-hackrx-api
   Action: Click on the service name
   ```

3. **Navigate to Environment Settings**
   ```
   Location: Left sidebar
   Button: Click "Environment"
   Result: Opens Environment Variables page
   ```

---

## Step 2: Add Required Environment Variables

### Code Comments for Adding Variables:
```python
# ENVIRONMENT VARIABLES SETUP INSTRUCTIONS
# ========================================
# 
# Your FastAPI app requires these environment variables to function:
# 
# Required Variables:
# - GEMINI_API_KEY: Google Gemini API authentication key
# - TEAM_TOKEN: HackRX competition team authentication token
# - DEFAULT_EMBEDDING_MODEL: Specifies which embedding model to use
# - PYTHONPATH: Python module path for proper imports
# 
# Adding Process:
# 1. Click the blue "+ Add Environment Variable" button
# 2. Enter the Key name exactly as shown (case-sensitive)
# 3. Enter the corresponding Value
# 4. Click "Add" to save the variable
# 5. Repeat for each required variable
```

### Commands and Steps:

#### Variable 1: GEMINI_API_KEY
```bash
# Step 2.1: Add Gemini API Key
# Click: "+ Add Environment Variable"
# Enter the following:

Key: GEMINI_API_KEY
Value: AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ

# Click: "Add" button to save
```

#### Variable 2: TEAM_TOKEN
```bash
# Step 2.2: Add Team Token
# Click: "+ Add Environment Variable" (again)
# Enter the following:

Key: TEAM_TOKEN
Value: your_hackrx_team_token_here

# IMPORTANT: Replace 'your_hackrx_team_token_here' with your actual HackRX team token
# Click: "Add" button to save
```

#### Variable 3: DEFAULT_EMBEDDING_MODEL
```bash
# Step 2.3: Add Default Embedding Model
# Click: "+ Add Environment Variable" (again)
# Enter the following:

Key: DEFAULT_EMBEDDING_MODEL
Value: embedding-001

# Click: "Add" button to save
```

#### Variable 4: PYTHONPATH
```bash
# Step 2.4: Add Python Path
# Click: "+ Add Environment Variable" (again)
# Enter the following:

Key: PYTHONPATH
Value: /opt/render/project/src

# Click: "Add" button to save
```

### Verification After Adding Variables:
```python
# VARIABLES VERIFICATION CHECKLIST
# ================================
# 
# After adding all variables, you should see:
# ✓ GEMINI_API_KEY: ••••••••••••••••••••••••••••••••• (hidden for security)
# ✓ TEAM_TOKEN: ••••••••••••••••••••••••••••••••••••• (hidden for security)
# ✓ DEFAULT_EMBEDDING_MODEL: embedding-001 (visible)
# ✓ PYTHONPATH: /opt/render/project/src (visible)
```

---

## Step 3: Save Changes and Redeploy

### Code Comments for Saving and Redeploying:
```python
# DEPLOYMENT PROCESS INSTRUCTIONS
# ==============================
# 
# After adding all environment variables, you need to redeploy your service
# so the new variables take effect in your running application.
# 
# Automatic Redeploy (Preferred Method):
# - Render automatically triggers a redeploy when environment variables change
# - This process takes 1-3 minutes to complete
# - Watch the deployment logs for progress and success confirmation
# 
# Manual Redeploy (If Automatic Fails):
# - Use this if automatic redeploy doesn't start
# - Go to service dashboard and click "Manual Deploy"
# - Select "Deploy latest commit" option
# - Confirm deployment by clicking "Yes, deploy"
```

### Save and Redeploy Commands:

#### Automatic Redeploy (Default):
```bash
# Step 3.1: Save Changes (Automatic Process)
# Action: Click "Save Changes" button (if visible)
# 
# Render will automatically:
# 1. Save all environment variables
# 2. Trigger a new deployment
# 3. Restart your service with new variables
# 
# Timeline: 1-3 minutes
# Status: Watch deployment logs for progress
```

#### Manual Redeploy (If Needed):
```bash
# Step 3.2: Manual Redeploy (Backup Method)
# 
# If automatic redeploy doesn't start:
# 1. Navigate to your service dashboard (main service page)
# 2. Look for "Manual Deploy" button (usually blue)
# 3. Click "Manual Deploy"
# 4. Select "Deploy latest commit"
# 5. Click "Yes, deploy" to confirm
# 
# Timeline: 1-3 minutes
# Status: Monitor deployment progress in logs
```

### Deployment Monitoring:
```python
# DEPLOYMENT MONITORING GUIDE
# ===========================
# 
# During redeploy, you'll see logs like:
# 
# ==> Building...
# ==> Installing dependencies
# ==> Starting service
# ==> Environment variables loaded: 4 variables
# ==> Your service is live at https://your-app.onrender.com
# 
# Success Indicators:
# - "Build succeeded" message
# - "Service started successfully"
# - No error messages in logs
# - Service status shows "Live"
```

---

## Step 4: Verify Deployment Success

### Code Comments for Verification:
```python
# DEPLOYMENT VERIFICATION INSTRUCTIONS
# ====================================
# 
# After successful redeploy, verify your API is working correctly:
# 
# Test Method 1: Root Endpoint Check
# - Tests basic service availability
# - Confirms FastAPI is running
# - Validates environment variables are loaded
# 
# Test Method 2: API Endpoint Check
# - Tests full API functionality
# - Validates authentication system
# - Confirms document processing pipeline
# 
# Expected Behaviors:
# - HTTP 200 status codes
# - JSON responses with correct structure
# - No error messages about missing environment variables
```

### Sample curl Command for Root Endpoint:
```bash
# Step 4.1: Test Root Endpoint
# This command tests basic service availability

curl https://your-app.onrender.com/

# Replace 'your-app' with your actual Render service name
# Example: curl https://bajaj-hackrx-api.onrender.com/
```

### Expected Response:
```json
// Step 4.2: Expected Root Endpoint Response
// This JSON response indicates successful deployment

{
  "message": "HackRX Document Q&A API (Fixed Version)",
  "version": "1.1.0",
  "status": "operational"
}

// Response Analysis:
// - "message": Confirms API identity and version
// - "version": Shows application version number  
// - "status": "operational" means service is running correctly
```

### Advanced API Endpoint Test:
```bash
# Step 4.3: Test Main API Endpoint (Advanced)
# This command tests full API functionality with authentication

curl -X POST "https://your-app.onrender.com/api/v1/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_team_token_here" \
  -d '{
    "document_url": "https://www.archives.gov/founding-docs/constitution-transcript",
    "questions": ["What are the three branches of government mentioned?"]
  }'

# Replace:
# - 'your-app' with your actual Render service name
# - 'your_team_token_here' with your actual HackRX team token
```

### Expected Advanced Response:
```json
// Step 4.4: Expected API Endpoint Response
// This response indicates full API functionality

{
  "answers": [
    "The three branches of government mentioned in the Constitution are the Legislative branch (Congress), the Executive branch (President), and the Judicial branch (Supreme Court)."
  ]
}

// Response Analysis:
// - "answers": Array containing AI-generated responses
// - Content shows successful document processing
// - Proper JSON structure confirms API is working
```

---

## Troubleshooting Common Issues

### Code Comments for Troubleshooting:
```python
# TROUBLESHOOTING GUIDE
# ====================
# 
# Common Issue 1: Environment Variables Not Loading
# Symptoms: API errors about missing GEMINI_API_KEY or TEAM_TOKEN
# Solution: Verify variables are saved and redeploy service
# 
# Common Issue 2: Service Won't Start
# Symptoms: Deployment fails with "Service failed to start"
# Solution: Check deployment logs for specific Python errors
# 
# Common Issue 3: 401 Unauthorized Errors
# Symptoms: API returns authentication errors
# Solution: Verify TEAM_TOKEN is set to actual token (not placeholder)
# 
# Common Issue 4: 500 Internal Server Errors  
# Symptoms: API returns server errors
# Solution: Check GEMINI_API_KEY is valid and has proper permissions
```

### Troubleshooting Commands:
```bash
# Troubleshooting Step 1: Check Service Status
curl -I https://your-app.onrender.com/
# Expected: HTTP/1.1 200 OK

# Troubleshooting Step 2: Check Environment Variables
# Go to Render Dashboard > Your Service > Environment
# Verify all 4 variables are present

# Troubleshooting Step 3: Manual Redeploy
# Render Dashboard > Manual Deploy > Deploy latest commit

# Troubleshooting Step 4: Check Deployment Logs
# Render Dashboard > Your Service > Logs tab
# Look for error messages or failed startup indicators
```

---

## Final Verification Checklist

```python
# COMPLETE VERIFICATION CHECKLIST
# ===============================
# 
# Before considering deployment complete, verify:
# 
# Environment Variables:
# ✓ All 4 variables added to Render dashboard
# ✓ Values are correct (no typos or placeholder text)
# ✓ Variables show as "Set" in Render UI
# 
# Deployment Status:
# ✓ Service shows "Live" status
# ✓ No error messages in deployment logs
# ✓ Latest deployment timestamp is recent
# 
# API Functionality:
# ✓ Root endpoint returns correct JSON response
# ✓ Main API endpoint accepts requests
# ✓ Authentication system works with team token
# ✓ Document processing pipeline operates correctly
# 
# Production Readiness:
# ✓ HTTPS URL is accessible publicly
# ✓ Response times are acceptable (< 30 seconds)
# ✓ No rate limiting or quota errors
# ✓ Ready for HackRX competition submission
```

---

## Summary

Your FastAPI HackRX application is now fully configured and deployed on Render with:
- ✅ **Environment variables properly set**
- ✅ **Service automatically redeployed**
- ✅ **API endpoints verified and working**
- ✅ **Ready for production use in HackRX competition**

**Live API Endpoint**: `https://your-app-name.onrender.com/api/v1/hackrx/run`
