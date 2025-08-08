from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, HttpUrl
import httpx
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio
import hashlib
import numpy as np
from robust_document_parser import RobustDocumentParser
# Import old working embedder for now
from gemini_vector_embedder import generate_embeddings, embed_document_chunks
from faiss_store import get_vector_store, reset_vector_store
from dotenv import load_dotenv
from advanced_search import advanced_similarity_search, multi_query_search, search_with_context
from gemini_answer import get_gemini_answer, get_gemini_answer_async

# Load environment variables from .env file
load_dotenv()

# Initialize robust document parser
document_parser = RobustDocumentParser()

def parse_document(file_path: str, min_chunk_words: int = 100, max_chunk_words: int = 500, **kwargs) -> Dict[str, Any]:
    """Bridge function to use RobustDocumentParser with the old API"""
    try:
        # Use the standalone function from robust_document_parser
        from robust_document_parser import parse_document as robust_parse_document
        result = robust_parse_document(file_path, min_chunk_words, max_chunk_words)
        
        # Convert to the expected format
        chunks = []
        for chunk in result.get("chunks", []):
            chunks.append({
                "text": chunk["text"],
                "chunk_id": chunk.get("chunk_id", len(chunks)),
                "start_char": chunk.get("start_char", 0),
                "end_char": chunk.get("end_char", len(chunk["text"])),
                "metadata": chunk.get("metadata", {})
            })
        
        return {
            "success": result.get("success", True),
            "chunks": chunks,
            "error": result.get("error"),
            "metadata": result.get("metadata", {}),
            "file_path": file_path,
            "extraction_quality": result.get("extraction_quality", {})
        }
    except Exception as e:
        return {
            "success": False,
            "chunks": [],
            "error": str(e),
            "metadata": {},
            "file_path": file_path
        }

app = FastAPI(title="Document Processing API", version="1.0.0")

async def generate_query_embedding(
    query_text: str,
    api_key: Optional[str] = None,
    model: str = "embedding-001"
) -> Dict[str, Any]:
    """
    Generate an embedding vector from a natural language query using Google Gemini's embedding API.
    Falls back to mock embeddings if Gemini API is unavailable or quota exceeded.
    
    Args:
        query_text: Natural language query text
        api_key: Optional Gemini API key (uses environment variable if not provided)
        model: Gemini embedding model to use
    
    Returns:
        Dictionary containing the embedding vector and metadata
    """
    try:
        # First try Gemini API
        embedding_result = await generate_embeddings(
            text_chunks=[query_text],
            api_key=api_key,
            model=model
        )
        
        if not embedding_result.get("success", True):
            error_msg = embedding_result.get("error", "Failed to generate query embedding")
            
            # Check if it's a quota/billing issue
            if "quota" in error_msg.lower() or "billing" in error_msg.lower() or "429" in error_msg or "rate limit" in error_msg.lower():
                print(f"⚠️  Gemini API quota exceeded, falling back to mock embeddings...")
                return await generate_mock_query_embedding_fallback(query_text, model)
            
            return {
                "success": False,
                "error": error_msg,
                "embedding": None,
                "metadata": None
            }
        
        # Extract the single embedding vector
        query_embedding = embedding_result["embeddings"][0]
        
        return {
            "success": True,
            "embedding": query_embedding,
            "query_text": query_text,
            "metadata": {
                "model": embedding_result["model"],
                "dimensions": embedding_result["dimensions"],
                "total_tokens": embedding_result["total_tokens"],
                "vector_length": len(query_embedding)
            }
        }
        
    except Exception as e:
        error_msg = str(e)
        
        # Check if it's a quota/API issue and fall back to mock
        if "quota" in error_msg.lower() or "billing" in error_msg.lower() or "429" in error_msg or "rate limit" in error_msg.lower() or "api key" in error_msg.lower():
            print(f"⚠️  Gemini API error, falling back to mock embeddings...")
            return await generate_mock_query_embedding_fallback(query_text, model)
        
        return {
            "success": False,
            "error": f"Error generating query embedding: {error_msg}",
            "embedding": None,
            "metadata": None
        }

async def generate_mock_query_embedding_fallback(
    query_text: str,
    model: str = "embedding-001"
) -> Dict[str, Any]:
    """
    Generate a mock embedding when Gemini API is unavailable.
    Creates deterministic embeddings based on text hash.
    Uses 768 dimensions to match Gemini's embedding model.
    """
    try:
        import hashlib
        import numpy as np
        
        if not query_text or not query_text.strip():
            return {
                "success": False,
                "error": "Query text cannot be empty",
                "embedding": None,
                "metadata": None
            }
        
        # Create deterministic embedding based on text hash
        text_hash = hashlib.md5(query_text.encode()).hexdigest()
        seed = int(text_hash[:8], 16)
        np.random.seed(seed)
        
        # Generate 768-dimensional mock embedding (matching Gemini's dimensions)
        mock_embedding = np.random.randn(768)
        # Normalize to unit vector
        mock_embedding = mock_embedding / np.linalg.norm(mock_embedding)
        mock_embedding = mock_embedding.tolist()
        
        # Estimate token count
        estimated_tokens = len(query_text.split()) + 2
        
        return {
            "success": True,
            "embedding": mock_embedding,
            "query_text": query_text,
            "metadata": {
                "model": f"{model} (MOCK - Gemini API unavailable)",
                "dimensions": 768,
                "total_tokens": estimated_tokens,
                "vector_length": len(mock_embedding),
                "note": "Mock embedding used due to Gemini API limitations"
            }
        }
        
    except ImportError:
        return {
            "success": False,
            "error": "Cannot generate mock embedding: numpy not available",
            "embedding": None,
            "metadata": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating mock embedding: {str(e)}",
            "embedding": None,
            "metadata": None
        }

class UploadRequest(BaseModel):
    documents: List[HttpUrl]

class ParseRequest(BaseModel):
    file_path: str
    min_chunk_words: int = 500
    max_chunk_words: int = 1000

class EmbedRequest(BaseModel):
    text_chunks: List[str]
    model: str = "embedding-001"
    api_key: Optional[str] = None

class ParseAndEmbedRequest(BaseModel):
    file_path: str
    min_chunk_words: int = 500
    max_chunk_words: int = 1000
    embedding_model: str = "embedding-001"
    api_key: Optional[str] = None

class AddToIndexRequest(BaseModel):
    embeddings: List[List[float]]
    file_path: str
    file_type: str
    chunk_texts: List[str]
    doc_id: Optional[str] = None

class SimilaritySearchRequest(BaseModel):
    query_embedding: List[float]
    k: int = 5
    score_threshold: Optional[float] = None
    filter_doc_ids: Optional[List[str]] = None

class SearchByTextRequest(BaseModel):
    query_text: str
    k: int = 5
    score_threshold: Optional[float] = None
    filter_doc_ids: Optional[List[str]] = None
    api_key: Optional[str] = None
    embedding_model: str = "embedding-001"

class QueryEmbeddingRequest(BaseModel):
    query_text: str
    api_key: Optional[str] = None
    embedding_model: str = "embedding-001"

class AdvancedSearchRequest(BaseModel):
    query: str
    k: int = 10
    score_threshold: Optional[float] = None
    min_score_threshold: Optional[float] = None
    filter_doc_ids: Optional[List[str]] = None
    filter_doc_types: Optional[List[str]] = None
    boost_recent: bool = False
    deduplicate: bool = True
    include_metadata: bool = True
    api_key: Optional[str] = None
    embedding_model: str = "embedding-001"

class MultiQuerySearchRequest(BaseModel):
    queries: List[str]
    k: int = 5
    combination_method: str = "average"
    score_threshold: Optional[float] = None
    filter_doc_ids: Optional[List[str]] = None
    api_key: Optional[str] = None
    embedding_model: str = "embedding-001"

class ContextSearchRequest(BaseModel):
    query: str
    context_window: int = 2
    k: int = 5
    score_threshold: Optional[float] = None
    filter_doc_ids: Optional[List[str]] = None
    api_key: Optional[str] = None
    embedding_model: str = "embedding-001"

class QuestionAnswerRequest(BaseModel):
    user_question: str
    k: int = 5
    score_threshold: Optional[float] = None
    filter_doc_ids: Optional[List[str]] = None
    filter_doc_types: Optional[List[str]] = None
    api_key: Optional[str] = None
    embedding_model: str = "embedding-001"
    answer_model: str = "gemini-2.0-flash-exp"
    max_tokens: int = 1000
    temperature: float = 0.3

class DirectAnswerRequest(BaseModel):
    user_question: str
    relevant_clauses: str
    api_key: Optional[str] = None
    model: str = "gemini-2.0-flash-exp"
    max_tokens: int = 1000
    temperature: float = 0.3

class HackRXRequest(BaseModel):
    documents: HttpUrl
    questions: List[str]

@app.get("/")
async def root():
    """
    Root endpoint providing API information and available endpoints.
    """
    return {
        "title": "Document Processing API with FAISS Vector Search",
        "version": "1.0.0",
        "description": "FastAPI application for document upload, parsing, embedding generation, and vector similarity search",
        "features": [
            "Document upload from URLs",
            "PDF, DOCX, EML parsing",
            "Google Gemini embedding generation", 
            "FAISS vector similarity search",
            "AI-powered question answering",
            "Complete document-to-search pipeline"
        ],
        "endpoints": {
            "health": "/health",
            "documentation": "/docs",
            "alternative_docs": "/redoc",
            "document_operations": {
                "upload": "POST /upload",
                "parse": "POST /parse", 
                "embed": "POST /embed",
                "query_embedding": "POST /query-embedding",
                "parse_and_embed": "POST /parse-and-embed",
                "upload_parse_embed": "POST /upload-parse-embed"
            },
            "vector_search": {
                "add_to_index": "POST /index/add",
                "search_by_embedding": "POST /index/search",
                "search_by_text": "POST /index/search-by-text",
                "advanced_search": "POST /index/advanced-search",
                "multi_query_search": "POST /index/multi-query-search", 
                "context_search": "POST /index/context-search",
                "search_similar_chunks": "POST /index/search-similar-chunks",
                "get_stats": "GET /index/stats",
                "get_document": "GET /index/document/{doc_id}",
                "remove_document": "DELETE /index/document/{doc_id}",
                "reset_index": "POST /index/reset",
                "complete_pipeline": "POST /upload-parse-embed-index"
            },
            "ai_question_answering": {
                "ask_question": "POST /ask",
                "direct_answer": "POST /answer"
            },
            "hackrx": {
                "complete_pipeline": "POST /hackrx/run"
            }
        },
        "quick_start": {
            "1": "Check health: GET /health",
            "2": "View API docs: GET /docs",
            "3": "Search by text: POST /index/search-by-text",
            "4": "Upload and index: POST /upload-parse-embed-index"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload_documents(request: UploadRequest):
    """
    Download files from provided URLs and save them temporarily.
    """
    temp_dir = tempfile.mkdtemp()
    saved_files = []
    
    async with httpx.AsyncClient() as client:
        for url in request.documents:
            try:
                # Download the file
                response = await client.get(str(url))
                response.raise_for_status()
                
                # Generate a filename from the URL
                filename = Path(url.path).name or f"document_{len(saved_files)}.tmp"
                if not filename:
                    filename = f"document_{len(saved_files)}.tmp"
                
                # Save to temporary directory
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                saved_files.append({
                    "url": str(url),
                    "filename": filename,
                    "path": file_path,
                    "size": len(response.content)
                })
                
            except httpx.RequestError as e:
                raise HTTPException(status_code=400, detail=f"Failed to download {url}: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing {url}: {str(e)}")
    
    return {
        "status": "success",
        "temp_directory": temp_dir,
        "files": saved_files,
        "total_files": len(saved_files)
    }

@app.post("/parse")
async def parse_document_endpoint(request: ParseRequest):
    """
    Parse a document (PDF, DOCX, or .eml) and extract text chunks.
    """
    try:
        file_path = Path(request.file_path)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
        # Check if file type is supported
        supported_extensions = {'.pdf', '.docx', '.doc', '.eml'}
        if file_path.suffix.lower() not in supported_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_path.suffix}. Supported types: {', '.join(supported_extensions)}"
            )
        
        # Parse the document
        result = parse_document(
            str(file_path), 
            request.min_chunk_words, 
            request.max_chunk_words
        )
        
        return result
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Missing dependency: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing document: {str(e)}")

@app.post("/upload-and-parse")
async def upload_and_parse_documents(request: UploadRequest):
    """
    Download files from URLs, save them temporarily, and parse them for text chunks.
    """
    # First, upload the documents
    temp_dir = tempfile.mkdtemp()
    saved_files = []
    parsed_results = []
    
    async with httpx.AsyncClient() as client:
        for url in request.documents:
            try:
                # Download the file
                response = await client.get(str(url))
                response.raise_for_status()
                
                # Generate a filename from the URL
                filename = Path(url.path).name or f"document_{len(saved_files)}.tmp"
                if not filename:
                    filename = f"document_{len(saved_files)}.tmp"
                
                # Save to temporary directory
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                file_info = {
                    "url": str(url),
                    "filename": filename,
                    "path": file_path,
                    "size": len(response.content)
                }
                saved_files.append(file_info)
                
                # Try to parse the document if it's a supported type
                try:
                    file_ext = Path(filename).suffix.lower()
                    if file_ext in {'.pdf', '.docx', '.doc', '.eml'}:
                        parsed_doc = parse_document(file_path)
                        parsed_results.append({
                            "file_info": file_info,
                            "parsed_content": parsed_doc
                        })
                except Exception as parse_error:
                    # If parsing fails, still include the file info but note the error
                    parsed_results.append({
                        "file_info": file_info,
                        "parsed_content": None,
                        "parse_error": str(parse_error)
                    })
                
            except httpx.RequestError as e:
                raise HTTPException(status_code=400, detail=f"Failed to download {url}: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing {url}: {str(e)}")
    
    return {
        "status": "success",
        "temp_directory": temp_dir,
        "files": saved_files,
        "total_files": len(saved_files),
        "parsed_documents": parsed_results,
        "total_parsed": len([r for r in parsed_results if r.get('parsed_content')])
    }

@app.post("/embed")
async def generate_embeddings_endpoint(request: EmbedRequest):
    """
    Generate vector embeddings for a list of text chunks using Google Gemini's embedding API.
    """
    try:
        if not request.text_chunks:
            raise HTTPException(status_code=400, detail="No text chunks provided")
        
        # Log the request for debugging
        print(f"🧠 Embedding request: {len(request.text_chunks)} chunks")
        for i, chunk in enumerate(request.text_chunks[:3]):
            print(f"   Chunk {i+1}: {len(chunk)} chars, ~{len(chunk)//4} tokens")
        
        # Generate embeddings
        result = await generate_embeddings(
            text_chunks=request.text_chunks,
            api_key=request.api_key,
            model=request.model
        )
        
        print(f"📊 Embedding result: success={result.get('success', False)}")
        
        if not result.get("success", True):
            error_msg = result.get("error", "Failed to generate embeddings")
            print(f"❌ Embedding error: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Ensure we have the required fields
        embeddings = result.get("embeddings", [])
        dimensions = result.get("dimensions", 0)
        
        if not embeddings:
            raise HTTPException(status_code=500, detail="No embeddings generated")
            
        print(f"✅ Returning {len(embeddings)} embeddings with {dimensions} dimensions")
        
        return {
            "success": True,
            "embeddings": embeddings,
            "model": result.get("model", request.model),
            "total_chunks": result.get("total_chunks", len(request.text_chunks)),
            "dimensions": dimensions,
            "total_tokens": result.get("total_tokens", 0)
        }
        
    except HTTPException:
        raise
    except ImportError as e:
        print(f"❌ Import error in embedding: {e}")
        raise HTTPException(status_code=500, detail=f"Missing dependency: {str(e)}")
    except ValueError as e:
        print(f"❌ Value error in embedding: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Unexpected error in embedding: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating embeddings: {str(e)}")

@app.post("/query-embedding")
async def generate_query_embedding_endpoint(request: QueryEmbeddingRequest):
    """
    Generate an embedding vector from a natural language query.
    This is useful for preparing queries for similarity search.
    """
    try:
        if not request.query_text.strip():
            raise HTTPException(status_code=400, detail="Query text cannot be empty")
        
        # Generate embedding for the query
        result = await generate_query_embedding(
            query_text=request.query_text,
            api_key=request.api_key,
            model=request.embedding_model
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate query embedding"))
        
        return {
            "status": "success",
            "query_text": result["query_text"],
            "embedding": result["embedding"],
            "metadata": result["metadata"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/parse-and-embed")
async def parse_and_embed_endpoint(request: ParseAndEmbedRequest):
    """
    Parse a document and generate vector embeddings for its text chunks.
    """
    try:
        file_path = Path(request.file_path)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
        # Check if file type is supported
        supported_extensions = {'.pdf', '.docx', '.doc', '.eml'}
        if file_path.suffix.lower() not in supported_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_path.suffix}. Supported types: {', '.join(supported_extensions)}"
            )
        
        # Parse the document
        parse_result = parse_document(
            str(file_path), 
            request.min_chunk_words, 
            request.max_chunk_words
        )
        
        # Generate embeddings for the chunks
        embedded_result = await embed_document_chunks(
            document_result=parse_result,
            api_key=request.api_key,
            model=request.embedding_model
        )
        
        return {
            "status": "success",
            "file_path": embedded_result["file_path"],
            "file_type": embedded_result["file_type"],
            "total_chunks": embedded_result["total_chunks"],
            "total_words": embedded_result["total_words"],
            "chunks_with_embeddings": embedded_result["chunks"],
            "embedding_metadata": embedded_result["embedding_metadata"]
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Missing dependency: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/upload-parse-embed")
async def upload_parse_and_embed_documents(
    documents: List[HttpUrl], 
    min_chunk_words: int = 500,
    max_chunk_words: int = 1000,
    embedding_model: str = "embedding-001",
    api_key: Optional[str] = None
):
    """
    Download files from URLs, parse them, and generate vector embeddings for their text chunks.
    """
    temp_dir = tempfile.mkdtemp()
    saved_files = []
    processed_results = []
    
    async with httpx.AsyncClient() as client:
        for url in documents:
            try:
                # Download the file
                response = await client.get(str(url))
                response.raise_for_status()
                
                # Generate a filename from the URL
                filename = Path(url.path).name or f"document_{len(saved_files)}.tmp"
                if not filename:
                    filename = f"document_{len(saved_files)}.tmp"
                
                # Save to temporary directory
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                file_info = {
                    "url": str(url),
                    "filename": filename,
                    "path": file_path,
                    "size": len(response.content)
                }
                saved_files.append(file_info)
                
                # Try to parse and embed the document if it's a supported type
                try:
                    file_ext = Path(filename).suffix.lower()
                    if file_ext in {'.pdf', '.docx', '.doc', '.eml'}:
                        # Parse the document
                        parsed_doc = parse_document(file_path, min_chunk_words, max_chunk_words)
                        
                        # Generate embeddings
                        embedded_doc = await embed_document_chunks(
                            document_result=parsed_doc,
                            api_key=api_key,
                            model=embedding_model
                        )
                        
                        processed_results.append({
                            "file_info": file_info,
                            "processing_result": {
                                "parsed": True,
                                "embedded": embedded_doc["embedding_metadata"].get("success", False),
                                "total_chunks": embedded_doc["total_chunks"],
                                "embedding_dimensions": embedded_doc["embedding_metadata"].get("dimensions", 0),
                                "chunks_with_embeddings": embedded_doc["chunks"]
                            }
                        })
                    else:
                        processed_results.append({
                            "file_info": file_info,
                            "processing_result": {
                                "parsed": False,
                                "embedded": False,
                                "error": f"Unsupported file type: {file_ext}"
                            }
                        })
                        
                except Exception as processing_error:
                    processed_results.append({
                        "file_info": file_info,
                        "processing_result": {
                            "parsed": False,
                            "embedded": False,
                            "error": str(processing_error)
                        }
                    })
                
            except httpx.RequestError as e:
                raise HTTPException(status_code=400, detail=f"Failed to download {url}: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing {url}: {str(e)}")
    
    # Calculate summary statistics
    total_parsed = len([r for r in processed_results if r["processing_result"].get("parsed")])
    total_embedded = len([r for r in processed_results if r["processing_result"].get("embedded")])
    total_chunks = sum([r["processing_result"].get("total_chunks", 0) for r in processed_results])
    
    return {
        "status": "success",
        "temp_directory": temp_dir,
        "total_files": len(saved_files),
        "total_parsed": total_parsed,
        "total_embedded": total_embedded,
        "total_chunks_with_embeddings": total_chunks,
        "embedding_model": embedding_model,
        "processed_documents": processed_results
    }

@app.post("/index/add")
async def add_to_index(request: AddToIndexRequest):
    """
    Add document embeddings to the FAISS index with unique IDs.
    """
    try:
        vector_store = get_vector_store()
        
        doc_id = vector_store.add_document_embeddings(
            embeddings=request.embeddings,
            file_path=request.file_path,
            file_type=request.file_type,
            chunk_texts=request.chunk_texts,
            doc_id=request.doc_id
        )
        
        stats = vector_store.get_stats()
        
        return {
            "status": "success",
            "doc_id": doc_id,
            "chunks_added": len(request.embeddings),
            "index_stats": stats
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to index: {str(e)}")

@app.post("/index/search")
async def similarity_search(request: SimilaritySearchRequest):
    """
    Perform similarity search against the FAISS index using a query embedding.
    """
    try:
        vector_store = get_vector_store()
        
        results = vector_store.similarity_search(
            query_embedding=request.query_embedding,
            k=request.k,
            score_threshold=request.score_threshold,
            filter_doc_ids=request.filter_doc_ids
        )
        
        return {
            "status": "success",
            "query_info": {
                "k": request.k,
                "score_threshold": request.score_threshold,
                "filter_doc_ids": request.filter_doc_ids
            },
            "results": results,
            "total_results": len(results)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")

@app.post("/index/search-by-text")
async def search_by_text(request: SearchByTextRequest):
    """
    Perform similarity search using natural language text query.
    Text will be converted to embedding first, then searched.
    """
    try:
        # First, generate embedding for the query text using our dedicated function
        embedding_result = await generate_query_embedding(
            query_text=request.query_text,
            api_key=request.api_key,
            model=request.embedding_model
        )
        
        if not embedding_result.get("success"):
            raise HTTPException(status_code=500, detail=embedding_result.get("error", "Failed to generate query embedding"))
        
        query_embedding = embedding_result["embedding"]
        
        # Perform similarity search
        vector_store = get_vector_store()
        results = vector_store.similarity_search(
            query_embedding=query_embedding,
            k=request.k,
            score_threshold=request.score_threshold,
            filter_doc_ids=request.filter_doc_ids
        )
        
        return {
            "status": "success",
            "query_info": {
                "query_text": request.query_text,
                "embedding_model": request.embedding_model,
                "k": request.k,
                "score_threshold": request.score_threshold,
                "filter_doc_ids": request.filter_doc_ids
            },
            "embedding_metadata": {
                "model": embedding_result["metadata"]["model"],
                "dimensions": embedding_result["metadata"]["dimensions"],
                "total_tokens": embedding_result["metadata"]["total_tokens"]
            },
            "results": results,
            "total_results": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing text search: {str(e)}")

@app.post("/index/advanced-search")
async def advanced_search_endpoint(request: AdvancedSearchRequest):
    """
    Perform advanced similarity search with comprehensive filtering and ranking.
    Supports relevance scoring, document filtering, deduplication, and recency boosting.
    """
    try:
        result = await advanced_similarity_search(
            query=request.query,
            k=request.k,
            score_threshold=request.score_threshold,
            min_score_threshold=request.min_score_threshold,
            filter_doc_ids=request.filter_doc_ids,
            filter_doc_types=request.filter_doc_types,
            boost_recent=request.boost_recent,
            deduplicate=request.deduplicate,
            include_metadata=request.include_metadata,
            api_key=request.api_key,
            embedding_model=request.embedding_model
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in advanced search: {str(e)}")

@app.post("/index/multi-query-search")
async def multi_query_search_endpoint(request: MultiQuerySearchRequest):
    """
    Perform similarity search with multiple queries and combine results.
    Useful for comprehensive searches with different phrasings of the same concept.
    """
    try:
        result = await multi_query_search(
            queries=request.queries,
            k=request.k,
            combination_method=request.combination_method,
            score_threshold=request.score_threshold,
            filter_doc_ids=request.filter_doc_ids,
            api_key=request.api_key,
            embedding_model=request.embedding_model
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in multi-query search: {str(e)}")

@app.post("/index/context-search")
async def context_search_endpoint(request: ContextSearchRequest):
    """
    Perform similarity search and include surrounding context chunks.
    Provides expanded context around matching chunks for better understanding.
    """
    try:
        result = await search_with_context(
            query=request.query,
            context_window=request.context_window,
            k=request.k,
            score_threshold=request.score_threshold,
            filter_doc_ids=request.filter_doc_ids,
            api_key=request.api_key,
            embedding_model=request.embedding_model
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in context search: {str(e)}")

@app.post("/index/search-similar-chunks")
async def search_similar_chunks_endpoint(
    query_embedding: List[float], 
    k: int = 10,
    score_threshold: Optional[float] = None,
    min_score_threshold: Optional[float] = None,
    filter_doc_ids: Optional[List[str]] = None,
    filter_doc_types: Optional[List[str]] = None,
    boost_recent: bool = False,
    deduplicate: bool = True,
    include_metadata: bool = True
):
    """
    Core function: Search the FAISS index for the top-N most similar chunks to a given query vector.
    
    This is the main similarity search function that finds the most relevant document chunks
    based on vector similarity using L2 distance in the FAISS index.
    
    Args:
        query_embedding: Pre-computed embedding vector (768 dimensions for Gemini)
        k: Number of top similar results to return
        score_threshold: Maximum similarity score (lower is better for L2 distance)
        min_score_threshold: Minimum similarity score for inclusion
        filter_doc_ids: Optional list of document IDs to restrict search to
        filter_doc_types: Optional list of document types to filter by
        boost_recent: Whether to boost more recently added documents
        deduplicate: Whether to remove similar results from same document
        include_metadata: Whether to include full metadata in results
    
    Returns:
        JSON response with ranked similar chunks, scores, and metadata
    """
    try:
        result = await advanced_similarity_search(
            query=query_embedding,
            k=k,
            score_threshold=score_threshold,
            min_score_threshold=min_score_threshold,
            filter_doc_ids=filter_doc_ids,
            filter_doc_types=filter_doc_types,
            boost_recent=boost_recent,
            deduplicate=deduplicate,
            include_metadata=include_metadata
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching similar chunks: {str(e)}")

@app.post("/ask")
async def ask_question_endpoint(request: QuestionAnswerRequest):
    """
    Complete Document Q&A Pipeline
    
    This endpoint provides the full document question-answering experience:
    searches your indexed documents, retrieves relevant content, and generates
    intelligent AI answers with comprehensive source attribution.
    
    **Process Flow:**
    1. Convert user question to vector embedding using Gemini
    2. Vector search across indexed document chunks
    3. Retrieve most relevant content segments
    4. AI-powered answer generation with reasoning
    5. Structured response with sources and rationale
    
    **Use Cases:**
    - Research queries across document collections
    - Legal document analysis and citation
    - Academic paper information extraction
    - Technical documentation Q&A
    
    **Request Example:**
    ```json
    {
        "user_question": "What are the data privacy requirements for user consent?",
        "api_key": os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here"),
        "search_strategy": "mmr",
        "top_k": 5,
        "embedding_model": "text-embedding-004",
        "generative_model": "gemini-2.0-flash-exp",
        "temperature": 0.2
    }
    ```
    
    **Response Example:**
    ```json
    {
        "success": true,
        "user_question": "What are the data privacy requirements for user consent?",
        "answer": "According to the retrieved documents, user consent for data privacy must be explicit, informed, and freely given...",
        "rationale": "I analyzed 5 relevant document sections covering GDPR compliance, consent mechanisms, and data protection standards...",
        "source_chunks": [
            "GDPR Article 7 requires that consent be freely given, specific, informed and unambiguous...",
            "Organizations must maintain clear records of when and how consent was obtained..."
        ],
        "search_results": [
            {
                "content": "GDPR Article 7 requires...",
                "metadata": {
                    "filename": "privacy_policy.pdf",
                    "page_number": 12,
                    "chunk_id": "chunk_45"
                },
                "similarity_score": 0.89
            }
        ],
        "embedding_model": "text-embedding-004",
        "generative_model": "gemini-2.0-flash-exp",
        "tokens_used": 234,
        "processing_time": "3.1s"
    }
    ```
    
    **Search Strategies:**
    - `similarity`: Standard cosine similarity search
    - `mmr`: Maximal Marginal Relevance (diverse results)
    - `similarity_score_threshold`: Results above similarity threshold
    - `hybrid`: Combined keyword + semantic search
    
    **Parameters:**
    - `user_question`: Your question about the documents
    - `api_key`: Gemini API key for embeddings and generation
    - `search_strategy`: How to search documents (default: "mmr")
    - `top_k`: Number of relevant chunks to retrieve (default: 5)
    - `embedding_model`: Model for question embedding
    - `generative_model`: Gemini model for answer generation
    - `temperature`: Response creativity level (0.0-1.0)
    
    Args:
        request: QuestionAnswerRequest with question and search parameters
    
    Returns:
        Complete Q&A response with answer, rationale, sources, and search results
    """
    try:
        # Step 1: Generate embedding for the user question
        embedding_result = await generate_query_embedding(
            query_text=request.user_question,
            api_key=request.api_key,
            model=request.embedding_model
        )
        
        if not embedding_result.get("success"):
            raise HTTPException(status_code=500, detail=f"Failed to generate question embedding: {embedding_result.get('error')}")
        
        query_embedding = embedding_result["embedding"]
        
        # Step 2: Search for relevant document chunks
        search_result = await advanced_similarity_search(
            query=query_embedding,
            k=request.k,
            score_threshold=request.score_threshold,
            filter_doc_ids=request.filter_doc_ids,
            filter_doc_types=request.filter_doc_types,
            deduplicate=True,
            include_metadata=True
        )
        
        if not search_result.get("results"):
            return {
                "status": "success",
                "user_question": request.user_question,
                "answer": "I couldn't find any relevant information in the indexed documents to answer your question.",
                "rationale": "No matching document content was found in the vector search.",
                "source_chunks": "No sources available",
                "search_results": [],
                "embedding_metadata": embedding_result["metadata"]
            }
        
        # Step 3: Combine relevant text from search results
        relevant_clauses = []
        for result in search_result["results"]:
            clause = f"[Document: {result['metadata']['file_path']}, Chunk {result['metadata']['chunk_index']}]\n{result['text']}"
            relevant_clauses.append(clause)
        
        combined_clauses = "\n\n".join(relevant_clauses)
        
        # Step 4: Get intelligent answer from Gemini
        answer_result = await get_gemini_answer_async(
            user_question=request.user_question,
            relevant_clauses=combined_clauses,
            api_key=request.api_key,
            model=request.answer_model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        if not answer_result.get("success"):
            return {
                "status": "partial_success",
                "user_question": request.user_question,
                "answer": "I found relevant documents but couldn't generate a structured answer.",
                "rationale": f"Gemini API error: {answer_result.get('error')}",
                "source_chunks": combined_clauses[:500] + "..." if len(combined_clauses) > 500 else combined_clauses,
                "search_results": search_result["results"],
                "embedding_metadata": embedding_result["metadata"],
                "error": answer_result.get("error")
            }
        
        # Step 5: Return comprehensive response
        return {
            "status": "success",
            "user_question": request.user_question,
            "answer": answer_result["answer"],
            "rationale": answer_result["rationale"],
            "source_chunks": answer_result["source_chunks"],
            "search_results": search_result["results"],
            "analytics": {
                "search_time_ms": search_result.get("analytics", {}).get("search_time_ms", 0),
                "documents_searched": search_result.get("analytics", {}).get("total_documents", 0),
                "relevant_chunks_found": len(search_result["results"]),
                "tokens_used": answer_result.get("tokens_used", 0),
                "embedding_model": request.embedding_model,
                "answer_model": request.answer_model
            },
            "embedding_metadata": embedding_result["metadata"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in question answering: {str(e)}")

@app.post("/answer")
async def direct_answer_endpoint(request: DirectAnswerRequest):
    """
    Direct AI Answer Generation
    
    Generates intelligent answers using Gemini AI based on provided context.
    This endpoint bypasses document search and directly processes your question
    with the provided relevant clauses/context.
    
    **Use Cases:**
    - General knowledge questions
    - Questions with pre-selected context
    - Direct AI consultation without document retrieval
    
    **Request Example:**
    ```json
    {
        "user_question": "What are the benefits of machine learning?",
        "relevant_clauses": "Machine learning is a subset of AI that enables systems to learn from data without explicit programming. It improves accuracy over time and can automate decision-making processes.",
        "model": "gemini-2.0-flash-exp",
        "temperature": 0.3
    }
    ```
    
    **Response Example:**
    ```json
    {
        "success": true,
        "user_question": "What are the benefits of machine learning?",
        "answer": "Machine learning offers several key benefits including automated decision-making, improved accuracy through continuous learning, and the ability to process large datasets efficiently...",
        "rationale": "Based on the provided context, I analyzed the core concepts of machine learning and identified three primary benefits...",
        "source_chunks": ["Machine learning is a subset of AI...", "It improves accuracy over time..."],
        "model": "gemini-2.0-flash-exp",
        "tokens_used": 156,
        "processing_time": "2.3s"
    }
    ```
    
    **Parameters:**
    - `user_question`: The question you want answered
    - `relevant_clauses`: Context/background information for the question
    - `model`: Gemini model to use (default: "gemini-2.0-flash-exp")
    - `temperature`: Response creativity 0.0-1.0 (default: 0.3)
    - `max_tokens`: Maximum response length (default: 1000)
    
    Args:
        request: DirectAnswerRequest with question and context
    
    Returns:
        Structured JSON response with AI answer, rationale, and source chunks
    """
    try:
        result = await get_gemini_answer_async(
            user_question=request.user_question,
            relevant_clauses=request.relevant_clauses,
            api_key=request.api_key,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return {
            "status": "success" if result["success"] else "error",
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

@app.get("/index/stats")
async def get_index_stats():
    """
    Get statistics about the current FAISS index.
    """
    try:
        vector_store = get_vector_store()
        stats = vector_store.get_stats()
        
        return {
            "status": "success",
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting index stats: {str(e)}")

@app.get("/index/document/{doc_id}")
async def get_document_chunks(doc_id: str):
    """
    Get all chunks for a specific document ID.
    """
    try:
        vector_store = get_vector_store()
        chunks = vector_store.get_document_chunks(doc_id)
        
        if not chunks:
            raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")
        
        return {
            "status": "success",
            "doc_id": doc_id,
            "chunks": chunks,
            "total_chunks": len(chunks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")

@app.delete("/index/document/{doc_id}")
async def remove_document(doc_id: str):
    """
    Remove all chunks for a specific document ID from the index.
    """
    try:
        vector_store = get_vector_store()
        removed = vector_store.remove_document(doc_id)
        
        if not removed:
            raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")
        
        stats = vector_store.get_stats()
        
        return {
            "status": "success",
            "doc_id": doc_id,
            "removed": True,
            "index_stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing document: {str(e)}")

@app.post("/index/reset")
async def reset_index():
    """
    Reset the FAISS index (remove all documents and embeddings).
    """
    try:
        reset_vector_store()
        
        return {
            "status": "success",
            "message": "Index has been reset",
            "index_stats": get_vector_store().get_stats()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting index: {str(e)}")

@app.post("/upload-parse-embed-index")
async def upload_parse_embed_and_index(
    documents: List[HttpUrl], 
    min_chunk_words: int = 500,
    max_chunk_words: int = 1000,
    embedding_model: str = "embedding-001",
    api_key: Optional[str] = None
):
    """
    Complete Document Processing Pipeline
    
    Downloads documents from URLs, parses content, generates embeddings,
    and indexes them in the FAISS vector store for searchable Q&A.
    
    **Process Flow:**
    1. Download documents from provided URLs
    2. Parse content (PDF, DOCX, TXT supported)
    3. Split text into semantic chunks
    4. Generate embeddings using Gemini
    5. Index in FAISS vector store
    6. Return processing summary
    
    **Use Cases:**
    - Bulk document ingestion from web sources
    - Research paper collection processing
    - Legal document database creation
    - Knowledge base construction
    
    **Request Example:**
    ```json
    {
        "documents": [
            "https://example.com/document1.pdf",
            "https://example.com/policy.docx"
        ],
        "min_chunk_words": 300,
        "max_chunk_words": 800,
        "embedding_model": "text-embedding-004",
        "api_key": os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")
    }
    ```
    
    **Response Example:**
    ```json
    {
        "success": true,
        "message": "Successfully processed and indexed 2 documents",
        "processed_documents": [
            {
                "url": "https://example.com/document1.pdf",
                "filename": "document1.pdf",
                "pages": 15,
                "chunks_created": 24,
                "embeddings_generated": 24,
                "status": "success"
            },
            {
                "url": "https://example.com/policy.docx",
                "filename": "policy.docx",
                "pages": 8,
                "chunks_created": 12,
                "embeddings_generated": 12,
                "status": "success"
            }
        ],
        "total_chunks": 36,
        "total_embeddings": 36,
        "vector_store_size": 156,
        "processing_time": "45.2s"
    }
    ```
    
    **Supported File Types:**
    - PDF (.pdf): Text extraction with page numbers
    - Word Documents (.docx): Full content parsing
    - Text Files (.txt): Direct content processing
    
    **Parameters:**
    - `documents`: List of HTTP/HTTPS URLs to documents
    - `min_chunk_words`: Minimum words per chunk (default: 500)
    - `max_chunk_words`: Maximum words per chunk (default: 1000)
    - `embedding_model`: Gemini embedding model (default: "embedding-001")
    - `api_key`: Gemini API key (uses default if not provided)
    
    Args:
        documents: List of document URLs to process
        min_chunk_words: Minimum chunk size in words
        max_chunk_words: Maximum chunk size in words
        embedding_model: Model for embedding generation
        api_key: Optional API key override
    
    Returns:
        Processing summary with document details and indexing results
    """
    temp_dir = tempfile.mkdtemp()
    saved_files = []
    processed_results = []
    vector_store = get_vector_store()
    
    async with httpx.AsyncClient() as client:
        for url in documents:
            try:
                # Download the file
                response = await client.get(str(url))
                response.raise_for_status()
                
                # Generate a filename from the URL
                filename = Path(url.path).name or f"document_{len(saved_files)}.tmp"
                if not filename:
                    filename = f"document_{len(saved_files)}.tmp"
                
                # Save to temporary directory
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                file_info = {
                    "url": str(url),
                    "filename": filename,
                    "path": file_path,
                    "size": len(response.content)
                }
                saved_files.append(file_info)
                
                # Try to parse, embed, and index the document
                try:
                    file_ext = Path(filename).suffix.lower()
                    if file_ext in {'.pdf', '.docx', '.doc', '.eml'}:
                        # Parse the document
                        parsed_doc = parse_document(file_path, min_chunk_words, max_chunk_words)
                        
                        # Generate embeddings
                        embedded_doc = await embed_document_chunks(
                            document_result=parsed_doc,
                            api_key=api_key,
                            model=embedding_model
                        )
                        
                        # Add to FAISS index
                        if embedded_doc["embedding_metadata"].get("success", False):
                            chunk_texts = [chunk["text"] for chunk in embedded_doc["chunks"]]
                            embeddings = [chunk["embedding"] for chunk in embedded_doc["chunks"]]
                            
                            doc_id = vector_store.add_document_embeddings(
                                embeddings=embeddings,
                                file_path=file_path,
                                file_type=file_ext,
                                chunk_texts=chunk_texts
                            )
                            
                            processed_results.append({
                                "file_info": file_info,
                                "processing_result": {
                                    "parsed": True,
                                    "embedded": True,
                                    "indexed": True,
                                    "doc_id": doc_id,
                                    "total_chunks": embedded_doc["total_chunks"],
                                    "embedding_dimensions": embedded_doc["embedding_metadata"].get("dimensions", 0)
                                }
                            })
                        else:
                            processed_results.append({
                                "file_info": file_info,
                                "processing_result": {
                                    "parsed": True,
                                    "embedded": False,
                                    "indexed": False,
                                    "error": "Embedding generation failed"
                                }
                            })
                    else:
                        processed_results.append({
                            "file_info": file_info,
                            "processing_result": {
                                "parsed": False,
                                "embedded": False,
                                "indexed": False,
                                "error": f"Unsupported file type: {file_ext}"
                            }
                        })
                        
                except Exception as processing_error:
                    processed_results.append({
                        "file_info": file_info,
                        "processing_result": {
                            "parsed": False,
                            "embedded": False,
                            "indexed": False,
                            "error": str(processing_error)
                        }
                    })
                
            except httpx.RequestError as e:
                raise HTTPException(status_code=400, detail=f"Failed to download {url}: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing {url}: {str(e)}")
    
    # Calculate summary statistics
    total_parsed = len([r for r in processed_results if r["processing_result"].get("parsed")])
    total_embedded = len([r for r in processed_results if r["processing_result"].get("embedded")])
    total_indexed = len([r for r in processed_results if r["processing_result"].get("indexed")])
    total_chunks = sum([r["processing_result"].get("total_chunks", 0) for r in processed_results])
    
    return {
        "status": "success",
        "temp_directory": temp_dir,
        "total_files": len(saved_files),
        "total_parsed": total_parsed,
        "total_embedded": total_embedded,
        "total_indexed": total_indexed,
        "total_chunks_indexed": total_chunks,
        "embedding_model": embedding_model,
        "processed_documents": processed_results,
        "index_stats": vector_store.get_stats()
    }

@app.post("/hackrx/run")
async def hackrx_run(
    request: HackRXRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Complete Document Processing and Q&A Pipeline
    
    This endpoint performs the full document processing workflow:
    1. Downloads document from URL
    2. Parses content (PDF, DOCX, TXT)
    3. Generates embeddings using Gemini
    4. Indexes in FAISS vector store
    5. Answers questions using AI with document context
    
    **Authentication Required:** Authorization header with valid token
    
    **Request Example:**
    ```json
    {
        "documents": "https://example.com/document.pdf",
        "questions": [
            "What is the main topic of this document?",
            "What are the key findings?",
            "What recommendations are provided?"
        ]
    }
    ```
    
    **Response Example:**
    ```json
    {
        "success": true,
        "document_url": "https://example.com/document.pdf",
        "document_processed": true,
        "document_id": "doc_abc123",
        "chunks_processed": 15,
        "questions_processed": 3,
        "answers": [
            {
                "question": "What is the main topic?",
                "success": true,
                "answer": "The document discusses AI and machine learning applications...",
                "rationale": "Based on my analysis of the document content, I identified...",
                "source_chunks": ["AI applications are becoming...", "Machine learning enables..."],
                "confidence": "high",
                "sources_used": 3,
                "model": "gemini-2.0-flash-exp"
            }
        ],
        "processing_summary": {
            "total_questions": 3,
            "successful_answers": 3,
            "failed_answers": 0,
            "document_chunks": 15,
            "embedding_model": "embedding-001",
            "ai_model": "gemini-2.0-flash-exp"
        }
    }
    ```
    
    **Authorization Headers:**
    - `Authorization: Bearer hackrx2024`
    - `Authorization: hackrx2024`
    - `Authorization: Bearer api-key-12345`
    
    **Error Responses:**
    - `401`: Missing Authorization header
    - `403`: Invalid authorization token
    - `400`: Invalid document URL or parsing error
    - `500`: Internal processing error
    
    **Supported Document Types:**
    - PDF files (.pdf)
    - Word documents (.docx)
    - Text files (.txt)
    - Any publicly accessible URL
    
    Args:
        request: HackRXRequest containing document URL and questions list
        authorization: Authorization header (required for access)
    
    Returns:
        JSON response with processing results and AI answers for each question
    """
    
    # Authorization check
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required"
        )
    
    # Validate authorization token (customize this logic as needed)
    valid_tokens = [
        "Bearer hackrx2024",
        "Bearer api-key-12345", 
        "hackrx2024",
        os.getenv("HACKRX_API_KEY", "hackrx2024")
    ]
    
    if authorization not in valid_tokens:
        raise HTTPException(
            status_code=403,
            detail="Invalid authorization token"
        )
    
    try:
        # Step 1: Download document from URL
        document_url = str(request.documents)
        
        # Create temporary directory for downloaded file
        temp_dir = tempfile.mkdtemp()
        
        # Download the document
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(document_url)
            response.raise_for_status()
            
            # Determine file extension from URL or content type
            file_extension = Path(document_url).suffix.lower()
            if not file_extension and 'content-type' in response.headers:
                content_type = response.headers['content-type']
                if 'pdf' in content_type:
                    file_extension = '.pdf'
                elif 'word' in content_type or 'msword' in content_type:
                    file_extension = '.docx'
                else:
                    file_extension = '.txt'
            
            # Save downloaded file
            temp_file_path = os.path.join(temp_dir, f"document{file_extension}")
            with open(temp_file_path, 'wb') as f:
                f.write(response.content)
        
        # Step 2: Parse document content
        parse_result = parse_document(temp_file_path)
        
        if not parse_result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse document: {parse_result.get('error', 'Unknown error')}"
            )
        
        text_chunks = parse_result.get("chunks", [])
        
        if not text_chunks:
            raise HTTPException(
                status_code=400,
                detail="No text content extracted from document"
            )
        
        # Step 3: Generate embeddings for document chunks
        embedding_result = await embed_document_chunks(
            text_chunks=text_chunks,
            file_path=temp_file_path
        )
        
        if not embedding_result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate embeddings: {embedding_result.get('error', 'Unknown error')}"
            )
        
        # Step 4: Add to FAISS vector store
        vector_store = get_vector_store()
        doc_id = vector_store.add_document_embeddings(
            embeddings=embedding_result["embeddings"],
            file_path=document_url,  # Use URL as file path for reference
            file_type=file_extension,
            chunk_texts=text_chunks,
            doc_id=None  # Auto-generate doc ID
        )
        
        # Step 5: Process all questions
        answers = []
        
        for question in request.questions:
            try:
                # Search for relevant content
                search_results = await advanced_similarity_search(
                    query_text=question,
                    top_k=5,
                    score_threshold=0.6,
                    search_strategy="comprehensive"
                )
                
                # Combine relevant chunks for context
                relevant_clauses = []
                if search_results.get("results"):
                    for result in search_results["results"][:3]:  # Top 3 most relevant
                        relevant_clauses.append(result["text"])
                
                combined_context = "\n\n".join(relevant_clauses) if relevant_clauses else "No specific context found in document."
                
                # Generate AI answer
                ai_result = await get_gemini_answer_async(
                    user_question=question,
                    relevant_clauses=combined_context,
                    model="gemini-2.0-flash-exp"
                )
                
                # Format answer
                answer_data = {
                    "question": question,
                    "success": ai_result.get("success", False),
                }
                
                if ai_result.get("success"):
                    answer_data.update({
                        "answer": ai_result.get("answer", ""),
                        "rationale": ai_result.get("rationale", ""),
                        "source_chunks": ai_result.get("source_chunks", []),
                        "confidence": ai_result.get("confidence", "medium"),
                        "sources_used": len(relevant_clauses),
                        "model": ai_result.get("model", "gemini-2.0-flash-exp")
                    })
                else:
                    answer_data.update({
                        "error": ai_result.get("error", "Failed to generate answer"),
                        "answer": None,
                        "rationale": None,
                        "source_chunks": []
                    })
                
                answers.append(answer_data)
                
            except Exception as e:
                # Handle individual question errors
                answers.append({
                    "question": question,
                    "success": False,
                    "error": str(e),
                    "answer": None,
                    "rationale": None,
                    "source_chunks": []
                })
        
        # Cleanup temporary files
        try:
            os.unlink(temp_file_path)
            os.rmdir(temp_dir)
        except:
            pass  # Ignore cleanup errors
        
        # Return comprehensive results
        return {
            "success": True,
            "document_url": document_url,
            "document_processed": True,
            "document_id": doc_id,
            "chunks_processed": len(text_chunks),
            "questions_processed": len(request.questions),
            "answers": answers,
            "processing_summary": {
                "total_questions": len(request.questions),
                "successful_answers": sum(1 for a in answers if a.get("success")),
                "failed_answers": sum(1 for a in answers if not a.get("success")),
                "document_chunks": len(text_chunks),
                "embedding_model": "embedding-001",
                "ai_model": "gemini-2.0-flash-exp"
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
