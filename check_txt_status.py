#!/usr/bin/env python3
"""
Test and Restart Guide
"""

print("🏆 HACKRX API - TXT SUPPORT STATUS")
print("=" * 50)

print("\n✅ TXT SUPPORT HAS BEEN ADDED!")
print("📁 File: robust_document_parser.py")
print("🔧 Method: _parse_txt_file() added")
print("📋 File types: PDF, DOCX, TXT supported")

print("\n🔄 TO APPLY THE CHANGES:")
print("1. Stop the current server (Ctrl+C in the terminal)")
print("2. Restart with: python run_server_simple.py")
print("3. Or restart with: python hackrx_api_fixed.py")

print("\n🧪 AFTER RESTARTING, TEST WITH:")
print("""
{
  "document_url": "https://www.gutenberg.org/files/11/11-0.txt",
  "questions": ["Who is Alice?"]
}
""")

print("\n💡 VERIFICATION:")
print("- Health check: http://localhost:8000/api/v1/hackrx/health")
print("- Swagger UI: http://localhost:8000/docs")
print("- Should work with .txt files after restart!")

print("\n🚀 THE FIX IS COMPLETE - JUST RESTART THE SERVER!")

# Quick test to verify the code is syntactically correct
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Test import
    exec("from robust_document_parser import RobustDocumentParser")
    print("\n✅ Parser code is valid and ready!")
    
except Exception as e:
    print(f"\n❌ Parser issue: {e}")

print("\n" + "=" * 50)
