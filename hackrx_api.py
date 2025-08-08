#!/usr/bin/env python3
"""
HackRX Document Q&A API - Production Version

A comprehensive FastAPI service that processes documents and answers questions using:
- Document parsing and chunking
- Gemini AI embeddings and text generation
- FAISS vector similarity search
- Async/await for high performance

Author: Aditya Gehlot
Version: 1.1.0
Created for: Bajaj HackRX Competition
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl, Field
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

# Import our custom modules
from robust_document_parser import RobustDocumentParser
from gemini_vector_embedder import GeminiVectorEmbedder
from faiss_store import FAISSVectorStore
from gemini_answer import get_gemini_answer_async
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize authentication
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify Bearer token authentication
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        Token string if valid
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials
    
    # Simple token validation - require minimum 10 characters
    if not token or len(token) < 10:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return token

# Initialize FastAPI app with comprehensive metadata
app = FastAPI(
    title="HackRX Document Q&A API",
    description="""
    **Bajaj HackRX Competition API**
    
    A production-ready document processing and question-answering service that:
    
    - **Downloads** documents from URLs (PDF, DOCX supported)
    - **Parses** and chunks documents intelligently  
    - **Generates** embeddings using Gemini AI
    - **Indexes** content with FAISS vector search
    - **Answers** questions using retrieved context and Gemini 1.5 Flash
    
    ## Authentication
    All endpoints require Bearer token authentication with minimum 10 characters.
    
    ## Rate Limits
    - Document processing: ~30 seconds per document
    - Question answering: ~2 seconds per question
    - Concurrent requests supported via async processing
    
    ## Supported Formats
    - PDF documents
    - Microsoft Word documents (DOCX)
    - URLs with direct file access
    """,
    version="1.1.0",
    contact={
        "name": "Aditya Gehlot",
        "url": "https://github.com/Adityagehlot25/Bajaj-Hackrx"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class HackRXRequest(BaseModel):
    """
    Request model for HackRX document Q&A endpoint
    
    Attributes:
        document_url: Direct URL to document file (PDF or DOCX)
        questions: List of questions to answer about the document
    """
    document_url: HttpUrl = Field(
        ...,
        description="Direct URL to document file (PDF or DOCX format)",
        example="https://example.com/document.pdf"
    )
    questions: List[str] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of questions to answer (1-10 questions)",
        example=["What is the main topic?", "What are the key requirements?"]
    )

class HackRXResponse(BaseModel):
    """
    Response model for HackRX document Q&A endpoint
    
    Attributes:
        answers: List of generated answers corresponding to input questions
        processing_info: Optional metadata about processing performance
    """
    answers: List[str] = Field(
        ...,
        description="Generated answers for each question in order",
        example=["The main topic is...", "The key requirements are..."]
    )
    processing_info: Optional[Dict[str, Any]] = Field(
        None,
        description="Processing metadata including timing and chunk counts"
    )

class DocumentQAPipeline:
    """
    Complete document Q&A processing pipeline for HackRX API
    
    This class orchestrates the entire workflow:
    1. Document download and parsing
    2. Text chunking and embedding generation
    3. Vector indexing with FAISS
    4. Question answering with retrieval augmented generation
    
    Attributes:
        api_key: Gemini API key for embeddings and text generation
        parser: Document parsing engine
        embedder: Gemini embedding generator
        vector_store: FAISS vector search index
    """
    
    def __init__(self):
        """Initialize the document Q&A pipeline with required components"""
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
            
        Raises:
            HTTPException: If download fails
        """        
        async with aiohttp.ClientSession() as session:
            async with session.get(str(url)) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to download document: HTTP {response.status}"
                    )
                
                # Determine file extension from URL or content type
                content_type = response.headers.get('content-type', '')
                if 'pdf' in content_type.lower() or str(url).lower().endswith('.pdf'):
                    suffix = '.pdf'
                elif 'word' in content_type.lower() or str(url).lower().endswith(('.docx', '.doc')):
                    suffix = '.docx'
                else:
                    suffix = '.pdf'  # Default to PDF
                
                # Create temporary file and download content
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                content = await response.read()
                temp_file.write(content)
                temp_file.close()
                
                return temp_file.name
    
    def parse_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse document into text chunks for processing
        
        Args:
            file_path: Path to document file
            
        Returns:
            List of text chunks with metadata
            
        Raises:
            HTTPException: If parsing fails
        """        
        try:
            # Parse document using robust parser
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
async def hackrx_run(request: HackRXRequest, token: str = Depends(verify_token)):
    """
    **HackRX Main Endpoint - Document Q&A Processing**
    
    Complete workflow for document processing and question answering:
    
    1. **Download**: Retrieves document from provided URL
    2. **Parse**: Extracts and chunks text content  
    3. **Embed**: Generates vector embeddings using Gemini
    4. **Index**: Creates searchable FAISS vector index
    5. **Query**: For each question, finds relevant chunks and generates answers
    
    **Authentication**: Requires Bearer token with minimum 10 characters
    
    **Processing Time**: 
    - Document processing: ~20-30 seconds
    - Question answering: ~2-3 seconds per question
    
    **Supported Formats**: PDF, DOCX
    **Question Limit**: 1-10 questions per request
    **Response Format**: JSON with answers array
    
    Args:
        request: HackRXRequest with document URL and questions
        token: Bearer authentication token
        
    Returns:
        HackRXResponse with generated answers
        
    Raises:
        HTTPException: For authentication, download, or processing errors
    """
    try:
        logger.info(f"Processing request: {len(request.questions)} questions")
        
        # Execute the complete pipeline
        result = await pipeline.process_pipeline(
            document_url=str(request.document_url),
            questions=request.questions
        )
        
        # Return structured response (processing_info optional for production)
        return HackRXResponse(
            answers=result["answers"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in HackRX pipeline: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during document processing"
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
    
    # Production server configuration
    uvicorn.run(
        "hackrx_api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload in production
        log_level="info"
    )
