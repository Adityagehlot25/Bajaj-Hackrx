#!/usr/bin/env python3
"""
Interactive Multi-Document Q&A System
Ready to use when API quota resets
"""

import os
import sys
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from robust_document_parser import parse_document
    from gemini_vector_embedder import GeminiVectorEmbedder, embed_document_chunks
    from faiss_store import FAISSVectorStore, reset_vector_store
    from gemini_answer import get_gemini_answer_async

    class InteractiveQASystem:
        """Interactive multi-document Q&A system"""
        
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.vector_store = None
            self.embedder = GeminiVectorEmbedder(api_key=api_key)
            self.processed_docs = {}
            self.working_models = [
                "gemini-1.5-flash",
                "gemini-1.5-pro", 
                "gemini-pro",
                "gemini-2.0-flash-exp"
            ]
        
        async def initialize_system(self):
            """Initialize the system"""
            print("🚀 INITIALIZING MULTI-DOCUMENT Q&A SYSTEM")
            print("=" * 50)
            
            # Reset and create vector store
            try:
                reset_vector_store()
            except:
                pass
            
            self.vector_store = FAISSVectorStore(dimension=768)
            print("✅ Vector store initialized")
            
            return True
        
        async def process_documents(self, pdf_files=None):
            """Process available PDF documents"""
            
            if pdf_files is None:
                import glob
                pdf_files = glob.glob("*.pdf")
            
            if not pdf_files:
                print("❌ No PDF files found")
                return False
            
            print(f"\n📄 PROCESSING {len(pdf_files)} DOCUMENTS")
            print("-" * 40)
            
            successful = 0
            
            for pdf_path in pdf_files:
                filename = os.path.basename(pdf_path)
                print(f"📄 Processing {filename}...")
                
                try:
                    # Parse document
                    result = parse_document(pdf_path, min_chunk_tokens=100, max_chunk_tokens=2000)
                    chunks = result.get('chunks', [])
                    
                    if not chunks:
                        print(f"   ❌ No content extracted")
                        continue
                    
                    print(f"   ✅ Parsed: {len(chunks)} chunks")
                    
                    # Generate embeddings
                    document_result = {
                        "success": True,
                        "chunks": chunks,
                        "file_path": pdf_path,
                        "metadata": result.get('metadata', {})
                    }
                    
                    embedded_result = await embed_document_chunks(
                        document_result=document_result,
                        api_key=self.api_key,
                        model="embedding-001"
                    )
                    
                    if embedded_result.get("embedding_metadata", {}).get("success"):
                        embeddings = [chunk.get("embedding") for chunk in embedded_result.get("chunks", [])]
                        chunk_texts = [chunk.get("text") for chunk in embedded_result.get("chunks", [])]
                        
                        # Add to vector store
                        doc_id = self.vector_store.add_document_embeddings(
                            embeddings=embeddings,
                            file_path=pdf_path,
                            file_type=".pdf",
                            chunk_texts=chunk_texts
                        )
                        
                        self.processed_docs[filename] = {
                            'doc_id': doc_id,
                            'chunks': len(chunks),
                            'file_path': pdf_path
                        }
                        
                        print(f"   ✅ Indexed: {len(embeddings)} embeddings")
                        successful += 1
                    else:
                        print(f"   ❌ Embedding failed")
                
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
            
            print(f"\n📊 Processing complete: {successful}/{len(pdf_files)} documents successful")
            return successful > 0
        
        async def find_working_model(self):
            """Find a working Gemini model"""
            print(f"\n🔍 Finding available model...")
            
            for model in self.working_models:
                try:
                    result = await get_gemini_answer_async(
                        user_question="Test question",
                        relevant_clauses="Test context: This is a simple test.",
                        api_key=self.api_key,
                        model=model,
                        max_tokens=20,
                        temperature=0.1
                    )
                    
                    if result.get('success'):
                        print(f"✅ Found working model: {model}")
                        return model
                    else:
                        error = result.get('error', '')
                        if "429" not in str(error):
                            print(f"   ⚠️  {model}: {str(error)[:50]}...")
                
                except Exception as e:
                    print(f"   ❌ {model}: {str(e)[:50]}...")
            
            return None
        
        async def answer_question(self, question: str, working_model: str):
            """Answer a user question"""
            
            # Generate query embedding
            embed_result = await self.embedder.generate_embeddings([question])
            if not embed_result.get('success'):
                return {"success": False, "error": "Failed to generate query embedding"}
            
            query_embedding = embed_result.get('embeddings', [])[0]
            
            # Search for relevant chunks
            search_results = self.vector_store.similarity_search(
                query_embedding=query_embedding,
                k=5
            )
            
            if not search_results:
                return {"success": False, "error": "No relevant content found"}
            
            # Prepare context
            relevant_chunks = []
            for result in search_results:
                text = result.get('text', '')
                score = result.get('score', 0)
                doc_path = result.get('metadata', {}).get('file_path', 'unknown')
                doc_name = os.path.basename(doc_path) if doc_path != 'unknown' else 'unknown'
                chunk_info = f"[From: {doc_name}, Score: {score:.3f}]\n{text[:400]}..."
                relevant_chunks.append(chunk_info)
            
            combined_context = "\n\n".join(relevant_chunks)
            
            # Generate answer
            return await get_gemini_answer_async(
                user_question=question,
                relevant_clauses=combined_context,
                api_key=self.api_key,
                model=working_model,
                max_tokens=500,
                temperature=0.3
            )
        
        async def run_interactive_session(self):
            """Run interactive Q&A session"""
            
            print(f"\n🎯 STARTING INTERACTIVE SESSION")
            print("=" * 40)
            print("Type 'quit' to exit, 'help' for commands")
            
            # Find working model
            working_model = await self.find_working_model()
            if not working_model:
                print("❌ No working models available. Try again later or upgrade API plan.")
                return False
            
            success_count = 0
            question_count = 0
            
            while True:
                try:
                    question = input(f"\n💬 Your question: ").strip()
                    
                    if question.lower() in ['quit', 'exit', 'q']:
                        break
                    elif question.lower() == 'help':
                        print(f"""
🔧 COMMANDS:
   • Ask any question about your documents
   • 'quit' or 'exit' - Exit the system
   • 'stats' - Show system statistics
   • 'docs' - List processed documents
                        """)
                        continue
                    elif question.lower() == 'stats':
                        stats = self.vector_store.get_stats()
                        print(f"""
📊 SYSTEM STATISTICS:
   • Documents: {stats['total_documents']}
   • Chunks: {stats['total_chunks']}  
   • Vectors: {stats['total_vectors']}
   • Success rate: {(success_count/question_count)*100:.1f}% ({success_count}/{question_count})
   • Model: {working_model}
                        """)
                        continue
                    elif question.lower() == 'docs':
                        print(f"\n📄 PROCESSED DOCUMENTS:")
                        for doc, info in self.processed_docs.items():
                            print(f"   • {doc}: {info['chunks']} chunks")
                        continue
                    
                    if not question:
                        continue
                    
                    question_count += 1
                    print(f"🤖 Processing question {question_count}...")
                    
                    # Get answer
                    result = await self.answer_question(question, working_model)
                    
                    if result.get('success'):
                        answer = result.get('answer', '')
                        print(f"✅ Answer: {answer}")
                        success_count += 1
                    else:
                        error = result.get('error', 'Unknown error')
                        print(f"❌ Error: {error}")
                        
                        # Check if model quota exhausted
                        if "429" in str(error):
                            print(f"🔄 Trying to find alternative model...")
                            new_model = await self.find_working_model()
                            if new_model:
                                working_model = new_model
                                print(f"✅ Switched to {working_model}")
                            else:
                                print(f"❌ All models quota exhausted")
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            print(f"\n📊 SESSION SUMMARY:")
            print(f"   Questions asked: {question_count}")
            print(f"   Successful answers: {success_count}")
            if question_count > 0:
                print(f"   Success rate: {(success_count/question_count)*100:.1f}%")
            print(f"👋 Thank you for using the Multi-Document Q&A system!")
            
            return success_count > 0

    async def main():
        """Main function"""
        print("🎯 MULTI-DOCUMENT INTERACTIVE Q&A SYSTEM")
        print("=" * 50)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found")
            return False
        
        # Initialize system
        qa_system = InteractiveQASystem(api_key)
        
        if not await qa_system.initialize_system():
            return False
        
        # Process documents
        if not await qa_system.process_documents():
            return False
        
        # Run interactive session
        return await qa_system.run_interactive_session()

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print(f"\n👋 System stopped by user")
        sys.exit(0)
