#!/usr/bin/env python3
"""
Simple server runner for HackRX API
"""

if __name__ == "__main__":
    try:
        import uvicorn
        print("🚀 Starting HackRX API Server...")
        print("📍 API: http://localhost:8000/api/v1/hackrx/run")
        print("📊 Health: http://localhost:8000/api/v1/hackrx/health") 
        print("📚 Docs: http://localhost:8000/docs")
        
        uvicorn.run(
            "hackrx_api_fixed:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Try installing: pip install uvicorn")
