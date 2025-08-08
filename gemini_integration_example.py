#!/usr/bin/env python3
"""
Example demonstrating the refactored Gemini API integration
Shows how to use Google Gemini instead of OpenAI for embeddings
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_gemini_integration():
    """Test the Gemini API integration with examples."""
    
    print("🔄 Testing Gemini API Integration")
    print("=" * 50)
    
    # Import the refactored functions
    from gemini_vector_embedder import generate_embeddings, GeminiVectorEmbedder
    from main import generate_query_embedding
    
    # Test 1: Direct Gemini embedder
    print("\n1️⃣ Testing direct Gemini embedder:")
    print("-" * 30)
    
    try:
        embedder = GeminiVectorEmbedder()
        
        test_texts = [
            "Machine learning algorithms process data to find patterns.",
            "Natural language processing helps computers understand text.",
            "Vector embeddings represent semantic meaning numerically."
        ]
        
        result = await embedder.generate_embeddings(test_texts)
        
        if result.get("success"):
            print("✅ Success!")
            print(f"📊 Model: {result['model']}")
            print(f"📊 Dimensions: {result['dimensions']} (Gemini uses 768-dim vectors)")
            print(f"📊 Total chunks: {result['total_chunks']}")
            print(f"📊 Total tokens: {result['total_tokens']}")
            
            if result['embeddings']:
                sample = result['embeddings'][0]
                print(f"🎯 Sample embedding: [{sample[0]:.4f}, {sample[1]:.4f}, ..., {sample[-1]:.4f}]")
        else:
            print(f"❌ Error: {result.get('error')}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")
    
    # Test 2: Query embedding function (with fallback)
    print("\n2️⃣ Testing query embedding function:")
    print("-" * 30)
    
    try:
        query = "What are the benefits of machine learning?"
        result = await generate_query_embedding(query)
        
        if result.get("success"):
            print("✅ Success!")
            metadata = result["metadata"]
            print(f"📊 Model: {metadata['model']}")
            print(f"📊 Dimensions: {metadata['dimensions']}")
            print(f"📊 Vector length: {metadata['vector_length']}")
            
            embedding = result["embedding"]
            print(f"🎯 Query: {result['query_text']}")
            print(f"🎯 Embedding preview: [{embedding[0]:.4f}, {embedding[1]:.4f}, ..., {embedding[-1]:.4f}]")
            
            # Check if it's using mock or real embeddings
            if "MOCK" in metadata["model"]:
                print("⚠️  Using mock embeddings (API unavailable)")
            else:
                print("✅ Using real Gemini embeddings")
        else:
            print(f"❌ Error: {result.get('error')}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")
    
    # Test 3: Synchronous version
    print("\n3️⃣ Testing synchronous Gemini API:")
    print("-" * 30)
    
    try:
        embedder = GeminiVectorEmbedder()
        
        test_text = ["This is a synchronous test of the Gemini API integration."]
        result = embedder.generate_embeddings_sync(test_text)
        
        if result.get("success"):
            print("✅ Sync API works!")
            print(f"📊 Model: {result['model']}")
            print(f"📊 Dimensions: {result['dimensions']}")
            print(f"📊 Total chunks: {result['total_chunks']}")
        else:
            print(f"❌ Sync API error: {result.get('error')}")
            
    except Exception as e:
        print(f"💥 Sync API exception: {e}")

def setup_gemini_api_key():
    """Helper function to set up Gemini API key."""
    print("🔑 Gemini API Setup")
    print("=" * 30)
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("\n📝 To set up your Gemini API key:")
        print("1. Go to: https://makersuite.google.com/app/apikey")
        print("2. Create a new API key")
        print("3. Add to your .env file:")
        print("   GEMINI_API_KEY=your-api-key-here")
        print("\n⚠️  This example will use mock embeddings until you set up the API key")
        return False
    else:
        print(f"✅ GEMINI_API_KEY found: {api_key[:20]}...")
        return True

async def compare_openai_vs_gemini():
    """Compare the old OpenAI implementation with the new Gemini implementation."""
    print("🔄 OpenAI vs Gemini Comparison")
    print("=" * 50)
    
    print("📊 Key Differences:")
    print("-" * 20)
    print("• OpenAI text-embedding-3-small: 1536 dimensions")
    print("• Gemini text-embedding-004:     768 dimensions")
    print("• OpenAI: Uses OpenAI library")
    print("• Gemini: Uses HTTP requests (aiohttp/requests)")
    print("• OpenAI: $0.00002 per 1K tokens")
    print("• Gemini: Free tier available")
    
    print("\n🔧 API Changes:")
    print("-" * 20)
    print("• Environment variable: OPENAI_API_KEY → GEMINI_API_KEY")
    print("• Default model: text-embedding-3-small → text-embedding-004")
    print("• Import: vector_embedder → gemini_vector_embedder")
    print("• Mock embeddings: 1536 → 768 dimensions")
    
    print("\n✅ Preserved Features:")
    print("-" * 20)
    print("• Same function signatures")
    print("• Same response format")
    print("• Automatic fallback to mock embeddings")
    print("• Batch processing")
    print("• Error handling")
    print("• Token estimation")

def main():
    """Main function to run all tests."""
    print("🚀 Gemini API Integration Examples")
    print("=" * 60)
    
    # Check API key setup
    has_api_key = setup_gemini_api_key()
    
    print("\n" + "=" * 60)
    
    # Run async tests
    asyncio.run(test_gemini_integration())
    
    print("\n" + "=" * 60)
    
    # Show comparison
    asyncio.run(compare_openai_vs_gemini())
    
    print("\n🎉 Testing complete!")
    
    if not has_api_key:
        print("\n💡 Next steps:")
        print("1. Set up your Gemini API key")
        print("2. Re-run this script to test real API calls")
        print("3. Update your FastAPI application to use Gemini")

if __name__ == "__main__":
    main()
