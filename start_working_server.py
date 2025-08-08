#!/usr/bin/env python3
"""
Simple server startup script that works
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import uvicorn
    from main import app
    
    print("🚀 Starting FastAPI server on http://localhost:3001")
    print("✅ PDF parsing with robust multi-library fallback enabled")
    print("✅ Document processing and Q&A endpoints ready")
    
    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=3001, reload=False)
    
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()
