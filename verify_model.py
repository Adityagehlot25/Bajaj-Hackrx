#!/usr/bin/env python3
"""
Simple Gemini 2.0 Flash Verification
"""

import sys
import os
sys.path.append('.')

def verify_gemini_2_flash():
    try:
        from gemini_answer import get_gemini_answer
        
        print("🚀 GEMINI 2.0 FLASH VERIFICATION")
        print("=" * 50)
        
        # Check API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ API Key not found")
            return False
            
        print(f"✅ API Key: {api_key[:10]}...")
        
        # Quick test
        result = get_gemini_answer(
            user_question="What is this model?",
            relevant_clauses="This is Gemini 2.0 Flash, the latest AI model from Google.",
            model="gemini-2.0-flash-exp"
        )
        
        if result["success"]:
            print("✅ SUCCESS: Gemini 2.0 Flash is working!")
            print(f"🤖 Model: {result.get('model')}")
            print(f"📝 Response: {result['answer'][:100]}...")
            return True
        else:
            print(f"❌ ERROR: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = verify_gemini_2_flash()
    if success:
        print("\n🎊 Your system is using Gemini 2.0 Flash!")
    else:
        print("\n🔧 Check your API key setup")
