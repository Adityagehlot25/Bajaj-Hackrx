"""
Quick API Test - Minimal Script for HackRX API Testing

This script provides a simple way to test your deployed HackRX API.
Just run: python quick_test.py YOUR_API_URL
"""

import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import time

def test_hackrx_api(base_url):
    """Test HackRX API using only Python standard library"""
    
    print(f"Testing HackRX API: {base_url}")
    print("=" * 50)
    
    # Test configuration
    valid_token = "hackrx_test_token_2024"
    invalid_token = "short"
    
    # Test payload
    payload = {
        "document_url": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?"
        ]
    }
    
    payload_json = json.dumps(payload).encode('utf-8')
    
    # Test 1: Health Check
    print("\\n1. Health Check:")
    try:
        req = urllib.request.Request(f"{base_url}/health")
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.getcode() == 200:
                print("✅ PASS - API is accessible")
            else:
                print(f"❌ FAIL - Status: {response.getcode()}")
                return False
    except Exception as e:
        print(f"❌ FAIL - Connection error: {e}")
        return False
    
    # Test 2: Valid Authentication
    print("\\n2. Valid Authentication:")
    try:
        req = urllib.request.Request(
            f"{base_url}/api/v1/hackrx/run",
            data=payload_json,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {valid_token}'
            }
        )
        
        print("   Sending request... (may take 60-120 seconds)")
        start_time = time.time()
        
        with urllib.request.urlopen(req, timeout=180) as response:
            elapsed = time.time() - start_time
            
            if response.getcode() == 200:
                data = json.loads(response.read().decode())
                if 'answers' in data and isinstance(data['answers'], list):
                    print(f"✅ PASS - Got {len(data['answers'])} answers ({elapsed:.1f}s)")
                    if data['answers']:
                        preview = data['answers'][0][:80] + "..." if len(data['answers'][0]) > 80 else data['answers'][0]
                        print(f"   Sample: {preview}")
                else:
                    print(f"❌ FAIL - Wrong format: {list(data.keys())}")
                    return False
            else:
                print(f"❌ FAIL - Status: {response.getcode()}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ FAIL - HTTP Error: {e.code}")
        return False
    except Exception as e:
        print(f"❌ FAIL - Error: {e}")
        return False
    
    # Test 3: Invalid Authentication
    print("\\n3. Invalid Authentication:")
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
            print("✅ PASS - Correctly rejected invalid token")
        else:
            print(f"❌ FAIL - Expected 401, got {e.code}")
            return False
    except Exception as e:
        print(f"❌ FAIL - Error: {e}")
        return False
    
    # Test 4: Missing Authentication
    print("\\n4. Missing Authentication:")
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
            print("✅ PASS - Correctly rejected missing auth")
        else:
            print(f"❌ FAIL - Expected 403, got {e.code}")
            return False
    except Exception as e:
        print(f"❌ FAIL - Error: {e}")
        return False
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python quick_test.py <API_URL>")
        print("Example: python quick_test.py https://your-hackrx-api.onrender.com")
        print("Example: python quick_test.py http://localhost:8000")
        sys.exit(1)
    
    api_url = sys.argv[1].rstrip('/')
    
    print("HackRX API Quick Test")
    print("Tests: Health, Valid Auth, Invalid Auth, Missing Auth")
    
    success = test_hackrx_api(api_url)
    
    print("\\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your HackRX API is working correctly")
        print("✅ Authentication is properly configured")  
        print("✅ Response format is valid")
        print("\\n🚀 API is ready for production use!")
    else:
        print("❌ SOME TESTS FAILED")
        print("🔧 Check your API deployment and configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()
