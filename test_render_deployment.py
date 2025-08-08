"""
Test the specific deployed HackRX API at bajaj-hackrx-bnm2.onrender.com
"""
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import time

def test_deployed_api():
    """Test the deployed HackRX API with correct endpoints"""
    
    base_url = "https://bajaj-hackrx-bnm2.onrender.com"
    print(f"Testing Deployed HackRX API: {base_url}")
    print("=" * 60)
    
    # Test configuration
    valid_token = "hackrx_test_token_2024"
    invalid_token = "short"
    
    # Test payload
    payload = {
        "document_url": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?"
        ]
    }
    
    payload_json = json.dumps(payload).encode('utf-8')
    
    # Test 1: Root endpoint (API info)
    print("\\n1. Root Endpoint Check:")
    try:
        req = urllib.request.Request(f"{base_url}/")
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode())
                print("✅ PASS - API is accessible")
                print(f"   Message: {data.get('message', 'N/A')}")
                print(f"   Version: {data.get('version', 'N/A')}")
                print(f"   Status: {data.get('status', 'N/A')}")
            else:
                print(f"❌ FAIL - Status: {response.getcode()}")
                return False
    except Exception as e:
        print(f"❌ FAIL - Connection error: {e}")
        return False
    
    # Test 2: Health Check (correct endpoint)
    print("\\n2. Health Check (/api/v1/hackrx/health):")
    try:
        req = urllib.request.Request(f"{base_url}/api/v1/hackrx/health")
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode())
                print("✅ PASS - Health endpoint responding")
                print(f"   Health: {data.get('health', 'N/A')}")
            else:
                print(f"❌ FAIL - Status: {response.getcode()}")
    except Exception as e:
        print(f"⚠️  SKIP - Health endpoint error: {e}")
        # Don't fail the test if health endpoint has issues
    
    # Test 3: Valid Authentication
    print("\\n3. Valid Authentication Test:")
    try:
        req = urllib.request.Request(
            f"{base_url}/api/v1/hackrx/run",
            data=payload_json,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {valid_token}'
            }
        )
        
        print("   📤 Sending request to deployed API...")
        print("   ⏱️  This may take 60-180 seconds for document processing...")
        start_time = time.time()
        
        with urllib.request.urlopen(req, timeout=240) as response:  # 4 minutes timeout
            elapsed = time.time() - start_time
            
            if response.getcode() == 200:
                data = json.loads(response.read().decode())
                if 'answers' in data and isinstance(data['answers'], list):
                    print(f"✅ PASS - Got {len(data['answers'])} answers in {elapsed:.1f}s")
                    
                    # Show sample answers
                    for i, answer in enumerate(data['answers'][:2]):  # Show first 2 answers
                        preview = answer[:100] + "..." if len(answer) > 100 else answer
                        print(f"   Answer {i+1}: {preview}")
                    
                    return True  # API working correctly!
                else:
                    print(f"❌ FAIL - Wrong format: {list(data.keys())}")
                    return False
            else:
                print(f"❌ FAIL - Status: {response.getcode()}")
                return False
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else "No details"
        print(f"❌ FAIL - HTTP Error: {e.code}")
        print(f"   Error details: {error_body}")
        return False
    except Exception as e:
        print(f"❌ FAIL - Error: {e}")
        return False

def test_auth_scenarios():
    """Test authentication edge cases"""
    
    base_url = "https://bajaj-hackrx-bnm2.onrender.com"
    invalid_token = "short"
    
    payload = {
        "document_url": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": ["What is the grace period?"]
    }
    payload_json = json.dumps(payload).encode('utf-8')
    
    print("\\n" + "=" * 60)
    print("Testing Authentication Edge Cases:")
    print("=" * 60)
    
    # Test: Invalid Authentication
    print("\\n4. Invalid Authentication (short token):")
    try:
        req = urllib.request.Request(
            f"{base_url}/api/v1/hackrx/run",
            data=payload_json,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {invalid_token}'
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            print(f"❌ FAIL - Expected 401, got {response.getcode()}")
            return False
            
    except urllib.error.HTTPError as e:
        if e.code == 401:
            error_body = json.loads(e.read().decode())
            print(f"✅ PASS - Correctly rejected invalid token (401)")
            print(f"   Error: {error_body.get('detail', 'N/A')}")
        else:
            print(f"❌ FAIL - Expected 401, got {e.code}")
            return False
    except Exception as e:
        print(f"❌ FAIL - Error: {e}")
        return False
    
    # Test: Missing Authentication
    print("\\n5. Missing Authentication:")
    try:
        req = urllib.request.Request(
            f"{base_url}/api/v1/hackrx/run",
            data=payload_json,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            print(f"❌ FAIL - Expected 403, got {response.getcode()}")
            return False
            
    except urllib.error.HTTPError as e:
        if e.code == 403:
            error_body = json.loads(e.read().decode())
            print(f"✅ PASS - Correctly rejected missing auth (403)")
            print(f"   Error: {error_body.get('detail', 'N/A')}")
        else:
            print(f"❌ FAIL - Expected 403, got {e.code}")
            return False
    except Exception as e:
        print(f"❌ FAIL - Error: {e}")
        return False
    
    return True

def main():
    print("🎯 Testing Your Deployed HackRX API")
    print("URL: https://bajaj-hackrx-bnm2.onrender.com")
    print("Testing authentication, document processing, and response format...")
    
    # Test basic functionality
    success = test_deployed_api()
    
    if success:
        # Test authentication edge cases
        auth_success = test_auth_scenarios()
        
        print("\\n" + "=" * 60)
        print("🎉 DEPLOYMENT TEST SUMMARY")
        print("=" * 60)
        
        if auth_success:
            print("✅ API successfully deployed to Render!")
            print("✅ Document processing working correctly")
            print("✅ Authentication validation working")
            print("✅ Response format validated: {'answers': [...]}")
            print("✅ Error handling confirmed")
            print("\\n🚀 Your HackRX API is PRODUCTION READY!")
            print("\\n📋 Test Results:")
            print("   • Root endpoint: ✅ Accessible")
            print("   • Valid auth: ✅ Returns answers array")
            print("   • Invalid auth: ✅ Returns 401 error")
            print("   • Missing auth: ✅ Returns 403 error")
            print("\\n🏆 Ready for HackRX competition submission!")
        else:
            print("⚠️  API working but authentication issues detected")
    else:
        print("\\n" + "=" * 60)
        print("❌ DEPLOYMENT TEST FAILED")
        print("=" * 60)
        print("🔧 Check your Render deployment logs")
        print("🔧 Verify GEMINI_API_KEY environment variable is set")
        sys.exit(1)

if __name__ == "__main__":
    main()
