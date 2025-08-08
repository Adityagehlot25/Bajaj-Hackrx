#!/usr/bin/env python3
"""
Simple HTTP File Server for Testing
Serves local files so we can test with guaranteed working documents
"""

import http.server
import socketserver
import os
import threading
import time

def start_file_server():
    """Start a simple HTTP server to serve test files"""
    PORT = 8080
    
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            print(f"✅ File server started on http://localhost:{PORT}")
            print(f"📄 Test document: http://localhost:{PORT}/constitution_excerpt.txt")
            print(f"📄 Small test: http://localhost:{PORT}/small_test_document.txt")
            print("🔥 Press Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 File server stopped")

if __name__ == "__main__":
    print("🌐 STARTING LOCAL FILE SERVER FOR TESTING")
    print("=" * 50)
    start_file_server()
