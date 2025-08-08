"""
Simple HackRX API Test Script (requests only)

A lightweight test script that requires only the 'requests' library.
Tests your deployed HackRX API with authentication scenarios.

Install dependencies:
    pip install requests

Usage:
    python simple_api_test.py
    python simple_api_test.py https://your-deployed-api.com
"""

import sys
import json
import time

try:
    import requests
except ImportError:
    print("❌ Error: 'requests' library not found")
    print("Install with: pip install requests")
    sys.exit(1)

# Configuration
API_BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
VALID_TOKEN = "hackrx_test_token_2024"  # Valid token (>= 10 chars)
INVALID_TOKEN = "short"  # Invalid token (< 10 chars)

# Test payload
SAMPLE_PAYLOAD = {
    "document_url": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the waiting period for cataract surgery?",
        "Are the medical expenses for an organ donor covered under this policy?"
    ]
}

def test_api():
    """Test the HackRX API with different authentication scenarios"""
    
    print("=" * 70)
    print(f"  Testing HackRX API: {API_BASE_URL}")
    print("=" * 70)
    
    endpoint = f"{API_BASE_URL}/api/v1/hackrx/run"
    health_endpoint = f"{API_BASE_URL}/health"
    
    # Test 1: Health Check
    print("\n🔍 Test 1: Health Check")
    try:
        response = requests.get(health_endpoint, timeout=10)
        if response.status_code == 200:
            print(f"✅ PASS | Health Check | Status: {response.status_code}")
        else:
            print(f"❌ FAIL | Health Check | Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL | Health Check | Error: {e}")
        return False
    
    # Test 2: Valid Authentication
    print("\n🔍 Test 2: Valid Authentication (Expect 200 + answers)")
    print(f"   📤 Sending request with token: {VALID_TOKEN[:10]}...")
    
    try:
        headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
        start_time = time.time()
        
        response = requests.post(endpoint, json=SAMPLE_PAYLOAD, headers=headers, timeout=120)
        elapsed_time = time.time() - start_time
        
        print(f"   ⏱️  Response time: {elapsed_time:.2f} seconds")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "answers" in data and isinstance(data["answers"], list):
                    print(f"✅ PASS | Valid Auth + Format | Got {len(data['answers'])} answers")
                    if data["answers"]:
                        preview = data["answers"][0][:100] + "..." if len(data["answers"][0]) > 100 else data["answers"][0]
                        print(f"      Sample answer: {preview}")
                else:
                    print(f"❌ FAIL | Valid Auth + Format | Wrong format: {list(data.keys())}")
                    return False
            except json.JSONDecodeError:
                print("❌ FAIL | Valid Auth + Format | Invalid JSON")
                return False
        else:
            print(f"❌ FAIL | Valid Auth | Status: {response.status_code}")
            print(f"      Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ FAIL | Valid Auth | Timeout (>120s)")
        return False
    except Exception as e:
        print(f"❌ FAIL | Valid Auth | Error: {e}")
        return False
    
    # Test 3: Invalid Authentication
    print("\n🔍 Test 3: Invalid Authentication (Expect 401)")
    try:
        headers = {"Authorization": f"Bearer {INVALID_TOKEN}"}
        response = requests.post(endpoint, json=SAMPLE_PAYLOAD, headers=headers, timeout=10)
        
        if response.status_code == 401:
            data = response.json()
            print(f"✅ PASS | Invalid Auth → 401 | Error: {data.get('detail', 'No detail')}")
        else:
            print(f"❌ FAIL | Invalid Auth | Expected 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL | Invalid Auth | Error: {e}")
        return False
    
    # Test 4: Missing Authentication
    print("\n🔍 Test 4: Missing Authentication (Expect 403)")
    try:
        response = requests.post(endpoint, json=SAMPLE_PAYLOAD, timeout=10)
        
        if response.status_code == 403:
            data = response.json()
            print(f"✅ PASS | Missing Auth → 403 | Error: {data.get('detail', 'No detail')}")
        else:
            print(f"❌ FAIL | Missing Auth | Expected 403, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL | Missing Auth | Error: {e}")
        return False
    
    return True

def show_curl_examples():
    """Show equivalent curl commands"""
    print("\n" + "=" * 70)
    print("  Equivalent CURL Commands")
    print("=" * 70)
    
    endpoint = f"{API_BASE_URL}/api/v1/hackrx/run"
    payload_str = json.dumps(SAMPLE_PAYLOAD)
    
    print(f"\n1️⃣ Health Check:")
    print(f"curl -X GET {API_BASE_URL}/health")
    
    print(f"\n2️⃣ Valid Authentication:")
    print(f"curl -X POST {endpoint} \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -H 'Authorization: Bearer {VALID_TOKEN}' \\")
    print(f"  -d '{payload_str}'")
    
    print(f"\n3️⃣ Invalid Authentication:")
    print(f"curl -X POST {endpoint} \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -H 'Authorization: Bearer {INVALID_TOKEN}' \\")
    print(f"  -d '{payload_str}'")
    
    print(f"\n4️⃣ Missing Authentication:")
    print(f"curl -X POST {endpoint} \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -d '{payload_str}'")

if __name__ == "__main__":
    print("HackRX API Deployment Test")
    print(f"Testing {len(SAMPLE_PAYLOAD['questions'])} questions against API...")
    
    success = test_api()
    
    if success:
        show_curl_examples()
        
        print("\n" + "=" * 70)
        print("  Test Summary")
        print("=" * 70)
        print("🎉 All tests PASSED!")
        print("✅ Authentication working correctly")
        print("✅ Response format validated")
        print("✅ Error handling confirmed")
        print("\n🚀 Your HackRX API is ready for production!")
    else:
        print("\n" + "=" * 70)
        print("  Test Summary")
        print("=" * 70)
        print("❌ Some tests FAILED")
        print("🔧 Check deployment status and API logs")
        sys.exit(1)
