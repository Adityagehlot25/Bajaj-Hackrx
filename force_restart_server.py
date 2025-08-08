#!/usr/bin/env python3
"""
Force Restart Server with TXT Support
"""

import subprocess
import sys
import time
import os

def force_restart_server():
    """Force restart with fresh Python process"""
    print("🔄 Force restarting HackRX API Server...")
    
    # Kill all Python processes
    try:
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                      capture_output=True, text=True)
        print("✅ Stopped existing Python processes")
    except:
        print("ℹ️ No Python processes to stop")
    
    time.sleep(2)
    
    # Start fresh server
    print("🚀 Starting fresh server with TXT support...")
    
    # Import test first
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from robust_document_parser import parse_document
        print("✅ Parser imports successfully - TXT support ready")
    except Exception as e:
        print(f"❌ Parser import error: {e}")
        return False
    
    # Start server
    try:
        import uvicorn
        print("📍 Starting on http://localhost:8000")
        print("📚 Swagger UI: http://localhost:8000/docs")
        print("🧪 Ready to test Alice in Wonderland TXT file!")
        
        uvicorn.run(
            "hackrx_api_fixed:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🏆 HACKRX API - FORCE RESTART WITH TXT SUPPORT")
    print("=" * 60)
    
    force_restart_server()
