#!/usr/bin/env python3
"""
HackRX API Server Fix
Addresses CORS, file path, and connection issues
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl, ValidationError
from typing import List, Dict, Any, Optional
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

# Initialize FastAPI app with enhanced CORS
app = FastAPI(
    title="HackRX Document Q&A API (Fixed)",
    description="Fixed version with enhanced CORS and error handling",
    version="1.1.0"
)

# Security scheme for authorization
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify authorization token (optional - add your own logic)
    For now, we'll just check if a token is provided
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=401, 
            detail="Authorization token required"
        )
    
    # Add your token validation logic here
    # For example: validate against database, JWT validation, etc.
    token = credentials.credentials
    
    # Simple validation - you can replace with your own logic
    if len(token) < 10:  # Basic validation
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization token"
        )
    
    return token

# Enhanced CORS middleware - more permissive for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]  # Expose all headers
)

# Pydantic models
class HackRXRequest(BaseModel):
    document_url: HttpUrl
    questions: List[str]

class HackRXResponse(BaseModel):
    answers: List[str]

class DocumentQAPipelineFixed:
    """Fixed version of the document Q&A processing pipeline"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.embedder = GeminiVectorEmbedder(api_key=self.api_key)
        self.vector_store = None
        logger.info(f"Pipeline initialized with API key: {self.api_key[:10]}...")
        
    async def download_document(self, url: str) -> str:
        """Download document with comprehensive error handling"""
        logger.info(f"Downloading document from: {url}")
        
        try:
            # Validate URL format
            if not url or not url.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Document download error: URL cannot be empty"
                )
            
            url = url.strip()
            if not url.startswith(('http://', 'https://')):
                raise HTTPException(
                    status_code=400,
                    detail="Document download error: URL must be HTTP or HTTPS"
                )
            
            # Set timeout and connection limits
            timeout = aiohttp.ClientTimeout(total=60)  # 60 second timeout
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:
                    async with session.get(url) as response:
                        # Check for various HTTP error conditions
                        if response.status == 404:
                            raise HTTPException(
                                status_code=400,
                                detail="Document download error: Document not found (404)"
                            )
                        elif response.status == 403:
                            raise HTTPException(
                                status_code=400,
                                detail="Document download error: Access forbidden (403)"
                            )
                        elif response.status == 401:
                            raise HTTPException(
                                status_code=400,
                                detail="Document download error: Authentication required (401)"
                            )
                        elif response.status >= 500:
                            raise HTTPException(
                                status_code=500,
                                detail=f"Document download error: Server error ({response.status})"
                            )
                        elif response.status != 200:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Document download error: HTTP {response.status}"
                            )
                        
                        # Check content length
                        content_length = response.headers.get('content-length')
                        if content_length:
                            size_mb = int(content_length) / (1024 * 1024)
                            if size_mb > 50:  # 50MB limit
                                raise HTTPException(
                                    status_code=400,
                                    detail=f"Document download error: File too large ({size_mb:.1f}MB, max 50MB)"
                                )
                        
                        # Determine file type
                        content_type = response.headers.get('content-type', '').lower()
                        url_lower = url.lower()
                        
                        if 'pdf' in content_type or url_lower.endswith('.pdf'):
                            suffix = '.pdf'
                        elif 'word' in content_type or 'officedocument' in content_type or url_lower.endswith(('.docx', '.doc')):
                            suffix = '.docx'
                        elif 'text' in content_type or url_lower.endswith('.txt'):
                            suffix = '.txt'
                        else:
                            # Try to detect from content
                            suffix = '.pdf'  # Default assumption
                        
                        # Download content
                        try:
                            content = await response.read()
                            
                            if not content:
                                raise HTTPException(
                                    status_code=400,
                                    detail="Document download error: Downloaded file is empty"
                                )
                            
                            # Validate minimum file size (at least 100 bytes)
                            if len(content) < 100:
                                raise HTTPException(
                                    status_code=400,
                                    detail="Document download error: File too small to be a valid document"
                                )
                            
                        except aiohttp.ClientPayloadError as e:
                            raise HTTPException(
                                status_code=500,
                                detail=f"Document download error: Payload error - {str(e)}"
                            )
                            
                except aiohttp.ClientConnectorError as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Document download error: Connection failed - {str(e)}"
                    )
                except aiohttp.ServerTimeoutError:
                    raise HTTPException(
                        status_code=500,
                        detail="Document download error: Server timeout (60s)"
                    )
                except aiohttp.ClientError as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Document download error: Network error - {str(e)}"
                    )
            
            # Create temporary file in current directory for better access
            try:
                temp_dir = os.getcwd()
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, 
                    suffix=suffix, 
                    dir=temp_dir
                )
                
                temp_file.write(content)
                temp_file.close()
                
                # Verify file exists and is readable
                if not os.path.exists(temp_file.name):
                    raise HTTPException(
                        status_code=500,
                        detail="Document download error: Failed to create temporary file"
                    )
                
                file_size = os.path.getsize(temp_file.name)
                if file_size == 0:
                    # Clean up empty file
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
                    raise HTTPException(
                        status_code=400,
                        detail="Document download error: Downloaded file is empty"
                    )
                
                logger.info(f"Document downloaded: {temp_file.name} ({file_size} bytes)")
                return temp_file.name
                
            except HTTPException:
                raise
            except OSError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Document download error: File system error - {str(e)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Document download error: Unexpected error creating file - {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Document download failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Document download error: {str(e)}"
            )
    
    def parse_document_fixed(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse document with comprehensive error handling"""
        logger.info(f"Parsing document: {file_path}")
        
        try:
            # File validation
            if not file_path or not file_path.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Document parsing error: Invalid file path"
                )
            
            if not os.path.exists(file_path):
                raise HTTPException(
                    status_code=400,
                    detail="Document parsing error: File not found"
                )
            
            # Check file size
            try:
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    raise HTTPException(
                        status_code=400,
                        detail="Document parsing error: File is empty"
                    )
                if file_size > 100 * 1024 * 1024:  # 100MB limit
                    raise HTTPException(
                        status_code=400,
                        detail=f"Document parsing error: File too large ({file_size / (1024*1024):.1f}MB, max 100MB)"
                    )
            except OSError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Document parsing error: Cannot access file - {str(e)}"
                )
            
            logger.info(f"Parsing file: {file_path} ({file_size} bytes)")
            
            # Parse document with error handling
            try:
                result = parse_document(
                    file_path=file_path,
                    min_chunk_tokens=100,
                    max_chunk_tokens=2000,
                    target_chunk_tokens=1000
                )
            except FileNotFoundError:
                raise HTTPException(
                    status_code=400,
                    detail="Document parsing error: File not found during parsing"
                )
            except PermissionError:
                raise HTTPException(
                    status_code=500,
                    detail="Document parsing error: Permission denied accessing file"
                )
            except Exception as e:
                error_msg = str(e).lower()
                if 'corrupted' in error_msg or 'invalid' in error_msg:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Document parsing error: File appears to be corrupted or invalid - {str(e)}"
                    )
                elif 'password' in error_msg or 'encrypted' in error_msg:
                    raise HTTPException(
                        status_code=400,
                        detail="Document parsing error: Document is password protected or encrypted"
                    )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Document parsing error: {str(e)}"
                    )
            
            # Validate parsing result
            if not result:
                raise HTTPException(
                    status_code=500,
                    detail="Document parsing error: Parser returned no result"
                )
            
            if not isinstance(result, dict):
                raise HTTPException(
                    status_code=500,
                    detail="Document parsing error: Invalid parser result format"
                )
            
            if not result.get('chunks'):
                raise HTTPException(
                    status_code=400,
                    detail="Document parsing error: No text content could be extracted from document"
                )
            
            # Convert to expected format with error handling
            try:
                chunks = []
                raw_chunks = result.get('chunks', [])
                
                if not raw_chunks:
                    raise HTTPException(
                        status_code=400,
                        detail="Document parsing error: No chunks found in parsing result"
                    )
                
                for i, chunk_data in enumerate(raw_chunks):
                    try:
                        # Extract text from chunk data - handle both 'text' and 'content' fields
                        chunk_text = ""
                        if isinstance(chunk_data, dict):
                            # Try 'text' first (from TextChunk.to_dict()), then 'content' as fallback
                            chunk_text = chunk_data.get('text', chunk_data.get('content', ''))
                        else:
                            chunk_text = str(chunk_data)
                        
                        if not chunk_text or not chunk_text.strip():
                            logger.warning(f"Chunk {i+1} is empty, skipping")
                            continue
                        
                        logger.info(f"Chunk {i+1}: extracted {len(chunk_text)} characters from chunk_data keys: {list(chunk_data.keys()) if isinstance(chunk_data, dict) else 'not dict'}")
                        
                        chunks.append({
                            'text': chunk_text,
                            'chunk_index': i,
                            'metadata': {
                                'source_file': file_path,
                                'chunk_id': i,
                                'char_count': len(chunk_text)
                            }
                        })
                        
                    except Exception as e:
                        logger.error(f"Error processing chunk {i+1}: {str(e)}")
                        # Continue with other chunks instead of failing completely
                        continue
                
                if not chunks:
                    raise HTTPException(
                        status_code=400,
                        detail="Document parsing error: No valid text chunks could be extracted"
                    )
                
                logger.info(f"Successfully parsed document into {len(chunks)} chunks")
                return chunks
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Document parsing error: Chunk processing failed - {str(e)}"
                )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Document parsing failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Document parsing error: {str(e)}"
            )

    async def process_pipeline(self, document_url: str, questions: List[str]) -> Dict[str, Any]:
        """Execute the complete pipeline with comprehensive error handling"""
        start_time = datetime.now()
        temp_file_path = None
        
        processing_info = {
            "document_url": document_url,
            "total_questions": len(questions),
            "processing_started": start_time.isoformat()
        }
        
        try:
            # Step 1: Download document with error handling
            logger.info("Step 1: Downloading document")
            try:
                temp_file_path = await self.download_document(document_url)
                processing_info["download_completed"] = True
                processing_info["temp_file"] = temp_file_path
            except HTTPException:
                raise  # Re-raise HTTP exceptions from download_document
            except Exception as e:
                logger.error(f"Document download stage failed: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Document download failed: {str(e)}"
                )
            
            # Step 2: Parse document with error handling
            logger.info("Step 2: Parsing document")
            try:
                chunks = self.parse_document_fixed(temp_file_path)
                processing_info["chunks_created"] = len(chunks)
                if not chunks:
                    raise HTTPException(
                        status_code=400,
                        detail="Document parsing failed: No content extracted"
                    )
            except HTTPException:
                raise  # Re-raise HTTP exceptions from parse_document_fixed
            except Exception as e:
                logger.error(f"Document parsing stage failed: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Document parsing failed: {str(e)}"
                )
            
            # Step 3: Generate embeddings with error handling
            logger.info("Step 3: Generating embeddings")
            try:
                # Extract text from chunks
                chunk_texts = []
                
                for i, chunk in enumerate(chunks):
                    if isinstance(chunk, dict):
                        text = chunk.get('content', chunk.get('text', ''))
                        if text and text.strip():
                            chunk_texts.append(text)
                    else:
                        if chunk and str(chunk).strip():
                            chunk_texts.append(str(chunk))
                
                logger.info(f"Extracted {len(chunk_texts)} text chunks from {len(chunks)} parsed chunks")
                
                if not chunk_texts:
                    raise HTTPException(
                        status_code=400,
                        detail="Embedding generation failed: No text content to embed"
                    )
                
                # Generate embeddings
                result = await self.embedder.generate_embeddings(
                    chunk_texts,
                    batch_size=5  # Smaller batches to avoid rate limits
                )
                
                if not result.get('success'):
                    error_msg = result.get('error', 'Unknown embedding error')
                    if 'api key' in error_msg.lower() or 'unauthorized' in error_msg.lower():
                        raise HTTPException(
                            status_code=500,
                            detail="Embedding API error: Invalid or missing API key"
                        )
                    elif 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower():
                        raise HTTPException(
                            status_code=500,
                            detail="Embedding API error: Rate limit or quota exceeded"
                        )
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Embedding generation failed: {error_msg}"
                        )
                
                embeddings = result['embeddings']
                processing_info["embeddings_generated"] = len(embeddings)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Embedding generation stage failed: {str(e)}")
                if 'timeout' in str(e).lower():
                    raise HTTPException(
                        status_code=500,
                        detail="Embedding generation failed: API timeout"
                    )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Embedding generation failed: {str(e)}"
                    )
            
            # Step 4: Index embeddings with error handling
            logger.info("Step 4: Indexing embeddings")
            try:
                # Get processed chunks that match the embeddings
                processed_chunk_texts = result.get('processed_chunks', chunk_texts)
                logger.info(f"Using {len(processed_chunk_texts)} processed chunks for {len(embeddings)} embeddings")
                
                if len(embeddings) != len(processed_chunk_texts):
                    raise HTTPException(
                        status_code=500,
                        detail=f"Vector indexing failed: Embedding count ({len(embeddings)}) doesn't match chunk count ({len(processed_chunk_texts)})"
                    )
                
                embedding_dim = len(embeddings[0]) if embeddings else 768
                self.vector_store = FAISSVectorStore(dimension=embedding_dim)
                
                doc_id = self.vector_store.add_document_embeddings(
                    embeddings=embeddings,
                    file_path=temp_file_path,
                    file_type="pdf",
                    chunk_texts=processed_chunk_texts
                )
                processing_info["document_indexed"] = doc_id
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Vector indexing stage failed: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Vector indexing failed: {str(e)}"
                )
            
            # Step 5: Answer questions with error handling
            logger.info("Step 5: Answering questions")
            try:
                answers = []
                failed_questions = 0
                
                for i, question in enumerate(questions):
                    logger.info(f"Processing question {i+1}/{len(questions)}: {question[:50]}...")
                    try:
                        answer = await self.answer_question(question)
                        if not answer or not answer.strip():
                            answer = "I couldn't generate an answer for this question."
                        answers.append(answer)
                    except HTTPException as e:
                        # LLM API specific errors
                        if e.status_code >= 400 and e.status_code < 500:
                            error_msg = "I encountered an API error while processing this question."
                        else:
                            error_msg = "I encountered a server error while processing this question."
                        answers.append(error_msg)
                        failed_questions += 1
                        logger.error(f"Question {i+1} failed with HTTP {e.status_code}: {e.detail}")
                    except Exception as e:
                        error_str = str(e).lower()
                        if 'timeout' in error_str:
                            error_msg = "The question processing timed out. Please try a simpler question."
                        elif 'api key' in error_str or 'unauthorized' in error_str:
                            error_msg = "There was an authentication error with the AI service."
                        elif 'rate limit' in error_str or 'quota' in error_str:
                            error_msg = "The AI service rate limit was exceeded. Please try again later."
                        else:
                            error_msg = "I encountered an unexpected error processing this question."
                        
                        answers.append(error_msg)
                        failed_questions += 1
                        logger.error(f"Question {i+1} failed: {str(e)}")
                
                # Validate we have the right number of answers
                if len(answers) != len(questions):
                    # Pad with error messages if needed
                    while len(answers) < len(questions):
                        answers.append("Error: Unable to process this question")
                
                # Log summary
                if failed_questions > 0:
                    logger.warning(f"Completed with {failed_questions}/{len(questions)} questions failed")
                else:
                    logger.info(f"Successfully answered all {len(questions)} questions")
                
                processing_info["answers_generated"] = len(answers)
                processing_info["failed_questions"] = failed_questions
                processing_info["processing_completed"] = datetime.now().isoformat()
                processing_info["total_time_seconds"] = (datetime.now() - start_time).total_seconds()
                
                return {
                    "answers": answers,
                    "processing_info": processing_info
                }
                
            except Exception as e:
                logger.error(f"Question answering stage failed: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Question answering failed: {str(e)}"
                )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            logger.error(traceback.format_exc())
            processing_info["error"] = str(e)
            processing_info["processing_failed"] = datetime.now().isoformat()
            raise HTTPException(
                status_code=500,
                detail=f"Pipeline processing failed: {str(e)}"
            )
        
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.info(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file: {e}")
    
    async def answer_question(self, question: str) -> str:
        """Answer a question with comprehensive error handling"""
        try:
            # Input validation
            if not question or not question.strip():
                return "Error: Question cannot be empty"
            
            question = question.strip()
            if len(question) > 1000:
                return "Error: Question is too long (maximum 1000 characters)"
            
            # Generate query embedding with error handling
            try:
                query_result = await self.embedder.generate_embeddings([question])
                
                if not query_result.get('success'):
                    error_msg = query_result.get('error', 'Unknown embedding error')
                    if 'api key' in error_msg.lower():
                        raise HTTPException(status_code=500, detail="Embedding API authentication failed")
                    elif 'rate limit' in error_msg.lower() or 'quota' in error_msg.lower():
                        raise HTTPException(status_code=500, detail="Embedding API rate limit exceeded")
                    else:
                        raise HTTPException(status_code=500, detail=f"Query embedding failed: {error_msg}")
                
                query_embedding = query_result['embeddings'][0]
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Query embedding generation failed: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")
            
            # Vector search with error handling
            try:
                if not self.vector_store:
                    raise HTTPException(status_code=500, detail="Vector store not initialized")
                
                search_results = self.vector_store.similarity_search(
                    query_embedding=query_embedding,
                    k=3,
                    score_threshold=1.5
                )
                
                if not search_results:
                    # Try with lower threshold
                    search_results = self.vector_store.similarity_search(
                        query_embedding=query_embedding,
                        k=5,
                        score_threshold=2.0  # More lenient threshold
                    )
                
                if not search_results:
                    return "I couldn't find relevant information in the document to answer this question. The question may be outside the scope of the document content."
                
            except Exception as e:
                logger.error(f"Vector search failed: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Document search failed: {str(e)}")
            
            # Compose context with error handling
            try:
                context_chunks = []
                for result in search_results:
                    chunk_text = result.get('text', '')
                    if chunk_text and chunk_text.strip():
                        score = result.get('score', 0)
                        context_chunks.append(f"[Relevance: {score:.3f}] {chunk_text}")
                
                if not context_chunks:
                    return "I found some potentially relevant sections but couldn't extract readable text from them."
                
                relevant_context = "\n\n".join(context_chunks)
                
                # Limit context size to avoid token limits
                if len(relevant_context) > 8000:  # Approximate token limit
                    relevant_context = relevant_context[:8000] + "\n\n[Content truncated...]"
                
            except Exception as e:
                logger.error(f"Context composition failed: {str(e)}")
                return "I found relevant information but encountered an error processing it."
            
            # Generate answer with LLM error handling
            try:
                answer_result = await get_gemini_answer_async(
                    user_question=question,
                    relevant_clauses=relevant_context,
                    api_key=self.api_key,
                    model="gemini-2.0-flash-exp",
                    max_tokens=800,
                    temperature=0.3
                )
                
                if not answer_result.get('success'):
                    error_msg = answer_result.get('error', 'Unknown LLM error')
                    if 'api key' in error_msg.lower() or 'unauthorized' in error_msg.lower():
                        raise HTTPException(status_code=500, detail="LLM API authentication failed")
                    elif 'rate limit' in error_msg.lower() or 'quota' in error_msg.lower():
                        raise HTTPException(status_code=500, detail="LLM API rate limit exceeded")
                    elif 'timeout' in error_msg.lower():
                        raise HTTPException(status_code=500, detail="LLM API timeout")
                    else:
                        raise HTTPException(status_code=500, detail=f"LLM API error: {error_msg}")
                
                answer = answer_result.get('answer', '')
                
                if not answer or not answer.strip():
                    return "I processed your question but couldn't generate a meaningful answer. Please try rephrasing your question."
                
                # Clean and validate answer
                answer = answer.strip()
                
                # Truncate if too long
                if len(answer) > 2000:
                    answer = answer[:1997] + "..."
                
                return answer
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"LLM answer generation failed: {str(e)}")
                error_str = str(e).lower()
                if 'timeout' in error_str:
                    return "The AI service timed out while generating an answer. Please try again."
                elif 'connection' in error_str:
                    return "There was a connection error with the AI service. Please try again."
                else:
                    return "I encountered an unexpected error while generating the answer. Please try again."
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Question answering failed: {str(e)}")
            return f"I encountered an error processing your question: {str(e)}"

# Global pipeline instance
# Global pipeline instance
pipeline = DocumentQAPipelineFixed()

@app.get("/")
async def root():
    """Enhanced root endpoint with system status"""
    return {
        "message": "HackRX Document Q&A API (Fixed Version)",
        "version": "1.1.0",
        "status": "operational",
        "api_key_status": "configured" if os.getenv('GEMINI_API_KEY') else "missing",
        "endpoints": {
            "main": "/api/v1/hackrx/run",
            "health": "/api/v1/hackrx/health", 
            "docs": "/docs"
        },
        "cors": "enabled",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/hackrx/health")
async def health_check():
    """Enhanced health check"""
    try:
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
            },
            "system": {
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "temp_directory": tempfile.gettempdir()
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/v1/hackrx/run", response_model=HackRXResponse)
async def hackrx_run(
    request: HackRXRequest, 
    token: str = Depends(verify_token)
):
    """
    Enhanced HackRX API endpoint with comprehensive error handling
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Processing HackRX request: {len(request.questions)} questions for {request.document_url}")
        logger.info(f"Authorized with token: {token[:10]}...")
        
        # Input validation
        try:
            if not request.questions:
                raise HTTPException(
                    status_code=422, 
                    detail="Validation error: At least one question is required"
                )
            
            if len(request.questions) > 20:
                raise HTTPException(
                    status_code=422, 
                    detail="Validation error: Maximum 20 questions allowed"
                )
            
            # Validate questions are not empty
            for i, question in enumerate(request.questions):
                if not question or not question.strip():
                    raise HTTPException(
                        status_code=422,
                        detail=f"Validation error: Question {i+1} is empty"
                    )
                if len(question.strip()) > 500:
                    raise HTTPException(
                        status_code=422,
                        detail=f"Validation error: Question {i+1} too long (max 500 characters)"
                    )
            
            # Validate URL format
            url_str = str(request.document_url)
            if not url_str.startswith(('http://', 'https://')):
                raise HTTPException(
                    status_code=422,
                    detail="Validation error: Document URL must be a valid HTTP/HTTPS URL"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Input validation error: {str(e)}")
            raise HTTPException(
                status_code=422,
                detail=f"Validation error: {str(e)}"
            )
        
        # Execute pipeline with enhanced error handling
        try:
            result = await pipeline.process_pipeline(
                document_url=url_str,
                questions=request.questions
            )
            
            # Validate pipeline result
            if not result or "answers" not in result:
                raise HTTPException(
                    status_code=500,
                    detail="Internal server error: Invalid pipeline result"
                )
            
            answers = result["answers"]
            if not isinstance(answers, list):
                raise HTTPException(
                    status_code=500,
                    detail="Internal server error: Answers must be a list"
                )
            
            if len(answers) != len(request.questions):
                logger.warning(f"Answer count mismatch: {len(answers)} answers for {len(request.questions)} questions")
                # Pad with error messages if needed
                while len(answers) < len(request.questions):
                    answers.append("Error: Unable to process this question")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Successfully processed {len(request.questions)} questions in {processing_time:.2f}s")
            
            return HackRXResponse(answers=answers)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Pipeline execution error: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error during pipeline execution: {str(e)}"
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValidationError as e:
        logger.error(f"Request validation error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=f"Request validation failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in HackRX endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Internal server error: An unexpected error occurred"
        )

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 STARTING HACKRX API SERVER (FIXED VERSION)")
    print("=" * 60)
    print("🔧 Fixes applied:")
    print("   • Enhanced CORS configuration")
    print("   • Better file path handling")
    print("   • Improved error handling")
    print("   • Enhanced logging")
    print()
    print("📍 Endpoints:")
    print("   • Main API: http://localhost:8000/api/v1/hackrx/run")
    print("   • Health: http://localhost:8000/api/v1/hackrx/health")
    print("   • Docs: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to prevent issues
        log_level="info"
    )
