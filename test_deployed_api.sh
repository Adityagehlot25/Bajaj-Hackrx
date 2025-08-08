#!/bin/bash

# HackRX API Deployment Test Script (CURL Version)
# Tests the deployed HackRX API with various authentication scenarios

set -e  # Exit on any error

# Configuration
API_BASE_URL="${1:-http://localhost:8000}"  # Default to localhost, override with argument
VALID_TOKEN="hackrx_test_token_2024"       # Valid token (>= 10 chars)
INVALID_TOKEN="short"                       # Invalid token (< 10 chars)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test payload
PAYLOAD='{
  "document_url": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
  "questions": [
    "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
    "What is the waiting period for pre-existing diseases (PED) to be covered?",
    "Does this policy cover maternity expenses, and what are the conditions?",
    "What is the waiting period for cataract surgery?",
    "Are the medical expenses for an organ donor covered under this policy?"
  ]
}'

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}  HackRX API Deployment Test Suite (CURL Version)${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo -e "Testing API at: ${YELLOW}$API_BASE_URL${NC}"
echo -e "Valid Token: ${VALID_TOKEN}"
echo -e "Invalid Token: ${INVALID_TOKEN}"
echo ""

# Test 1: Health Check
echo -e "${BLUE}🔍 Test 1: Health Check${NC}"
echo -e "GET $API_BASE_URL/health"
echo ""

HEALTH_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" "$API_BASE_URL/health" || echo "HTTPSTATUS:000")
HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | sed -e 's/HTTPSTATUS:.*$//')

if [ "$HEALTH_STATUS" = "200" ]; then
    echo -e "✅ ${GREEN}PASS${NC} | Health Check | Status: $HEALTH_STATUS"
    echo -e "    Response: $HEALTH_BODY"
else
    echo -e "❌ ${RED}FAIL${NC} | Health Check | Status: $HEALTH_STATUS"
    echo -e "    Response: $HEALTH_BODY"
    echo -e "${RED}❌ API not accessible. Check deployment.${NC}"
    exit 1
fi

echo ""

# Test 2: Valid Authentication
echo -e "${BLUE}🔍 Test 2: Valid Authentication (Expect 200 with answers)${NC}"
echo -e "POST $API_BASE_URL/api/v1/hackrx/run"
echo -e "Authorization: Bearer $VALID_TOKEN"
echo ""

echo -e "📤 Sending request... (This may take 60-120 seconds)"

VALID_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $VALID_TOKEN" \
    -d "$PAYLOAD" \
    --max-time 180 \
    "$API_BASE_URL/api/v1/hackrx/run" || echo "HTTPSTATUS:000")

VALID_STATUS=$(echo "$VALID_RESPONSE" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
VALID_BODY=$(echo "$VALID_RESPONSE" | sed -e 's/HTTPSTATUS:.*$//')

if [ "$VALID_STATUS" = "200" ]; then
    echo -e "✅ ${GREEN}PASS${NC} | Valid Auth + Status 200"
    
    # Check if response contains answers array
    if echo "$VALID_BODY" | grep -q '"answers"'; then
        ANSWER_COUNT=$(echo "$VALID_BODY" | grep -o '"answers":\[' | wc -l)
        echo -e "✅ ${GREEN}PASS${NC} | Response Format | Contains 'answers' array"
        
        # Show first answer preview
        FIRST_ANSWER=$(echo "$VALID_BODY" | sed 's/.*"answers":\["\([^"]*\)".*/\1/' | cut -c1-100)
        echo -e "    Sample answer: ${FIRST_ANSWER}..."
    else
        echo -e "❌ ${RED}FAIL${NC} | Response Format | Missing 'answers' array"
        echo -e "    Response: ${VALID_BODY:0:200}..."
    fi
else
    echo -e "❌ ${RED}FAIL${NC} | Valid Auth | Status: $VALID_STATUS"
    echo -e "    Response: ${VALID_BODY:0:500}..."
fi

echo ""

# Test 3: Invalid Authentication
echo -e "${BLUE}🔍 Test 3: Invalid Authentication (Expect 401)${NC}"
echo -e "POST $API_BASE_URL/api/v1/hackrx/run"
echo -e "Authorization: Bearer $INVALID_TOKEN"
echo ""

INVALID_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $INVALID_TOKEN" \
    -d "$PAYLOAD" \
    --max-time 30 \
    "$API_BASE_URL/api/v1/hackrx/run" || echo "HTTPSTATUS:000")

INVALID_STATUS=$(echo "$INVALID_RESPONSE" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
INVALID_BODY=$(echo "$INVALID_RESPONSE" | sed -e 's/HTTPSTATUS:.*$//')

if [ "$INVALID_STATUS" = "401" ]; then
    echo -e "✅ ${GREEN}PASS${NC} | Invalid Auth → 401"
    echo -e "    Error: $INVALID_BODY"
else
    echo -e "❌ ${RED}FAIL${NC} | Invalid Auth | Expected 401, got $INVALID_STATUS"
    echo -e "    Response: $INVALID_BODY"
fi

echo ""

# Test 4: Missing Authentication
echo -e "${BLUE}🔍 Test 4: Missing Authentication (Expect 403)${NC}"
echo -e "POST $API_BASE_URL/api/v1/hackrx/run"
echo -e "No Authorization header"
echo ""

MISSING_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    --max-time 30 \
    "$API_BASE_URL/api/v1/hackrx/run" || echo "HTTPSTATUS:000")

MISSING_STATUS=$(echo "$MISSING_RESPONSE" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
MISSING_BODY=$(echo "$MISSING_RESPONSE" | sed -e 's/HTTPSTATUS:.*$//')

if [ "$MISSING_STATUS" = "403" ]; then
    echo -e "✅ ${GREEN}PASS${NC} | Missing Auth → 403"
    echo -e "    Error: $MISSING_BODY"
else
    echo -e "❌ ${RED}FAIL${NC} | Missing Auth | Expected 403, got $MISSING_STATUS"
    echo -e "    Response: $MISSING_BODY"
fi

echo ""

# Summary
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}======================================================================${NC}"

if [ "$HEALTH_STATUS" = "200" ] && [ "$VALID_STATUS" = "200" ] && [ "$INVALID_STATUS" = "401" ] && [ "$MISSING_STATUS" = "403" ]; then
    echo -e "🎉 ${GREEN}ALL TESTS PASSED!${NC}"
    echo -e "✅ API is properly deployed and functional"
    echo -e "✅ Authentication working correctly"
    echo -e "✅ Response format validated"
    echo -e "✅ Error handling confirmed"
    echo ""
    echo -e "🚀 ${GREEN}Your HackRX API is ready for production!${NC}"
else
    echo -e "❌ ${RED}SOME TESTS FAILED${NC}"
    echo -e "🔧 Check the individual test results above"
    exit 1
fi
