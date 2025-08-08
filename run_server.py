#!/usr/bin/env python3
"""Start the FastAPI server for testing"""

import subprocess
import sys
import os

def start_server():
    """Start the FastAPI server."""
    try:
        # Change to the correct directory
        os.chdir(r"e:\final try")
        
        # Start the server
        print("🚀 Starting FastAPI server...")
        print("   URL: http://localhost:8000")
        print("   Press Ctrl+C to stop")
        
        # Run the server
        subprocess.run([sys.executable, "start_server.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n⏹️ Server stopped by user")
    except Exception as e:
        print(f"❌ Server start failed: {e}")

if __name__ == "__main__":
    start_server()
