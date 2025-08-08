#!/usr/bin/env python3
"""
HackRX API Endpoint - Full Document Q&A Pipeline
FastAPI implementation with complete document processing and Q&A workflow
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
import tempfile
import os
import sys
from pathlib import Path
import logging
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from robust_document_parser import RobustDocumentParser
from gemini_vector_embedder import GeminiVectorEmbedder
from faiss_store import FAISSVectorStore
from gemini_answer import get_gemini_answer_async
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HackRX Document Q&A API (Fixed Version)",
    description="Full pipeline for document processing and question answering using Gemini 1.5 Flash",
    version="1.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class HackRXRequest(BaseModel):
    """Request model for HackRX API endpoint"""
    document_url: HttpUrl
    questions: List[str]

class HackRXResponse(BaseModel):
    """Response model for HackRX API endpoint"""
    answers: List[str]
    processing_info: Optional[Dict[str, Any]] = None

class DocumentQAPipeline:
    """Complete document Q&A processing pipeline"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyBH6ls3I80rOI3il-uX-7p8eUTSoox05cc')
        if not self.api_key or self.api_key == 'your_gemini_api_key_here':
            self.api_key = 'AIzaSyBH6ls3I80rOI3il-uX-7p8eUTSoox05cc'
        
        self.parser = RobustDocumentParser()
        self.embedder = GeminiVectorEmbedder(api_key=self.api_key)
        self.vector_store = None
        
    async def download_document(self, url: str) -> str:
        """
        Download document from URL to temporary file
        
        Args:
            url: Document URL to download
            
        Returns:
            Path to downloaded temporary file
        """
        logger.info(f"Downloading document from: {url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(str(url)) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to download document: HTTP {response.status}"
                    )
                
                # Get file extension from URL or content type
                content_type = response.headers.get('content-type', '')
                if 'pdf' in content_type.lower() or str(url).lower().endswith('.pdf'):
                    suffix = '.pdf'
                elif 'word' in content_type.lower() or str(url).lower().endswith(('.docx', '.doc')):
                    suffix = '.docx'
                else:
                    # Default to PDF if unclear
                    suffix = '.pdf'
                
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                
                # Download content
                content = await response.read()
                temp_file.write(content)
                temp_file.close()
                
                logger.info(f"Document downloaded to: {temp_file.name} ({len(content)} bytes)")
                return temp_file.name
    
    def parse_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse document into chunks
        
        Args:
            file_path: Path to document file
            
        Returns:
            List of text chunks with metadata
        """
        logger.info(f"Parsing document: {file_path}")
        
        try:
            # Parse document using our robust parser
            from robust_document_parser import parse_document
            
            parsed_result = parse_document(
                file_path=file_path,
                min_chunk_tokens=100,
                max_chunk_tokens=2000,
                target_chunk_tokens=1000
            )
            
            # Convert to expected format
            chunks = []
            if parsed_result.get('success') and parsed_result.get('chunks'):
                for i, chunk_text in enumerate(parsed_result['chunks']):
                    chunks.append({
                        'text': chunk_text,
                        'chunk_index': i,
                        'metadata': {
                            'source_file': file_path,
                            'chunk_id': i
                        }
                    })
            else:
                raise Exception(f"Document parsing failed: {parsed_result.get('error', 'Unknown error')}")
            
            logger.info(f"Document parsed into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Document parsing failed: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse document: {str(e)}"
            )
    
    async def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """
        Generate embeddings for all chunks
        
        Args:
            chunks: List of text chunks
            
        Returns:
            List of embedding vectors
        """
        logger.info(f"Generating embeddings for {len(chunks)} chunks")
        
        try:
            # Extract text from chunks
            chunk_texts = [chunk['text'] for chunk in chunks]
            
            # Generate embeddings using Gemini
            result = await self.embedder.generate_embeddings_async(
                chunk_texts,
                batch_size=10  # Process in batches to avoid rate limits
            )
            
            if not result.get('success'):
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate embeddings: {result.get('error')}"
                )
            
            embeddings = result['embeddings']
            logger.info(f"Generated {len(embeddings)} embeddings ({result.get('dimensions')}D)")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate embeddings: {str(e)}"
            )
    
    def index_embeddings(self, embeddings: List[List[float]], chunks: List[Dict[str, Any]]) -> str:
        """
        Index embeddings using FAISS vector store
        
        Args:
            embeddings: List of embedding vectors
            chunks: List of text chunks with metadata
            
        Returns:
            Document ID for the indexed document
        """
        logger.info(f"Indexing {len(embeddings)} embeddings in FAISS")
        
        try:
            # Initialize vector store with correct dimensions
            embedding_dim = len(embeddings[0]) if embeddings else 768
            self.vector_store = FAISSVectorStore(dimension=embedding_dim)
            
            # Prepare chunk texts
            chunk_texts = [chunk['text'] for chunk in chunks]
            
            # Add embeddings to vector store
            doc_id = self.vector_store.add_document_embeddings(
                embeddings=embeddings,
                file_path="hackrx_document",
                file_type="pdf",
                chunk_texts=chunk_texts
            )
            
            logger.info(f"Embeddings indexed with document ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Embedding indexing failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to index embeddings: {str(e)}"
            )
    
    async def answer_question(self, question: str) -> str:
        """
        Answer a single question using the indexed document
        
        Args:
            question: User question
            
        Returns:
            Generated answer
        """
        try:
            # Generate query embedding
            query_result = await self.embedder.generate_embeddings_async([question])
            
            if not query_result.get('success'):
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate query embedding: {query_result.get('error')}"
                )
            
            query_embedding = query_result['embeddings'][0]
            
            # Retrieve relevant chunks via similarity search
            search_results = self.vector_store.similarity_search(
                query_embedding=query_embedding,
                k=5,  # Get top 5 most relevant chunks
                score_threshold=1.5  # Adjust threshold as needed
            )
            
            if not search_results:
                return "I couldn't find relevant information in the document to answer this question."
            
            # Compose context from retrieved chunks
            context_chunks = []
            for result in search_results:
                chunk_text = result.get('text', '')
                score = result.get('score', 0)
                context_chunks.append(f"[Relevance: {score:.3f}] {chunk_text}")
            
            relevant_context = "\n\n".join(context_chunks)
            
            # Generate answer using Gemini 1.5 Flash
            answer_result = await get_gemini_answer_async(
                user_question=question,
                relevant_clauses=relevant_context,
                model="gemini-1.5-flash",
                max_tokens=1000,
                temperature=0.3
            )
            
            if not answer_result.get('success'):
                logger.error(f"Failed to generate answer: {answer_result.get('error')}")
                return f"I encountered an error while generating the answer: {answer_result.get('error')}"
            
            # Extract answer from structured response
            answer = answer_result.get('answer', '')
            
            # If answer is too long, truncate it
            if len(answer) > 2000:
                answer = answer[:1997] + "..."
            
            return answer
            
        except Exception as e:
            logger.error(f"Question answering failed for '{question}': {e}")
            return f"I encountered an error while processing this question: {str(e)}"
    
    async def process_pipeline(self, document_url: str, questions: List[str]) -> Dict[str, Any]:
        """
        Execute the complete document Q&A pipeline
        
        Args:
            document_url: URL of document to process
            questions: List of questions to answer
            
        Returns:
            Dictionary with answers and processing info
        """
        start_time = datetime.now()
        processing_info = {
            "document_url": document_url,
            "total_questions": len(questions),
            "processing_started": start_time.isoformat()
        }
        
        try:
            # Step 1: Download document
            temp_file_path = await self.download_document(document_url)
            processing_info["download_completed"] = True
            
            try:
                # Step 2: Parse document into chunks
                chunks = self.parse_document(temp_file_path)
                processing_info["chunks_created"] = len(chunks)
                
                # Step 3: Generate embeddings for all chunks
                embeddings = await self.generate_embeddings(chunks)
                processing_info["embeddings_generated"] = len(embeddings)
                
                # Step 4: Index embeddings using FAISS
                doc_id = self.index_embeddings(embeddings, chunks)
                processing_info["document_indexed"] = doc_id
                
                # Step 5: Answer all questions
                answers = []
                for i, question in enumerate(questions):
                    logger.info(f"Processing question {i+1}/{len(questions)}: {question[:50]}...")
                    answer = await self.answer_question(question)
                    answers.append(answer)
                
                processing_info["answers_generated"] = len(answers)
                processing_info["processing_completed"] = datetime.now().isoformat()
                processing_info["total_time_seconds"] = (datetime.now() - start_time).total_seconds()
                
                return {
                    "answers": answers,
                    "processing_info": processing_info
                }
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                    logger.info(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file: {e}")
        
        except Exception as e:
            processing_info["error"] = str(e)
            processing_info["processing_failed"] = datetime.now().isoformat()
            raise e

# Global pipeline instance
pipeline = DocumentQAPipeline()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "HackRX Document Q&A API (Fixed Version)",
        "version": "1.1.0",
        "status": "operational",
        "api_key_status": "configured",
        "endpoints": {
            "main": "/api/v1/hackrx/run",
            "health": "/api/v1/hackrx/health",
            "docs": "/docs"
        },
        "cors": "enabled"
    }

@app.post("/api/v1/hackrx/run", response_model=HackRXResponse)
async def hackrx_run(request: HackRXRequest):
    """
    HackRX API endpoint - Full document Q&A pipeline
    
    This endpoint implements the complete workflow:
    1. Downloads document from provided URL
    2. Parses and chunks the document
    3. Generates embeddings using Gemini API
    4. Indexes embeddings using FAISS
    5. For each question:
       - Generates query embedding
       - Retrieves relevant chunks via similarity search
       - Composes LLM prompt with question and context
       - Calls Gemini 2.0 Flash to generate answer
    6. Returns all answers in JSON response
    """
    try:
        logger.info(f"Processing HackRX request: {len(request.questions)} questions for {request.document_url}")
        
        # Execute the complete pipeline
        result = await pipeline.process_pipeline(
            document_url=str(request.document_url),
            questions=request.questions
        )
        
        # Return structured response
        return HackRXResponse(
            answers=result["answers"],
            processing_info=result["processing_info"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in HackRX pipeline: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/v1/hackrx/health")
async def health_check():
    """Detailed health check for HackRX endpoint"""
    try:
        # Check if API key is available
        api_key_status = "configured" if os.getenv('GEMINI_API_KEY') else "missing"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "api_key_status": api_key_status,
            "components": {
                "document_parser": "ready",
                "gemini_embedder": "ready",
                "faiss_vector_store": "ready",
                "gemini_answer_engine": "ready"
            },
            "endpoints": {
                "/api/v1/hackrx/run": "operational"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    print("🚀 Starting HackRX Document Q&A API Server")
    print("📄 Full pipeline: Download → Parse → Embed → Index → Answer")
    print("🤖 Powered by Gemini 2.0 Flash")
    print("🔍 FAISS vector search")
    print()
    print("📍 API Endpoint: http://localhost:8000/api/v1/hackrx/run")
    print("📊 Health Check: http://localhost:8000/api/v1/hackrx/health")
    print("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "hackrx_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
