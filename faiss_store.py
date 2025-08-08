"""
FAISS Vector Store for Document Embeddings
Handles vector similarity search with unique document IDs
"""

import faiss
import numpy as np
import json
import pickle
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import uuid
from datetime import datetime


class DocumentMetadata:
    """Metadata for stored documents"""
    def __init__(self, doc_id: str, file_path: str, file_type: str, 
                 chunk_index: int, chunk_text: str, total_chunks: int,
                 created_at: str = None):
        self.doc_id = doc_id
        self.file_path = file_path
        self.file_type = file_type
        self.chunk_index = chunk_index
        self.chunk_text = chunk_text
        self.total_chunks = total_chunks
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "chunk_index": self.chunk_index,
            "chunk_text": self.chunk_text,
            "total_chunks": self.total_chunks,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentMetadata':
        return cls(**data)


class FAISSVectorStore:
    """
    FAISS-based vector store for document embeddings with similarity search
    """
    
    def __init__(self, dimension: int = 768, index_type: str = "flat"):
        """
        Initialize FAISS vector store
        
        Args:
            dimension: Vector dimension (768 for embedding-001, 1536 for text-embedding-3-small)
            index_type: Type of FAISS index ('flat', 'ivf', 'hnsw')
        """
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.metadata_store: Dict[int, DocumentMetadata] = {}
        self.doc_id_to_indices: Dict[str, List[int]] = {}
        self.next_id = 0
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize the FAISS index based on the specified type"""
        if self.index_type == "flat":
            # Exact search using L2 distance
            self.index = faiss.IndexFlatL2(self.dimension)
        elif self.index_type == "ivf":
            # Inverted file index for faster approximate search
            nlist = 100  # number of clusters
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
        elif self.index_type == "hnsw":
            # Hierarchical Navigable Small World for fast approximate search
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            self.index.hnsw.efConstruction = 200
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")
    
    def add_document_embeddings(self, 
                              embeddings: List[List[float]], 
                              file_path: str,
                              file_type: str,
                              chunk_texts: List[str],
                              doc_id: Optional[str] = None) -> str:
        """
        Add document embeddings to the FAISS index
        
        Args:
            embeddings: List of embedding vectors
            file_path: Path to the source document
            file_type: Type of document (pdf, docx, eml)
            chunk_texts: List of text chunks corresponding to embeddings
            doc_id: Optional unique document ID (will generate if not provided)
        
        Returns:
            Document ID used for storage
        """
        if not embeddings:
            raise ValueError("No embeddings provided")
        
        if len(embeddings) != len(chunk_texts):
            raise ValueError("Number of embeddings must match number of chunk texts")
        
        # Generate unique document ID if not provided
        if doc_id is None:
            doc_id = str(uuid.uuid4())
        
        # Convert embeddings to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Check dimension consistency
        if embeddings_array.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension {embeddings_array.shape[1]} doesn't match index dimension {self.dimension}")
        
        # Train index if needed (for IVF)
        if self.index_type == "ivf" and not self.index.is_trained:
            if embeddings_array.shape[0] >= 100:  # Need enough training data
                self.index.train(embeddings_array)
            else:
                # Use existing data if available, otherwise create dummy training data
                if self.index.ntotal > 100:
                    print("IVF index already trained")
                else:
                    # Create some dummy training data if we don't have enough
                    dummy_data = np.random.random((100, self.dimension)).astype(np.float32)
                    self.index.train(dummy_data)
        
        # Get starting index for this document
        start_idx = self.next_id
        indices_for_doc = []
        
        # Add embeddings and metadata
        for i, (embedding, chunk_text) in enumerate(zip(embeddings_array, chunk_texts)):
            current_idx = self.next_id
            indices_for_doc.append(current_idx)
            
            # Store metadata
            metadata = DocumentMetadata(
                doc_id=doc_id,
                file_path=file_path,
                file_type=file_type,
                chunk_index=i,
                chunk_text=chunk_text,
                total_chunks=len(embeddings)
            )
            self.metadata_store[current_idx] = metadata
            
            self.next_id += 1
        
        # Add all embeddings to index at once
        self.index.add(embeddings_array)
        
        # Track document ID to indices mapping
        if doc_id in self.doc_id_to_indices:
            self.doc_id_to_indices[doc_id].extend(indices_for_doc)
        else:
            self.doc_id_to_indices[doc_id] = indices_for_doc
        
        return doc_id
    
    def similarity_search(self, 
                         query_embedding: List[float], 
                         k: int = 5,
                         score_threshold: Optional[float] = None,
                         filter_doc_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Perform similarity search against stored embeddings
        
        Args:
            query_embedding: Query vector for similarity search
            k: Number of results to return
            score_threshold: Optional score threshold (lower is better for L2)
            filter_doc_ids: Optional list of document IDs to filter results
        
        Returns:
            List of search results with metadata and scores
        """
        if self.index.ntotal == 0:
            return []
        
        # Convert query to numpy array
        query_vector = np.array([query_embedding], dtype=np.float32)
        
        if query_vector.shape[1] != self.dimension:
            raise ValueError(f"Query embedding dimension {query_vector.shape[1]} doesn't match index dimension {self.dimension}")
        
        # Perform search
        scores, indices = self.index.search(query_vector, min(k * 2, self.index.ntotal))  # Get extra results for filtering
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
                
            if idx not in self.metadata_store:
                continue
                
            metadata = self.metadata_store[idx]
            
            # Apply document ID filter if specified
            if filter_doc_ids and metadata.doc_id not in filter_doc_ids:
                continue
            
            # Apply score threshold if specified
            if score_threshold is not None and score > score_threshold:
                continue
            
            result = {
                "score": float(score),
                "index": int(idx),
                "metadata": metadata.to_dict(),
                "text": metadata.chunk_text
            }
            results.append(result)
            
            if len(results) >= k:
                break
        
        return results
    
    def get_document_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific document ID
        
        Args:
            doc_id: Document ID to retrieve chunks for
        
        Returns:
            List of document chunks with metadata
        """
        if doc_id not in self.doc_id_to_indices:
            return []
        
        chunks = []
        for idx in self.doc_id_to_indices[doc_id]:
            if idx in self.metadata_store:
                metadata = self.metadata_store[idx]
                chunks.append({
                    "index": idx,
                    "metadata": metadata.to_dict(),
                    "text": metadata.chunk_text
                })
        
        # Sort by chunk index
        chunks.sort(key=lambda x: x["metadata"]["chunk_index"])
        return chunks
    
    def remove_document(self, doc_id: str) -> bool:
        """
        Remove all chunks for a specific document ID
        Note: FAISS doesn't support removal, so we just remove from metadata
        
        Args:
            doc_id: Document ID to remove
        
        Returns:
            True if document was found and removed, False otherwise
        """
        if doc_id not in self.doc_id_to_indices:
            return False
        
        # Remove metadata
        indices_to_remove = self.doc_id_to_indices[doc_id]
        for idx in indices_to_remove:
            if idx in self.metadata_store:
                del self.metadata_store[idx]
        
        # Remove document ID mapping
        del self.doc_id_to_indices[doc_id]
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": self.index_type,
            "total_documents": len(self.doc_id_to_indices),
            "total_chunks": len(self.metadata_store),
            "is_trained": getattr(self.index, 'is_trained', True)
        }
    
    def save(self, filepath: str):
        """
        Save the FAISS index and metadata to disk
        
        Args:
            filepath: Base filepath (without extension)
        """
        # Save FAISS index
        faiss.write_index(self.index, f"{filepath}.faiss")
        
        # Save metadata and mappings
        metadata_dict = {
            "metadata_store": {k: v.to_dict() for k, v in self.metadata_store.items()},
            "doc_id_to_indices": self.doc_id_to_indices,
            "next_id": self.next_id,
            "dimension": self.dimension,
            "index_type": self.index_type
        }
        
        with open(f"{filepath}_metadata.json", 'w') as f:
            json.dump(metadata_dict, f, indent=2)
    
    def load(self, filepath: str):
        """
        Load the FAISS index and metadata from disk
        
        Args:
            filepath: Base filepath (without extension)
        """
        # Load FAISS index
        if os.path.exists(f"{filepath}.faiss"):
            self.index = faiss.read_index(f"{filepath}.faiss")
        
        # Load metadata and mappings
        if os.path.exists(f"{filepath}_metadata.json"):
            with open(f"{filepath}_metadata.json", 'r') as f:
                metadata_dict = json.load(f)
            
            # Restore metadata store
            self.metadata_store = {
                int(k): DocumentMetadata.from_dict(v) 
                for k, v in metadata_dict["metadata_store"].items()
            }
            
            # Restore mappings
            self.doc_id_to_indices = {
                k: [int(idx) for idx in v] 
                for k, v in metadata_dict["doc_id_to_indices"].items()
            }
            
            self.next_id = metadata_dict["next_id"]
            self.dimension = metadata_dict["dimension"]
            self.index_type = metadata_dict["index_type"]


# Global vector store instance
vector_store = None

def get_vector_store(dimension: int = 768, index_type: str = "flat") -> FAISSVectorStore:
    """
    Get or create global vector store instance
    
    Args:
        dimension: Vector dimension
        index_type: Type of FAISS index
    
    Returns:
        FAISSVectorStore instance
    """
    global vector_store
    if vector_store is None:
        vector_store = FAISSVectorStore(dimension=dimension, index_type=index_type)
    return vector_store

def reset_vector_store():
    """Reset the global vector store instance"""
    global vector_store
    vector_store = None
