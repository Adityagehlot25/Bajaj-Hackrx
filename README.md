# 🚀 Document AI Q&A System API Documentation

A comprehensive FastAPI-based document processing and question-answering system powered by Google's Gemini AI and FAISS vector search.

## Features

- ✅ Health check endpoint
- ✅ Document upload from URLs
- ✅ Document parsing (PDF, DOCX, EML)
- ✅ Intelligent text chunking (500-1000 words)
- ✅ **Vector embeddings generation (OpenAI API)**
- ✅ **FAISS vector database for similarity search**
- ✅ **Document indexing with unique IDs**
- ✅ **Similarity search by embedding or natural language**
- ✅ **Complete document-to-embeddings-to-search pipeline**
- ✅ Temporary file storage
- ✅ Async file downloading with httpx
- ✅ Error handling and comprehensive logging
- ✅ Automatic API documentation

## Installation

1. Install the dependencies:
```bash
pip install -r requirements.txt
```

Or use the installation script:
```bash
install_with_faiss.bat
```

2. **Set up OpenAI API key** (required for embedding functionality):
```bash
# Linux/Mac
export OPENAI_API_KEY="your-openai-api-key-here"

# Windows
set OPENAI_API_KEY=your-openai-api-key-here
```

**Required packages:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `httpx` - Async HTTP client
- `pydantic` - Data validation
- `PyPDF2` - PDF text extraction
- `python-docx` - DOCX document parsing
- `openai` - **OpenAI API client for embeddings**
- `faiss-cpu` - **Vector similarity search engine**
- `numpy` - **Numerical computing for vectors**
- `email` - Email (.eml) parsing (built-in)

## Running the Application

Run the FastAPI application:
```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload
```

The application will be available at `http://localhost:8000`

## Endpoints

### GET /health
Returns the health status of the application.

**Response:**
```json
{"status": "ok"}
```

### POST /embed
Generate vector embeddings for text chunks using OpenAI's embedding API.

**Request Body:**
```json
{
  "text_chunks": [
    "This is the first chunk of text to embed...",
    "This is the second chunk of text to embed..."
  ],
  "model": "text-embedding-3-small",
  "api_key": "optional_api_key_override"
}
```

**Response:**
```json
{
  "status": "success",
  "embeddings": [
    [0.1234, -0.5678, 0.9012, ...],
    [0.2345, -0.6789, 0.8901, ...]
  ],
  "model": "text-embedding-3-small",
  "total_chunks": 2,
  "dimensions": 1536,
  "total_tokens": 245
}
```

### POST /parse-and-embed
Parse a document and generate embeddings for its text chunks in one step.

**Request Body:**
```json
{
  "file_path": "/path/to/document.pdf",
  "min_chunk_words": 500,
  "max_chunk_words": 1000,
  "embedding_model": "text-embedding-3-small",
  "api_key": "optional_api_key_override"
}
```

**Response:**
```json
{
  "status": "success",
  "file_path": "/path/to/document.pdf",
  "file_type": "pdf",
  "total_chunks": 5,
  "total_words": 3500,
  "chunks_with_embeddings": [
    {
      "chunk_id": 0,
      "text": "Chunk text content...",
      "word_count": 750,
      "embedding": [0.1234, -0.5678, ...],
      "embedding_model": "text-embedding-3-small"
    }
  ],
  "embedding_metadata": {
    "model": "text-embedding-3-small",
    "total_embedded": 5,
    "dimensions": 1536,
    "total_tokens": 1250,
    "success": true
  }
}
```

### POST /upload-parse-embed
Complete pipeline: Download files, parse them, and generate embeddings.

**Request:**
```bash
curl -X POST "http://localhost:8000/upload-parse-embed" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": ["https://example.com/document.pdf"],
    "min_chunk_words": 500,
    "max_chunk_words": 1000,
    "embedding_model": "text-embedding-3-small"
  }'
```

### POST /upload-and-parse
Download files from URLs and immediately parse supported document types.

**Request Body:**
```json
{
  "documents": [
    "https://example.com/document.pdf",
    "https://example.com/email.eml"
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "temp_directory": "/tmp/tmpXXXXXX",
  "files": [...],
  "total_files": 2,
  "parsed_documents": [
    {
      "file_info": {
        "url": "https://example.com/document.pdf",
        "filename": "document.pdf",
        "path": "/tmp/tmpXXXXXX/document.pdf",
        "size": 1024
      },
      "parsed_content": {
        "file_type": "pdf",
        "chunks": [...],
        "total_chunks": 3
      }
    }
  ],
  "total_parsed": 2
}
```

## FAISS Vector Search Endpoints

### POST /index/add
Add document embeddings to the FAISS index with unique IDs.

**Request Body:**
```json
{
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
  "file_path": "/path/to/document.pdf",
  "file_type": "pdf",
  "chunk_texts": ["First chunk text", "Second chunk text"],
  "doc_id": "optional-unique-id"
}
```

**Response:**
```json
{
  "status": "success",
  "doc_id": "generated-or-provided-id",
  "chunks_added": 2,
  "index_stats": {
    "total_vectors": 2,
    "dimension": 1536,
    "index_type": "flat",
    "total_documents": 1,
    "total_chunks": 2
  }
}
```

### POST /index/search
Perform similarity search using a query embedding vector.

**Request Body:**
```json
{
  "query_embedding": [0.1, 0.2, 0.3, ...],
  "k": 5,
  "score_threshold": 1.0,
  "filter_doc_ids": ["doc-id-1", "doc-id-2"]
}
```

**Response:**
```json
{
  "status": "success",
  "results": [
    {
      "score": 0.234,
      "index": 0,
      "metadata": {
        "doc_id": "document-123",
        "file_path": "/path/to/doc.pdf",
        "chunk_index": 0,
        "total_chunks": 5
      },
      "text": "Similar text content..."
    }
  ],
  "total_results": 3
}
```

### POST /index/search-by-text
Perform similarity search using natural language text (converted to embedding automatically).

**Request Body:**
```json
{
  "query_text": "Find information about machine learning algorithms",
  "k": 5,
  "score_threshold": 1.0,
  "filter_doc_ids": ["doc-1", "doc-2"],
  "api_key": "optional-api-key-override",
  "embedding_model": "text-embedding-3-small"
}
```

### GET /index/stats
Get statistics about the current FAISS index.

**Response:**
```json
{
  "status": "success",
  "stats": {
    "total_vectors": 150,
    "dimension": 1536,
    "index_type": "flat",
    "total_documents": 25,
    "total_chunks": 150,
    "is_trained": true
  }
}
```

### GET /index/document/{doc_id}
Get all chunks for a specific document ID.

**Response:**
```json
{
  "status": "success",
  "doc_id": "document-123",
  "chunks": [
    {
      "index": 0,
      "metadata": {
        "doc_id": "document-123",
        "chunk_index": 0,
        "file_path": "/path/to/doc.pdf",
        "total_chunks": 3
      },
      "text": "First chunk text..."
    }
  ],
  "total_chunks": 3
}
```

### DELETE /index/document/{doc_id}
Remove all chunks for a specific document ID.

### POST /index/reset
Reset the FAISS index (remove all documents and embeddings).

### POST /upload-parse-embed-index
Complete pipeline: Download files, parse them, generate embeddings, and add to FAISS index.

**Request Body:**
```json
{
  "documents": ["https://example.com/doc1.pdf", "https://example.com/doc2.docx"],
  "min_chunk_words": 500,
  "max_chunk_words": 1000,
  "embedding_model": "text-embedding-3-small",
  "api_key": "your-openai-api-key"
}
```

### Additional Endpoints
- `GET /docs` - FastAPI automatic interactive API documentation
- `GET /redoc` - Alternative API documentation

## Testing

### Health Endpoint
```bash
curl http://localhost:3000/health
```

### FAISS Vector Search Test
Run the comprehensive FAISS test suite:
```bash
python test_faiss.py
```

### Embedding Generation
```bash
curl -X POST "http://localhost:3000/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "text_chunks": [
      "Vector embeddings represent text as numerical vectors.",
      "These vectors capture semantic meaning and relationships."
    ],
    "model": "text-embedding-3-small"
  }'
```

### Add to FAISS Index
```bash
curl -X POST "http://localhost:3000/index/add" \
  -H "Content-Type: application/json" \
  -d '{
    "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
    "file_path": "test.txt",
    "file_type": "txt",
    "chunk_texts": ["Sample text chunk 1", "Sample text chunk 2"]
  }'
```

### Search by Text
```bash
curl -X POST "http://localhost:3000/index/search-by-text" \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "machine learning algorithms",
    "k": 5,
    "api_key": "your-openai-api-key"
  }'
```

### Parse and Embed Document
```bash
curl -X POST "http://localhost:3000/parse-and-embed" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/your/document.pdf",
    "embedding_model": "text-embedding-3-small"
  }'
```

### Complete Pipeline (Upload → Parse → Embed → Index)
```bash
curl -X POST "http://localhost:3000/upload-parse-embed-index" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": ["https://example.com/sample.pdf"],
    "min_chunk_words": 500,
    "max_chunk_words": 1000,
    "embedding_model": "text-embedding-3-small",
    "api_key": "your-openai-api-key"
  }'
```

### Test Vector Embeddings
Run the embedding test script:
```bash
python test_embeddings.py
```

## Vector Embeddings Features

### Supported Models
- **text-embedding-3-small** (1536 dimensions) - Recommended, cost-effective
- **text-embedding-3-large** (3072 dimensions) - Higher accuracy
- **text-embedding-ada-002** (1536 dimensions) - Legacy model

### Key Capabilities
- ✅ **Batch Processing** - Process multiple chunks efficiently
- ✅ **Rate Limiting** - Built-in delays to respect API limits
- ✅ **Token Management** - Automatic text truncation for large chunks
- ✅ **Error Handling** - Graceful handling of API failures
- ✅ **Metadata Preservation** - Maintains chunk information with embeddings
- ✅ **Async Processing** - Non-blocking embedding generation

### Use Cases
- **Semantic Search** - Find relevant content by meaning
- **Document Similarity** - Compare documents semantically
- **Content Clustering** - Group similar text automatically
- **Recommendation Systems** - Suggest related content
- **Knowledge Base Search** - Smart search through documentation

## Document Parser Features

### Supported File Types
- **PDF** (.pdf) - Extracts text from all pages
- **DOCX** (.docx, .doc) - Extracts text from paragraphs and tables  
- **EML** (.eml) - Extracts email headers and body content

### Text Chunking Algorithm
- Splits text into logical chunks of 500-1000 words (configurable)
- Preserves sentence boundaries for better readability
- Maintains context and coherence within chunks
- Includes metadata for each chunk (word count, source file, etc.)

### Error Handling
- Graceful handling of unsupported file types
- Missing dependency detection with helpful error messages
- File not found and permission error handling
- Partial parsing success for multi-file operations

## Features

- ✅ Health check endpoint
- ✅ Document upload from URLs
- ✅ Temporary file storage
- ✅ Async file downloading with httpx
- ✅ Error handling for failed downloads
- ✅ Automatic API documentation
