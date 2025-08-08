# 🚀 Quick Render Deployment Card

## 📋 One-Page Render Setup Guide

### 1️⃣ **Render Account Setup**
- Go to **https://render.com**
- Sign up with **GitHub account**
- Authorize **repository access**

### 2️⃣ **Create Web Service**
- Click **"New +" → "Web Service"**
- Connect repository: **`Adityagehlot25/Bajaj-Hackrx`**
- Click **"Connect"**

### 3️⃣ **Configuration Settings**
```
Service Name:    bajaj-hackrx-api
Runtime:         Python 3
Build Command:   pip install -r requirements.txt
Start Command:   uvicorn hackrx_api_fixed:app --host 0.0.0.0 --port $PORT
Instance Type:   Free
Branch:          main
```

### 4️⃣ **Environment Variables** (Critical!)
```
GEMINI_API_KEY = AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ
TEAM_TOKEN = your_hackrx_team_token_here
DEFAULT_EMBEDDING_MODEL = embedding-001
```

### 5️⃣ **Deploy & Test**
- Click **"Create Web Service"**
- Wait **2-5 minutes** for deployment
- Test: **`https://your-app.onrender.com/`**

---

## 🔗 **Your Live URLs**
```
Root:     https://bajaj-hackrx-api.onrender.com/
API:      https://bajaj-hackrx-api.onrender.com/api/v1/hackrx/run
```

## ✅ **Quick Test**
```bash
curl https://bajaj-hackrx-api.onrender.com/
```

**Expected**: `{"message": "HackRX Document Q&A API (Fixed Version)"}`

---

## 📖 **Full Guides Available:**
- `RENDER_DEPLOYMENT_GUIDE.md` - Complete step-by-step (recommended)
- `DEPLOYMENT_GUIDE.md` - Multi-platform options
- `API_TEST_SCRIPTS.md` - Testing your deployed API

**Ready for HackRX Competition!** 🏆
