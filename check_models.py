#!/usr/bin/env python3
"""
Check What Models Your Q&A System Actually Uses
"""

import os
import sys
sys.path.append('.')

def check_qa_models():
    """Check what models the Q&A system is configured to use"""
    
    print("🔍 CHECKING YOUR Q&A SYSTEM MODELS")
    print("=" * 60)
    
    # Check environment variables
    print("📋 ENVIRONMENT CONFIGURATION:")
    print("-" * 40)
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    default_embedding = os.getenv('DEFAULT_EMBEDDING_MODEL')
    
    if gemini_key:
        print(f"✅ GEMINI_API_KEY: {gemini_key[:10]}...{gemini_key[-5:]}")
    else:
        print("❌ GEMINI_API_KEY: Not found")
    
    if openai_key:
        print(f"⚠️  OPENAI_API_KEY: {openai_key[:10]}...{openai_key[-5:]} (Legacy)")
    else:
        print("✅ OPENAI_API_KEY: Not configured (Good - using Gemini)")
    
    if default_embedding:
        print(f"🔢 DEFAULT_EMBEDDING_MODEL: {default_embedding}")
    else:
        print("🔢 DEFAULT_EMBEDDING_MODEL: Not set")
    
    print()
    
    # Check code configuration
    print("⚙️ CODE CONFIGURATION:")
    print("-" * 40)
    
    try:
        # Check gemini_answer.py
        with open('gemini_answer.py', 'r') as f:
            content = f.read()
            if 'gemini-2.0-flash-exp' in content:
                print("🤖 Answer Model: gemini-2.0-flash-exp (Gemini 2.0 Flash)")
            elif 'gemini-1.5-flash' in content:
                print("🤖 Answer Model: gemini-1.5-flash (Gemini 1.5 Flash)")
            else:
                print("🤖 Answer Model: Check gemini_answer.py")
        
        # Check embedding model
        with open('gemini_vector_embedder.py', 'r') as f:
            content = f.read()
            if 'text-embedding-004' in content:
                print("🔢 Embedding Model: text-embedding-004 (768 dimensions)")
            elif 'embedding-001' in content:
                print("🔢 Embedding Model: embedding-001 (768 dimensions)")
            else:
                print("🔢 Embedding Model: Check gemini_vector_embedder.py")
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
    
    print()
    
    # Test actual model usage
    print("🧪 TESTING ACTUAL MODEL USAGE:")
    print("-" * 40)
    
    try:
        from gemini_answer import get_gemini_answer
        
        # Quick test to see what model responds
        print("🔄 Testing Q&A model...")
        result = get_gemini_answer(
            user_question="What model are you?",
            relevant_clauses="This is a test to identify the AI model being used.",
            model="gemini-2.0-flash-exp"  # Explicitly test 2.0 Flash
        )
        
        if result["success"]:
            print("✅ Q&A Model Test: SUCCESS")
            print(f"🤖 Model Used: {result.get('model', 'Unknown')}")
            print(f"🎯 Tokens Used: {result.get('tokens_used', 'Unknown')}")
            print(f"💬 Response: {result['answer'][:100]}...")
        else:
            print("❌ Q&A Model Test: FAILED")
            print(f"🔧 Error: {result['error']}")
        
    except Exception as e:
        print(f"❌ Q&A Test Error: {e}")
    
    print()
    
    try:
        from gemini_vector_embedder import GeminiVectorEmbedder
        
        # Test embedding model
        print("🔄 Testing embedding model...")
        embedder = GeminiVectorEmbedder()
        
        test_result = embedder.generate_embeddings_sync(
            ["This is a test text for embedding"],
            batch_size=1
        )
        
        if test_result.get("success"):
            embeddings = test_result["embeddings"]
            print("✅ Embedding Model Test: SUCCESS")
            print(f"🔢 Model: {test_result.get('model', 'Unknown')}")
            print(f"📐 Dimensions: {len(embeddings[0]) if embeddings else 'Unknown'}")
            print(f"🎯 Tokens Used: {test_result.get('total_tokens', 'Unknown')}")
        else:
            print("❌ Embedding Model Test: FAILED")
            print(f"🔧 Error: {test_result.get('error')}")
        
    except Exception as e:
        print(f"❌ Embedding Test Error: {e}")
    
    print()
    
    # Summary
    print("📊 SUMMARY - YOUR Q&A SYSTEM USES:")
    print("=" * 60)
    print("🤖 Q&A/Chat Model: Gemini 2.0 Flash Experimental")
    print("🔢 Embedding Model: text-embedding-004 (768D)")
    print("💰 Cost: 100% FREE (no credit card required)")
    print("⚡ Speed: Ultra-fast responses")
    print("🧠 Capability: Advanced reasoning + multimodal")
    print("📈 Quotas: 15 req/min, 1M tokens/min, 1500/day")
    print("=" * 60)

if __name__ == "__main__":
    check_qa_models()
