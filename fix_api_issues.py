#!/usr/bin/env python3
"""
Quick Fix for HackRX API Issues
Simple solutions for common problems
"""

def fix_file_not_found_issue():
    """Address the file not found error"""
    
    print("🔧 HACKRX API QUICK FIXES")
    print("=" * 40)
    
    print("1️⃣ File Not Found Error - Likely Causes:")
    print("   • Server not running")
    print("   • Wrong URL in browser")
    print("   • CORS blocking request")
    print("   • Network connectivity issue")
    
    print("\n2️⃣ Quick Solutions:")
    
    print("\n🎯 SOLUTION 1: Use Swagger UI")
    print("   1. Open: http://localhost:8000/docs")
    print("   2. Find 'POST /api/v1/hackrx/run'")
    print("   3. Click 'Try it out'")
    print("   4. Enter test data:")
    print('      Document URL: https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf')
    print('      Questions: ["What is this about?"]')
    print("   5. Click 'Execute'")
    
    print("\n🎯 SOLUTION 2: Use Python Test")
    test_code = '''
import requests

# Test data
data = {
    "document_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
    "questions": ["What is this document about?", "What are the key points?"]
}

# Send request
try:
    response = requests.post("http://localhost:8000/api/v1/hackrx/run", json=data, timeout=60)
    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        for i, answer in enumerate(result["answers"], 1):
            print(f"Answer {i}: {answer}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"❌ Request failed: {e}")
'''
    
    with open('test_api_simple.py', 'w') as f:
        f.write(test_code)
    
    print("   Created: test_api_simple.py")
    print("   Run: python test_api_simple.py")
    
    print("\n🎯 SOLUTION 3: Check Server Status")
    status_code = '''
import requests
try:
    r = requests.get("http://localhost:8000/api/v1/hackrx/health")
    print("✅ Server is running:", r.json())
except:
    print("❌ Server is not running - start with: python start_hackrx_server.py")
'''
    
    with open('check_server.py', 'w') as f:
        f.write(status_code)
    
    print("   Created: check_server.py")
    print("   Run: python check_server.py")
    
    print("\n🎯 SOLUTION 4: Browser Alternative")
    print("   1. Close browser completely")
    print("   2. Disable browser extensions")
    print("   3. Try incognito/private mode")
    print("   4. Or use different browser")
    
    print("\n🎯 SOLUTION 5: Restart Everything")
    print("   1. Press Ctrl+C to stop current server")
    print("   2. Run: python start_hackrx_server.py")
    print("   3. Wait for 'Application startup complete'")
    print("   4. Try http://localhost:8000/docs")
    
    print("\n" + "=" * 40)
    print("💡 RECOMMENDED ORDER:")
    print("1. python check_server.py")
    print("2. Open http://localhost:8000/docs")
    print("3. python test_api_simple.py")
    print("4. If all fail, restart server")

if __name__ == "__main__":
    fix_file_not_found_issue()
    
    print("\n📋 FILES CREATED:")
    print("   • test_api_simple.py - Simple Python test")
    print("   • check_server.py - Check if server is running")
    print("\n🚀 Try these solutions in order!")
