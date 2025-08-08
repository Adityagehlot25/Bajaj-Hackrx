# 🧪 API Testing Scripts for Deployed Endpoint

## 📋 Test Script Overview

This script tests your deployed HackRX FastAPI endpoint with:
- ✅ Valid token authentication
- ✅ JSON response format validation
- ✅ Invalid token (401 error) testing
- ✅ Multiple document formats
- ✅ Error handling verification

---

## 🔧 Curl Commands (PowerShell/CMD)

### Test 1: Valid Authentication Test
```powershell
# Replace YOUR_APP_URL with your actual deployed URL
# Example: https://hackrx-api-production.onrender.com

curl -X POST "https://YOUR_APP_URL/api/v1/hackrx/run" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer your_valid_token_here" `
  -d '{
    "document_url": "https://www.archives.gov/founding-docs/constitution-transcript",
    "questions": ["What are the three branches of government mentioned?"]
  }'
```

### Test 2: Invalid Token (401 Error) Test
```powershell
# Test with invalid token - should return 401 Unauthorized
curl -X POST "https://YOUR_APP_URL/api/v1/hackrx/run" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer invalid_token_123" `
  -d '{
    "document_url": "https://www.archives.gov/founding-docs/constitution-transcript",
    "questions": ["What are the three branches of government?"]
  }'
```

### Test 3: No Authorization Header (401 Error)
```powershell
# Test without Authorization header - should return 401
curl -X POST "https://YOUR_APP_URL/api/v1/hackrx/run" `
  -H "Content-Type: application/json" `
  -d '{
    "document_url": "https://www.archives.gov/founding-docs/constitution-transcript",
    "questions": ["What is the main purpose of this document?"]
  }'
```

### Test 4: Multiple Questions Test
```powershell
# Test with multiple questions
curl -X POST "https://YOUR_APP_URL/api/v1/hackrx/run" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer your_valid_token_here" `
  -d '{
    "document_url": "https://www.archives.gov/founding-docs/constitution-transcript",
    "questions": [
      "What is the purpose of the Constitution?",
      "How many articles are there?",
      "What does Article I establish?"
    ]
  }'
```

### Test 5: PDF Document Test
```powershell
# Test with a PDF document
curl -X POST "https://YOUR_APP_URL/api/v1/hackrx/run" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer your_valid_token_here" `
  -d '{
    "document_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
    "questions": ["What is the main content of this document?"]
  }'
```

---

## 🐍 Python Requests Test Script

```python
#!/usr/bin/env python3
"""
Comprehensive API Testing Script for HackRX FastAPI Deployment
Tests authentication, JSON response format, and error handling
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE_URL = "https://YOUR_APP_URL"  # Replace with your deployed URL
VALID_TOKEN = "your_valid_token_here"  # Replace with your valid token
INVALID_TOKEN = "invalid_token_123"

def test_api_endpoint(url: str, headers: Dict[str, str], payload: Dict[str, Any], 
                     test_name: str, expected_status: int = 200):
    """Test API endpoint with given parameters"""
    print(f"\n🧪 {test_name}")
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"Status Code: {response.status_code}")
        print(f"Expected: {expected_status}")
        
        # Print response
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
            
            # Validate response format for successful requests
            if response.status_code == 200:
                if "answers" in response_json and isinstance(response_json["answers"], list):
                    print("✅ PASS: Response has correct format with 'answers' array")
                    return True
                else:
                    print("❌ FAIL: Response missing 'answers' array")
                    return False
            elif response.status_code == expected_status:
                print(f"✅ PASS: Got expected error status {expected_status}")
                return True
            else:
                print(f"❌ FAIL: Expected {expected_status}, got {response.status_code}")
                return False
                
        except json.JSONDecodeError:
            print(f"❌ FAIL: Response is not valid JSON: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ FAIL: Request timed out")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ FAIL: Request failed: {e}")
        return False

def main():
    """Run comprehensive API tests"""
    print("🚀 Starting HackRX API Testing Suite")
    print(f"Testing endpoint: {API_BASE_URL}/api/v1/hackrx/run")
    
    endpoint = f"{API_BASE_URL}/api/v1/hackrx/run"
    results = []
    
    # Test 1: Valid authentication
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {VALID_TOKEN}"
    }
    payload = {
        "document_url": "https://www.archives.gov/founding-docs/constitution-transcript",
        "questions": ["What are the three branches of government mentioned?"]
    }
    results.append(test_api_endpoint(
        endpoint, headers, payload, 
        "Test 1: Valid Authentication", 200
    ))
    
    time.sleep(2)  # Rate limiting courtesy
    
    # Test 2: Invalid token (should return 401)
    headers_invalid = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {INVALID_TOKEN}"
    }
    results.append(test_api_endpoint(
        endpoint, headers_invalid, payload,
        "Test 2: Invalid Token (401 Expected)", 401
    ))
    
    time.sleep(2)
    
    # Test 3: No authorization header (should return 401)
    headers_no_auth = {
        "Content-Type": "application/json"
    }
    results.append(test_api_endpoint(
        endpoint, headers_no_auth, payload,
        "Test 3: No Authorization Header (401 Expected)", 401
    ))
    
    time.sleep(2)
    
    # Test 4: Multiple questions
    payload_multi = {
        "document_url": "https://www.archives.gov/founding-docs/constitution-transcript",
        "questions": [
            "What is the purpose of the Constitution?",
            "How many articles are in the Constitution?",
            "What does Article I establish?"
        ]
    }
    results.append(test_api_endpoint(
        endpoint, headers, payload_multi,
        "Test 4: Multiple Questions", 200
    ))
    
    time.sleep(2)
    
    # Test 5: Invalid payload format (should return 422)
    payload_invalid = {
        "document_url": "not_a_valid_url",
        "questions": "this should be an array"
    }
    results.append(test_api_endpoint(
        endpoint, headers, payload_invalid,
        "Test 5: Invalid Payload Format (422 Expected)", 422
    ))
    
    # Summary
    print("\n" + "="*50)
    print("🏆 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = sum(results)
    total = len(results)
    
    for i, result in enumerate(results, 1):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"Test {i}: {status}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your API is working correctly!")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    # Instructions for user
    print("📝 SETUP INSTRUCTIONS:")
    print("1. Replace 'YOUR_APP_URL' with your deployed URL")
    print("2. Replace 'your_valid_token_here' with your actual token")
    print("3. Run this script: python api_test_script.py")
    print("")
    
    # Check if configuration is updated
    if "YOUR_APP_URL" in API_BASE_URL:
        print("⚠️  Please update API_BASE_URL with your deployed URL")
        print("Example: https://hackrx-api-production.onrender.com")
        exit(1)
    
    if "your_valid_token_here" in VALID_TOKEN:
        print("⚠️  Please update VALID_TOKEN with your actual token")
        exit(1)
    
    # Run tests
    main()
```

---

## 🔧 PowerShell Test Script

```powershell
# PowerShell API Testing Script
# Save as: test_api.ps1

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiUrl,
    
    [Parameter(Mandatory=$true)]
    [string]$ValidToken
)

Write-Host "🚀 Starting HackRX API Tests" -ForegroundColor Green
Write-Host "Testing URL: $ApiUrl/api/v1/hackrx/run" -ForegroundColor Cyan

$endpoint = "$ApiUrl/api/v1/hackrx/run"
$testResults = @()

# Test 1: Valid Authentication
Write-Host "`n🧪 Test 1: Valid Authentication" -ForegroundColor Yellow

$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $ValidToken"
}

$payload = @{
    document_url = "https://www.archives.gov/founding-docs/constitution-transcript"
    questions = @("What are the three branches of government mentioned?")
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri $endpoint -Method Post -Headers $headers -Body $payload
    if ($response.answers -is [array]) {
        Write-Host "✅ PASS: Valid response with answers array" -ForegroundColor Green
        Write-Host "Response: $($response | ConvertTo-Json -Depth 3)" -ForegroundColor White
        $testResults += $true
    } else {
        Write-Host "❌ FAIL: No answers array in response" -ForegroundColor Red
        $testResults += $false
    }
} catch {
    Write-Host "❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
    $testResults += $false
}

Start-Sleep 2

# Test 2: Invalid Token (401 Expected)
Write-Host "`n🧪 Test 2: Invalid Token (401 Expected)" -ForegroundColor Yellow

$headersInvalid = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer invalid_token_123"
}

try {
    $response = Invoke-RestMethod -Uri $endpoint -Method Post -Headers $headersInvalid -Body $payload
    Write-Host "❌ FAIL: Should have returned 401 error" -ForegroundColor Red
    $testResults += $false
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "✅ PASS: Got expected 401 Unauthorized" -ForegroundColor Green
        $testResults += $true
    } else {
        Write-Host "❌ FAIL: Expected 401, got $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        $testResults += $false
    }
}

# Summary
$passed = ($testResults | Where-Object { $_ -eq $true }).Count
$total = $testResults.Count

Write-Host "`n" + "="*50 -ForegroundColor Cyan
Write-Host "🏆 TEST RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host "="*50 -ForegroundColor Cyan
Write-Host "📊 Overall: $passed/$total tests passed ($([math]::Round($passed/$total*100,1))%)" -ForegroundColor White

if ($passed -eq $total) {
    Write-Host "🎉 ALL TESTS PASSED! Your API is working correctly!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed. Check the logs above for details." -ForegroundColor Yellow
}
```

---

## 📋 Usage Instructions

### For Curl Commands:
1. Replace `YOUR_APP_URL` with your deployed URL (e.g., `https://hackrx-api-production.onrender.com`)
2. Replace `your_valid_token_here` with your actual team token
3. Run each command in PowerShell

### For Python Script:
```powershell
# Save as api_test_script.py and run:
python api_test_script.py
```

### For PowerShell Script:
```powershell
# Save as test_api.ps1 and run:
.\test_api.ps1 -ApiUrl "https://your-app.onrender.com" -ValidToken "your_token"
```

---

## ✅ Expected Results

### Successful Response (200):
```json
{
  "answers": [
    "The three branches of government mentioned are the Legislative branch (Congress), the Executive branch (President), and the Judicial branch (Supreme Court)."
  ]
}
```

### Invalid Token Response (401):
```json
{
  "detail": "Invalid or expired token"
}
```

### Invalid Payload Response (422):
```json
{
  "detail": [
    {
      "loc": ["body", "questions"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Your deployed API is now fully testable with comprehensive validation!** 🚀✨
