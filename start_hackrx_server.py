#!/usr/bin/env python3
"""
Start HackRX API Server
Install dependencies and run the FastAPI server
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies for HackRX API"""
    print("📦 Installing HackRX API dependencies...")
    
    try:
        # Install FastAPI requirements
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements_hackrx.txt"
        ], check=True)
        
        print("✅ Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_api_key():
    """Check if Gemini API key is configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"✅ Gemini API Key: {api_key[:10]}...{api_key[-5:]}")
        return True
    else:
        print("❌ Gemini API Key not found!")
        print("🔧 Please set GEMINI_API_KEY in your .env file")
        return False

def start_server():
    """Start the HackRX API server"""
    print("\n🚀 STARTING HACKRX API SERVER")
    print("=" * 50)
    print("📍 Endpoint: http://localhost:8000/api/v1/hackrx/run")
    print("📊 Health: http://localhost:8000/api/v1/hackrx/health") 
    print("📚 Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    try:
        import uvicorn
        uvicorn.run(
            "hackrx_api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn not installed. Installing dependencies first...")
        if install_dependencies():
            import uvicorn
            uvicorn.run(
                "hackrx_api:app",
                host="0.0.0.0", 
                port=8000,
                reload=True,
                log_level="info"
            )

if __name__ == "__main__":
    print("🏆 HACKRX DOCUMENT Q&A API SERVER")
    print("🤖 Powered by Gemini 2.0 Flash")
    print()
    
    # Check if dependencies are installed
    try:
        import fastapi
        import uvicorn
        print("✅ Dependencies already installed")
    except ImportError:
        print("📦 Installing required dependencies...")
        if not install_dependencies():
            sys.exit(1)
    
    # Check API key
    if not check_api_key():
        print("\n🔧 Setup your API key first:")
        print("python setup_api_key.py")
        sys.exit(1)
    
    # Start server
    start_server()
