"""
Natural Language Query Embedding - Usage Examples

This demonstrates how to use the new generate_query_embedding function
and the /query-embedding endpoint for natural language search.
"""

import asyncio
import sys
import os

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Example of direct function usage (if running within the same application)
async def example_direct_usage():
    """Example of using the generate_query_embedding function directly"""
    print("📚 Direct Function Usage Example")
    print("=" * 50)
    
    # Import the function (this would work if running in the same process)
    try:
        # Note: This would only work if running in the same Python process as main.py
        # For external usage, use the HTTP API endpoint instead
        from main import generate_query_embedding
        
        query = "Find documents about machine learning algorithms"
        
        result = await generate_query_embedding(
            query_text=query,
            api_key="your-openai-api-key",  # Use your actual API key
            model="text-embedding-3-small"
        )
        
        if result["success"]:
            print(f"✅ Query: {result['query_text']}")
            print(f"📊 Model: {result['metadata']['model']}")
            print(f"📊 Dimensions: {result['metadata']['dimensions']}")
            print(f"📊 Tokens: {result['metadata']['total_tokens']}")
            print(f"🎯 Embedding preview: {result['embedding'][:5]}")
        else:
            print(f"❌ Error: {result['error']}")
            
    except ImportError:
        print("ℹ️  Direct import not available - use HTTP API endpoint instead")

# Example curl commands for API usage
def show_api_examples():
    """Show API usage examples"""
    print("\n🌐 HTTP API Usage Examples")
    print("=" * 50)
    
    print("\n1️⃣ Generate Query Embedding:")
    print("curl -X POST 'http://localhost:3000/query-embedding' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "query_text": "Find information about artificial intelligence",')
    print('    "api_key": "your-openai-api-key",')
    print('    "embedding_model": "text-embedding-3-small"')
    print("  }'")
    
    print("\n2️⃣ Use for Similarity Search:")
    print("# Step 1: Get the embedding")
    print("EMBEDDING=$(curl -s -X POST 'http://localhost:3000/query-embedding' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"query_text\": \"machine learning\", \"api_key\": \"your-key\"}' \\")
    print("  | jq -r '.embedding')")
    print()
    print("# Step 2: Use it for search")
    print("curl -X POST 'http://localhost:3000/index/search' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d \"{")
    print('    \\\"query_embedding\\\": $EMBEDDING,')
    print('    \\\"k\\\": 5')
    print("  }\"")
    
    print("\n3️⃣ Direct Text Search (Easier):")
    print("curl -X POST 'http://localhost:3000/index/search-by-text' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "query_text": "machine learning algorithms",')
    print('    "k": 5,')
    print('    "api_key": "your-openai-api-key"')
    print("  }'")

# Python requests example
def show_python_requests_example():
    """Show Python requests library example"""
    print("\n🐍 Python Requests Example")
    print("=" * 50)
    
    code_example = '''
import requests
import json

# Configuration
BASE_URL = "http://localhost:3000"
API_KEY = "your-openai-api-key"

def generate_query_embedding(query_text):
    """Generate embedding for a query using the API"""
    url = f"{BASE_URL}/query-embedding"
    payload = {
        "query_text": query_text,
        "api_key": API_KEY,
        "embedding_model": "text-embedding-3-small"
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        return result["embedding"]
    else:
        raise Exception(f"API error: {response.status_code} - {response.text}")

def search_by_embedding(embedding_vector, k=5):
    """Search using an embedding vector"""
    url = f"{BASE_URL}/index/search"
    payload = {
        "query_embedding": embedding_vector,
        "k": k
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json()["results"]
    else:
        raise Exception(f"Search error: {response.status_code} - {response.text}")

# Usage example
if __name__ == "__main__":
    query = "Find documents about web development with Python"
    
    # Generate embedding
    embedding = generate_query_embedding(query)
    print(f"Generated embedding with {len(embedding)} dimensions")
    
    # Search using the embedding
    results = search_by_embedding(embedding, k=3)
    
    print(f"Found {len(results)} similar documents:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.4f}")
        print(f"   Text: {result['text'][:100]}...")
    '''
    
    print(code_example)

# Use cases
def show_use_cases():
    """Show practical use cases"""
    print("\n🎯 Practical Use Cases")
    print("=" * 50)
    
    use_cases = [
        {
            "title": "Document Search Engine",
            "description": "Convert user search queries into embeddings for semantic document search",
            "example": "Query: 'How to deploy machine learning models?' → Find relevant documentation"
        },
        {
            "title": "FAQ Matching", 
            "description": "Match user questions to pre-indexed FAQ answers",
            "example": "Query: 'Password reset issues' → Find FAQ: 'How to reset your password'"
        },
        {
            "title": "Content Recommendation",
            "description": "Recommend similar articles or documents based on current reading",
            "example": "Query: Current article content → Find related articles to suggest"
        },
        {
            "title": "Chatbot Context Retrieval",
            "description": "Retrieve relevant context for chatbot responses using RAG",
            "example": "Query: User message → Find relevant knowledge base entries"
        },
        {
            "title": "Code Search",
            "description": "Search code repositories using natural language descriptions",
            "example": "Query: 'Function to parse JSON files' → Find relevant code snippets"
        }
    ]
    
    for i, use_case in enumerate(use_cases, 1):
        print(f"{i}️⃣ {use_case['title']}")
        print(f"   📝 {use_case['description']}")
        print(f"   💡 {use_case['example']}")
        print()

if __name__ == "__main__":
    print("🔍 Natural Language Query Embedding - Complete Guide")
    print("=" * 60)
    
    try:
        # Show all examples
        asyncio.run(example_direct_usage())
        show_api_examples()
        show_python_requests_example()
        show_use_cases()
        
        print("\n✨ Key Benefits:")
        print("• 🚀 Dedicated function for query processing")
        print("• 🎯 Consistent API for generating query embeddings")  
        print("• 🔄 Easy integration with FAISS similarity search")
        print("• 📊 Detailed metadata about the embedding process")
        print("• 🛡️ Error handling and validation")
        
        print(f"\n🔗 Test your implementation at: http://localhost:3000/docs")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
