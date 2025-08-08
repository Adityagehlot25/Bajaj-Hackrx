#!/usr/bin/env python3
"""
Direct test of Gemini API key validation
"""

import requests
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_gemini_api_key():
    """Test the Gemini API key directly."""
    print("🔑 Gemini API Key Validation Test")
    print("=" * 50)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ No GEMINI_API_KEY found in environment")
        return False
        
    print(f"✅ API key found: {api_key}")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Format: {'✅ Correct' if api_key.startswith('AIza') else '❌ Invalid'}")
    
    # Test 1: Try the embeddings endpoint
    print("\n📡 Testing Embeddings Endpoint:")
    print("-" * 30)
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    payload = {
        "content": {
            "parts": [{"text": "Hello, this is a test."}]
        },
        "taskType": "RETRIEVAL_DOCUMENT"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            embedding = data.get("embedding", {}).get("values", [])
            print("✅ SUCCESS! API key is working")
            print(f"📊 Embedding dimensions: {len(embedding)}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            # Parse the error for more details
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_info = error_data["error"]
                    print(f"🚨 Error Code: {error_info.get('code')}")
                    print(f"🚨 Error Message: {error_info.get('message')}")
                    print(f"🚨 Error Status: {error_info.get('status')}")
            except:
                pass
                
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"💥 Network error: {e}")
        return False
    
    # Test 2: Try listing models (if embeddings fails)
    print("\n📡 Testing Models List Endpoint:")
    print("-" * 30)
    
    models_url = "https://generativelanguage.googleapis.com/v1beta/models"
    
    try:
        response = requests.get(f"{models_url}?key={api_key}", timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            print(f"✅ Models endpoint works! Found {len(models)} models")
            
            # Look for embedding models
            embedding_models = [m for m in models if "embedding" in m.get("name", "").lower()]
            print(f"📊 Embedding models available: {len(embedding_models)}")
            for model in embedding_models[:3]:  # Show first 3
                print(f"   - {model.get('name')}")
                
            return True
        else:
            print(f"❌ Models endpoint error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"💥 Network error: {e}")
        return False

def check_api_key_format():
    """Check if the API key format is correct."""
    print("\n🔍 API Key Format Validation:")
    print("-" * 30)
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    # Check format
    checks = [
        ("Length", len(api_key) == 39, f"Expected 39, got {len(api_key)}"),
        ("Prefix", api_key.startswith("AIza"), f"Should start with 'AIza', starts with '{api_key[:4]}'"),
        ("Characters", api_key.replace("-", "").replace("_", "").isalnum(), "Should be alphanumeric with possible - or _"),
    ]
    
    all_good = True
    for check_name, passed, message in checks:
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}: {message}")
        if not passed:
            all_good = False
    
    return all_good

def provide_troubleshooting():
    """Provide troubleshooting steps."""
    print("\n🛠️ Troubleshooting Steps:")
    print("-" * 30)
    print("1. Verify API Key:")
    print("   - Go to: https://makersuite.google.com/app/apikey")
    print("   - Check if your key is active and not restricted")
    print("   - Regenerate if necessary")
    
    print("\n2. Check API Key Restrictions:")
    print("   - Ensure the key has access to 'Generative Language API'")
    print("   - Check if there are IP or domain restrictions")
    
    print("\n3. Verify Billing:")
    print("   - Go to: https://console.cloud.google.com/billing")
    print("   - Ensure billing is enabled for the project")
    
    print("\n4. Alternative: Create New Key:")
    print("   - Create a new API key")
    print("   - Update your .env file with the new key")

def main():
    """Run all tests."""
    print("🚀 Gemini API Key Diagnostic Tool")
    print("=" * 60)
    
    # Check format
    format_ok = check_api_key_format()
    
    # Test API
    api_ok = test_gemini_api_key()
    
    print("\n" + "=" * 60)
    print("📊 Diagnostic Results:")
    print(f"   🔍 Key Format: {'✅ PASS' if format_ok else '❌ FAIL'}")
    print(f"   📡 API Access: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if not api_ok:
        provide_troubleshooting()
    else:
        print("\n🎉 Your API key is working correctly!")

if __name__ == "__main__":
    main()
