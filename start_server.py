#!/usr/bin/env python3

"""
Start the FastAPI server with the new API key
"""

import uvicorn
from main import app
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Start the FastAPI server"""
    
    # Verify API key is loaded
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"✅ API Key loaded: {api_key[:10]}...{api_key[-5:]}")
        print(f"✅ API Key length: {len(api_key)}")
        print(f"✅ API Key format valid: {len(api_key) == 39 and api_key.startswith('AIza')}")
    else:
        print("❌ No API key found!")
        return
    
    print(f"\n🚀 Starting FastAPI server with working Gemini API key...")
    print(f"📡 Server will be available at: http://localhost:8000")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"🔍 Alternative docs: http://localhost:8000/redoc")
    
    # Start the server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
