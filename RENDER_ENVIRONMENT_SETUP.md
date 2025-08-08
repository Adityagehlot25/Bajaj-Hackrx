# 🔐 Render Environment Variables Setup Guide

## 📋 Quick Environment Variables Setup

### 🎯 Method 1: During Service Creation

**When creating your Web Service:**

1. **Scroll down** to "Environment Variables" section
2. **Click "Add Environment Variable"** 
3. **Add each variable** (see list below)
4. **Continue with deployment**

---

### 🎯 Method 2: After Service is Created

**If your service already exists:**

#### Step 1: Access Your Service
1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Find your service**: `bajaj-hackrx-api` (or your service name)
3. **Click on the service** to open it

#### Step 2: Open Environment Settings
1. **In the left sidebar**, click **"Environment"**
2. **You'll see the Environment Variables page**

#### Step 3: Add Variables
1. **Click the blue "+ Add Environment Variable"** button
2. **Add each variable below, one by one**
3. **Click "Add" after each variable**

---

## 🔑 Required Environment Variables

### Variable 1: Gemini API Key
**Click "+ Add Environment Variable"** and enter:
```
Key:   GEMINI_API_KEY
Value: AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ
```
**Click "Add"**

### Variable 2: HackRX Team Token  
**Click "+ Add Environment Variable"** and enter:
```
Key:   TEAM_TOKEN
Value: your_actual_hackrx_team_token_here
```
**⚠️ IMPORTANT**: Replace `your_actual_hackrx_team_token_here` with your real HackRX team token!
**Click "Add"**

### Variable 3: Default Model
**Click "+ Add Environment Variable"** and enter:
```
Key:   DEFAULT_EMBEDDING_MODEL  
Value: embedding-001
```
**Click "Add"**

### Variable 4: Python Path (Optional)
**Click "+ Add Environment Variable"** and enter:
```
Key:   PYTHONPATH
Value: /opt/render/project/src
```
**Click "Add"**

---

## 💾 Save and Deploy Changes

### Step 1: Save Changes
1. **After adding all 4 variables**, they should be listed
2. **Look for a "Save Changes"** button (if present)
3. **Click "Save Changes"**

### Step 2: Automatic Redeploy
- **Render automatically redeploys** when environment variables change
- **Wait for the redeploy** to complete (1-3 minutes)
- **Watch the deployment logs** for success

### Step 3: Manual Redeploy (If Needed)
If automatic redeploy doesn't happen:
1. **Go to your service dashboard**
2. **Click "Manual Deploy"** button  
3. **Select "Deploy latest commit"**
4. **Click "Yes, deploy"**

---

## ✅ Verify Environment Variables

### Check Variables Are Set
After deployment, verify in Render dashboard:
- ✅ **GEMINI_API_KEY**: `••••••••••••••••••••••••••••••••••••••••` (hidden for security)
- ✅ **TEAM_TOKEN**: `••••••••••••••••••••••••••••••••••••••••` (hidden for security)  
- ✅ **DEFAULT_EMBEDDING_MODEL**: `embedding-001`
- ✅ **PYTHONPATH**: `/opt/render/project/src`

### Test Your API
After redeployment, test your API:
```bash
curl https://your-app-name.onrender.com/
```

**Expected Response:**
```json
{
  "message": "HackRX Document Q&A API (Fixed Version)",
  "version": "1.1.0", 
  "status": "operational"
}
```

---

## 🚨 Common Issues & Solutions

### Issue 1: Variables Not Taking Effect
**Problem**: API returns errors about missing environment variables

**Solution**: 
1. Check variables are saved in Render dashboard
2. Manual redeploy: Dashboard → Manual Deploy → Deploy latest commit
3. Wait for deployment to complete

### Issue 2: TEAM_TOKEN Not Set
**Problem**: API returns `401 Unauthorized` errors

**Solution**:
1. Get your actual HackRX team token
2. Update TEAM_TOKEN variable with real value (not placeholder)
3. Save changes and redeploy

### Issue 3: Service Won't Start
**Problem**: Service shows "Deploy failed" 

**Solution**:
1. Check deployment logs for specific errors
2. Verify all 4 environment variables are set correctly
3. Ensure no extra spaces in variable names or values

### Issue 4: Can't Find Environment Tab
**Problem**: Don't see "Environment" in sidebar

**Solution**:
1. Make sure you're on your service page (not main dashboard)
2. Click your service name first
3. Environment tab should be in left sidebar

---

## 🎯 Environment Variables Summary

**Copy this for easy reference:**

```env
GEMINI_API_KEY=AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ
TEAM_TOKEN=your_actual_hackrx_team_token_here
DEFAULT_EMBEDDING_MODEL=embedding-001
PYTHONPATH=/opt/render/project/src
```

**⚠️ Remember**: Replace `your_actual_hackrx_team_token_here` with your real HackRX team token!

---

**✅ Once all variables are set and service is redeployed, your HackRX FastAPI will be fully functional!** 🚀
