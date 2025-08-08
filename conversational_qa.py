#!/usr/bin/env python3
"""Enhanced AI Q&A system with conversation memory and query history"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from robust_document_parser import parse_document
from gemini_vector_embedder import GeminiVectorEmbedder, embed_document_chunks
from faiss_store import FAISSVectorStore
from gemini_answer import get_gemini_answer_async

load_dotenv()

class ConversationalQA:
    """AI Q&A system with conversation memory and context awareness"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.vector_store = None
        self.embedder = GeminiVectorEmbedder(api_key=api_key)
        
        # Conversation memory
        self.conversation_history = []
        self.session_context = {}
        self.patient_profile = {}
        
    async def initialize_document(self, pdf_path: str = 'bajaj.pdf'):
        """Initialize the vector store with insurance document"""
        if self.vector_store is None:
            print("🔄 Initializing document database...")
            self.vector_store = FAISSVectorStore(dimension=768)
            
            # Check if document needs processing
            if not hasattr(self.vector_store, 'next_id') or self.vector_store.next_id == 0:
                # Process document
                result = parse_document(pdf_path, min_chunk_tokens=100, max_chunk_tokens=2000)
                chunks = result.get('chunks', [])
                
                document_result = {"success": True, "chunks": chunks, "file_path": pdf_path}
                embedded_result = await embed_document_chunks(document_result, self.api_key, "embedding-001")
                
                if embedded_result.get("embedding_metadata", {}).get("success"):
                    embeddings = [chunk.get("embedding") for chunk in embedded_result.get("chunks", [])]
                    chunk_texts = [chunk.get("text") for chunk in embedded_result.get("chunks", [])]
                    
                    self.vector_store.add_document_embeddings(embeddings, pdf_path, ".pdf", chunk_texts)
                    print("✅ Document processed and indexed")
                else:
                    print("❌ Failed to process document")
            else:
                print("✅ Using existing document index")
    
    def extract_context_from_history(self) -> Dict[str, Any]:
        """Extract relevant context from conversation history"""
        context = {
            'patient_info': {},
            'previous_questions': [],
            'established_facts': [],
            'ongoing_topic': None
        }
        
        # Extract patient information from history
        for entry in self.conversation_history:
            query = entry['query'].lower()
            
            # Extract age
            if 'age' in query and not context['patient_info'].get('age'):
                import re
                age_match = re.search(r'age[d]?\s*(\d+)', query)
                if age_match:
                    context['patient_info']['age'] = age_match.group(1)
            
            # Extract gender
            if 'female' in query and not context['patient_info'].get('gender'):
                context['patient_info']['gender'] = 'female'
            elif 'male' in query and not context['patient_info'].get('gender'):
                context['patient_info']['gender'] = 'male'
            
            # Extract procedure
            procedures = ['cataract surgery', 'bypass', 'angioplasty', 'dialysis']
            for proc in procedures:
                if proc in query and not context['patient_info'].get('procedure'):
                    context['patient_info']['procedure'] = proc
            
            # Store previous questions
            context['previous_questions'].append(entry['query'][:100])
            
            # Extract established facts from answers
            if entry.get('answer'):
                answer = entry['answer'].lower()
                if 'eligible' in answer:
                    context['established_facts'].append('eligibility_discussed')
                if 'covered' in answer:
                    context['established_facts'].append('coverage_discussed')
                if 'payout' in answer or 'amount' in answer:
                    context['established_facts'].append('payout_discussed')
        
        return context
    
    def create_contextual_query(self, current_query: str, context: Dict[str, Any]) -> str:
        """Enhance current query with conversation context"""
        
        # Build context summary
        context_parts = []
        
        # Add patient information
        if context['patient_info']:
            patient_info = []
            for key, value in context['patient_info'].items():
                patient_info.append(f"{key}: {value}")
            context_parts.append(f"Patient Profile: {', '.join(patient_info)}")
        
        # Add conversation context
        if context['previous_questions']:
            recent_questions = context['previous_questions'][-3:]  # Last 3 questions
            context_parts.append(f"Previous Questions: {'; '.join(recent_questions)}")
        
        # Add established facts
        if context['established_facts']:
            context_parts.append(f"Already Discussed: {', '.join(set(context['established_facts']))}")
        
        # Create enhanced query
        if context_parts:
            contextual_query = f"""
CONVERSATION CONTEXT:
{chr(10).join(context_parts)}

CURRENT QUERY: {current_query}

Please provide an answer that:
1. References previous discussion points when relevant
2. Avoids repeating already established information
3. Builds upon the existing conversation context
4. Addresses the current query in light of what we've already discussed
"""
        else:
            contextual_query = current_query
        
        return contextual_query
    
    def detect_follow_up_type(self, query: str, context: Dict[str, Any]) -> str:
        """Detect what type of follow-up question this is"""
        query_lower = query.lower()
        
        # Reference to previous answer
        if any(word in query_lower for word in ['that', 'this', 'it', 'what about', 'how about']):
            return 'reference_followup'
        
        # Clarification request
        if any(word in query_lower for word in ['explain', 'clarify', 'more details', 'elaborate']):
            return 'clarification'
        
        # Additional information
        if any(word in query_lower for word in ['also', 'additionally', 'furthermore', 'what else']):
            return 'additional_info'
        
        # Comparison question
        if any(word in query_lower for word in ['compare', 'difference', 'vs', 'versus', 'better']):
            return 'comparison'
        
        # New topic
        return 'new_topic'
    
    async def ask_with_context(self, query: str) -> Dict[str, Any]:
        """Ask a question with full conversation context"""
        
        print(f"🤖 CONVERSATIONAL AI Q&A")
        print("=" * 60)
        print(f"📝 Current Query: {query}")
        
        # Initialize document if needed
        await self.initialize_document()
        
        # Extract context from conversation history
        context = self.extract_context_from_history()
        
        # Detect follow-up type
        followup_type = self.detect_follow_up_type(query, context)
        print(f"🔍 Query Type: {followup_type.replace('_', ' ').title()}")
        
        # Show conversation context
        if context['patient_info']:
            print(f"👤 Patient Profile: {context['patient_info']}")
        
        if self.conversation_history:
            print(f"💭 Previous Questions: {len(self.conversation_history)}")
        
        # Create contextual query
        contextual_query = self.create_contextual_query(query, context)
        
        # For follow-up questions, also search using the original query
        search_queries = [query]
        if followup_type in ['reference_followup', 'clarification', 'additional_info']:
            # Add context-enhanced query
            search_queries.append(contextual_query)
            # Also search with patient context
            if context['patient_info']:
                patient_context_query = f"{query} " + " ".join([f"{k} {v}" for k, v in context['patient_info'].items()])
                search_queries.append(patient_context_query)
        
        # Search for relevant information
        all_relevant_chunks = []
        unique_chunks = set()
        
        for search_query in search_queries:
            embed_result = await self.embedder.generate_embeddings([search_query])
            
            if embed_result.get('success'):
                query_embedding = embed_result.get('embeddings', [])[0]
                search_results = self.vector_store.similarity_search(query_embedding, k=5)
                
                for result in search_results:
                    text = result.get('text', '')
                    score = result.get('score', 0)
                    text_id = text[:100]
                    
                    if text_id not in unique_chunks and score > 0.3:
                        unique_chunks.add(text_id)
                        all_relevant_chunks.append({'text': text, 'score': score})
        
        # Sort and select top chunks
        all_relevant_chunks.sort(key=lambda x: x['score'], reverse=True)
        top_chunks = all_relevant_chunks[:8]
        
        print(f"✅ Found {len(top_chunks)} relevant chunks")
        
        if not top_chunks:
            return {'success': False, 'error': 'No relevant information found'}
        
        # Create context with conversation history
        context_sections = []
        for chunk in top_chunks:
            context_sections.append(f"[Relevance: {chunk['score']:.3f}]\n{chunk['text']}")
        
        combined_context = "\n\n".join(context_sections)
        
        # Generate answer with conversation context
        print("🤖 Generating contextual response...")
        answer_result = await get_gemini_answer_async(
            user_question=contextual_query,
            relevant_clauses=combined_context,
            api_key=self.api_key,
            model="gemini-2.0-flash-exp",
            max_tokens=1000,
            temperature=0.3
        )
        
        if answer_result.get('success'):
            answer = answer_result.get('answer', '')
            rationale = answer_result.get('rationale', '')
            
            # Store in conversation history
            conversation_entry = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'contextual_query': contextual_query,
                'followup_type': followup_type,
                'answer': answer,
                'rationale': rationale,
                'context_used': context
            }
            
            self.conversation_history.append(conversation_entry)
            
            return {
                'success': True,
                'answer': answer,
                'rationale': rationale,
                'followup_type': followup_type,
                'context_used': context,
                'conversation_length': len(self.conversation_history)
            }
        else:
            return {'success': False, 'error': 'Failed to generate answer'}
    
    def show_conversation_summary(self):
        """Display conversation summary"""
        print("\n📊 CONVERSATION SUMMARY")
        print("=" * 50)
        print(f"Total Questions Asked: {len(self.conversation_history)}")
        
        if self.conversation_history:
            print(f"Session Duration: {len(self.conversation_history)} exchanges")
            
            # Extract patient profile from entire conversation
            context = self.extract_context_from_history()
            if context['patient_info']:
                print(f"Patient Profile: {context['patient_info']}")
            
            print("\nConversation Flow:")
            for i, entry in enumerate(self.conversation_history, 1):
                print(f"  {i}. [{entry['followup_type']}] {entry['query'][:80]}...")

async def main():
    """Interactive conversational Q&A session"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return
    
    qa_system = ConversationalQA(api_key)
    
    print("🚀 CONVERSATIONAL AI Q&A SYSTEM")
    print("💡 Now with conversation memory and context awareness!")
    print("💡 Ask follow-up questions - I'll remember our conversation")
    print("💡 Type 'summary' to see conversation history")
    print("💡 Type 'quit' to exit")
    print("=" * 60)
    
    while True:
        try:
            query = input("\n❓ Your question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                qa_system.show_conversation_summary()
                print("👋 Goodbye!")
                break
            
            if query.lower() == 'summary':
                qa_system.show_conversation_summary()
                continue
            
            if not query:
                print("Please enter a question!")
                continue
            
            result = await qa_system.ask_with_context(query)
            
            if result['success']:
                print(f"\n🎯 AI RESPONSE:")
                print("=" * 60)
                print(result['answer'])
                print(f"\n📋 CONTEXT INFO:")
                print(f"   Follow-up Type: {result['followup_type']}")
                print(f"   Conversation Length: {result['conversation_length']} exchanges")
                print("=" * 60)
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
        except KeyboardInterrupt:
            qa_system.show_conversation_summary()
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
