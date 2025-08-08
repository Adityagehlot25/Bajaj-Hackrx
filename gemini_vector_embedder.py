"""
Vector embedding module for generating embeddings from text chunks using Google Gemini API.
Refactored from OpenAI API to use Google Gemini with HTTP requests.
"""

import os
import asyncio
import aiohttp
import requests
from typing import List, Dict, Any, Optional
import logging
from pydantic import BaseModel
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingRequest(BaseModel):
    """Request model for embedding generation."""
    text_chunks: List[str]
    model: str = "text-embedding-004"  # Gemini's embedding model
    api_key: Optional[str] = None

class EmbeddingResponse(BaseModel):
    """Response model for embedding generation."""
    embeddings: List[List[float]]
    model: str
    total_chunks: int
    dimensions: int
    total_tokens: int

class GeminiVectorEmbedder:
    """Class for generating vector embeddings using Google Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "embedding-001"):
        """
        Initialize the Gemini vector embedder.
        
        Args:
            api_key: Google Gemini API key. If not provided, will look for GEMINI_API_KEY env var
            model: Gemini embedding model to use (embedding-001 is the standard model)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        self.model = model
        # Updated base URL for the correct Gemini API endpoint
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        # Model configuration for Gemini (with correct model names)
        self.model_configs = {
            "text-embedding-004": {"dimensions": 768, "max_tokens": 2048},  # Gemini embedding model
            "embedding-001": {"dimensions": 768, "max_tokens": 2048}  # Alternative Gemini model
        }
        
        # Keep the model as-is since we're using the correct Gemini model names
        # The actual model endpoint will be constructed in the API calls
        
        # Request headers - try both authentication methods
        self.headers = {
            "Content-Type": "application/json"
        }
        
        # Store whether to use query param or header auth (will be determined on first call)
        self._auth_method = None
    
    async def generate_embeddings(self, text_chunks: List[str], batch_size: int = 100) -> Dict[str, Any]:
        """
        Generate vector embeddings for a list of text chunks using Gemini API.
        
        Args:
            text_chunks: List of text strings to embed
            batch_size: Number of chunks to process in each API call
            
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
            async with aiohttp.ClientSession() as session:
                for i in range(0, len(processed_chunks), batch_size):
                    batch = processed_chunks[i:i + batch_size]
                    
                    logger.info(f"Processing batch {i//batch_size + 1}/{(len(processed_chunks) + batch_size - 1)//batch_size}")
                    
                    # Process each chunk in the batch (Gemini typically processes one at a time)
                    batch_embeddings = []
                    for text in batch:
                        embedding = await self._generate_single_embedding(session, text)
                        if embedding:
                            batch_embeddings.append(embedding)
                            total_tokens += self._estimate_tokens(text)
                    
                    all_embeddings.extend(batch_embeddings)
                    
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
                "processed_chunks": processed_chunks,  # Include processed chunks for indexing
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
    
    async def _generate_single_embedding(self, session: aiohttp.ClientSession, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text using Gemini API.
        Uses the same simple method that works in our direct tests.
        
        Args:
            session: aiohttp session
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        payload = {
            "content": {
                "parts": [{"text": text}]
            },
            "taskType": "RETRIEVAL_DOCUMENT"
        }
        
        # Use the simple query parameter method that we know works
        url = f"{self.base_url}/{self.model}:embedContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    embedding = data.get("embedding", {}).get("values", [])
                    if embedding:
                        logger.info(f"Successfully generated embedding with {len(embedding)} dimensions")
                        return embedding
                    else:
                        logger.error("No embedding found in response")
                        return None
                else:
                    error_text = await response.text()
                    logger.error(f"Gemini API error {response.status}: {error_text}")
                    
                    # Handle specific error cases
                    if response.status == 429:
                        logger.warning("Rate limit exceeded, waiting before retry...")
                        await asyncio.sleep(1)
                        return await self._generate_single_embedding(session, text)
                    elif response.status == 403:
                        raise Exception("API access denied. Check your API key permissions and billing status.")
                    else:
                        raise Exception(f"API error {response.status}: {error_text}")
                        
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            raise Exception(f"Network error: {e}")
        
        return None
    
    def generate_embeddings_sync(self, text_chunks: List[str]) -> Dict[str, Any]:
        """
        Synchronous version of generate_embeddings using requests library.
        
        Args:
            text_chunks: List of text strings to embed
            
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
        
        # Preprocess text chunks
        processed_chunks = self._preprocess_chunks(text_chunks)
        
        all_embeddings = []
        total_tokens = 0
        
        try:
            for i, text in enumerate(processed_chunks):
                logger.info(f"Processing chunk {i+1}/{len(processed_chunks)}")
                
                # Standard Gemini API endpoint (authentication via query parameter like working queries)
                url = f"{self.base_url}/{self.model}:embedContent?key={self.api_key}"
                
                payload = {
                    "content": {
                        "parts": [{"text": text}]
                    },
                    "taskType": "RETRIEVAL_DOCUMENT"
                }
                
                # Use empty headers for query param auth (like working query embeddings)
                headers = {"Content-Type": "application/json"}
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    embedding = data.get("embedding", {}).get("values", [])
                    if embedding:
                        all_embeddings.append(embedding)
                        total_tokens += self._estimate_tokens(text)
                else:
                    error_text = response.text
                    logger.error(f"Gemini API error {response.status_code}: {error_text}")
                    
                    # Handle specific error cases
                    if response.status_code == 429:
                        logger.warning("Rate limit exceeded, waiting before retry...")
                        import time
                        time.sleep(1)
                        # Retry once with same auth method
                        url_retry = f"{self.base_url}/{self.model}:embedContent?key={self.api_key}"
                        headers_retry = {"Content-Type": "application/json"}
                        response = requests.post(url_retry, headers=headers_retry, json=payload, timeout=30)
                        if response.status_code == 200:
                            data = response.json()
                            embedding = data.get("embedding", {}).get("values", [])
                            if embedding:
                                all_embeddings.append(embedding)
                                total_tokens += self._estimate_tokens(text)
                        else:
                            raise Exception(f"Retry failed: {response.status_code}")
                    elif response.status_code == 403:
                        raise Exception("API key invalid or insufficient permissions")
                    elif response.status_code == 400:
                        raise Exception(f"Bad request: {error_text}")
                    else:
                        raise Exception(f"API error {response.status_code}: {error_text}")
            
            dimensions = len(all_embeddings[0]) if all_embeddings else 0
            
            return {
                "embeddings": all_embeddings,
                "model": self.model,
                "total_chunks": len(processed_chunks),
                "dimensions": dimensions,
                "total_tokens": total_tokens,
                "processed_chunks": processed_chunks,  # Include processed chunks for indexing
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
        Split large chunks and ensure they fit within token limits.
        
        Args:
            text_chunks: Raw text chunks
            
        Returns:
            Processed text chunks that fit within API limits
        """
        processed = []
        max_tokens = self.model_configs[self.model]["max_tokens"]
        
        logger.info(f"Starting preprocessing of {len(text_chunks)} chunks with max_tokens={max_tokens}")
        
        for i, chunk in enumerate(text_chunks):
            # Debug: Check what we're getting as input
            chunk_text = ""
            if isinstance(chunk, dict):
                # Handle chunk dictionaries (from document parser)
                chunk_text = chunk.get('content', chunk.get('text', ''))
            else:
                # Handle raw text
                chunk_text = str(chunk)
            
            logger.info(f"Processing chunk {i+1}: {len(chunk_text)} chars, type: {type(chunk)}")
            
            if not chunk_text or not chunk_text.strip():
                logger.warning(f"Skipping empty chunk {i+1}")
                continue
            
            # Clean the text
            cleaned_chunk = self._clean_text(chunk_text)
            
            if not cleaned_chunk or not cleaned_chunk.strip():
                logger.warning(f"Chunk {i+1} became empty after cleaning")
                continue
            
            # Estimate tokens (rough estimate: 1 token ≈ 4 characters)
            estimated_tokens = len(cleaned_chunk) // 4
            
            logger.info(f"Chunk {i+1}: {len(cleaned_chunk)} chars, ~{estimated_tokens} tokens (limit: {max_tokens})")
            
            if estimated_tokens > max_tokens:
                # Split large chunk into smaller chunks
                max_chars = max_tokens * 4
                words = cleaned_chunk.split()
                
                current_chunk = ""
                current_length = 0
                
                for word in words:
                    word_length = len(word) + 1  # +1 for space
                    
                    if current_length + word_length > max_chars and current_chunk:
                        # Add current chunk and start a new one
                        if current_chunk.strip():
                            processed.append(current_chunk.strip())
                            logger.info(f"Split large chunk into smaller chunk of {len(current_chunk)} characters")
                        current_chunk = word
                        current_length = word_length
                    else:
                        current_chunk += " " + word if current_chunk else word
                        current_length += word_length
                
                # Add the last chunk
                if current_chunk.strip():
                    processed.append(current_chunk.strip())
                    logger.info(f"Added final chunk of {len(current_chunk)} characters")
                    
            else:
                # Chunk is already within limits
                processed.append(cleaned_chunk)
                logger.info(f"Added chunk {i+1} directly ({len(cleaned_chunk)} chars)")
        
        logger.info(f"Preprocessed {len(text_chunks)} input chunks into {len(processed)} API-ready chunks")
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
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for a text string.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters for most languages
        return len(text) // 4

class GeminiChunkEmbedder:
    """Helper class for embedding document chunks with metadata preservation using Gemini."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-004"):
        self.embedder = GeminiVectorEmbedder(api_key=api_key, model=model)
    
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

# Convenience functions for backward compatibility
async def generate_embeddings(text_chunks: List[str], api_key: Optional[str] = None, 
                            model: str = "text-embedding-004") -> Dict[str, Any]:
    """
    Convenience function to generate embeddings for text chunks using Gemini API.
    
    Args:
        text_chunks: List of text strings to embed
        api_key: Gemini API key (optional if set in environment)
        model: Gemini embedding model to use
        
    Returns:
        Dictionary containing embeddings and metadata
    """
    embedder = GeminiVectorEmbedder(api_key=api_key, model=model)
    return await embedder.generate_embeddings(text_chunks)

async def embed_document_chunks(document_result: Dict[str, Any], api_key: Optional[str] = None,
                               model: str = "text-embedding-004") -> Dict[str, Any]:
    """
    Convenience function to embed document chunks with metadata preservation using Gemini.
    
    Args:
        document_result: Result from document_parser.parse_document()
        api_key: Gemini API key (optional if set in environment)
        model: Gemini embedding model to use
        
    Returns:
        Enhanced document result with embeddings
    """
    chunk_embedder = GeminiChunkEmbedder(api_key=api_key, model=model)
    return await chunk_embedder.embed_document_chunks(document_result)

# Example usage and testing functions
async def test_gemini_embeddings():
    """Test function to verify Gemini API integration."""
    print("🧪 Testing Gemini Embeddings API")
    print("=" * 50)
    
    try:
        # Initialize embedder
        embedder = GeminiVectorEmbedder()
        
        # Test with sample text
        test_texts = [
            "This is a test of the Gemini embedding API.",
            "Machine learning is transforming how we process information.",
            "Natural language processing enables computers to understand human language."
        ]
        
        print(f"📝 Testing with {len(test_texts)} text chunks...")
        
        # Generate embeddings
        result = await embedder.generate_embeddings(test_texts)
        
        if result.get("success"):
            print("✅ Success!")
            print(f"📊 Model: {result['model']}")
            print(f"📊 Total chunks: {result['total_chunks']}")
            print(f"📊 Dimensions: {result['dimensions']}")
            print(f"📊 Total tokens: {result['total_tokens']}")
            
            if result['embeddings']:
                sample_embedding = result['embeddings'][0]
                print(f"🎯 Sample embedding (first 5 values): {sample_embedding[:5]}")
                print(f"🎯 Sample embedding (last 5 values): {sample_embedding[-5:]}")
        else:
            print(f"❌ Error: {result.get('error')}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

def test_gemini_embeddings_sync():
    """Synchronous test function to verify Gemini API integration."""
    print("🧪 Testing Gemini Embeddings API (Sync)")
    print("=" * 50)
    
    try:
        # Initialize embedder
        embedder = GeminiVectorEmbedder()
        
        # Test with sample text
        test_texts = [
            "This is a synchronous test of the Gemini embedding API.",
            "Vector embeddings capture semantic meaning in numerical form."
        ]
        
        print(f"📝 Testing with {len(test_texts)} text chunks...")
        
        # Generate embeddings synchronously
        result = embedder.generate_embeddings_sync(test_texts)
        
        if result.get("success"):
            print("✅ Success!")
            print(f"📊 Model: {result['model']}")
            print(f"📊 Total chunks: {result['total_chunks']}")
            print(f"📊 Dimensions: {result['dimensions']}")
            print(f"📊 Total tokens: {result['total_tokens']}")
            
            if result['embeddings']:
                sample_embedding = result['embeddings'][0]
                print(f"🎯 Sample embedding (first 5 values): {sample_embedding[:5]}")
                print(f"🎯 Sample embedding (last 5 values): {sample_embedding[-5:]}")
        else:
            print(f"❌ Error: {result.get('error')}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    print("🚀 Gemini Vector Embedder Test Suite")
    print("=" * 60)
    
    # Test synchronous version
    test_gemini_embeddings_sync()
    
    print("\n" + "=" * 60)
    
    # Test asynchronous version
    asyncio.run(test_gemini_embeddings())
