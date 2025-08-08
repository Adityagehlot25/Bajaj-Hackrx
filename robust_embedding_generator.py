"""
Robust Embedding Generator with Retry Logic and Comprehensive Error Handling
Supports multiple embedding providers: OpenAI, Google Gemini, HuggingFace
"""

import os
import time
import logging
import json
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import hashlib
import backoff
from pathlib import Path

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Available embedding providers
EMBEDDING_PROVIDERS = {}

try:
    import openai
    EMBEDDING_PROVIDERS['openai'] = openai
    logger.info("OpenAI client available for embeddings")
except ImportError:
    logger.warning("OpenAI not available. Install with: pip install openai")

try:
    import google.generativeai as genai
    EMBEDDING_PROVIDERS['gemini'] = genai
    logger.info("Google Gemini client available for embeddings")
except ImportError:
    logger.warning("Google Gemini not available. Install with: pip install google-generativeai")

try:
    # Skip sentence transformers if environment variable is set to avoid compatibility issues
    if not os.getenv('SKIP_SENTENCE_TRANSFORMERS'):
        from sentence_transformers import SentenceTransformer
        EMBEDDING_PROVIDERS['sentence_transformers'] = SentenceTransformer
        logger.info("Sentence Transformers available for embeddings")
    else:
        logger.info("Sentence Transformers skipped due to environment variable")
except ImportError:
    logger.warning("Sentence Transformers not available. Install with: pip install sentence-transformers")

try:
    import requests
    HTTP_CLIENT_AVAILABLE = True
except ImportError:
    HTTP_CLIENT_AVAILABLE = False
    logger.warning("requests not available for HTTP calls")


class EmbeddingCache:
    """Simple file-based cache for embeddings to avoid redundant API calls."""
    
    def __init__(self, cache_dir: str = "embedding_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        logger.info(f"Embedding cache initialized at: {self.cache_dir}")
    
    def _get_cache_key(self, text: str, model: str, provider: str) -> str:
        """Generate cache key for text-model-provider combination."""
        content = f"{provider}:{model}:{text}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, text: str, model: str, provider: str) -> Optional[List[float]]:
        """Get cached embedding if available."""
        cache_key = self._get_cache_key(text, model, provider)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    return cache_data.get('embedding')
            except Exception as e:
                logger.warning(f"Failed to load cache entry {cache_key}: {e}")
        
        return None
    
    def set(self, text: str, model: str, provider: str, embedding: List[float]):
        """Cache embedding for future use."""
        cache_key = self._get_cache_key(text, model, provider)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            cache_data = {
                'text_hash': hashlib.md5(text.encode()).hexdigest()[:16],
                'model': model,
                'provider': provider,
                'embedding': embedding,
                'cached_at': datetime.now().isoformat(),
                'text_length': len(text)
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f)
                
        except Exception as e:
            logger.warning(f"Failed to cache embedding {cache_key}: {e}")


class RobustEmbeddingGenerator:
    """Robust embedding generator with multiple providers and comprehensive error handling."""
    
    def __init__(self, 
                 default_provider: str = "gemini",
                 use_cache: bool = True,
                 max_retries: int = 3,
                 retry_delay: float = 1.0):
        
        self.default_provider = default_provider
        self.use_cache = use_cache
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Initialize cache
        if use_cache:
            self.cache = EmbeddingCache()
        
        # Load environment variables
        self._load_environment()
        
        # Initialize providers
        self._initialize_providers()
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'retries_used': 0,
            'providers_used': {},
            'total_tokens_processed': 0
        }
        
        logger.info(f"Initialized embedding generator with provider: {default_provider}")
        logger.info(f"Available providers: {list(EMBEDDING_PROVIDERS.keys())}")
    
    def _load_environment(self):
        """Load API keys and configuration from environment variables."""
        self.api_keys = {}
        
        # OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.api_keys['openai'] = openai_key
            logger.info("OpenAI API key loaded from environment")
        else:
            logger.warning("OPENAI_API_KEY not found in environment")
        
        # Google Gemini
        gemini_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if gemini_key:
            self.api_keys['gemini'] = gemini_key
            logger.info("Gemini API key loaded from environment")
        else:
            logger.warning("GOOGLE_API_KEY or GEMINI_API_KEY not found in environment")
        
        # Hugging Face
        hf_key = os.getenv('HUGGINGFACE_API_KEY')
        if hf_key:
            self.api_keys['huggingface'] = hf_key
            logger.info("Hugging Face API key loaded from environment")
    
    def _initialize_providers(self):
        """Initialize available embedding providers."""
        self.initialized_providers = {}
        
        # Initialize OpenAI
        if 'openai' in EMBEDDING_PROVIDERS and 'openai' in self.api_keys:
            try:
                client = EMBEDDING_PROVIDERS['openai']
                client.api_key = self.api_keys['openai']
                self.initialized_providers['openai'] = client
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        
        # Initialize Gemini
        if 'gemini' in EMBEDDING_PROVIDERS and 'gemini' in self.api_keys:
            try:
                genai = EMBEDDING_PROVIDERS['gemini']
                genai.configure(api_key=self.api_keys['gemini'])
                self.initialized_providers['gemini'] = genai
                logger.info("Gemini client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
        
        # Initialize Sentence Transformers (no API key needed)
        if 'sentence_transformers' in EMBEDDING_PROVIDERS:
            try:
                self.initialized_providers['sentence_transformers'] = EMBEDDING_PROVIDERS['sentence_transformers']
                logger.info("Sentence Transformers available")
            except Exception as e:
                logger.error(f"Failed to initialize Sentence Transformers: {e}")
        
        if not self.initialized_providers:
            logger.error("No embedding providers available! Please install libraries and set API keys.")
    
    def generate_embeddings(self, 
                          text_chunks: List[str], 
                          model: str = "text-embedding-3-small",
                          provider: str = None,
                          api_key: str = None) -> Dict[str, Any]:
        """
        Generate embeddings for text chunks with comprehensive error handling.
        
        Args:
            text_chunks: List of text strings to embed
            model: Model name for embeddings
            provider: Embedding provider ('openai', 'gemini', 'sentence_transformers')
            api_key: Optional API key override
            
        Returns:
            Dictionary with embeddings and metadata
        """
        start_time = datetime.now()
        
        # Input validation
        if not text_chunks:
            logger.error("Empty text_chunks provided")
            raise ValueError("text_chunks cannot be empty")
        
        if not isinstance(text_chunks, list):
            logger.error("text_chunks must be a list")
            raise ValueError("text_chunks must be a list")
        
        # Clean and validate text chunks
        cleaned_chunks = []
        for i, chunk in enumerate(text_chunks):
            if not chunk or not isinstance(chunk, str):
                logger.warning(f"Skipping invalid chunk at index {i}: {type(chunk)}")
                continue
            
            cleaned_text = self._clean_text(chunk)
            if len(cleaned_text.strip()) < 10:
                logger.warning(f"Skipping too short chunk at index {i}: {len(cleaned_text)} chars")
                continue
            
            cleaned_chunks.append(cleaned_text)
        
        if not cleaned_chunks:
            logger.error("No valid text chunks after cleaning")
            raise ValueError("No valid text chunks after cleaning")
        
        logger.info(f"Processing {len(cleaned_chunks)} valid chunks (from {len(text_chunks)} input chunks)")
        
        # Determine provider
        provider = provider or self.default_provider
        if provider not in self.initialized_providers:
            # Fallback to first available provider
            if self.initialized_providers:
                provider = list(self.initialized_providers.keys())[0]
                logger.warning(f"Requested provider not available, using: {provider}")
            else:
                raise RuntimeError("No embedding providers available")
        
        self.stats['total_requests'] += 1
        
        try:
            # Generate embeddings based on provider
            if provider == 'openai':
                result = self._generate_openai_embeddings(cleaned_chunks, model, api_key)
            elif provider == 'gemini':
                result = self._generate_gemini_embeddings(cleaned_chunks, model, api_key)
            elif provider == 'sentence_transformers':
                result = self._generate_sentence_transformer_embeddings(cleaned_chunks, model)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Add metadata
            result.update({
                'provider': provider,
                'model': model,
                'processing_time_seconds': (datetime.now() - start_time).total_seconds(),
                'processed_at': datetime.now().isoformat(),
                'input_chunks': len(text_chunks),
                'valid_chunks': len(cleaned_chunks),
                'cache_hits': result.get('cache_hits', 0)
            })
            
            self.stats['successful_requests'] += 1
            self.stats['providers_used'][provider] = self.stats['providers_used'].get(provider, 0) + 1
            self.stats['total_tokens_processed'] += sum(len(chunk.split()) for chunk in cleaned_chunks)
            
            logger.info(f"Successfully generated embeddings using {provider}: {len(result['embeddings'])} vectors")
            
            return result
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"Failed to generate embeddings with {provider}: {e}")
            raise
    
    @backoff.on_exception(
        backoff.expo,
        (Exception,),
        max_tries=3,
        max_time=30,
        on_backoff=lambda details: logger.warning(f"Retrying OpenAI embedding request: attempt {details['tries']}")
    )
    def _generate_openai_embeddings(self, text_chunks: List[str], model: str, api_key: str = None) -> Dict[str, Any]:
        """Generate embeddings using OpenAI API with retry logic."""
        if 'openai' not in self.initialized_providers:
            raise RuntimeError("OpenAI provider not initialized")
        
        client = self.initialized_providers['openai']
        
        # Override API key if provided
        if api_key:
            client.api_key = api_key
        
        embeddings = []
        cache_hits = 0
        
        # Process chunks in batches to avoid rate limits
        batch_size = 100  # OpenAI recommended batch size
        
        for i in range(0, len(text_chunks), batch_size):
            batch = text_chunks[i:i+batch_size]
            batch_embeddings = []
            
            # Check cache first
            if self.use_cache:
                for chunk in batch:
                    cached_embedding = self.cache.get(chunk, model, 'openai')
                    if cached_embedding:
                        batch_embeddings.append(cached_embedding)
                        cache_hits += 1
                    else:
                        batch_embeddings.append(None)  # Placeholder
            else:
                batch_embeddings = [None] * len(batch)
            
            # Collect chunks that need embedding
            chunks_to_embed = []
            indices_to_embed = []
            
            for j, embedding in enumerate(batch_embeddings):
                if embedding is None:
                    chunks_to_embed.append(batch[j])
                    indices_to_embed.append(j)
            
            # Generate embeddings for non-cached chunks
            if chunks_to_embed:
                logger.debug(f"Generating OpenAI embeddings for {len(chunks_to_embed)} chunks")
                
                try:
                    response = client.embeddings.create(
                        model=model,
                        input=chunks_to_embed,
                        encoding_format="float"
                    )
                    
                    # Extract embeddings and cache them
                    for idx, embedding_data in enumerate(response.data):
                        embedding = embedding_data.embedding
                        chunk_idx = indices_to_embed[idx]
                        batch_embeddings[chunk_idx] = embedding
                        
                        # Cache the embedding
                        if self.use_cache:
                            self.cache.set(chunks_to_embed[idx], model, 'openai', embedding)
                    
                except Exception as e:
                    logger.error(f"OpenAI API error: {e}")
                    raise
            
            embeddings.extend(batch_embeddings)
            
            # Rate limiting
            if i + batch_size < len(text_chunks):
                time.sleep(0.1)
        
        return {
            'success': True,
            'embeddings': embeddings,
            'embedding_dimension': len(embeddings[0]) if embeddings else 0,
            'total_embeddings': len(embeddings),
            'cache_hits': cache_hits
        }
    
    @backoff.on_exception(
        backoff.expo,
        (Exception,),
        max_tries=3,
        max_time=30,
        on_backoff=lambda details: logger.warning(f"Retrying Gemini embedding request: attempt {details['tries']}")
    )
    def _generate_gemini_embeddings(self, text_chunks: List[str], model: str, api_key: str = None) -> Dict[str, Any]:
        """Generate embeddings using Google Gemini API with retry logic."""
        if 'gemini' not in self.initialized_providers:
            raise RuntimeError("Gemini provider not initialized")
        
        genai = self.initialized_providers['gemini']
        
        # Override API key if provided
        if api_key:
            genai.configure(api_key=api_key)
        
        # Map model names for Gemini
        model_mapping = {
            'text-embedding-3-small': 'text-embedding-004',
            'text-embedding-3-large': 'text-embedding-004',
            'embedding-001': 'text-embedding-004'
        }
        
        gemini_model = model_mapping.get(model, 'text-embedding-004')
        
        embeddings = []
        cache_hits = 0
        
        # Process chunks individually due to Gemini API limitations
        for i, chunk in enumerate(text_chunks):
            try:
                # Check cache first
                if self.use_cache:
                    cached_embedding = self.cache.get(chunk, gemini_model, 'gemini')
                    if cached_embedding:
                        embeddings.append(cached_embedding)
                        cache_hits += 1
                        continue
                
                logger.debug(f"Generating Gemini embedding for chunk {i+1}/{len(text_chunks)}")
                
                # Generate embedding
                result = genai.embed_content(
                    model=f"models/{gemini_model}",
                    content=chunk,
                    task_type="retrieval_document"
                )
                
                embedding = result['embedding']
                embeddings.append(embedding)
                
                # Cache the embedding
                if self.use_cache:
                    self.cache.set(chunk, gemini_model, 'gemini', embedding)
                
                # Rate limiting for Gemini
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Gemini API error for chunk {i}: {e}")
                raise
        
        return {
            'success': True,
            'embeddings': embeddings,
            'embedding_dimension': len(embeddings[0]) if embeddings else 0,
            'total_embeddings': len(embeddings),
            'cache_hits': cache_hits
        }
    
    def _generate_sentence_transformer_embeddings(self, text_chunks: List[str], model: str) -> Dict[str, Any]:
        """Generate embeddings using Sentence Transformers."""
        if 'sentence_transformers' not in self.initialized_providers:
            raise RuntimeError("Sentence Transformers provider not initialized")
        
        SentenceTransformer = self.initialized_providers['sentence_transformers']
        
        # Map model names
        model_mapping = {
            'text-embedding-3-small': 'all-MiniLM-L6-v2',
            'text-embedding-3-large': 'all-mpnet-base-v2',
            'embedding-001': 'all-MiniLM-L6-v2'
        }
        
        st_model = model_mapping.get(model, 'all-MiniLM-L6-v2')
        
        embeddings = []
        cache_hits = 0
        
        # Load model
        try:
            logger.info(f"Loading Sentence Transformer model: {st_model}")
            transformer_model = SentenceTransformer(st_model)
        except Exception as e:
            logger.error(f"Failed to load Sentence Transformer model: {e}")
            raise
        
        # Check cache and generate embeddings
        chunks_to_embed = []
        chunk_indices = []
        
        for i, chunk in enumerate(text_chunks):
            if self.use_cache:
                cached_embedding = self.cache.get(chunk, st_model, 'sentence_transformers')
                if cached_embedding:
                    embeddings.append(cached_embedding)
                    cache_hits += 1
                else:
                    embeddings.append(None)  # Placeholder
                    chunks_to_embed.append(chunk)
                    chunk_indices.append(i)
            else:
                chunks_to_embed.append(chunk)
                chunk_indices.append(i)
                embeddings.append(None)
        
        # Generate embeddings for non-cached chunks
        if chunks_to_embed:
            logger.info(f"Generating Sentence Transformer embeddings for {len(chunks_to_embed)} chunks")
            
            try:
                batch_embeddings = transformer_model.encode(
                    chunks_to_embed,
                    convert_to_numpy=True,
                    show_progress_bar=True if len(chunks_to_embed) > 10 else False
                )
                
                # Insert embeddings back and cache them
                for idx, embedding in enumerate(batch_embeddings):
                    chunk_idx = chunk_indices[idx]
                    embeddings[chunk_idx] = embedding.tolist()
                    
                    # Cache the embedding
                    if self.use_cache:
                        self.cache.set(chunks_to_embed[idx], st_model, 'sentence_transformers', embedding.tolist())
                
            except Exception as e:
                logger.error(f"Sentence Transformer encoding error: {e}")
                raise
        
        return {
            'success': True,
            'embeddings': embeddings,
            'embedding_dimension': len(embeddings[0]) if embeddings else 0,
            'total_embeddings': len(embeddings),
            'cache_hits': cache_hits
        }
    
    def generate_query_embedding(self, 
                                query_text: str, 
                                model: str = "text-embedding-3-small",
                                provider: str = None,
                                api_key: str = None) -> Dict[str, Any]:
        """Generate embedding for a single query with error handling."""
        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty")
        
        cleaned_query = self._clean_text(query_text)
        
        logger.info(f"Generating query embedding for: {cleaned_query[:100]}...")
        
        result = self.generate_embeddings([cleaned_query], model, provider, api_key)
        
        return {
            'success': result['success'],
            'embedding': result['embeddings'][0],
            'embedding_dimension': result['embedding_dimension'],
            'query_text': cleaned_query,
            'provider': result['provider'],
            'model': result['model'],
            'processing_time_seconds': result['processing_time_seconds']
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and prepare text for embedding."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        # Truncate if too long (embedding models have token limits)
        max_chars = 8000  # Conservative limit
        if len(text) > max_chars:
            text = text[:max_chars]
            logger.warning(f"Text truncated to {max_chars} characters")
        
        return text.strip()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get embedding generation statistics."""
        return {
            **self.stats,
            'success_rate': self.stats['successful_requests'] / max(1, self.stats['total_requests']),
            'cache_hit_rate': self.stats['cache_hits'] / max(1, self.stats['total_requests']),
            'available_providers': list(self.initialized_providers.keys())
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all providers."""
        health_status = {}
        
        test_text = "This is a test embedding request for health check."
        
        for provider in self.initialized_providers:
            try:
                logger.info(f"Testing {provider} provider...")
                result = self.generate_embeddings([test_text], provider=provider)
                health_status[provider] = {
                    'status': 'healthy',
                    'embedding_dimension': result['embedding_dimension'],
                    'response_time': result['processing_time_seconds']
                }
                logger.info(f"{provider} provider is healthy")
                
            except Exception as e:
                health_status[provider] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                logger.error(f"{provider} provider is unhealthy: {e}")
        
        return {
            'overall_status': 'healthy' if any(status['status'] == 'healthy' for status in health_status.values()) else 'unhealthy',
            'providers': health_status,
            'checked_at': datetime.now().isoformat()
        }


# Factory functions for backward compatibility
def generate_embeddings(text_chunks: List[str], 
                       model: str = "text-embedding-3-small", 
                       api_key: str = None,
                       provider: str = "gemini") -> Dict[str, Any]:
    """
    Generate embeddings with robust error handling.
    
    Args:
        text_chunks: List of text strings to embed
        model: Model name for embeddings
        api_key: API key for the embedding service
        provider: Embedding provider
        
    Returns:
        Dictionary with embeddings and metadata
    """
    generator = RobustEmbeddingGenerator(default_provider=provider)
    return generator.generate_embeddings(text_chunks, model, provider, api_key)


def generate_query_embedding(query_text: str,
                           model: str = "text-embedding-3-small",
                           api_key: str = None,
                           provider: str = "gemini") -> Dict[str, Any]:
    """Generate embedding for a single query."""
    generator = RobustEmbeddingGenerator(default_provider=provider)
    return generator.generate_query_embedding(query_text, model, provider, api_key)


if __name__ == "__main__":
    # Test the embedding generator
    generator = RobustEmbeddingGenerator()
    
    print("Available providers:", list(generator.initialized_providers.keys()))
    
    # Health check
    health = generator.health_check()
    print("Health check:", health)
    
    # Test embedding generation
    test_chunks = [
        "This is a test document about machine learning.",
        "Natural language processing is a subset of AI.",
        "Vector embeddings capture semantic meaning."
    ]
    
    try:
        result = generator.generate_embeddings(test_chunks)
        print(f"Generated {len(result['embeddings'])} embeddings")
        print(f"Embedding dimension: {result['embedding_dimension']}")
        print("Statistics:", generator.get_stats())
    except Exception as e:
        print(f"Error: {e}")
