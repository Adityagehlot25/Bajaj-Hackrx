"""
Simple demonstration of FAISS vector store functionality
Run this after installing FAISS: pip install faiss-cpu numpy
"""

import sys
import os

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from faiss_store import FAISSVectorStore, DocumentMetadata
    import numpy as np
    print("✅ FAISS and numpy imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required packages:")
    print("pip install faiss-cpu numpy")
    sys.exit(1)

def demo_faiss_functionality():
    """Demonstrate FAISS vector store capabilities"""
    
    print("\n🧪 FAISS Vector Store Demo")
    print("=" * 50)
    
    # Create vector store
    print("\n1️⃣ Creating FAISS vector store...")
    vector_store = FAISSVectorStore(dimension=1536, index_type="flat")
    print(f"   ✅ Created vector store with {vector_store.dimension} dimensions")
    
    # Create sample embeddings (1536 dimensions for OpenAI text-embedding-3-small)
    print("\n2️⃣ Creating sample embeddings...")
    np.random.seed(42)  # For reproducible results
    sample_embeddings = [
        np.random.rand(1536).tolist(),
        np.random.rand(1536).tolist(),
        np.random.rand(1536).tolist()
    ]
    
    sample_texts = [
        "This is a document about machine learning and artificial intelligence.",
        "FastAPI is a modern web framework for building APIs with Python 3.6+.",
        "Vector databases enable efficient similarity search and retrieval."
    ]
    
    print(f"   ✅ Generated {len(sample_embeddings)} sample embeddings")
    
    # Add documents to index
    print("\n3️⃣ Adding documents to FAISS index...")
    doc_id_1 = vector_store.add_document_embeddings(
        embeddings=sample_embeddings,
        file_path="sample_document.txt",
        file_type="txt",
        chunk_texts=sample_texts,
        doc_id="demo-doc-1"
    )
    print(f"   ✅ Added document with ID: {doc_id_1}")
    
    # Get index statistics
    print("\n4️⃣ Index statistics...")
    stats = vector_store.get_stats()
    print(f"   📊 Total vectors: {stats['total_vectors']}")
    print(f"   📊 Total documents: {stats['total_documents']}")
    print(f"   📊 Total chunks: {stats['total_chunks']}")
    print(f"   📊 Index type: {stats['index_type']}")
    
    # Perform similarity search
    print("\n5️⃣ Performing similarity search...")
    # Use the first embedding as a query (should find itself with score 0)
    query_embedding = sample_embeddings[0]
    
    results = vector_store.similarity_search(
        query_embedding=query_embedding,
        k=3
    )
    
    print(f"   🔍 Found {len(results)} similar documents:")
    for i, result in enumerate(results):
        print(f"      {i+1}. Score: {result['score']:.4f}")
        print(f"          Text: {result['text'][:60]}...")
        print(f"          Doc ID: {result['metadata']['doc_id']}")
    
    # Get document chunks
    print("\n6️⃣ Retrieving document chunks...")
    chunks = vector_store.get_document_chunks(doc_id_1)
    print(f"   📄 Document {doc_id_1} has {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"      Chunk {i+1}: {chunk['text'][:50]}...")
    
    # Add another document
    print("\n7️⃣ Adding second document...")
    more_embeddings = [
        np.random.rand(1536).tolist(),
        np.random.rand(1536).tolist()
    ]
    
    more_texts = [
        "Python is a versatile programming language for data science and web development.",
        "FAISS (Facebook AI Similarity Search) enables efficient similarity search at scale."
    ]
    
    doc_id_2 = vector_store.add_document_embeddings(
        embeddings=more_embeddings,
        file_path="second_document.txt",
        file_type="txt",
        chunk_texts=more_texts,
        doc_id="demo-doc-2"
    )
    print(f"   ✅ Added second document with ID: {doc_id_2}")
    
    # Final statistics
    print("\n8️⃣ Final statistics...")
    final_stats = vector_store.get_stats()
    print(f"   📊 Total vectors: {final_stats['total_vectors']}")
    print(f"   📊 Total documents: {final_stats['total_documents']}")
    print(f"   📊 Total chunks: {final_stats['total_chunks']}")
    
    # Test filtered search
    print("\n9️⃣ Testing filtered search...")
    results = vector_store.similarity_search(
        query_embedding=more_embeddings[0],
        k=5,
        filter_doc_ids=["demo-doc-2"]
    )
    print(f"   🔍 Filtered search found {len(results)} results from demo-doc-2")
    
    print("\n🎉 FAISS demo completed successfully!")
    return vector_store

if __name__ == "__main__":
    try:
        demo_faiss_functionality()
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
