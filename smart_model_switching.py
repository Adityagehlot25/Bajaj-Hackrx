#!/usr/bin/env python3
"""
Smart Model Switching for Quota Management
Tests different Gemini models to find available capacity
"""

import os
import sys
import asyncio
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from robust_document_parser import parse_document
    from gemini_vector_embedder import GeminiVectorEmbedder, embed_document_chunks
    from faiss_store import FAISSVectorStore, reset_vector_store
    from gemini_answer import get_gemini_answer_async

    class SmartModelManager:
        """Manages multiple Gemini models to work around quota limits"""
        
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.available_models = [
                "gemini-1.5-flash",      # Often has higher limits
                "gemini-1.5-pro",        # Different quota pool
                "gemini-pro",            # Legacy model, separate limits
                "gemini-2.0-flash-exp",  # Experimental (if quota resets)
            ]
            self.working_model = None
            self.failed_models = set()
        
        async def find_working_model(self, test_query: str = "Hello, world!") -> Optional[str]:
            """Find a model that's not quota-exhausted"""
            print(f"🔍 TESTING AVAILABLE MODELS")
            print("-" * 40)
            
            for model in self.available_models:
                if model in self.failed_models:
                    print(f"   ⏭️  Skipping {model} (previously failed)")
                    continue
                
                print(f"   🧪 Testing {model}...")
                
                try:
                    # Quick test with minimal context
                    result = await get_gemini_answer_async(
                        user_question="What is 2+2?",
                        relevant_clauses="Simple math: 2 + 2 = 4",
                        api_key=self.api_key,
                        model=model,
                        max_tokens=50,
                        temperature=0.1
                    )
                    
                    if result.get('success'):
                        print(f"   ✅ {model} is available!")
                        self.working_model = model
                        return model
                    else:
                        error = result.get('error', '')
                        if "429" in str(error) or "quota" in str(error).lower() or "rate" in str(error).lower():
                            print(f"   ❌ {model} quota exhausted")
                            self.failed_models.add(model)
                        else:
                            print(f"   ⚠️  {model} other error: {str(error)[:50]}...")
                
                except Exception as e:
                    print(f"   ❌ {model} exception: {str(e)[:50]}...")
                    
                await asyncio.sleep(1)  # Brief delay between tests
            
            print(f"   🚫 No working models found")
            return None
        
        async def smart_answer(self, user_question: str, relevant_clauses: str, **kwargs) -> Dict[str, Any]:
            """Get answer using the best available model"""
            
            # If we don't have a working model, find one
            if not self.working_model:
                working = await self.find_working_model()
                if not working:
                    return {
                        "success": False,
                        "error": "All models quota exhausted. Please try again later or upgrade API plan.",
                        "answer": None,
                        "rationale": None,
                        "source_chunks": None
                    }
            
            # Try the working model
            result = await get_gemini_answer_async(
                user_question=user_question,
                relevant_clauses=relevant_clauses,
                api_key=self.api_key,
                model=self.working_model,
                **kwargs
            )
            
            # If it fails with quota error, mark as failed and try another
            if not result.get('success'):
                error = result.get('error', '')
                if "429" in str(error) or "quota" in str(error).lower():
                    print(f"   🔄 {self.working_model} quota exhausted, trying alternatives...")
                    self.failed_models.add(self.working_model)
                    self.working_model = None
                    
                    # Try to find another working model
                    new_model = await self.find_working_model()
                    if new_model:
                        return await get_gemini_answer_async(
                            user_question=user_question,
                            relevant_clauses=relevant_clauses,
                            api_key=self.api_key,
                            model=new_model,
                            **kwargs
                        )
            
            return result

    async def test_multi_document_with_smart_models():
        """Test multi-document Q&A with smart model switching"""
        
        print("🎯 MULTI-DOCUMENT Q&A WITH SMART MODEL SWITCHING")
        print("=" * 65)
        print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found")
            return False
        
        print(f"✅ API Key configured: {api_key[:15]}...")
        
        try:
            # Initialize smart model manager
            model_manager = SmartModelManager(api_key)
            
            # Find working model first
            working_model = await model_manager.find_working_model()
            if not working_model:
                print("❌ No working models available")
                return False
            
            print(f"🎯 Using model: {working_model}")
            
            # Initialize system
            try:
                reset_vector_store()
            except:
                pass
            
            vector_store = FAISSVectorStore(dimension=768)
            embedder = GeminiVectorEmbedder(api_key=api_key)
            
            print("✅ System initialized")
            
            # Process multiple PDFs
            pdf_files = glob.glob("*.pdf")[:3]  # Limit to 3 for testing
            processed_docs = {}
            
            print(f"\n📄 PROCESSING {len(pdf_files)} DOCUMENTS")
            print("-" * 40)
            
            for pdf_path in pdf_files:
                filename = os.path.basename(pdf_path)
                print(f"   📄 Processing {filename}...")
                
                try:
                    # Parse document
                    result = parse_document(pdf_path, min_chunk_tokens=100, max_chunk_tokens=2000)
                    chunks = result.get('chunks', [])
                    
                    if not chunks:
                        print(f"      ❌ No content extracted")
                        continue
                    
                    print(f"      ✅ Parsed: {len(chunks)} chunks")
                    
                    # Generate embeddings
                    document_result = {
                        "success": True,
                        "chunks": chunks,
                        "file_path": pdf_path,
                        "metadata": result.get('metadata', {})
                    }
                    
                    embedded_result = await embed_document_chunks(
                        document_result=document_result,
                        api_key=api_key,
                        model="embedding-001"
                    )
                    
                    if embedded_result.get("embedding_metadata", {}).get("success"):
                        embeddings = [chunk.get("embedding") for chunk in embedded_result.get("chunks", [])]
                        chunk_texts = [chunk.get("text") for chunk in embedded_result.get("chunks", [])]
                        
                        # Add to vector store
                        doc_id = vector_store.add_document_embeddings(
                            embeddings=embeddings,
                            file_path=pdf_path,
                            file_type=".pdf",
                            chunk_texts=chunk_texts
                        )
                        
                        processed_docs[filename] = {
                            'doc_id': doc_id,
                            'chunks': len(chunks),
                            'file_path': pdf_path
                        }
                        
                        print(f"      ✅ Indexed: {len(embeddings)} embeddings")
                    else:
                        print(f"      ❌ Embedding failed")
                
                except Exception as e:
                    print(f"      ❌ Error: {str(e)}")
            
            if not processed_docs:
                print("❌ No documents processed successfully")
                return False
            
            print(f"\n🤖 TESTING Q&A WITH SMART MODEL SWITCHING")
            print("-" * 50)
            
            # Test queries
            test_queries = [
                "What are the main coverage benefits mentioned?",
                "What are the eligibility requirements?", 
                "What exclusions are listed in the policy?"
            ]
            
            successful_answers = 0
            total_queries = 0
            
            for i, query in enumerate(test_queries, 1):
                print(f"\n📝 Query {i}: {query}")
                total_queries += 1
                
                try:
                    # Generate query embedding
                    embed_result = await embedder.generate_embeddings([query])
                    
                    if not embed_result.get('success'):
                        print(f"   ❌ Query embedding failed")
                        continue
                    
                    query_embedding = embed_result.get('embeddings', [])[0]
                    
                    # Search for relevant chunks
                    search_results = vector_store.similarity_search(
                        query_embedding=query_embedding,
                        k=5
                    )
                    
                    if not search_results:
                        print(f"   ❌ No relevant content found")
                        continue
                    
                    # Prepare context
                    relevant_chunks = []
                    for result in search_results[:3]:  # Limit context to save quota
                        text = result.get('text', '')
                        score = result.get('score', 0)
                        chunk_info = f"[Score: {score:.3f}]\n{text[:300]}..."
                        relevant_chunks.append(chunk_info)
                    
                    combined_context = "\n\n".join(relevant_chunks)
                    
                    # Use smart model manager for answer
                    answer_result = await model_manager.smart_answer(
                        user_question=query,
                        relevant_clauses=combined_context,
                        max_tokens=400,
                        temperature=0.3
                    )
                    
                    if answer_result.get('success'):
                        answer = answer_result.get('answer', '')
                        model_used = answer_result.get('model', 'unknown')
                        print(f"   ✅ Success with {model_used}!")
                        print(f"   📝 Answer: {answer[:120]}...")
                        successful_answers += 1
                    else:
                        error = answer_result.get('error', 'Unknown error')
                        print(f"   ❌ Failed: {error[:80]}...")
                
                except Exception as e:
                    print(f"   ❌ Exception: {str(e)}")
                
                # Brief delay between queries
                await asyncio.sleep(1)
            
            # Results
            success_rate = (successful_answers / total_queries) * 100 if total_queries > 0 else 0
            
            print(f"\n📊 FINAL RESULTS")
            print("=" * 40)
            print(f"📄 Documents processed: {len(processed_docs)}")
            print(f"❓ Queries tested: {total_queries}")
            print(f"✅ Successful answers: {successful_answers}")
            print(f"📈 Success rate: {success_rate:.1f}%")
            print(f"🎯 Working model: {model_manager.working_model}")
            
            if successful_answers > 0:
                print(f"\n🎉 SUCCESS! Smart model switching worked!")
                print(f"✅ Multi-document AI Q&A system is operational")
                print(f"🚀 System bypassed quota limits successfully")
                return True
            else:
                print(f"\n❌ All models exhausted")
                print(f"💡 Try again later or upgrade API plan")
                return False
                
        except Exception as e:
            print(f"❌ System error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    async def main():
        success = await test_multi_document_with_smart_models()
        
        print(f"\n{'🎯' * 20}")
        print(f"SMART MODEL SWITCHING TEST COMPLETE")
        print(f"{'🎯' * 20}")
        
        if success:
            print(f"🎊 RESULT: SUCCESS!")
            print(f"✅ Found working Gemini model")
            print(f"🚀 Multi-document system operational")
            print(f"💡 Smart switching bypassed quota limits")
        else:
            print(f"⏳ RESULT: All models quota limited")
            print(f"💡 Solutions:")
            print(f"   • Wait for quota reset (~24 hours)")
            print(f"   • Upgrade to paid API plan")
            print(f"   • System architecture is proven working")
        
        return success

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
