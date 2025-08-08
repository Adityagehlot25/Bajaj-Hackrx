# 🔐 Environment Variables Setup - Complete Instructions

## 📍 Location in Render Dashboard

### **Go to Your Service Settings:**
1. **Open Render Dashboard**: https://dashboard.render.com
2. **Click your service**: `bajaj-hackrx-api`
3. **In left sidebar, click "Environment"**
4. **Click "+ Add Environment Variable"**

---

## ➕ Adding Environment Variables

### **Variable 1: GEMINI_API_KEY**
```
Key:   GEMINI_API_KEY
Value: AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ
```
**Click "Add"**

### **Variable 2: TEAM_TOKEN**
```
Key:   TEAM_TOKEN
Value: your_hackrx_team_token_here
```
**⚠️ Replace with your actual HackRX team token**
**Click "Add"**

### **Variable 3: DEFAULT_EMBEDDING_MODEL**
```
Key:   DEFAULT_EMBEDDING_MODEL
Value: embedding-001
```
**Click "Add"**

### **Variable 4: PYTHONPATH**
```
Key:   PYTHONPATH
Value: /opt/render/project/src
```
**Click "Add"**

---

## 💾 Save and Redeploy

### **Automatic Process:**
1. **Click "Save Changes"** (if button appears)
2. **Render automatically redeploys** when environment variables change
3. **Wait 1-3 minutes** for redeployment to complete
4. **Check deployment logs** for success confirmation

### **Manual Redeploy (if needed):**
1. **Go to service dashboard**
2. **Click "Manual Deploy"**
3. **Select "Deploy latest commit"**
4. **Click "Yes, deploy"**
5. **Wait for deployment** to finish

---

## ✅ Verification Checklist

**After redeployment, verify:**
- ✅ All 4 environment variables show in Render dashboard
- ✅ API responds: `curl https://your-app.onrender.com/`
- ✅ Expected response: `{"message": "HackRX Document Q&A API..."}`
- ✅ No environment variable errors in logs

---

## 📖 Complete Guides Available

- **`RENDER_ENVIRONMENT_SETUP.md`** - Detailed environment setup
- **`RENDER_DEPLOYMENT_GUIDE.md`** - Full deployment walkthrough  
- **`RENDER_QUICK_GUIDE.md`** - One-page quick reference

**Your HackRX FastAPI will be fully functional once environment variables are configured!** 🚀
