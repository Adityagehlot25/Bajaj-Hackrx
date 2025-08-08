# Render Service Update - Quick Visual Guide

```
🔄 RENDER SERVICE UPDATE PROCESS
================================

Option A: EXISTING SERVICE UPDATE
┌─────────────────────────────────┐
│  1. Open Render Dashboard       │
│     https://dashboard.render.com│
└─────────────┬───────────────────┘
              │
┌─────────────▼───────────────────┐
│  2. Find Your Service           │
│     → Click service name        │
└─────────────┬───────────────────┘
              │
┌─────────────▼───────────────────┐
│  3. Manual Deploy               │
│     → Click "Manual Deploy"     │
│     → "Deploy latest commit"    │
│     → Confirm "Yes, deploy"     │
└─────────────┬───────────────────┘
              │
┌─────────────▼───────────────────┐
│  4. Wait & Monitor              │
│     → Watch logs tab            │
│     → 2-5 minutes completion    │
│     → Status shows "Live"       │
└─────────────────────────────────┘

Option B: NEW SERVICE CREATION
┌─────────────────────────────────┐
│  1. Dashboard → New +           │
│     → Select "Web Service"      │
└─────────────┬───────────────────┘
              │
┌─────────────▼───────────────────┐
│  2. Connect Repository          │
│  github.com/Adityagehlot25/    │
│  Bajaj-Hackrx                   │
└─────────────┬───────────────────┘
              │
┌─────────────▼───────────────────┐
│  3. Configure Service           │
│  Name: bajaj-hackrx-api         │
│  Build: pip install -r req...   │
│  Start: python hackrx_api_...   │
└─────────────┬───────────────────┘
              │
┌─────────────▼───────────────────┐
│  4. Add Environment Variables   │
│  GEMINI_API_KEY=AIza...         │
│  TEAM_TOKEN=your_token...       │
│  DEFAULT_EMBEDDING_MODEL=...    │
│  PYTHONPATH=/opt/render/...     │
└─────────────┬───────────────────┘
              │
┌─────────────▼───────────────────┐
│  5. Create Web Service          │
│     → Wait 3-5 minutes          │
│     → Monitor deployment        │
└─────────────────────────────────┘

SUCCESS VERIFICATION
┌─────────────────────────────────┐
│  ✅ Service Status: "Live"      │
│  ✅ No build errors in logs     │
│  ✅ API responds to curl test   │
│  ✅ Environment vars loaded     │
└─────────────────────────────────┘
```

## 🎯 One-Minute Update Steps

### If You Already Have a Render Service:
1. **Go to:** https://dashboard.render.com
2. **Click:** Your service name  
3. **Click:** "Manual Deploy"
4. **Select:** "Deploy latest commit"
5. **Wait:** 2-5 minutes ⏱️
6. **Verify:** Service shows "Live" ✅

### If This is Your First Deployment:
1. **Go to:** https://dashboard.render.com
2. **Click:** "New +" → "Web Service"
3. **Connect:** `Adityagehlot25/Bajaj-Hackrx`
4. **Configure:**
   - Build: `pip install -r requirements.txt`
   - Start: `python hackrx_api_fixed.py`
5. **Add Environment Variables** (4 total)
6. **Click:** "Create Web Service"
7. **Wait:** 3-5 minutes ⏱️

## 🔍 Quick Test Commands

```bash
# Replace 'your-service-name' with actual Render service name

# Test basic connectivity
curl https://your-service-name.onrender.com/

# Test full API (with your actual team token)
curl -X POST "https://your-service-name.onrender.com/api/v1/hackrx/run" \
  -H "Authorization: Bearer YOUR_TEAM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_url": "https://example.com/doc.pdf", "questions": ["test?"]}'
```

## ⚡ Expected Results

**✅ Successful Update Indicators:**
- Service status shows "Live" (green)
- Build logs show "python-magic" installed (Linux version)
- API returns JSON with version info
- No dependency conflicts in logs

**❌ Common Issues:**
- Still getting `python-magic-bin` errors? → Clear build cache & redeploy
- 500 errors? → Check environment variables are set
- Build timeout? → Try again or upgrade to paid plan
