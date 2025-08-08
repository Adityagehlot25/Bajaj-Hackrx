#!/usr/bin/env python3
"""
Interactive Q&A Session System
Real-time document conversations using FAISS vector store
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from robust_document_parser import parse_document
    from faiss_store import get_vector_store, reset_vector_store
    from gemini_answer import get_gemini_answer_async
    import google.generativeai as genai

    class DocumentQASession:
        """Interactive Q&A session with documents using FAISS vector store"""
        
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.vector_store = None
            self.loaded_documents = {}
            self.conversation_history = []
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
        async def get_embedding(self, text: str) -> List[float]:
            """Get embedding for text using Gemini"""
            try:
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="retrieval_query"
                )
                return result['embedding']
            except Exception as e:
                raise Exception(f"Embedding error: {e}")
        
        async def load_document(self, file_path: str, doc_id: str = None) -> bool:
            """Load a document into the vector store"""
            print(f"\n📄 Loading document: {file_path}")
            
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return False
            
            try:
                # Parse document
                print("🔄 Parsing document...")
                result = parse_document(file_path)
                chunks = result.get('chunks', [])
                
                if not chunks:
                    print("❌ No chunks extracted from document")
                    return False
                
                token_stats = result.get('token_statistics', {})
                print(f"✅ Parsed {len(chunks)} chunks")
                if token_stats:
                    print(f"📊 {token_stats['total_tokens']} tokens, avg {token_stats['avg_tokens_per_chunk']:.1f} per chunk")
                
                # Initialize vector store if needed
                if self.vector_store is None:
                    reset_vector_store()
                    self.vector_store = get_vector_store(dimension=768)
                    print("✅ Vector store initialized")
                
                # Generate embeddings
                print(f"🔄 Generating embeddings for {len(chunks)} chunks...")
                embeddings = []
                chunk_texts = []
                
                for i, chunk in enumerate(chunks[:10]):  # Limit to first 10 chunks for demo
                    try:
                        chunk_text = chunk.get('text', '') if isinstance(chunk, dict) else chunk
                        embedding = await self.get_embedding(chunk_text)
                        embeddings.append(embedding)
                        chunk_texts.append(chunk_text)
                        print(f"   ✅ Chunk {i+1}/10 embedded")
                        await asyncio.sleep(0.3)  # Rate limiting
                    except Exception as e:
                        print(f"   ❌ Chunk {i+1} failed: {e}")
                
                if not embeddings:
                    print("❌ No embeddings generated")
                    return False
                
                # Store in vector store
                file_type = file_path.split('.')[-1].lower()
                stored_doc_id = self.vector_store.add_document_embeddings(
                    embeddings=embeddings,
                    file_path=file_path,
                    file_type=file_type,
                    chunk_texts=chunk_texts,
                    doc_id=doc_id
                )
                
                # Track loaded document
                self.loaded_documents[stored_doc_id] = {
                    'file_path': file_path,
                    'chunks_count': len(embeddings),
                    'loaded_at': datetime.now().isoformat()
                }
                
                print(f"✅ Document loaded successfully!")
                print(f"📊 Document ID: {stored_doc_id[:8]}...")
                print(f"📊 {len(embeddings)} chunks stored in vector database")
                
                return True
                
            except Exception as e:
                print(f"❌ Error loading document: {e}")
                return False
        
        async def ask_question(self, question: str, k: int = 3) -> Dict[str, Any]:
            """Ask a question and get an AI-powered answer"""
            if self.vector_store is None:
                return {"success": False, "error": "No documents loaded"}
            
            try:
                # Get query embedding
                query_embedding = await self.get_embedding(question)
                
                # Search similar chunks
                search_results = self.vector_store.similarity_search(
                    query_embedding=query_embedding,
                    k=k,
                    score_threshold=2.5  # L2 distance threshold
                )
                
                if not search_results:
                    return {
                        "success": False,
                        "error": "No relevant content found",
                        "suggestion": "Try rephrasing your question or asking about different topics"
                    }
                
                # Prepare context for AI
                relevant_context = "\n\n".join([
                    f"Context {i+1} (relevance: {result['score']:.3f}):\n{result['text']}"
                    for i, result in enumerate(search_results)
                ])
                
                # Try different models for answer generation
                models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
                
                for model in models:
                    try:
                        answer_result = await get_gemini_answer_async(
                            user_question=question,
                            relevant_clauses=relevant_context,
                            api_key=self.api_key,
                            model=model,
                            max_tokens=300,
                            temperature=0.3
                        )
                        
                        if answer_result.get('success'):
                            # Store in conversation history
                            self.conversation_history.append({
                                'question': question,
                                'answer': answer_result['answer'],
                                'model': model,
                                'sources': len(search_results),
                                'timestamp': datetime.now().isoformat()
                            })
                            
                            return {
                                "success": True,
                                "answer": answer_result['answer'],
                                "model": model,
                                "sources": search_results,
                                "context_used": len(search_results)
                            }
                    
                    except Exception as e:
                        continue
                
                return {
                    "success": False,
                    "error": "All AI models unavailable (quota exhausted)",
                    "sources": search_results
                }
                
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        def get_session_stats(self) -> Dict[str, Any]:
            """Get session statistics"""
            stats = self.vector_store.get_stats() if self.vector_store else {}
            return {
                "loaded_documents": len(self.loaded_documents),
                "total_chunks": stats.get('total_chunks', 0),
                "total_vectors": stats.get('total_vectors', 0),
                "questions_asked": len(self.conversation_history),
                "vector_store_dimension": stats.get('dimension', 0)
            }
        
        def show_loaded_documents(self):
            """Display loaded documents"""
            if not self.loaded_documents:
                print("📄 No documents loaded yet")
                return
            
            print(f"\n📚 LOADED DOCUMENTS ({len(self.loaded_documents)})")
            print("-" * 40)
            for doc_id, info in self.loaded_documents.items():
                print(f"📄 {info['file_path']}")
                print(f"   ID: {doc_id[:8]}...")
                print(f"   Chunks: {info['chunks_count']}")
                print(f"   Loaded: {info['loaded_at'][:19]}")
        
        def show_conversation_history(self):
            """Display conversation history"""
            if not self.conversation_history:
                print("💬 No questions asked yet")
                return
            
            print(f"\n💬 CONVERSATION HISTORY ({len(self.conversation_history)} questions)")
            print("-" * 60)
            for i, conv in enumerate(self.conversation_history[-5:], 1):  # Last 5
                print(f"❓ Q{i}: {conv['question']}")
                print(f"✅ A{i}: {conv['answer'][:100]}...")
                print(f"   Model: {conv['model']}, Sources: {conv['sources']}")
                print()

    async def interactive_qa_session():
        """Run interactive Q&A session"""
        print("🤖 INTERACTIVE DOCUMENT Q&A SESSION")
        print("=" * 50)
        print("Ask questions about your documents in natural language!")
        print("Commands: 'load <file>', 'docs', 'history', 'stats', 'quit'")
        print()
        
        # Check API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY environment variable not set")
            print("Please set it with: set GEMINI_API_KEY=your_key_here")
            return
        
        # Initialize session
        session = DocumentQASession(api_key)
        
        # Auto-load available documents
        available_docs = []
        for file in ['bajaj.pdf', 'chotgdp.pdf']:
            if os.path.exists(file):
                available_docs.append(file)
        
        if available_docs:
            print(f"📄 Found documents: {', '.join(available_docs)}")
            load_choice = input("Load documents automatically? (y/n): ").lower().strip()
            
            if load_choice in ['y', 'yes', '']:
                for doc in available_docs[:1]:  # Load first document
                    print(f"\n🔄 Auto-loading {doc}...")
                    success = await session.load_document(doc)
                    if success:
                        break
        
        print(f"\n🎯 Ready for questions! Type 'help' for commands.")
        
        while True:
            try:
                print("\n" + "-" * 50)
                user_input = input("❓ Your question (or command): ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye! Session ended.")
                    break
                
                elif user_input.lower() in ['help', 'h']:
                    print("\n📖 AVAILABLE COMMANDS:")
                    print("  load <filename>  - Load a document")
                    print("  docs            - Show loaded documents")  
                    print("  history         - Show conversation history")
                    print("  stats           - Show session statistics")
                    print("  quit            - Exit session")
                    print("  Or just ask any question!")
                    continue
                
                elif user_input.lower().startswith('load '):
                    filename = user_input[5:].strip()
                    await session.load_document(filename)
                    continue
                
                elif user_input.lower() == 'docs':
                    session.show_loaded_documents()
                    continue
                
                elif user_input.lower() == 'history':
                    session.show_conversation_history()
                    continue
                
                elif user_input.lower() == 'stats':
                    stats = session.get_session_stats()
                    print(f"\n📊 SESSION STATISTICS:")
                    print(f"   📄 Documents loaded: {stats['loaded_documents']}")
                    print(f"   🔢 Total chunks: {stats['total_chunks']}")
                    print(f"   📐 Vector dimension: {stats['vector_store_dimension']}")
                    print(f"   💬 Questions asked: {stats['questions_asked']}")
                    continue
                
                # Handle questions
                if session.vector_store is None:
                    print("❌ No documents loaded. Use 'load <filename>' first.")
                    continue
                
                print(f"\n🔍 Searching for relevant information...")
                result = await session.ask_question(user_input)
                
                if result['success']:
                    print(f"\n✅ Answer ({result['model']}):")
                    print("-" * 30)
                    print(result['answer'])
                    print(f"\n📊 Based on {result['context_used']} relevant sections")
                    
                    # Show sources briefly
                    if result.get('sources'):
                        print(f"\n📋 Sources (relevance scores):")
                        for i, source in enumerate(result['sources'][:3], 1):
                            preview = source['text'][:80].replace('\n', ' ') + "..."
                            print(f"   {i}. Score {source['score']:.3f}: {preview}")
                
                else:
                    print(f"\n❌ {result['error']}")
                    if result.get('suggestion'):
                        print(f"💡 {result['suggestion']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

    async def main():
        await interactive_qa_session()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required modules are available")
    sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
