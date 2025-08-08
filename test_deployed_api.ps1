# HackRX API Deployment Test Script (PowerShell Version)
# Tests the deployed HackRX API with various authentication scenarios

param(
    [string]$ApiBaseUrl = "http://localhost:8000",
    [switch]$Help
)

if ($Help) {
    Write-Host @"
HackRX API Deployment Test Script

Usage:
    .\test_deployed_api.ps1                          # Test localhost:8000
    .\test_deployed_api.ps1 -ApiBaseUrl "https://your-api.com"  # Test custom URL

Tests:
    1. Health check endpoint
    2. Valid authentication (expect 200 + answers)
    3. Invalid authentication (expect 401)
    4. Missing authentication (expect 403)
"@
    exit 0
}

# Configuration
$ValidToken = "hackrx_test_token_2024"  # Valid token (>= 10 chars)
$InvalidToken = "short"                  # Invalid token (< 10 chars)

# Test payload
$Payload = @{
    document_url = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
    questions = @(
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the waiting period for cataract surgery?",
        "Are the medical expenses for an organ donor covered under this policy?"
    )
} | ConvertTo-Json -Depth 3

# Helper Functions
function Write-Header($Title) {
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Blue
    Write-Host "  $Title" -ForegroundColor Blue
    Write-Host ("=" * 70) -ForegroundColor Blue
}

function Write-TestResult($TestName, $Success, $Details = "") {
    $Status = if ($Success) { "✅ PASS" } else { "❌ FAIL" }
    $Color = if ($Success) { "Green" } else { "Red" }
    Write-Host "$Status | $TestName" -ForegroundColor $Color
    if ($Details) {
        Write-Host "      $Details" -ForegroundColor Gray
    }
}

# Main Test Function
function Test-HackRXAPI($BaseUrl) {
    Write-Header "Testing HackRX API: $BaseUrl"
    
    $HealthEndpoint = "$BaseUrl/health"
    $ApiEndpoint = "$BaseUrl/api/v1/hackrx/run"
    $OverallSuccess = $true
    
    # Test 1: Health Check
    Write-Host ""
    Write-Host "🔍 Test 1: Health Check" -ForegroundColor Cyan
    
    try {
        $HealthResponse = Invoke-RestMethod -Uri $HealthEndpoint -Method Get -TimeoutSec 10
        Write-TestResult "Health Check" $true "API is accessible"
    }
    catch {
        Write-TestResult "Health Check" $false "Connection failed: $($_.Exception.Message)"
        $OverallSuccess = $false
        return $false
    }
    
    # Test 2: Valid Authentication
    Write-Host ""
    Write-Host "🔍 Test 2: Valid Authentication" -ForegroundColor Cyan
    Write-Host "   📤 Sending request with token: $($ValidToken.Substring(0, 10))..." -ForegroundColor Gray
    
    try {
        $Headers = @{
            "Authorization" = "Bearer $ValidToken"
            "Content-Type" = "application/json"
        }
        
        $StartTime = Get-Date
        Write-Host "   ⏱️  Processing... (this may take 60-120 seconds)" -ForegroundColor Yellow
        
        $ValidResponse = Invoke-RestMethod -Uri $ApiEndpoint -Method Post -Body $Payload -Headers $Headers -TimeoutSec 180
        $ElapsedTime = (Get-Date) - $StartTime
        
        Write-Host "   ⏱️  Response time: $([math]::Round($ElapsedTime.TotalSeconds, 2)) seconds" -ForegroundColor Gray
        
        if ($ValidResponse.PSObject.Properties.Name -contains "answers" -and $ValidResponse.answers -is [array]) {
            $AnswerCount = $ValidResponse.answers.Count
            Write-TestResult "Valid Auth + Correct Format" $true "Got $AnswerCount answers"
            
            if ($ValidResponse.answers.Count -gt 0) {
                $FirstAnswer = $ValidResponse.answers[0]
                $Preview = if ($FirstAnswer.Length -gt 100) { $FirstAnswer.Substring(0, 100) + "..." } else { $FirstAnswer }
                Write-Host "      Sample answer: $Preview" -ForegroundColor Gray
            }
        }
        else {
            Write-TestResult "Valid Auth + Correct Format" $false "Invalid response format"
            $OverallSuccess = $false
        }
    }
    catch {
        $ErrorMsg = $_.Exception.Message
        if ($_.Exception.Response) {
            $StatusCode = $_.Exception.Response.StatusCode
            Write-TestResult "Valid Auth + Correct Format" $false "Status: $StatusCode, Error: $ErrorMsg"
        }
        else {
            Write-TestResult "Valid Auth + Correct Format" $false "Request failed: $ErrorMsg"
        }
        $OverallSuccess = $false
    }
    
    # Test 3: Invalid Authentication
    Write-Host ""
    Write-Host "🔍 Test 3: Invalid Authentication" -ForegroundColor Cyan
    
    try {
        $InvalidHeaders = @{
            "Authorization" = "Bearer $InvalidToken"
            "Content-Type" = "application/json"
        }
        
        $InvalidResponse = Invoke-RestMethod -Uri $ApiEndpoint -Method Post -Body $Payload -Headers $InvalidHeaders -TimeoutSec 30
        Write-TestResult "Invalid Auth → 401" $false "Expected 401, but request succeeded"
        $OverallSuccess = $false
    }
    catch {
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode -eq 401) {
            Write-TestResult "Invalid Auth → 401" $true "Correctly rejected with 401"
        }
        else {
            $StatusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { "Unknown" }
            Write-TestResult "Invalid Auth → 401" $false "Expected 401, got $StatusCode"
            $OverallSuccess = $false
        }
    }
    
    # Test 4: Missing Authentication
    Write-Host ""
    Write-Host "🔍 Test 4: Missing Authentication" -ForegroundColor Cyan
    
    try {
        $NoAuthHeaders = @{
            "Content-Type" = "application/json"
        }
        
        $MissingResponse = Invoke-RestMethod -Uri $ApiEndpoint -Method Post -Body $Payload -Headers $NoAuthHeaders -TimeoutSec 30
        Write-TestResult "Missing Auth → 403" $false "Expected 403, but request succeeded"
        $OverallSuccess = $false
    }
    catch {
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode -eq 403) {
            Write-TestResult "Missing Auth → 403" $true "Correctly rejected with 403"
        }
        else {
            $StatusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { "Unknown" }
            Write-TestResult "Missing Auth → 403" $false "Expected 403, got $StatusCode"
            $OverallSuccess = $false
        }
    }
    
    return $OverallSuccess
}

# Generate curl commands for reference
function Show-CurlCommands($BaseUrl) {
    Write-Header "Equivalent CURL Commands"
    
    Write-Host ""
    Write-Host "1️⃣ Health Check:" -ForegroundColor Yellow
    Write-Host "curl -X GET $BaseUrl/health" -ForegroundColor White
    
    Write-Host ""
    Write-Host "2️⃣ Valid Authentication Test:" -ForegroundColor Yellow
    Write-Host @"
curl -X POST $BaseUrl/api/v1/hackrx/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ValidToken" \
  -d '$($Payload -replace "`n", " " -replace "`r", "")'
"@ -ForegroundColor White
    
    Write-Host ""
    Write-Host "3️⃣ Invalid Authentication Test:" -ForegroundColor Yellow
    Write-Host @"
curl -X POST $BaseUrl/api/v1/hackrx/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $InvalidToken" \
  -d '$($Payload -replace "`n", " " -replace "`r", "")'
"@ -ForegroundColor White
    
    Write-Host ""
    Write-Host "4️⃣ Missing Authentication Test:" -ForegroundColor Yellow
    Write-Host @"
curl -X POST $BaseUrl/api/v1/hackrx/run \
  -H "Content-Type: application/json" \
  -d '$($Payload -replace "`n", " " -replace "`r", "")'
"@ -ForegroundColor White
}

# Main Execution
Write-Header "HackRX API Deployment Test Suite"
Write-Host "Testing authentication, validation, and response format..." -ForegroundColor Gray
Write-Host "Test payload contains $($Payload | ConvertFrom-Json | Select-Object -ExpandProperty questions | Measure-Object | Select-Object -ExpandProperty Count) questions" -ForegroundColor Gray

$TestSuccess = Test-HackRXAPI $ApiBaseUrl

if ($TestSuccess) {
    Show-CurlCommands $ApiBaseUrl
}

# Final Summary
Write-Header "Test Summary"

if ($TestSuccess) {
    Write-Host "🎉 API deployment test PASSED!" -ForegroundColor Green
    Write-Host "✅ Authentication working correctly" -ForegroundColor Green
    Write-Host "✅ Response format validated" -ForegroundColor Green
    Write-Host "✅ Error handling confirmed" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Your HackRX API is ready for production!" -ForegroundColor Green
}
else {
    Write-Host "❌ API deployment test FAILED" -ForegroundColor Red
    Write-Host "🔧 Check deployment status and try again" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Verify API is deployed and accessible" -ForegroundColor White
    Write-Host "2. Check environment variables (GEMINI_API_KEY)" -ForegroundColor White
    Write-Host "3. Review deployment logs for errors" -ForegroundColor White
    exit 1
}
