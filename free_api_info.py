#!/usr/bin/env python3
"""
Free Gemini API Demo - No Cost Q&A System
Shows how to use free Gemini models effectively
"""

import os
import sys
from datetime import datetime

def show_free_api_info():
    """Display free API information and setup"""
    
    print("🆓 FREE GEMINI API FOR YOUR Q&A SYSTEM")
    print("=" * 60)
    print(f"📅 Info Current as of: {datetime.now().strftime('%Y-%m-%d')}")
    print()
    
    # Free Models Available
    print("🤖 FREE MODELS AVAILABLE")
    print("-" * 40)
    
    models = [
        {
            "name": "Gemini 1.5 Flash",
            "model_id": "gemini-1.5-flash", 
            "speed": "⚡ ULTRA FAST",
            "quota": "15 req/min, 1M tokens/min",
            "best_for": "Q&A, Chat, Fast responses",
            "recommended": "✅ RECOMMENDED FOR YOUR SYSTEM"
        },
        {
            "name": "Gemini 1.5 Pro",
            "model_id": "gemini-1.5-pro",
            "speed": "🧠 SMART",
            "quota": "2 req/min, 32K tokens/min", 
            "best_for": "Complex analysis, reasoning",
            "recommended": "✅ Good for detailed answers"
        },
        {
            "name": "Gemini Pro",
            "model_id": "gemini-pro",
            "speed": "📊 BALANCED", 
            "quota": "60 req/min",
            "best_for": "General purpose",
            "recommended": "✅ Stable fallback"
        },
        {
            "name": "Text Embedding 004",
            "model_id": "text-embedding-004",
            "speed": "🔢 EMBEDDING",
            "quota": "1500 req/min",
            "best_for": "Document embeddings (768D)",
            "recommended": "✅ REQUIRED FOR VECTOR SEARCH"
        }
    ]
    
    for model in models:
        print(f"🤖 {model['name']} ({model['speed']})")
        print(f"   📝 Model ID: {model['model_id']}")
        print(f"   🎯 Free Quota: {model['quota']}")
        print(f"   💡 Best For: {model['best_for']}")
        print(f"   ⭐ Status: {model['recommended']}")
        print()
    
    # Cost Comparison
    print("💰 COST COMPARISON")
    print("-" * 40)
    print("🆓 FREE TIER (What you get):")
    print("   • Gemini 1.5 Flash: 1,500 requests/day")
    print("   • Gemini 1.5 Pro: 50 requests/day")
    print("   • Text Embeddings: 100,000 requests/day")
    print("   • NO CREDIT CARD REQUIRED")
    print()
    print("💳 Paid Tier (if you exceed free):")
    print("   • Gemini 1.5 Flash: $0.075 per 1M tokens")
    print("   • Gemini 1.5 Pro: $1.25 per 1M tokens")
    print("   • Text Embeddings: $0.00025 per 1K tokens")
    print()
    
    # Your System Configuration
    print("⚙️ YOUR SYSTEM CONFIGURATION")
    print("-" * 40)
    print("Your Q&A system is optimized for FREE usage:")
    print()
    print("📊 Model Priority (Smart Switching):")
    print("   1. 🥇 gemini-1.5-flash (fastest, highest quota)")
    print("   2. 🥈 gemini-1.5-pro (if flash is exhausted)")  
    print("   3. 🥉 gemini-pro (fallback)")
    print()
    print("🔢 Embedding Model:")
    print("   • text-embedding-004 (768 dimensions)")
    print("   • Perfect for your FAISS vector store")
    print()
    print("⚡ Rate Limiting Built-in:")
    print("   • Automatic delays between requests")
    print("   • Smart quota management")
    print("   • Graceful fallbacks")
    print()
    
    # Usage Estimates
    print("📈 USAGE ESTIMATES FOR YOUR SYSTEM")
    print("-" * 40)
    print("Typical Q&A Session (FREE tier):")
    print()
    print("📄 Document Processing:")
    print("   • bajaj.pdf (24 chunks) → 24 embedding requests")
    print("   • ✅ Well within 100K/day limit")
    print()
    print("💬 Q&A Sessions:")
    print("   • ~50-100 questions/day with Gemini 1.5 Flash")
    print("   • Each question uses 1 request")
    print("   • ✅ Perfect for personal/small business use")
    print()
    print("🎯 Real-world Usage:")
    print("   • Small team: 20-30 questions/day")
    print("   • Personal use: 5-10 questions/day")  
    print("   • ✅ FREE tier covers most use cases!")
    print()
    
    # Setup Instructions
    print("🚀 GET STARTED (100% FREE)")
    print("-" * 40)
    print("1. 🔑 Get your FREE API key:")
    print("   → Visit: https://aistudio.google.com/app/apikey")
    print("   → Click 'Create API Key'")
    print("   → No credit card required!")
    print()
    print("2. ⚙️ Set up the key:")
    print("   → setx GEMINI_API_KEY \"your_key_here\"")
    print("   → Or run: python setup_api_key.py")
    print()
    print("3. 🎯 Start using:")
    print("   → python interactive_qa.py")
    print("   → python test_bajaj_queries.py")
    print()
    
    # Current Status
    api_key = os.getenv('GEMINI_API_KEY')
    print("🎯 CURRENT STATUS")
    print("-" * 40)
    if api_key:
        print(f"✅ API Key: Configured ({api_key[:10]}...)")
        print("✅ System: Ready for FREE usage!")
        print("🎊 You can start asking questions immediately!")
    else:
        print("❌ API Key: Not set")
        print("🔧 Next Step: Set your FREE Gemini API key")
        print("💡 Run: python setup_api_key.py")
    
    # Available Documents
    docs_found = []
    for doc in ['bajaj.pdf', 'chotgdp.pdf']:
        if os.path.exists(doc):
            size_mb = os.path.getsize(doc) / (1024 * 1024)
            docs_found.append(f"{doc} ({size_mb:.1f}MB)")
    
    if docs_found:
        print(f"\n📚 Documents Ready: {', '.join(docs_found)}")
        print("✅ Ready for immediate Q&A testing!")
    
    print()
    print("=" * 60)
    print("🎊 SUMMARY: Your system uses 100% FREE Gemini models!")
    print("💡 No costs, no credit card, generous quotas!")
    print("🚀 Perfect for document Q&A and learning!")
    print("=" * 60)

def main():
    show_free_api_info()
    
    # Quick test if API key is available
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"\n🧪 READY TO TEST!")
        print(f"Try these commands:")
        print(f"   python test_bajaj_queries.py")
        print(f"   python interactive_qa.py")
        print(f"   python demo_qa_session.py")
    else:
        print(f"\n🔧 SETUP NEEDED:")
        print(f"Run: python setup_api_key.py")

if __name__ == "__main__":
    main()
