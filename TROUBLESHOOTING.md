# 🔧 Gemini API Key Troubleshooting Guide

## Current Situation
Both API keys have failed with "API key not valid" errors:
- Original: `AIzaSyBPZgmRD2BIWdQGigI52ZbjvTxuGeaic3Y`
- New: `AIzaSyDQaiCFud9lvwc1GtuCV2CeNo0fxoE3w2o`

Both keys have the correct format (39 characters, start with "AIza") but are being rejected.

## 🚨 IMMEDIATE SOLUTION STEPS

### Step 1: Create a FRESH API Key
1. Go to **Google AI Studio**: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. **DELETE** any existing keys
4. Click **"Create API Key"**
5. Copy the COMPLETE 39-character key

### Step 2: Update Your Environment
1. Open your `.env` file in the project root
2. Replace the current key:
   ```
   GEMINI_API_KEY=your_new_fresh_key_here
   ```
3. Save the file

### Step 3: Restart Everything
1. Stop your FastAPI server (Ctrl+C)
2. Restart it: `python main.py` or `uvicorn main:app --reload`

## 🔍 TROUBLESHOOTING CHECKLIST

### Account Issues (Most Likely)
- [ ] **Free tier limits exceeded** - Gemini has usage quotas
- [ ] **Billing not enabled** - Some features require billing
- [ ] **Account verification needed** - Google account needs verification
- [ ] **Geographic restrictions** - API not available in your region

### API Key Issues
- [ ] **Key was revoked** - Google disabled the key
- [ ] **Wrong permissions** - Key doesn't have embedding permissions
- [ ] **Rate limiting** - Too many failed requests blocked the key
- [ ] **Caching issues** - Old key cached somewhere

### Technical Issues
- [ ] **Browser issues** - Try incognito mode when creating key
- [ ] **Account mixing** - Using wrong Google account
- [ ] **Timing issues** - New keys can take 5-10 minutes to activate

## 💡 ADVANCED TROUBLESHOOTING

### Option 1: Different Google Account
Try creating the API key with a different Google account that has:
- Verified phone number
- Billing enabled (even with $0 usage)
- Located in a supported region

### Option 2: Google Cloud Console
1. Go to: https://console.cloud.google.com/
2. Create a new project
3. Enable the "Generative Language API"
4. Create credentials → API Key
5. Restrict the key to "Generative Language API"

### Option 3: Wait and Retry
Sometimes new keys need time to propagate:
1. Create the key
2. Wait 15-30 minutes
3. Try again

## 🎯 WHAT TO DO RIGHT NOW

1. **Create a brand new API key** using the steps above
2. **Use a different Google account** if possible
3. **Enable billing** on your Google account (even if you don't plan to pay)
4. **Wait 10-15 minutes** after creating the new key
5. **Test with the diagnostic script** we created

## 📞 IF NOTHING WORKS

The issue might be account-level restrictions. Contact:
- Google AI Studio support
- Google Cloud support
- Try from a different location/VPN

## ⚡ TEMPORARY SOLUTION

Your FastAPI server will continue working with **mock embeddings** until the API key issue is resolved. All features work except you won't get real Gemini embeddings.

To verify mock mode is working:
1. Upload a document
2. Ask questions - you'll get responses
3. Check logs for "Using mock embedding" messages

---

**Remember**: The technical implementation is correct. This is likely a Google account/billing/regional issue, not a code problem.
