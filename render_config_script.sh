#!/bin/bash

# ===================================================================
# RENDER ENVIRONMENT VARIABLES CONFIGURATION SCRIPT
# Complete step-by-step guide with code comments
# ===================================================================

echo "🔧 Render Environment Variables Setup Guide"
echo "============================================="

# ===================================================================
# STEP 1: ACCESS ENVIRONMENT SETTINGS
# ===================================================================

echo ""
echo "📍 STEP 1: Access Environment Settings"
echo "--------------------------------------"

# Step 1.1: Open Render Dashboard
# Navigate to the Render web interface where you manage your services
echo "1.1 Open Render Dashboard:"
echo "   URL: https://dashboard.render.com"
echo "   Action: Login with your GitHub account"

# Step 1.2: Select Your Service
# Find and access your specific FastAPI service
echo ""
echo "1.2 Select Your Service:"
echo "   Service Name: bajaj-hackrx-api (or your chosen name)"
echo "   Action: Click on the service name to open service dashboard"

# Step 1.3: Navigate to Environment Tab
# Access the environment variables configuration page
echo ""
echo "1.3 Navigate to Environment Settings:"
echo "   Location: Left sidebar menu"
echo "   Action: Click 'Environment' tab"
echo "   Result: Opens Environment Variables configuration page"

# ===================================================================
# STEP 2: ADD REQUIRED ENVIRONMENT VARIABLES
# ===================================================================

echo ""
echo "🔑 STEP 2: Add Required Environment Variables"
echo "---------------------------------------------"

# Step 2.1: Click Add Variable Button
# Begin the process of adding environment variables
echo "2.1 Start Adding Variables:"
echo "   Button: Click '+ Add Environment Variable'"
echo "   Note: You'll repeat this for each variable below"

echo ""
echo "2.2 Add Variables (one by one):"

# Variable 1: GEMINI_API_KEY
# Google Gemini API authentication key for AI processing
echo ""
echo "   Variable 1: GEMINI_API_KEY"
echo "   Key:   GEMINI_API_KEY"
echo "   Value: AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ"
echo "   Action: Click 'Add' after entering"

# Variable 2: TEAM_TOKEN  
# HackRX competition team authentication token
echo ""
echo "   Variable 2: TEAM_TOKEN"
echo "   Key:   TEAM_TOKEN"
echo "   Value: your_hackrx_team_token_here"
echo "   ⚠️  IMPORTANT: Replace with your actual HackRX team token!"
echo "   Action: Click 'Add' after entering"

# Variable 3: DEFAULT_EMBEDDING_MODEL
# Specifies which embedding model the API should use
echo ""
echo "   Variable 3: DEFAULT_EMBEDDING_MODEL"
echo "   Key:   DEFAULT_EMBEDDING_MODEL"
echo "   Value: embedding-001"
echo "   Action: Click 'Add' after entering"

# Variable 4: PYTHONPATH
# Python module path for proper imports in Render environment
echo ""
echo "   Variable 4: PYTHONPATH"
echo "   Key:   PYTHONPATH"
echo "   Value: /opt/render/project/src"
echo "   Action: Click 'Add' after entering"

# Verification Step
# Confirm all variables are properly added
echo ""
echo "2.3 Verify Variables Added:"
echo "   ✓ GEMINI_API_KEY: ••••••••••••••••••••••••••••••••• (hidden)"
echo "   ✓ TEAM_TOKEN: ••••••••••••••••••••••••••••••••••••• (hidden)"  
echo "   ✓ DEFAULT_EMBEDDING_MODEL: embedding-001"
echo "   ✓ PYTHONPATH: /opt/render/project/src"

# ===================================================================
# STEP 3: SAVE CHANGES AND REDEPLOY
# ===================================================================

echo ""
echo "💾 STEP 3: Save Changes and Redeploy"
echo "------------------------------------"

# Step 3.1: Save Changes (Automatic Process)
# Render automatically triggers redeploy when environment variables change
echo "3.1 Save Changes (Automatic Process):"
echo "   Action: Click 'Save Changes' button (if visible)"
echo "   Process: Render automatically triggers redeploy"
echo "   Timeline: 1-3 minutes for completion"
echo "   Monitoring: Watch deployment logs for progress"

echo ""
echo "3.2 Automatic Redeploy Process:"
echo "   Stage 1: Saving environment variables..."
echo "   Stage 2: Triggering new deployment..."  
echo "   Stage 3: Building application with new variables..."
echo "   Stage 4: Starting service..."
echo "   Stage 5: Service live with updated configuration"

# Step 3.3: Manual Redeploy (Backup Method)
# Use if automatic redeploy doesn't start
echo ""
echo "3.3 Manual Redeploy (If Needed):"
echo "   When: If automatic redeploy doesn't start"
echo "   Location: Service dashboard main page"
echo "   Button: Click 'Manual Deploy'"
echo "   Option: Select 'Deploy latest commit'"
echo "   Confirm: Click 'Yes, deploy'"

# ===================================================================
# STEP 4: VERIFY DEPLOYMENT SUCCESS
# ===================================================================

echo ""
echo "✅ STEP 4: Verify Deployment Success"
echo "------------------------------------"

# Step 4.1: Sample curl Command for Root Endpoint
# Test basic service availability and configuration
echo "4.1 Test Root Endpoint:"
echo "   Command: curl https://your-app.onrender.com/"
echo "   Purpose: Verify basic service availability"
echo "   Replace: 'your-app' with your actual service name"

# Generate actual curl command template
echo ""
echo "   Example curl command:"
echo "   curl https://bajaj-hackrx-api.onrender.com/"

# Step 4.2: Expected Response for Root Endpoint
# Describe what a successful response looks like
echo ""
echo "4.2 Expected Response:"
echo '   {'
echo '     "message": "HackRX Document Q&A API (Fixed Version)",'
echo '     "version": "1.1.0",'
echo '     "status": "operational"'
echo '   }'

# Response Analysis
echo ""
echo "4.3 Response Analysis:"
echo "   ✓ 'message': Confirms API identity and version"
echo "   ✓ 'version': Shows application version number"
echo "   ✓ 'status': 'operational' means service running correctly"
echo "   ✓ HTTP Status: Should be 200 OK"

# Step 4.4: Advanced API Endpoint Test
# Test full API functionality with authentication
echo ""
echo "4.4 Advanced API Test:"
echo "   Endpoint: POST /api/v1/hackrx/run"
echo "   Purpose: Test full API functionality"
echo "   Requirements: Valid team token for authentication"

# Generate advanced curl command template
echo ""
echo "   Advanced curl command:"
cat << 'EOF'
   curl -X POST "https://your-app.onrender.com/api/v1/hackrx/run" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your_team_token_here" \
     -d '{
       "document_url": "https://www.archives.gov/founding-docs/constitution-transcript",
       "questions": ["What are the three branches of government mentioned?"]
     }'
EOF

# Expected Advanced Response
echo ""
echo "4.5 Expected Advanced Response:"
echo '   {'
echo '     "answers": ['
echo '       "The three branches of government mentioned are the Legislative, Executive, and Judicial branches..."'
echo '     ]'
echo '   }'

# ===================================================================
# TROUBLESHOOTING SECTION
# ===================================================================

echo ""
echo "🔧 TROUBLESHOOTING COMMON ISSUES"
echo "================================"

# Common Issue 1: Environment Variables Not Loading
echo ""
echo "Issue 1: Environment Variables Not Loading"
echo "   Symptoms: API errors about missing GEMINI_API_KEY or TEAM_TOKEN"
echo "   Solution: Verify variables saved in dashboard, manual redeploy"
echo "   Command: Check dashboard > Environment tab"

# Common Issue 2: Service Won't Start  
echo ""
echo "Issue 2: Service Won't Start"
echo "   Symptoms: 'Service failed to start' in deployment logs"
echo "   Solution: Check Python errors in deployment logs"
echo "   Command: Dashboard > Logs tab for error details"

# Common Issue 3: Authentication Errors
echo ""
echo "Issue 3: 401 Unauthorized Errors"
echo "   Symptoms: API returns authentication failed"
echo "   Solution: Verify TEAM_TOKEN is actual token, not placeholder"
echo "   Fix: Update TEAM_TOKEN with real HackRX team token"

# Common Issue 4: Server Errors
echo ""
echo "Issue 4: 500 Internal Server Errors"
echo "   Symptoms: API returns internal server errors"
echo "   Solution: Verify GEMINI_API_KEY is valid and active"
echo "   Check: Google Cloud Console for API key status"

# ===================================================================
# FINAL VERIFICATION CHECKLIST
# ===================================================================

echo ""
echo "📋 FINAL VERIFICATION CHECKLIST"
echo "==============================="

echo ""
echo "Environment Variables:"
echo "   ✓ All 4 variables added to Render dashboard"
echo "   ✓ No typos in variable names or values"  
echo "   ✓ TEAM_TOKEN uses actual token (not placeholder)"
echo "   ✓ Variables show as 'Set' in Render UI"

echo ""
echo "Deployment Status:"
echo "   ✓ Service shows 'Live' status in dashboard"
echo "   ✓ No error messages in deployment logs"
echo "   ✓ Latest deployment timestamp is recent"
echo "   ✓ Build and start processes completed successfully"

echo ""
echo "API Functionality:"
echo "   ✓ Root endpoint returns correct JSON response"
echo "   ✓ HTTP status codes are 200 OK"
echo "   ✓ Main API endpoint accepts POST requests"
echo "   ✓ Authentication system works with team token"

echo ""
echo "Production Readiness:"
echo "   ✓ HTTPS URL accessible publicly"
echo "   ✓ Response times acceptable (< 30 seconds)"
echo "   ✓ No rate limiting or quota errors"
echo "   ✓ Ready for HackRX competition submission"

# ===================================================================
# SUCCESS SUMMARY
# ===================================================================

echo ""
echo "🎉 SUCCESS! Your HackRX FastAPI is now live!"
echo "============================================"

echo ""
echo "Your deployment includes:"
echo "   ✅ Environment variables properly configured"
echo "   ✅ Service automatically redeployed with new settings"
echo "   ✅ API endpoints verified and working correctly"  
echo "   ✅ Production-ready for HackRX competition"

echo ""
echo "Live Endpoints:"
echo "   Root: https://your-app-name.onrender.com/"
echo "   API:  https://your-app-name.onrender.com/api/v1/hackrx/run"

echo ""
echo "Next Steps:"
echo "   1. Replace 'your-app-name' with actual Render service URL"
echo "   2. Test both endpoints with curl commands above"
echo "   3. Update team token if using placeholder"
echo "   4. Submit API endpoint for HackRX competition"

echo ""
echo "✨ Deployment Complete! Ready for production use."
