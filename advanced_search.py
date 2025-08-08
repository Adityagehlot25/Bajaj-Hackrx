"""
Advanced Vector Search Functions for FAISS and Pinecone Integration
Provides comprehensive similarity search capabilities with filtering, ranking, and analytics
"""

from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np
import asyncio
from datetime import datetime
import logging
from faiss_store import get_vector_store
from gemini_vector_embedder import generate_embeddings

# Configure logging
logger = logging.getLogger(__name__)


class SearchResult:
    """Enhanced search result with additional metadata and methods"""
    
    def __init__(self, score: float, index: int, doc_id: str, chunk_text: str, 
                 metadata: Dict[str, Any], rank: int):
        self.score = score
        self.index = index
        self.doc_id = doc_id
        self.chunk_text = chunk_text
        self.metadata = metadata
        self.rank = rank
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "rank": self.rank,
            "index": self.index,
            "doc_id": self.doc_id,
            "text": self.chunk_text,
            "metadata": self.metadata,
            "relevance": self.get_relevance_category(),
            "snippet": self.get_text_snippet()
        }
    
    def get_relevance_category(self) -> str:
        """Categorize relevance based on similarity score"""
        if self.score < 0.3:
            return "high"
        elif self.score < 0.6:
            return "medium"
        elif self.score < 0.9:
            return "low"
        else:
            return "very_low"
    
    def get_text_snippet(self, max_length: int = 200) -> str:
        """Get a snippet of the text with ellipsis if too long"""
        if len(self.chunk_text) <= max_length:
            return self.chunk_text
        return self.chunk_text[:max_length-3] + "..."


async def advanced_similarity_search(
    query: Union[str, List[float]], 
    k: int = 10,
    score_threshold: Optional[float] = None,
    min_score_threshold: Optional[float] = None,
    filter_doc_ids: Optional[List[str]] = None,
    filter_doc_types: Optional[List[str]] = None,
    boost_recent: bool = False,
    deduplicate: bool = True,
    include_metadata: bool = True,
    api_key: Optional[str] = None,
    embedding_model: str = "embedding-001"
) -> Dict[str, Any]:
    """
    Advanced similarity search with comprehensive filtering and ranking
    
    Args:
        query: Query text string or pre-computed embedding vector
        k: Number of top results to return
        score_threshold: Maximum similarity score (lower is better for L2 distance)
        min_score_threshold: Minimum similarity score for inclusion
        filter_doc_ids: List of document IDs to restrict search to
        filter_doc_types: List of document types to filter by (pdf, docx, eml)
        boost_recent: Whether to boost more recently added documents
        deduplicate: Whether to remove similar results from same document
        include_metadata: Whether to include full metadata in results
        api_key: Optional Gemini API key for text queries
        embedding_model: Embedding model to use for text queries
        
    Returns:
        Comprehensive search results with analytics and metadata
    """
    start_time = datetime.now()
    
    try:
        # Get vector store
        vector_store = get_vector_store()
        
        if vector_store.get_stats()["total_vectors"] == 0:
            return {
                "status": "success",
                "results": [],
                "total_results": 0,
                "query_info": {
                    "query_type": "text" if isinstance(query, str) else "vector",
                    "query_text": query if isinstance(query, str) else None,
                    "k": k,
                    "filters_applied": {
                        "score_threshold": score_threshold,
                        "doc_ids": filter_doc_ids,
                        "doc_types": filter_doc_types
                    }
                },
                "analytics": {
                    "search_time_ms": 0,
                    "index_size": 0,
                    "total_documents": 0
                },
                "message": "No documents in index"
            }
        
        # Convert query to embedding if it's text
        query_embedding = None
        query_metadata = {}
        
        if isinstance(query, str):
            from main import generate_query_embedding
            
            embedding_result = await generate_query_embedding(
                query_text=query,
                api_key=api_key,
                model=embedding_model
            )
            
            if not embedding_result.get("success"):
                return {
                    "status": "error",
                    "error": f"Failed to generate query embedding: {embedding_result.get('error')}",
                    "results": []
                }
            
            query_embedding = embedding_result["embedding"]
            query_metadata = embedding_result["metadata"]
            
        else:
            query_embedding = query
            query_metadata = {"dimensions": len(query_embedding)}
        
        # Perform initial similarity search with extra results for filtering
        search_k = min(k * 3, vector_store.get_stats()["total_vectors"])
        
        raw_results = vector_store.similarity_search(
            query_embedding=query_embedding,
            k=search_k,
            score_threshold=score_threshold,
            filter_doc_ids=filter_doc_ids
        )
        
        # Apply additional filters and enhancements
        enhanced_results = []
        seen_doc_chunks = set() if deduplicate else None
        
        for idx, result in enumerate(raw_results):
            metadata = result["metadata"]
            
            # Filter by document type
            if filter_doc_types and metadata.get("file_type", "").lower() not in [t.lower() for t in filter_doc_types]:
                continue
            
            # Apply minimum score threshold
            if min_score_threshold is not None and result["score"] > min_score_threshold:
                continue
            
            # Deduplicate similar chunks from same document
            if deduplicate:
                doc_chunk_key = f"{metadata['doc_id']}_{metadata['chunk_index']//3}"  # Group nearby chunks
                if doc_chunk_key in seen_doc_chunks:
                    continue
                seen_doc_chunks.add(doc_chunk_key)
            
            # Create enhanced result
            enhanced_result = SearchResult(
                score=result["score"],
                index=result["index"],
                doc_id=metadata["doc_id"],
                chunk_text=result["text"],
                metadata=metadata if include_metadata else {},
                rank=len(enhanced_results) + 1
            )
            
            enhanced_results.append(enhanced_result)
            
            if len(enhanced_results) >= k:
                break
        
        # Apply recency boost if requested
        if boost_recent and enhanced_results:
            enhanced_results = _apply_recency_boost(enhanced_results)
            enhanced_results.sort(key=lambda x: x.score)  # Re-sort by adjusted scores
            
            # Update ranks
            for i, result in enumerate(enhanced_results):
                result.rank = i + 1
        
        # Calculate analytics
        end_time = datetime.now()
        search_time_ms = (end_time - start_time).total_seconds() * 1000
        
        index_stats = vector_store.get_stats()
        
        # Prepare final results
        final_results = [result.to_dict() for result in enhanced_results]
        
        return {
            "status": "success",
            "results": final_results,
            "total_results": len(final_results),
            "query_info": {
                "query_type": "text" if isinstance(query, str) else "vector",
                "query_text": query if isinstance(query, str) else None,
                "embedding_metadata": query_metadata,
                "k": k,
                "filters_applied": {
                    "score_threshold": score_threshold,
                    "min_score_threshold": min_score_threshold,
                    "doc_ids": filter_doc_ids,
                    "doc_types": filter_doc_types,
                    "boost_recent": boost_recent,
                    "deduplicate": deduplicate
                }
            },
            "analytics": {
                "search_time_ms": round(search_time_ms, 2),
                "initial_candidates": len(raw_results),
                "filtered_results": len(final_results),
                "index_size": index_stats["total_vectors"],
                "total_documents": index_stats["total_documents"],
                "relevance_distribution": _calculate_relevance_distribution(enhanced_results)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in advanced similarity search: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "results": []
        }


def _apply_recency_boost(results: List[SearchResult]) -> List[SearchResult]:
    """Apply recency boost to search results based on document creation time"""
    
    if not results:
        return results
    
    # Get creation times and calculate recency scores
    now = datetime.now()
    
    for result in results:
        created_at_str = result.metadata.get("created_at", now.isoformat())
        try:
            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            days_ago = (now - created_at).days
            
            # Apply exponential decay: more recent = lower boost to distance
            # This reduces the similarity score (making it better) for recent documents
            recency_factor = np.exp(-days_ago / 30.0) * 0.1  # 30-day half-life
            result.score = result.score * (1.0 - recency_factor)
            
        except (ValueError, TypeError):
            # If we can't parse the date, don't apply boost
            continue
    
    return results


def _calculate_relevance_distribution(results: List[SearchResult]) -> Dict[str, int]:
    """Calculate distribution of relevance categories in results"""
    
    distribution = {"high": 0, "medium": 0, "low": 0, "very_low": 0}
    
    for result in results:
        category = result.get_relevance_category()
        distribution[category] += 1
    
    return distribution


async def multi_query_search(
    queries: List[str],
    k: int = 5,
    combination_method: str = "average",
    **kwargs
) -> Dict[str, Any]:
    """
    Perform similarity search with multiple queries and combine results
    
    Args:
        queries: List of query strings
        k: Number of results per query
        combination_method: How to combine scores ('average', 'max', 'min', 'weighted')
        **kwargs: Additional arguments passed to advanced_similarity_search
        
    Returns:
        Combined search results from multiple queries
    """
    
    if not queries:
        return {"status": "error", "error": "No queries provided", "results": []}
    
    # Perform search for each query
    all_results = []
    query_results = {}
    
    for i, query in enumerate(queries):
        result = await advanced_similarity_search(query, k=k*2, **kwargs)  # Get extra results
        if result["status"] == "success":
            query_results[f"query_{i}"] = result
            all_results.extend(result["results"])
    
    if not all_results:
        return {"status": "error", "error": "No results from any query", "results": []}
    
    # Combine results by document chunk
    combined_scores = {}
    
    for result in all_results:
        key = f"{result['doc_id']}_{result['index']}"
        
        if key not in combined_scores:
            combined_scores[key] = {
                "result": result,
                "scores": [],
                "queries": []
            }
        
        combined_scores[key]["scores"].append(result["score"])
        combined_scores[key]["queries"].append(len(combined_scores[key]["scores"]) - 1)
    
    # Apply combination method
    final_results = []
    
    for key, data in combined_scores.items():
        scores = data["scores"]
        result = data["result"].copy()
        
        if combination_method == "average":
            combined_score = np.mean(scores)
        elif combination_method == "max":
            combined_score = np.max(scores)
        elif combination_method == "min":
            combined_score = np.min(scores)
        elif combination_method == "weighted":
            # Weight by number of queries that returned this result
            weights = [1.0 / (i + 1) for i in range(len(scores))]
            combined_score = np.average(scores, weights=weights)
        else:
            combined_score = np.mean(scores)
        
        result["score"] = float(combined_score)
        result["multi_query_info"] = {
            "query_count": len(scores),
            "individual_scores": scores,
            "combination_method": combination_method
        }
        
        final_results.append(result)
    
    # Sort by combined score and limit results
    final_results.sort(key=lambda x: x["score"])
    final_results = final_results[:k]
    
    # Update ranks
    for i, result in enumerate(final_results):
        result["rank"] = i + 1
    
    return {
        "status": "success",
        "results": final_results,
        "total_results": len(final_results),
        "query_info": {
            "queries": queries,
            "combination_method": combination_method,
            "individual_query_results": len(query_results)
        }
    }


async def search_with_context(
    query: str,
    context_window: int = 2,
    k: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """
    Perform similarity search and include surrounding context chunks
    
    Args:
        query: Search query
        context_window: Number of adjacent chunks to include before/after matches
        k: Number of primary results
        **kwargs: Additional search parameters
        
    Returns:
        Search results with expanded context
    """
    
    # Perform initial search
    search_result = await advanced_similarity_search(query, k=k, **kwargs)
    
    if search_result["status"] != "success":
        return search_result
    
    vector_store = get_vector_store()
    enhanced_results = []
    
    for result in search_result["results"]:
        doc_id = result["doc_id"]
        chunk_index = result["metadata"]["chunk_index"]
        
        # Get all chunks for this document
        doc_chunks = vector_store.get_document_chunks(doc_id)
        
        # Find context chunks
        context_chunks = []
        start_idx = max(0, chunk_index - context_window)
        end_idx = min(len(doc_chunks), chunk_index + context_window + 1)
        
        for i in range(start_idx, end_idx):
            if i < len(doc_chunks):
                context_chunk = doc_chunks[i]
                context_chunk["is_match"] = (i == chunk_index)
                context_chunk["context_position"] = i - chunk_index
                context_chunks.append(context_chunk)
        
        # Enhance result with context
        enhanced_result = result.copy()
        enhanced_result["context_chunks"] = context_chunks
        enhanced_result["context_text"] = " ".join([chunk["text"] for chunk in context_chunks])
        
        enhanced_results.append(enhanced_result)
    
    # Update the results
    search_result["results"] = enhanced_results
    search_result["query_info"]["context_window"] = context_window
    
    return search_result


# Export main search function for easy import
search_similar_chunks = advanced_similarity_search
