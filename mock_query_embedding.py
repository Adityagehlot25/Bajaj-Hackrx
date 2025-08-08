"""
Mock Query Embedding Function for Testing Without OpenAI API
This creates fake embeddings for testing when OpenAI quota is exceeded
"""

import numpy as np
from typing import Dict, Any, Optional
import hashlib

def generate_mock_query_embedding(
    query_text: str,
    api_key: Optional[str] = None,
    model: str = "text-embedding-3-small"
) -> Dict[str, Any]:
    """
    Generate a mock embedding vector for testing purposes.
    Uses a hash-based approach to create consistent, deterministic embeddings.
    """
    try:
        if not query_text or not query_text.strip():
            return {
                "success": False,
                "error": "Query text cannot be empty",
                "embedding": None,
                "metadata": None
            }
        
        # Create a deterministic "embedding" based on the text hash
        # This ensures the same text always produces the same embedding
        text_hash = hashlib.md5(query_text.encode()).hexdigest()
        
        # Use the hash to seed a random number generator for consistency
        seed = int(text_hash[:8], 16)
        np.random.seed(seed)
        
        # Generate a mock 1536-dimensional embedding (same as text-embedding-3-small)
        mock_embedding = np.random.randn(1536).tolist()
        
        # Normalize to unit vector (common practice for embeddings)
        norm = np.linalg.norm(mock_embedding)
        mock_embedding = (np.array(mock_embedding) / norm).tolist()
        
        # Estimate token count (rough approximation)
        estimated_tokens = len(query_text.split()) + 2
        
        return {
            "success": True,
            "embedding": mock_embedding,
            "query_text": query_text,
            "metadata": {
                "model": f"{model} (MOCK)",
                "dimensions": 1536,
                "total_tokens": estimated_tokens,
                "vector_length": len(mock_embedding),
                "note": "This is a mock embedding for testing purposes"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating mock query embedding: {str(e)}",
            "embedding": None,
            "metadata": None
        }

def create_demo_faiss_index():
    """Create a demo FAISS index with some sample data"""
    try:
        from faiss_store import FAISSVectorStore
        
        # Create vector store
        vector_store = FAISSVectorStore(dimension=1536, index_type="flat")
        
        # Sample documents
        sample_docs = [
            "Python is a high-level programming language known for its simplicity and readability.",
            "Machine learning is a subset of artificial intelligence that uses algorithms to learn patterns.",
            "FastAPI is a modern web framework for building APIs with Python 3.6+ based on standard Python type hints.",
            "Vector databases store high-dimensional vectors and enable efficient similarity search operations.",
            "Natural language processing (NLP) is a field of AI that focuses on human-computer language interaction.",
            "Web development involves creating websites and web applications using various technologies.",
            "Data science combines statistics, programming, and domain expertise to extract insights from data.",
            "Cloud computing provides on-demand access to computing resources over the internet.",
            "Neural networks are computing systems inspired by biological neural networks in animal brains.",
            "API development requires understanding of HTTP protocols, data serialization, and authentication."
        ]
        
        # Generate mock embeddings for each document
        embeddings = []
        for doc in sample_docs:
            result = generate_mock_query_embedding(doc)
            if result["success"]:
                embeddings.append(result["embedding"])
        
        # Add to FAISS index
        doc_id = vector_store.add_document_embeddings(
            embeddings=embeddings,
            file_path="demo_documents.txt",
            file_type="txt",
            chunk_texts=sample_docs,
            doc_id="demo-collection"
        )
        
        print(f"✅ Created demo FAISS index with {len(embeddings)} documents")
        print(f"📊 Document ID: {doc_id}")
        
        return vector_store
        
    except ImportError as e:
        print(f"❌ FAISS not available: {e}")
        return None
    except Exception as e:
        print(f"❌ Error creating demo index: {e}")
        return None

if __name__ == "__main__":
    print("🧪 Mock Query Embedding Demo")
    print("=" * 40)
    
    # Test mock embedding generation
    test_queries = [
        "What is machine learning?",
        "How to build web APIs?", 
        "Python programming tutorials",
        "Vector similarity search",
        "Natural language processing"
    ]
    
    print("\n📝 Testing Mock Query Embeddings:")
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        
        result = generate_mock_query_embedding(query)
        
        if result["success"]:
            print(f"   ✅ Success!")
            print(f"   📊 Dimensions: {result['metadata']['dimensions']}")
            print(f"   📊 Model: {result['metadata']['model']}")
            print(f"   🎯 First 5 values: {[round(x, 4) for x in result['embedding'][:5]]}")
        else:
            print(f"   ❌ Error: {result['error']}")
    
    # Test consistency
    print(f"\n🔄 Testing Consistency:")
    query = "Machine learning algorithms"
    
    result1 = generate_mock_query_embedding(query)
    result2 = generate_mock_query_embedding(query)
    
    if result1["success"] and result2["success"]:
        if result1["embedding"] == result2["embedding"]:
            print("   ✅ Same query produces identical embeddings (good!)")
        else:
            print("   ❌ Same query produces different embeddings (bad!)")
    
    # Create demo FAISS index
    print(f"\n🗃️  Creating Demo FAISS Index:")
    demo_store = create_demo_faiss_index()
    
    if demo_store:
        # Test search
        print(f"\n🔍 Testing Mock Search:")
        search_query = "web development with Python"
        query_result = generate_mock_query_embedding(search_query)
        
        if query_result["success"]:
            results = demo_store.similarity_search(
                query_embedding=query_result["embedding"],
                k=3
            )
            
            print(f"   Query: '{search_query}'")
            print(f"   Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. Score: {result['score']:.4f}")
                print(f"      Text: {result['text'][:60]}...")
    
    print(f"\n💡 This demonstrates the query embedding functionality")
    print(f"   even when OpenAI API quota is exceeded!")
