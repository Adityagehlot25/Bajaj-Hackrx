# 🧪 HackRX API Deployment Testing Guide

This guide provides multiple ways to test your deployed HackRX API endpoint with proper authentication validation.

## 📋 Test Scripts Overview

### 1. **Python Test Script** (Recommended)
- **File:** `test_deployed_api.py`
- **Features:** Comprehensive testing with colored output
- **Requirements:** `pip install requests`

### 2. **Simple Python Test**
- **File:** `simple_api_test.py`  
- **Features:** Lightweight, minimal dependencies
- **Requirements:** `pip install requests`

### 3. **Bash/Linux Script**
- **File:** `test_deployed_api.sh`
- **Features:** Pure curl commands, no dependencies
- **Requirements:** bash, curl

### 4. **PowerShell Script** 
- **File:** `test_deployed_api.ps1`
- **Features:** Windows-native, PowerShell cmdlets
- **Requirements:** PowerShell 5.1+

---

## 🚀 Quick Start Testing

### Option 1: Python Test (Recommended)

```bash
# Install requests if needed
pip install requests

# Test localhost (if running locally)
python simple_api_test.py

# Test your deployed API
python simple_api_test.py https://your-hackrx-api.onrender.com
```

### Option 2: PowerShell (Windows)

```powershell
# Test localhost
.\\test_deployed_api.ps1

# Test deployed API
.\\test_deployed_api.ps1 -ApiBaseUrl "https://your-hackrx-api.onrender.com"
```

### Option 3: Bash/Linux

```bash
# Make executable
chmod +x test_deployed_api.sh

# Test localhost
./test_deployed_api.sh

# Test deployed API  
./test_deployed_api.sh https://your-hackrx-api.onrender.com
```

---

## 🧪 Manual CURL Testing

### 1. Health Check
```bash
curl -X GET https://your-hackrx-api.onrender.com/health
```

**Expected:** `200 OK` with health status

### 2. Valid Authentication Test
```bash
curl -X POST https://your-hackrx-api.onrender.com/api/v1/hackrx/run \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer hackrx_test_token_2024" \\
  -d '{
    "document_url": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
      "What is the grace period for premium payment?",
      "What is the waiting period for pre-existing diseases?"
    ]
  }'
```

**Expected:** `200 OK` with JSON response:
```json
{
  "answers": [
    "The grace period for premium payment is thirty days.",
    "The waiting period for pre-existing diseases is thirty-six months."
  ]
}
```

### 3. Invalid Authentication Test
```bash
curl -X POST https://your-hackrx-api.onrender.com/api/v1/hackrx/run \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer short" \\
  -d '{
    "document_url": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": ["What is the grace period?"]
  }'
```

**Expected:** `401 Unauthorized` with error:
```json
{
  "detail": "Invalid authorization token"
}
```

### 4. Missing Authentication Test
```bash
curl -X POST https://your-hackrx-api.onrender.com/api/v1/hackrx/run \\
  -H "Content-Type: application/json" \\
  -d '{
    "document_url": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": ["What is the grace period?"]
  }'
```

**Expected:** `403 Forbidden` with error:
```json
{
  "detail": "Not authenticated"
}
```

---

## ✅ Expected Test Results

### Successful Test Run Output:
```
======================================================================
  Testing HackRX API: https://your-hackrx-api.onrender.com
======================================================================

🔍 Test 1: Health Check
✅ PASS | Health Check | Status: 200

🔍 Test 2: Valid Authentication (Expect 200 + answers)
   📤 Sending request with token: hackrx_tes...
   ⏱️  Response time: 45.67 seconds
✅ PASS | Valid Auth + Format | Got 5 answers
      Sample answer: The grace period for premium payment under...

🔍 Test 3: Invalid Authentication (Expect 401)
✅ PASS | Invalid Auth → 401 | Error: Invalid authorization token

🔍 Test 4: Missing Authentication (Expect 403)
✅ PASS | Missing Auth → 403 | Error: Not authenticated

======================================================================
  Test Summary
======================================================================
🎉 All tests PASSED!
✅ Authentication working correctly
✅ Response format validated
✅ Error handling confirmed

🚀 Your HackRX API is ready for production!
```

---

## 🔧 Authentication Details

### Valid Tokens (API will process these):
- Any Bearer token with **10 or more characters**
- Examples: `hackrx_test_token_2024`, `my_secret_api_key_123`

### Invalid Tokens (API will reject with 401):
- Any Bearer token with **less than 10 characters**
- Examples: `short`, `test123`, `abc`

### Missing Authentication (API will reject with 403):
- No `Authorization` header provided
- Empty `Authorization` header

---

## 🌐 Common Deployment URLs

Update the test scripts with your actual deployment URL:

### Render.com
```
https://your-hackrx-api.onrender.com
```

### Railway
```
https://your-hackrx-api.railway.app
```

### Heroku
```
https://your-hackrx-api.herokuapp.com
```

### Local Development
```
http://localhost:8000
```

---

## 📊 Performance Expectations

### Typical Response Times:
- **Health Check:** < 1 second
- **Valid Request:** 45-120 seconds (document processing + AI generation)
- **Authentication Errors:** < 1 second

### Response Sizes:
- **Successful Response:** 2-10 KB (depending on answer length)
- **Error Response:** < 1 KB

---

## 🐛 Troubleshooting

### Connection Refused Error
```
Max retries exceeded... Connection refused
```
**Solution:** 
- Check if API is deployed and running
- Verify the URL is correct
- Check deployment logs

### Timeout Error
```
Request timeout (>120s)
```  
**Solution:**
- Normal for large documents
- Increase timeout in test scripts
- Check API logs for processing issues

### Authentication Errors
```
401 Unauthorized / 403 Forbidden
```
**Solution:**
- Verify token format (Bearer prefix)
- Check token length (>=10 chars for valid)
- Confirm Authorization header is included

### Invalid JSON Response
```
JSONDecodeError: Expecting value
```
**Solution:**
- API might be returning HTML error page
- Check deployment status
- Review server logs

---

## 📝 Test Script Customization

### Update API URL
```python
# In Python scripts
API_BASE_URL = "https://your-actual-api-url.com"
```

```bash
# In bash script
API_BASE_URL="https://your-actual-api-url.com"
```

```powershell
# In PowerShell script  
$ApiBaseUrl = "https://your-actual-api-url.com"
```

### Custom Questions
```python
SAMPLE_PAYLOAD = {
    "document_url": "your_document_url",
    "questions": [
        "Your custom question 1?",
        "Your custom question 2?",
        # Add more questions...
    ]
}
```

---

## 🎯 Production Validation Checklist

- [ ] Health endpoint responds with 200
- [ ] Valid authentication returns answers array
- [ ] Invalid authentication returns 401
- [ ] Missing authentication returns 403  
- [ ] Response format matches `{"answers": [...]}`
- [ ] API processes within reasonable time (<120s)
- [ ] Error messages are informative
- [ ] CORS headers allow cross-origin requests

---

**🎉 Ready to test your HackRX API! Choose your preferred testing method above.**
