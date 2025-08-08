"""
Vector embedding module for generating embeddings from text chunks using OpenAI's API.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
import logging
from pydantic import BaseModel

try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None
    AsyncOpenAI = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingRequest(BaseModel):
    """Request model for embedding generation."""
    text_chunks: List[str]
    model: str = "text-embedding-3-small"  # OpenAI's latest embedding model
    api_key: Optional[str] = None

class EmbeddingResponse(BaseModel):
    """Response model for embedding generation."""
    embeddings: List[List[float]]
    model: str
    total_chunks: int
    dimensions: int
    total_tokens: int

class VectorEmbedder:
    """Class for generating vector embeddings using OpenAI's API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        """
        Initialize the vector embedder.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY env var
            model: OpenAI embedding model to use
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library is required. Install with: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # Model configuration
        self.model_configs = {
            "text-embedding-3-small": {"dimensions": 1536, "max_tokens": 8191},
            "text-embedding-3-large": {"dimensions": 3072, "max_tokens": 8191},
            "text-embedding-ada-002": {"dimensions": 1536, "max_tokens": 8191}
        }
    
    async def generate_embeddings(self, text_chunks: List[str], batch_size: int = 100) -> Dict[str, Any]:
        """
        Generate vector embeddings for a list of text chunks.
        
        Args:
            text_chunks: List of text strings to embed
            batch_size: Number of chunks to process in each API call (max 2048 for OpenAI)
            
        Returns:
            Dictionary containing embeddings and metadata
        """
        if not text_chunks:
            return {
                "embeddings": [],
                "model": self.model,
                "total_chunks": 0,
                "dimensions": 0,
                "total_tokens": 0,
                "error": "No text chunks provided"
            }
        
        # Validate model
        if self.model not in self.model_configs:
            available_models = list(self.model_configs.keys())
            raise ValueError(f"Unsupported model: {self.model}. Available models: {available_models}")
        
        # Preprocess text chunks
        processed_chunks = self._preprocess_chunks(text_chunks)
        
        all_embeddings = []
        total_tokens = 0
        
        try:
            # Process chunks in batches
            for i in range(0, len(processed_chunks), batch_size):
                batch = processed_chunks[i:i + batch_size]
                
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(processed_chunks) + batch_size - 1)//batch_size}")
                
                # Make API call
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    encoding_format="float"
                )
                
                # Extract embeddings
                batch_embeddings = [embedding.embedding for embedding in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Track token usage
                total_tokens += response.usage.total_tokens
                
                # Small delay to respect rate limits
                if i + batch_size < len(processed_chunks):
                    await asyncio.sleep(0.1)
            
            dimensions = len(all_embeddings[0]) if all_embeddings else 0
            
            return {
                "embeddings": all_embeddings,
                "model": self.model,
                "total_chunks": len(processed_chunks),
                "dimensions": dimensions,
                "total_tokens": total_tokens,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return {
                "embeddings": [],
                "model": self.model,
                "total_chunks": len(processed_chunks),
                "dimensions": 0,
                "total_tokens": total_tokens,
                "error": str(e),
                "success": False
            }
    
    def _preprocess_chunks(self, text_chunks: List[str]) -> List[str]:
        """
        Preprocess text chunks before embedding.
        
        Args:
            text_chunks: Raw text chunks
            
        Returns:
            Processed text chunks
        """
        processed = []
        max_tokens = self.model_configs[self.model]["max_tokens"]
        
        for chunk in text_chunks:
            # Clean and truncate text
            cleaned_chunk = self._clean_text(chunk)
            
            # Approximate token count (rough estimate: 1 token ≈ 4 characters)
            estimated_tokens = len(cleaned_chunk) // 4
            
            if estimated_tokens > max_tokens:
                # Truncate to fit within token limit
                max_chars = max_tokens * 4
                cleaned_chunk = cleaned_chunk[:max_chars].rsplit(' ', 1)[0]  # Truncate at word boundary
                logger.warning(f"Chunk truncated to {len(cleaned_chunk)} characters to fit token limit")
            
            if cleaned_chunk.strip():  # Only add non-empty chunks
                processed.append(cleaned_chunk)
        
        return processed
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text for better embedding quality.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove or replace problematic characters
        text = text.replace('\x00', '')  # Remove null bytes
        text = text.replace('\r\n', ' ')  # Replace Windows line endings
        text = text.replace('\n', ' ')    # Replace line breaks
        text = text.replace('\t', ' ')    # Replace tabs
        
        return text.strip()

class ChunkEmbedder:
    """Helper class for embedding document chunks with metadata preservation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        self.embedder = VectorEmbedder(api_key=api_key, model=model)
    
    async def embed_document_chunks(self, document_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate embeddings for document chunks while preserving metadata.
        
        Args:
            document_result: Result from document_parser.parse_document()
            
        Returns:
            Enhanced document result with embeddings
        """
        if not document_result.get("chunks"):
            return {
                **document_result,
                "embeddings": [],
                "embedding_metadata": {
                    "model": self.embedder.model,
                    "total_embedded": 0,
                    "dimensions": 0,
                    "error": "No chunks found to embed"
                }
            }
        
        # Extract text from chunks
        chunk_texts = [chunk["text"] for chunk in document_result["chunks"]]
        
        # Generate embeddings
        embedding_result = await self.embedder.generate_embeddings(chunk_texts)
        
        if embedding_result.get("success"):
            # Add embeddings to each chunk
            enhanced_chunks = []
            for i, chunk in enumerate(document_result["chunks"]):
                enhanced_chunk = {
                    **chunk,
                    "embedding": embedding_result["embeddings"][i],
                    "embedding_model": embedding_result["model"]
                }
                enhanced_chunks.append(enhanced_chunk)
            
            return {
                **document_result,
                "chunks": enhanced_chunks,
                "embedding_metadata": {
                    "model": embedding_result["model"],
                    "total_embedded": embedding_result["total_chunks"],
                    "dimensions": embedding_result["dimensions"],
                    "total_tokens": embedding_result["total_tokens"],
                    "success": True
                }
            }
        else:
            return {
                **document_result,
                "embedding_metadata": {
                    "model": embedding_result["model"],
                    "total_embedded": 0,
                    "dimensions": 0,
                    "error": embedding_result.get("error", "Unknown error"),
                    "success": False
                }
            }

# Convenience functions
async def generate_embeddings(text_chunks: List[str], api_key: Optional[str] = None, 
                            model: str = "text-embedding-3-small") -> Dict[str, Any]:
    """
    Convenience function to generate embeddings for text chunks.
    
    Args:
        text_chunks: List of text strings to embed
        api_key: OpenAI API key (optional if set in environment)
        model: OpenAI embedding model to use
        
    Returns:
        Dictionary containing embeddings and metadata
    """
    embedder = VectorEmbedder(api_key=api_key, model=model)
    return await embedder.generate_embeddings(text_chunks)

async def embed_document_chunks(document_result: Dict[str, Any], api_key: Optional[str] = None,
                               model: str = "text-embedding-3-small") -> Dict[str, Any]:
    """
    Convenience function to embed document chunks with metadata preservation.
    
    Args:
        document_result: Result from document_parser.parse_document()
        api_key: OpenAI API key (optional if set in environment)
        model: OpenAI embedding model to use
        
    Returns:
        Enhanced document result with embeddings
    """
    chunk_embedder = ChunkEmbedder(api_key=api_key, model=model)
    return await chunk_embedder.embed_document_chunks(document_result)
