#!/usr/bin/env python3
"""Enhanced AI Q&A system for insurance claim analysis"""

import os
import sys
import asyncio
import re
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from robust_document_parser import parse_document
from gemini_vector_embedder import GeminiVectorEmbedder, embed_document_chunks
from faiss_store import FAISSVectorStore
from gemini_answer import get_gemini_answer_async

load_dotenv()

class InsuranceClaimAnalyzer:
    """Enhanced AI system for insurance claim eligibility analysis"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.vector_store = None
        self.embedder = GeminiVectorEmbedder(api_key=api_key)
        
        # Insurance-specific keywords for better search
        self.medical_procedures = [
            'cataract surgery', 'bypass surgery', 'angioplasty', 'dialysis',
            'chemotherapy', 'radiotherapy', 'appendectomy', 'gallbladder',
            'knee replacement', 'hip replacement', 'cardiac surgery'
        ]
        
        self.claim_keywords = [
            'coverage', 'eligible', 'payout', 'deductible', 'copay',
            'waiting period', 'exclusion', 'pre-existing', 'limit', 'benefit'
        ]
    
    def extract_claim_details(self, query: str) -> Dict[str, Any]:
        """Extract structured information from claim query"""
        details = {
            'age': None,
            'gender': None,
            'procedure': None,
            'location': None,
            'policy_duration': None,
            'query_type': 'claim_eligibility'
        }
        
        # Extract age
        age_match = re.search(r'aged?\s*(\d+)', query.lower())
        if age_match:
            details['age'] = int(age_match.group(1))
        
        # Extract gender
        if 'female' in query.lower():
            details['gender'] = 'female'
        elif 'male' in query.lower():
            details['gender'] = 'male'
        
        # Extract medical procedures
        query_lower = query.lower()
        for procedure in self.medical_procedures:
            if procedure in query_lower:
                details['procedure'] = procedure
                break
        
        # Extract policy duration
        duration_match = re.search(r'policy.*?active.*?(\d+)\s*(month|year)', query.lower())
        if duration_match:
            duration = int(duration_match.group(1))
            unit = duration_match.group(2)
            details['policy_duration'] = f"{duration} {unit}{'s' if duration > 1 else ''}"
        
        # Extract location
        cities = ['chennai', 'mumbai', 'delhi', 'bangalore', 'hyderabad', 'kolkata']
        for city in cities:
            if city in query.lower():
                details['location'] = city.title()
                break
        
        return details
    
    async def initialize_document(self, pdf_path: str = 'bajaj.pdf'):
        """Initialize the vector store with insurance document"""
        print("🔄 Initializing insurance document database...")
        
        # Initialize vector store with correct dimensions
        self.vector_store = FAISSVectorStore(dimension=768)
        
        # Check if document is already processed
        if hasattr(self.vector_store, 'next_id') and self.vector_store.next_id > 0:
            print("✅ Using existing document index")
            return
        
        # Process the insurance document
        result = parse_document(
            pdf_path,
            min_chunk_tokens=100,
            max_chunk_tokens=2000,
            target_chunk_tokens=1000
        )
        
        chunks = result.get('chunks', [])
        if not chunks:
            raise ValueError("No chunks found in document")
        
        print(f"✅ Processed document: {len(chunks)} chunks")
        
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
            
            doc_id = self.vector_store.add_document_embeddings(
                embeddings=embeddings,
                file_path=pdf_path,
                file_type=".pdf",
                chunk_texts=chunk_texts
            )
            print(f"✅ Document indexed with ID: {doc_id}")
        else:
            raise ValueError("Failed to generate embeddings")
    
    def create_enhanced_search_queries(self, original_query: str, claim_details: Dict) -> List[str]:
        """Generate multiple search queries for comprehensive coverage analysis"""
        
        queries = [original_query]  # Always include original
        
        # Add procedure-specific queries
        if claim_details.get('procedure'):
            procedure = claim_details['procedure']
            queries.extend([
                f"{procedure} coverage eligibility requirements",
                f"{procedure} waiting period exclusions",
                f"{procedure} maximum payout limits",
                f"{procedure} age restrictions coverage"
            ])
        
        # Add age-specific queries
        if claim_details.get('age'):
            age = claim_details['age']
            queries.extend([
                f"age limit {age} years coverage eligibility",
                f"senior citizen coverage age {age}",
                f"age restrictions insurance policy {age}"
            ])
        
        # Add policy duration queries
        if claim_details.get('policy_duration'):
            duration = claim_details['policy_duration']
            queries.extend([
                f"waiting period {duration} policy coverage",
                f"pre-existing condition {duration} policy",
                f"coverage after {duration} policy active"
            ])
        
        # Add general eligibility queries
        queries.extend([
            "claim eligibility criteria requirements",
            "coverage exclusions limitations",
            "payout calculation method formula",
            "deductible copay amount limits"
        ])
        
        return queries[:8]  # Limit to avoid overwhelming
    
    async def analyze_claim(self, query: str) -> Dict[str, Any]:
        """Comprehensive insurance claim analysis"""
        
        print(f"🔍 INSURANCE CLAIM ANALYSIS")
        print("=" * 60)
        print(f"📝 Query: {query}")
        print("-" * 60)
        
        # Extract structured details
        claim_details = self.extract_claim_details(query)
        print(f"📊 Extracted Details:")
        for key, value in claim_details.items():
            if value:
                print(f"   {key.title()}: {value}")
        
        # Initialize document if needed
        if not self.vector_store:
            await self.initialize_document()
        
        # Generate enhanced search queries
        search_queries = self.create_enhanced_search_queries(query, claim_details)
        print(f"\n🔍 Generated {len(search_queries)} targeted search queries")
        
        # Search for relevant information
        all_relevant_chunks = []
        unique_chunks = set()  # Avoid duplicates
        
        for search_query in search_queries:
            # Generate query embedding
            embed_result = await self.embedder.generate_embeddings([search_query])
            
            if embed_result.get('success'):
                query_embedding = embed_result.get('embeddings', [])[0]
                
                # Search for relevant chunks
                search_results = self.vector_store.similarity_search(
                    query_embedding=query_embedding,
                    k=3,  # Fewer per query to get diverse results
                    score_threshold=None
                )
                
                for result in search_results:
                    text = result.get('text', '')
                    score = result.get('score', 0)
                    
                    # Use first 100 chars as unique identifier
                    text_id = text[:100]
                    if text_id not in unique_chunks and score > 0.3:  # Relevance threshold
                        unique_chunks.add(text_id)
                        all_relevant_chunks.append({
                            'text': text,
                            'score': score,
                            'query': search_query
                        })
        
        # Sort by relevance score and take top results
        all_relevant_chunks.sort(key=lambda x: x['score'], reverse=True)
        top_chunks = all_relevant_chunks[:10]  # Top 10 most relevant
        
        print(f"✅ Found {len(top_chunks)} highly relevant policy sections")
        
        if not top_chunks:
            return {
                'success': False,
                'error': 'No relevant policy information found',
                'claim_details': claim_details
            }
        
        # Create comprehensive context
        context_sections = []
        for chunk in top_chunks:
            context_sections.append(
                f"[Relevance: {chunk['score']:.3f} | Query: {chunk['query'][:50]}...]\n{chunk['text']}"
            )
        
        combined_context = "\n\n" + "="*50 + "\n\n".join(context_sections)
        
        # Generate specialized prompt for insurance claim analysis
        specialized_prompt = f"""
You are an expert insurance claim analyst. Analyze this specific claim request:

CLAIM DETAILS:
- Patient: {claim_details.get('gender', 'N/A')}, age {claim_details.get('age', 'N/A')}
- Procedure: {claim_details.get('procedure', 'N/A')}
- Location: {claim_details.get('location', 'N/A')}
- Policy Duration: {claim_details.get('policy_duration', 'N/A')}

ORIGINAL QUERY: {query}

Based on the policy documents below, provide a comprehensive analysis covering:

1. ELIGIBILITY: Is this claim covered? (Yes/No/Partial with specific reasons)
2. WAITING PERIODS: Any waiting periods that apply?
3. AGE RESTRICTIONS: Age-related limitations or exclusions?
4. PAYOUT CALCULATION: How much would be paid? (percentage, limits, deductibles)
5. REQUIRED DOCUMENTS: What documentation is needed?
6. EXCLUSIONS: Any specific exclusions that apply?
7. NEXT STEPS: What should the patient do to proceed?

Provide specific amounts, percentages, and timeframes where mentioned in the policy.
Be thorough but clear, and always reference the relevant policy sections.
"""
        
        # Generate AI analysis
        print("🤖 Generating comprehensive claim analysis...")
        answer_result = await get_gemini_answer_async(
            user_question=specialized_prompt,
            relevant_clauses=combined_context,
            api_key=self.api_key,
            model="gemini-2.0-flash-exp",
            max_tokens=1200,  # Longer for comprehensive analysis
            temperature=0.2   # Lower for more precise analysis
        )
        
        if answer_result.get('success'):
            analysis = answer_result.get('answer', '')
            rationale = answer_result.get('rationale', '')
            
            return {
                'success': True,
                'claim_details': claim_details,
                'analysis': analysis,
                'rationale': rationale,
                'relevant_sections': len(top_chunks),
                'search_queries_used': len(search_queries)
            }
        else:
            return {
                'success': False,
                'error': 'Failed to generate analysis',
                'claim_details': claim_details
            }

async def main():
    """Test the enhanced insurance claim analyzer"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return
    
    analyzer = InsuranceClaimAnalyzer(api_key)
    
    # Test query
    test_query = "Patient is female, aged 55, underwent cataract surgery in Chennai, insurance policy active for 5 months - Is this claim covered, and what's the eligible payout?"
    
    try:
        result = await analyzer.analyze_claim(test_query)
        
        if result['success']:
            print("\n🎯 COMPREHENSIVE CLAIM ANALYSIS")
            print("=" * 60)
            print(result['analysis'])
            print("\n📋 ANALYSIS RATIONALE:")
            print("-" * 40)
            print(result['rationale'])
            print(f"\n📊 ANALYSIS STATS:")
            print(f"   Relevant sections found: {result['relevant_sections']}")
            print(f"   Search queries used: {result['search_queries_used']}")
            print("=" * 60)
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
