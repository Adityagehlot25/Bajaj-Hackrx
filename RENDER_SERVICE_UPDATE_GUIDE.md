# How to Update Your Render Service with Updated Repository

## 🎯 **Overview**
Your GitHub repository now has the cross-platform `requirements.txt` fix. Here's how to update your Render service to use the latest code.

## 📋 **Prerequisites**
- ✅ GitHub repository updated with cross-platform requirements.txt
- ✅ Repository URL: https://github.com/Adityagehlot25/Bajaj-Hackrx
- 🔑 Need: Render account connected to GitHub

---

## 🚀 **Method 1: Update Existing Render Service** (Recommended)

### **Step 1: Access Your Render Service**
1. **Go to Render Dashboard:** https://dashboard.render.com
2. **Login** with your GitHub account
3. **Find your existing service** (e.g., "bajaj-hackrx-api" or similar name)
4. **Click on the service name** to open the service dashboard

### **Step 2: Trigger Manual Redeploy**
1. **In your service dashboard**, look for the **"Manual Deploy"** button
2. **Click "Manual Deploy"** 
3. **Select "Deploy latest commit"** (this pulls the latest code from your repository)
4. **Click "Yes, deploy"** to confirm
5. **Wait 2-5 minutes** for deployment to complete

### **Step 3: Monitor Deployment**
1. **Watch the "Logs" tab** for deployment progress
2. **Look for these success indicators:**
   ```
   ✅ Installing dependencies from requirements.txt
   ✅ Successfully installed python-magic (Linux version)
   ✅ Build completed successfully
   ✅ Service started on port 10000
   ```
3. **Service status should show "Live"** when complete

---

## 🆕 **Method 2: Create New Render Service** (If you haven't deployed yet)

### **Step 1: Create New Web Service**
1. **Go to Render Dashboard:** https://dashboard.render.com
2. **Click "New +"** button (top right)
3. **Select "Web Service"**

### **Step 2: Connect GitHub Repository**
1. **Click "Connect a repository"**
2. **Authorize Render** to access your GitHub if prompted
3. **Search for:** `Bajaj-Hackrx` 
4. **Click "Connect"** next to your repository

### **Step 3: Configure Service Settings**
```yaml
Service Configuration:
├── Name: bajaj-hackrx-api (or your choice)
├── Region: Oregon (US West) - Recommended
├── Branch: main
├── Root Directory: (leave blank)
├── Runtime: Python 3
├── Build Command: pip install -r requirements.txt
├── Start Command: python hackrx_api_fixed.py
└── Instance Type: Free (for testing) or Starter ($7/month)
```

### **Step 4: Add Environment Variables**
**⚠️ CRITICAL:** Add these environment variables before deploying:

```bash
# Click "Advanced" then "Add Environment Variable"
GEMINI_API_KEY=AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ
TEAM_TOKEN=your_hackrx_team_token_here  # ⚠️ Replace with actual token!
DEFAULT_EMBEDDING_MODEL=embedding-001
PYTHONPATH=/opt/render/project/src
```

### **Step 5: Deploy Service**
1. **Click "Create Web Service"**
2. **Wait 3-5 minutes** for initial deployment
3. **Monitor logs** for successful deployment

---

## 🔍 **Method 3: Auto-Deploy Setup** (For automatic updates)

### **Enable Auto-Deploy**
1. **In your service dashboard**
2. **Go to "Settings" tab**
3. **Find "Auto-Deploy"** section
4. **Set to "Yes"** 
5. **Branch:** `main`

**Result:** Every time you push to GitHub, Render automatically redeploys with the latest code.

---

## 📊 **Verify Successful Update**

### **Step 1: Check Service Status**
1. **Service Status:** Should show **"Live"** (green)
2. **Latest Deploy:** Should show recent timestamp
3. **Logs:** Should show no errors

### **Step 2: Test Your API**
```bash
# Test basic endpoint
curl https://your-service-name.onrender.com/

# Expected response:
{
  "message": "HackRX Document Q&A API (Fixed Version)",
  "version": "1.1.0", 
  "status": "operational"
}
```

### **Step 3: Test Full API Functionality**
```bash
# Test main API endpoint
curl -X POST "https://your-service-name.onrender.com/api/v1/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_team_token_here" \
  -d '{
    "document_url": "https://www.archives.gov/founding-docs/constitution-transcript",
    "questions": ["What are the three branches of government?"]
  }'
```

---

## ⚠️ **Common Update Issues & Solutions**

### **Issue 1: Service Still Using Old Requirements**
**Symptoms:** Deployment fails with `python-magic-bin` errors on Linux
**Solution:**
1. Force clear build cache: Settings → "Clear build cache"
2. Manual redeploy with "Deploy latest commit"
3. Verify your GitHub has the updated requirements.txt

### **Issue 2: Environment Variables Missing**  
**Symptoms:** API returns 500 errors or authentication failures
**Solution:**
1. Go to Environment tab
2. Verify all 4 variables are present:
   - ✓ GEMINI_API_KEY
   - ✓ TEAM_TOKEN  
   - ✓ DEFAULT_EMBEDDING_MODEL
   - ✓ PYTHONPATH
3. Save changes and redeploy

### **Issue 3: Build Timeout**
**Symptoms:** "Build exceeded time limit" 
**Solution:**
1. Try deploying again (sometimes temporary)
2. Consider upgrading to Starter plan for faster builds
3. Check if dependencies are installing correctly

---

## 🎯 **Quick Update Checklist**

- [ ] **GitHub repository** has latest cross-platform requirements.txt
- [ ] **Render service** connected to correct repository
- [ ] **Manual deploy** triggered or auto-deploy enabled  
- [ ] **Environment variables** all configured (4 total)
- [ ] **Service shows "Live"** status
- [ ] **API endpoints** respond correctly
- [ ] **No build errors** in logs
- [ ] **Ready for production** use

---

## 🚀 **Expected Timeline**

- **Manual Redeploy:** 2-5 minutes
- **New Service Creation:** 3-7 minutes  
- **Auto-Deploy Trigger:** 1-3 minutes after Git push

## 🎉 **Success Indicators**

✅ **Service Status:** "Live" (green indicator)  
✅ **Build Logs:** "Build completed successfully"  
✅ **Dependencies:** "Successfully installed python-magic" (Linux version)  
✅ **API Response:** Returns correct JSON with version info  
✅ **No Errors:** Clean logs with no dependency conflicts  

Your HackRX FastAPI is now updated and production-ready! 🎯
