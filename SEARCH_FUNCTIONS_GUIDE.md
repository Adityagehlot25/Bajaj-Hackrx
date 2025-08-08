# 🔍 Advanced Vector Search Functions - Usage Examples

Your FastAPI application now includes comprehensive vector search capabilities that go far beyond basic similarity search. Here's what you can do:

## 🎯 Core Function: `search_similar_chunks`

**POST /index/search-similar-chunks** - The main function for finding top-N similar chunks

```powershell
# PowerShell Example: Search with pre-computed embedding vector
$embedding = @(0.1, 0.2, 0.3)  # Your 768-dimensional vector here
$searchData = @{
    query_embedding = $embedding
    k = 10
    score_threshold = 0.8
    deduplicate = $true
    boost_recent = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:3000/index/search-similar-chunks" -Method Post -Body $searchData -ContentType "application/json"
```

## 🚀 Advanced Search Features

### 1. **Advanced Search** - POST /index/advanced-search
Most comprehensive search with all filtering options:

```powershell
$advancedSearch = @{
    query = "artificial intelligence machine learning"
    k = 15
    score_threshold = 0.7
    min_score_threshold = 0.1
    filter_doc_types = @("pdf", "docx")
    boost_recent = $true
    deduplicate = $true
    include_metadata = $true
    embedding_model = "embedding-001"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:3000/index/advanced-search" -Method Post -Body $advancedSearch -ContentType "application/json"
```

### 2. **Multi-Query Search** - POST /index/multi-query-search  
Search with multiple related queries and combine results:

```powershell
$multiQuery = @{
    queries = @(
        "artificial intelligence",
        "machine learning algorithms", 
        "neural networks deep learning"
    )
    k = 10
    combination_method = "average"  # or "max", "min", "weighted"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:3000/index/multi-query-search" -Method Post -Body $multiQuery -ContentType "application/json"
```

### 3. **Context Search** - POST /index/context-search
Get matching chunks plus surrounding context:

```powershell
$contextSearch = @{
    query = "machine learning"
    context_window = 3  # Include 3 chunks before/after each match
    k = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:3000/index/context-search" -Method Post -Body $contextSearch -ContentType "application/json"
```

## 🎛️ Search Parameters Explained

### **Core Parameters:**
- `k`: Number of results to return (default: 10)
- `query`: Search text or pre-computed embedding vector
- `score_threshold`: Maximum similarity score (lower = more similar)
- `min_score_threshold`: Minimum similarity score for inclusion

### **Filtering Options:**
- `filter_doc_ids`: Search only specific documents
- `filter_doc_types`: Filter by file type ("pdf", "docx", "eml")
- `boost_recent`: Boost more recently added documents
- `deduplicate`: Remove similar results from same document

### **Output Control:**
- `include_metadata`: Include full document metadata
- `context_window`: Include surrounding chunks (context search)

## 📊 Response Format

All search functions return comprehensive results:

```json
{
  "status": "success",
  "results": [
    {
      "score": 0.234,           // Lower = more similar
      "rank": 1,                // Position in results
      "doc_id": "uuid-string",  // Document identifier
      "text": "chunk content...", // The actual text
      "metadata": {
        "file_path": "/path/to/doc.pdf",
        "file_type": "pdf",
        "chunk_index": 5,
        "total_chunks": 20,
        "created_at": "2025-01-01T10:00:00"
      },
      "relevance": "high",      // high/medium/low/very_low
      "snippet": "short preview..."
    }
  ],
  "total_results": 5,
  "query_info": {
    "query_text": "your search query",
    "embedding_metadata": {
      "model": "embedding-001",
      "dimensions": 768,
      "total_tokens": 15
    },
    "filters_applied": {...}
  },
  "analytics": {
    "search_time_ms": 45.6,
    "initial_candidates": 100,
    "filtered_results": 5,
    "index_size": 1000,
    "total_documents": 50,
    "relevance_distribution": {
      "high": 2,
      "medium": 2, 
      "low": 1,
      "very_low": 0
    }
  }
}
```

## 🔬 Use Cases

### **1. Basic Similarity Search**
Find documents most similar to a query:
```
POST /index/search-similar-chunks
```

### **2. Filtered Document Search** 
Search only PDFs from specific documents:
```json
{
  "query": "financial analysis",
  "filter_doc_types": ["pdf"],
  "filter_doc_ids": ["doc1", "doc2"]
}
```

### **3. Comprehensive Research**
Multiple search terms with context:
```json
{
  "queries": ["climate change", "global warming", "carbon emissions"],
  "context_window": 2,
  "combination_method": "weighted"
}
```

### **4. Recent Document Priority**
Boost newer documents in results:
```json
{
  "query": "quarterly report",
  "boost_recent": true,
  "deduplicate": true
}
```

## 🎯 Key Features

✅ **Multiple search strategies** (single, multi-query, context-aware)  
✅ **Advanced filtering** by document type, ID, date, score thresholds  
✅ **Smart deduplication** to avoid repetitive results  
✅ **Recency boosting** for time-sensitive searches  
✅ **Relevance categorization** (high/medium/low scoring)  
✅ **Performance analytics** with timing and statistics  
✅ **Context expansion** to understand surrounding content  
✅ **Flexible result combination** methods for multi-query searches  

## 🚀 Your Search Arsenal

You now have **4 powerful search endpoints**:

1. `/index/search-similar-chunks` - Core vector similarity search
2. `/index/advanced-search` - Full-featured search with all options  
3. `/index/multi-query-search` - Multiple queries with result combination
4. `/index/context-search` - Search with surrounding context chunks

These functions provide enterprise-grade search capabilities suitable for:
- Document Q&A systems
- Knowledge base search
- Research and analysis tools
- Content discovery platforms
- Semantic search applications

**Your FastAPI server now rivals professional search platforms! 🎉**
