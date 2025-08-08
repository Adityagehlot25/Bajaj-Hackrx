# 🧪 Quick API Test Commands
# Copy and paste these curl commands to test your deployed API

# CONFIGURATION - Update these values:
# Replace YOUR_DEPLOYED_URL with your actual URL (e.g., https://hackrx-api-production.onrender.com)
# Replace YOUR_VALID_TOKEN with your actual team token

Write-Host "🚀 HackRX API Quick Test Suite" -ForegroundColor Green
Write-Host "Update the URL and TOKEN variables below, then run each test" -ForegroundColor Yellow

# Variables - UPDATE THESE
$API_URL = "YOUR_DEPLOYED_URL"  # e.g., https://hackrx-api-production.onrender.com
$VALID_TOKEN = "YOUR_VALID_TOKEN"  # Your actual team token

# Test 1: Valid Authentication Test
Write-Host "`n🧪 Test 1: Valid Authentication (Should return JSON with answers array)" -ForegroundColor Cyan

$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $VALID_TOKEN"
}

$body = @{
    document_url = "https://www.archives.gov/founding-docs/constitution-transcript"
    questions = @("What are the three branches of government mentioned in the Constitution?")
} | ConvertTo-Json

Write-Host "Command:" -ForegroundColor White
Write-Host "curl -X POST `"$API_URL/api/v1/hackrx/run`" -H `"Content-Type: application/json`" -H `"Authorization: Bearer $VALID_TOKEN`" -d '$body'" -ForegroundColor Gray

# Uncomment to run automatically:
# try {
#     $response = Invoke-RestMethod -Uri "$API_URL/api/v1/hackrx/run" -Method Post -Headers $headers -Body $body
#     Write-Host "✅ SUCCESS: $($response | ConvertTo-Json -Depth 3)" -ForegroundColor Green
# } catch {
#     Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
# }

# Test 2: Invalid Token Test (Should return 401)
Write-Host "`n🧪 Test 2: Invalid Token (Should return 401 Unauthorized)" -ForegroundColor Cyan

$invalidHeaders = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer invalid_token_123"
}

Write-Host "Command:" -ForegroundColor White
Write-Host "curl -X POST `"$API_URL/api/v1/hackrx/run`" -H `"Content-Type: application/json`" -H `"Authorization: Bearer invalid_token_123`" -d '$body'" -ForegroundColor Gray

# Test 3: No Authorization Header (Should return 401)
Write-Host "`n🧪 Test 3: Missing Authorization (Should return 401 Unauthorized)" -ForegroundColor Cyan

Write-Host "Command:" -ForegroundColor White
Write-Host "curl -X POST `"$API_URL/api/v1/hackrx/run`" -H `"Content-Type: application/json`" -d '$body'" -ForegroundColor Gray

# Expected Results
Write-Host "`n📋 Expected Results:" -ForegroundColor Yellow
Write-Host "✅ Test 1: Status 200 with JSON response containing 'answers' array" -ForegroundColor White
Write-Host "✅ Test 2: Status 401 with error message about invalid token" -ForegroundColor White  
Write-Host "✅ Test 3: Status 401 with error message about missing authorization" -ForegroundColor White

Write-Host "`n🔧 Manual Testing:" -ForegroundColor Yellow
Write-Host "1. Update the variables at the top of this script" -ForegroundColor White
Write-Host "2. Copy and paste each curl command into your terminal" -ForegroundColor White
Write-Host "3. Verify the responses match the expected results" -ForegroundColor White
