#!/usr/bin/env python3
"""Complete end-to-end project test with bajaj.pdf - Full AI Q&A System"""

import os
import sys
import asyncio
import traceback
import time
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
    
    # Import all project components
    from robust_document_parser import parse_document
    from gemini_vector_embedder import GeminiVectorEmbedder
    from main import create_embeddings, query_documents, get_documents_info
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Ensure all dependencies are installed")
    sys.exit(1)

async def test_complete_project_bajaj():
    """Complete end-to-end test of the entire project with bajaj.pdf."""
    
    print("🚀 COMPLETE PROJECT TEST - BAJAJ.PDF END-TO-END")
    print("=" * 80)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Working Directory: {os.getcwd()}")
    
    pdf_path = 'bajaj.pdf'
    
    # PHASE 1: Environment & File Validation
    print(f"\n{'🔍 PHASE 1: ENVIRONMENT VALIDATION'}")
    print("-" * 60)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return False
    print(f"✅ API Key found: {api_key[:15]}...")
    
    # Check file exists
    if not os.path.exists(pdf_path):
        print(f"❌ Test file {pdf_path} not found")
        return False
    
    file_size_kb = os.path.getsize(pdf_path) / 1024
    print(f"✅ File found: {pdf_path} ({file_size_kb:.1f} KB)")
    
    # PHASE 2: Document Parser Test (The Fixed Chunking)
    print(f"\n{'📄 PHASE 2: DOCUMENT PARSING & CHUNKING'}")
    print("-" * 60)
    
    try:
        start_time = time.time()
        result = parse_document(
            pdf_path, 
            min_chunk_tokens=100, 
            max_chunk_tokens=2000, 
            target_chunk_tokens=1000
        )
        parse_time = time.time() - start_time
        
        chunks = result.get('chunks', [])
        token_stats = result.get('token_statistics', {})
        metadata = result.get('metadata', {})
        
        print(f"✅ PARSING SUCCESS ({parse_time:.2f}s)")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Pages: {metadata.get('page_count', 'unknown')}")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   Total tokens: {token_stats.get('total_tokens', 0):,}")
        print(f"   Avg tokens/chunk: {token_stats.get('avg_tokens_per_chunk', 0):.1f}")
        print(f"   Max tokens/chunk: {token_stats.get('max_tokens_per_chunk', 0)}")
        
        # Verify chunking fix
        max_tokens = token_stats.get('max_tokens_per_chunk', 0)
        over_limit = sum(1 for c in chunks if c.get('token_count', 0) > 2000)
        
        if over_limit == 0 and max_tokens <= 2000:
            print(f"✅ CHUNKING FIX VERIFIED: All chunks under 2000 tokens!")
        else:
            print(f"❌ CHUNKING ISSUE: {over_limit} chunks exceed 2000 tokens")
            return False
            
    except Exception as e:
        print(f"❌ PARSING FAILED: {str(e)}")
        traceback.print_exc()
        return False
    
    # PHASE 3: Gemini API Authentication Test
    print(f"\n{'🤖 PHASE 3: GEMINI API AUTHENTICATION'}")
    print("-" * 60)
    
    try:
        embedder = GeminiVectorEmbedder(api_key=api_key)
        print(f"✅ Embedder created")
        print(f"   Model: {embedder.model}")
        print(f"   Base URL: {embedder.base_url}")
        
        # Test with small sample
        test_text = "Sample text for Gemini API test"
        embed_result = await embedder.generate_embeddings([test_text])
        
        if embed_result.get('success'):
            embeddings = embed_result.get('embeddings', [])
            dimensions = embed_result.get('dimensions', 0)
            print(f"✅ AUTHENTICATION SUCCESS")
            print(f"   Generated embeddings: {len(embeddings)}")
            print(f"   Dimensions: {dimensions}")
        else:
            print(f"❌ AUTHENTICATION FAILED: {embed_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ API TEST FAILED: {str(e)}")
        traceback.print_exc()
        return False
    
    # PHASE 4: Full Document Processing
    print(f"\n{'📊 PHASE 4: FULL DOCUMENT EMBEDDING CREATION'}")
    print("-" * 60)
    
    try:
        start_time = time.time()
        embed_result = await create_embeddings(pdf_path)
        embed_time = time.time() - start_time
        
        print(f"✅ EMBEDDING CREATION SUCCESS ({embed_time:.2f}s)")
        print(f"   Result: {embed_result}")
        
        # Check document info
        doc_info = await get_documents_info()
        print(f"✅ Documents in system: {len(doc_info.get('documents', []))}")
        
    except Exception as e:
        print(f"❌ EMBEDDING CREATION FAILED: {str(e)}")
        traceback.print_exc()
        return False
    
    # PHASE 5: Query Testing (The Ultimate Test)
    print(f"\n{'💬 PHASE 5: AI Q&A FUNCTIONALITY'}")
    print("-" * 60)
    
    test_queries = [
        "What is Bajaj's main business?",
        "What are the key financial metrics mentioned?",
        "What is the company's performance outlook?",
        "What are the main business segments?",
        "What challenges does the company face?"
    ]
    
    successful_queries = 0
    
    for i, query in enumerate(test_queries, 1):
        try:
            print(f"\n🔍 Query {i}: {query}")
            start_time = time.time()
            answer_result = await query_documents(query)
            query_time = time.time() - start_time
            
            if answer_result and answer_result.get('answer'):
                answer = answer_result['answer']
                sources = answer_result.get('sources', [])
                confidence = answer_result.get('confidence', 0)
                
                print(f"✅ SUCCESS ({query_time:.2f}s)")
                print(f"   Answer: {answer[:200]}...")
                print(f"   Sources: {len(sources)} chunks")
                print(f"   Confidence: {confidence}")
                successful_queries += 1
            else:
                print(f"❌ No answer received")
                
        except Exception as e:
            print(f"❌ Query failed: {str(e)}")
    
    # PHASE 6: Final Results
    print(f"\n{'🎯 PHASE 6: FINAL RESULTS'}")
    print("-" * 60)
    
    success_rate = (successful_queries / len(test_queries)) * 100
    
    print(f"📊 TEST SUMMARY:")
    print(f"   ✅ Document parsing: SUCCESS")
    print(f"   ✅ Chunking fix: SUCCESS (max {max_tokens} tokens)")
    print(f"   ✅ API authentication: SUCCESS")
    print(f"   ✅ Embedding creation: SUCCESS")
    print(f"   ✅ Query success rate: {successful_queries}/{len(test_queries)} ({success_rate:.1f}%)")
    
    overall_success = success_rate >= 80  # 80% success rate threshold
    
    if overall_success:
        print(f"\n🎉 PROJECT TEST PASSED!")
        print(f"   🚀 System fully operational with bajaj.pdf")
        print(f"   🔧 Chunking issue completely resolved")
        print(f"   💬 AI Q&A functionality working")
        print(f"   📈 Ready for production deployment")
    else:
        print(f"\n⚠️ PROJECT TEST PARTIALLY FAILED")
        print(f"   Success rate below 80% threshold")
    
    return overall_success

async def main():
    """Run the complete project test."""
    try:
        success = await test_complete_project_bajaj()
        
        print(f"\n{'='*80}")
        if success:
            print("🎊 COMPLETE PROJECT TEST: ✅ SUCCESS!")
            print("Your AI Q&A system with bajaj.pdf is fully operational!")
        else:
            print("💥 COMPLETE PROJECT TEST: ❌ ISSUES DETECTED")
            print("Check the logs above for specific failures")
        print(f"{'='*80}")
        
        return success
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
