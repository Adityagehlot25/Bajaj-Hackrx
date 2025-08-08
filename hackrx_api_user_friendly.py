#!/usr/bin/env python3
"""
HackRX API Server - User-Friendly Version
Accepts both single question and multiple questions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any, Optional, Union
import asyncio
import aiohttp
import tempfile
import os
import sys
from pathlib import Path
import logging
from datetime import datetime
import traceback

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules with error handling
try:
    from robust_document_parser import parse_document
    from gemini_vector_embedder import GeminiVectorEmbedder
    from faiss_store import FAISSVectorStore
    from gemini_answer import get_gemini_answer_async
    from dotenv import load_dotenv
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Module import error: {e}")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HackRX Document Q&A API - User Friendly",
    description="Accepts both single question and multiple questions",
    version="1.2.0"
)

# Enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Pydantic models - Flexible request format
class HackRXRequest(BaseModel):
    document_url: HttpUrl
    # Accept either single question or multiple questions
    question: Optional[str] = None
    questions: Optional[List[str]] = None
    
    def get_questions_list(self) -> List[str]:
        """Convert single question or multiple questions to a list"""
        if self.questions:
            return self.questions
        elif self.question:
            return [self.question]
        else:
            raise ValueError("Either 'question' or 'questions' must be provided")

class HackRXResponse(BaseModel):
    # For single question, return simple answer string
    # For multiple questions, return list of answers
    answer: Optional[str] = None
    answers: Optional[List[str]] = None
    confidence: Optional[float] = None
    processing_time: Optional[str] = None
    processing_info: Optional[Dict[str, Any]] = None

class DocumentQAPipelineUserFriendly:
    """User-friendly version of the document Q&A processing pipeline"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.embedder = GeminiVectorEmbedder(api_key=self.api_key)
        self.vector_store = None
        logger.info(f"Pipeline initialized with API key: {self.api_key[:10]}...")
        
    async def download_document(self, url: str) -> str:
        """Download document with better error handling"""
        logger.info(f"Downloading document from: {url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(str(url)) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Failed to download document: HTTP {response.status}"
                        )
                    
                    # Determine file type
                    content_type = response.headers.get('content-type', '')
                    url_lower = str(url).lower()
                    
                    if 'pdf' in content_type.lower() or url_lower.endswith('.pdf'):
                        suffix = '.pdf'
                    elif 'word' in content_type.lower() or url_lower.endswith(('.docx', '.doc')):
                        suffix = '.docx'
                    else:
                        suffix = '.txt'
                    
                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                        content = await response.read()
                        tmp_file.write(content)
                        temp_path = tmp_file.name
                    
                    logger.info(f"Document downloaded to: {temp_path}")
                    return temp_path
                    
        except aiohttp.ClientError as e:
            logger.error(f"Download error: {e}")
            raise HTTPException(status_code=400, detail=f"Download failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected download error: {e}")
            raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")
    
    async def process_pipeline(self, document_url: str, questions: List[str]) -> Dict[str, Any]:
        """Process the complete document Q&A pipeline"""
        start_time = datetime.now()
        
        try:
            result = {
                "document_url": document_url,
                "total_questions": len(questions),
                "answers": [],
                "processing_steps": []
            }
            
            # Step 1: Download document
            logger.info("Step 1: Downloading document")
            temp_file_path = await self.download_document(document_url)
            result["processing_steps"].append("Document downloaded")
            
            try:
                # Step 2: Parse document
                logger.info("Step 2: Parsing document") 
                document_text = parse_document(temp_file_path)
                
                if not document_text or len(document_text.strip()) < 10:
                    raise ValueError("Document appears to be empty or unreadable")
                
                result["document_length"] = len(document_text)
                result["processing_steps"].append("Document parsed")
                logger.info(f"Document parsed: {len(document_text)} characters")
                
                # Step 3: Generate embeddings
                logger.info("Step 3: Generating embeddings")
                chunks = self.embedder.split_text(document_text)
                embeddings = await self.embedder.generate_embeddings_async(chunks)
                
                result["total_chunks"] = len(chunks)
                result["processing_steps"].append("Embeddings generated")
                logger.info(f"Generated {len(embeddings)} embeddings")
                
                # Step 4: Create vector store
                logger.info("Step 4: Creating vector store")
                self.vector_store = FAISSVectorStore(embedding_dim=768)
                
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    self.vector_store.add_document(f"doc_{i}", chunk, embedding)
                
                result["processing_steps"].append("Vector store created")
                logger.info("Vector store populated")
                
                # Step 5: Answer questions
                logger.info("Step 5: Answering questions")
                answers = []
                
                for i, question in enumerate(questions):
                    logger.info(f"Processing question {i+1}/{len(questions)}: {question[:50]}...")
                    
                    try:
                        # Generate query embedding
                        query_embedding = await self.embedder.generate_embedding_async(question)
                        
                        # Search relevant chunks
                        relevant_docs = self.vector_store.similarity_search(
                            query_embedding, 
                            top_k=5
                        )
                        
                        # Prepare context
                        context = "\n\n".join([doc["content"] for doc in relevant_docs])
                        
                        # Generate answer
                        answer = await get_gemini_answer_async(
                            context=context,
                            question=question,
                            api_key=self.api_key
                        )
                        
                        answers.append(answer)
                        logger.info(f"Question {i+1} answered: {len(answer)} characters")
                        
                    except Exception as e:
                        logger.error(f"Error answering question {i+1}: {e}")
                        answers.append(f"Sorry, I encountered an error answering this question: {str(e)}")
                
                result["answers"] = answers
                result["processing_steps"].append("Questions answered")
                
                # Calculate processing time
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                result["processing_time"] = f"{processing_time:.2f} seconds"
                
                logger.info(f"Pipeline completed successfully in {processing_time:.2f} seconds")
                return result
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    logger.info("Temporary file cleaned up")
                    
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Pipeline processing failed: {str(e)}"
            )

# Initialize pipeline
pipeline = DocumentQAPipelineUserFriendly()

@app.get("/api/v1/hackrx/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "HackRX Document Q&A API - User Friendly",
        "version": "1.2.0",
        "timestamp": datetime.now().isoformat(),
        "api_key_configured": bool(os.getenv('GEMINI_API_KEY'))
    }

@app.post("/api/v1/hackrx/run", response_model=HackRXResponse)
async def process_hackrx_request(request: HackRXRequest):
    """
    Process HackRX document Q&A request
    Accepts either single 'question' or multiple 'questions'
    """
    try:
        # Get questions list (handles both single and multiple)
        questions_list = request.get_questions_list()
        
        logger.info(f"Processing HackRX request: {len(questions_list)} questions for {request.document_url}")
        
        # Validate questions
        if len(questions_list) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 questions allowed")
        
        # Process pipeline
        result = await pipeline.process_pipeline(
            document_url=str(request.document_url),
            questions=questions_list
        )
        
        # Format response based on input format
        if request.question and not request.questions:
            # Single question - return simple response
            return HackRXResponse(
                answer=result["answers"][0] if result["answers"] else "No answer generated",
                confidence=0.85,  # Default confidence
                processing_time=result.get("processing_time", "Unknown"),
                processing_info=result
            )
        else:
            # Multiple questions - return array response
            return HackRXResponse(
                answers=result["answers"],
                processing_time=result.get("processing_time", "Unknown"),
                processing_info=result
            )
            
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Request processing error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "HackRX Document Q&A API - User Friendly Version",
        "version": "1.2.0",
        "endpoints": {
            "health": "/api/v1/hackrx/health",
            "process": "/api/v1/hackrx/run",
            "docs": "/docs"
        },
        "example_request": {
            "single_question": {
                "document_url": "https://example.com/document.pdf",
                "question": "What is this document about?"
            },
            "multiple_questions": {
                "document_url": "https://example.com/document.pdf",
                "questions": ["What is this about?", "Who is the author?"]
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting HackRX API Server - User Friendly Version")
    print("📍 Single Question API: http://localhost:8000/api/v1/hackrx/run")
    print("📊 Health Check: http://localhost:8000/api/v1/hackrx/health")
    print("📚 Swagger Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
