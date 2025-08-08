# HackRX Document Q&A API

🏆 **Complete Document Q&A Pipeline with Gemini 2.0 Flash**

## 🚀 **Full Pipeline Implementation**

The `/api/v1/hackrx/run` endpoint implements the complete workflow:

1. **📥 Document Download** - Downloads document from provided URL
2. **📄 Document Parsing** - Extracts and chunks text using multiple PDF libraries
3. **🔢 Embedding Generation** - Creates 768D vectors using Gemini text-embedding-004
4. **🗂️ Vector Indexing** - Stores embeddings in FAISS for similarity search
5. **❓ Question Processing** - For each question:
   - Generates query embedding
   - Retrieves most relevant chunks via similarity search
   - Composes LLM prompt with question + context
   - Calls Gemini 2.0 Flash to generate answer
6. **📋 Response Collection** - Returns all answers in structured JSON

## 🛠️ **Setup Instructions**

### 1. Install Dependencies
```bash
# Option 1: Use batch installer (Windows)
install_hackrx.bat

# Option 2: Manual installation
pip install fastapi uvicorn[standard] pydantic aiohttp python-dotenv
pip install -r requirements.txt
```

### 2. Configure API Key
Make sure your `.env` file contains:
```properties
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Start Server
```bash
# Option 1: Use starter script
python start_hackrx_server.py

# Option 2: Direct launch
python hackrx_api.py
```

## 📍 **API Endpoints**

### Main Endpoint
- **URL**: `http://localhost:8000/api/v1/hackrx/run`
- **Method**: `POST`
- **Content-Type**: `application/json`

### Health Check
- **URL**: `http://localhost:8000/api/v1/hackrx/health`
- **Method**: `GET`

### Documentation
- **URL**: `http://localhost:8000/docs` (Interactive Swagger UI)

## 📨 **Request Format**

```json
{
  "document_url": "https://example.com/document.pdf",
  "questions": [
    "What is this document about?",
    "What are the key findings?", 
    "Who are the main stakeholders?",
    "What recommendations are provided?",
    "How does performance compare to previous years?"
  ]
}
```

## 📄 **Response Format**

```json
{
  "answers": [
    "This document is a comprehensive business report analyzing...",
    "The key findings include significant growth in revenue...",
    "Main stakeholders identified are shareholders, customers...",
    "The report recommends expanding into new markets...",
    "Performance shows 15% improvement over previous year..."
  ],
  "processing_info": {
    "document_url": "https://example.com/document.pdf",
    "total_questions": 5,
    "chunks_created": 24,
    "embeddings_generated": 24,
    "answers_generated": 5,
    "total_time_seconds": 12.5,
    "processing_completed": "2025-08-08T03:30:45.123456"
  }
}
```

## 🧪 **Testing**

### Automated Testing
```bash
python test_hackrx_api.py
```

### Manual Testing with cURL
```bash
curl -X POST "http://localhost:8000/api/v1/hackrx/run" \
  -H "Content-Type: application/json" \
  -d '{
    "document_url": "https://example.com/sample.pdf",
    "questions": [
      "What is the main topic of this document?",
      "What are the key conclusions?"
    ]
  }'
```

### Testing with Python requests
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/hackrx/run",
    json={
        "document_url": "https://example.com/document.pdf",
        "questions": [
            "What is this document about?",
            "What are the main findings?"
        ]
    }
)

result = response.json()
print("Answers:", result["answers"])
```

## 🏗️ **Architecture**

### Core Components
- **FastAPI**: Web framework with automatic API documentation
- **Gemini 2.0 Flash**: Latest AI model for question answering
- **text-embedding-004**: 768D embeddings for semantic search
- **FAISS**: High-performance vector similarity search
- **Multi-library PDF parsing**: PyMuPDF, pdfplumber, PyPDF2 fallbacks

### Processing Flow
```
URL → Download → Parse → Chunk → Embed → Index → Search → Answer → Return
```

### Performance Features
- **Async processing** for concurrent operations
- **Batch embedding** generation for efficiency
- **Automatic cleanup** of temporary files
- **Comprehensive error handling** with graceful fallbacks
- **Rate limiting** awareness for API quotas

## 🔧 **Configuration**

### Environment Variables
```properties
GEMINI_API_KEY=your_api_key          # Required: Gemini API access
DEFAULT_EMBEDDING_MODEL=embedding-001 # Optional: Embedding model
```

### API Parameters
- **Chunk size**: 100-2000 tokens (target: 1000)
- **Similarity search**: Top 5 relevant chunks
- **Answer length**: Up to 1000 tokens per answer
- **Temperature**: 0.3 (focused responses)
- **Model**: gemini-2.0-flash-exp

## 🎯 **Supported Formats**

### Document Types
- **PDF**: Primary support with multiple parsing libraries
- **DOCX**: Microsoft Word documents
- **URL Requirements**: Direct download links to documents

### Question Types
- **Factual queries**: "What is the revenue?"
- **Analysis requests**: "What are the trends?"  
- **Comparison questions**: "How does X compare to Y?"
- **Summary requests**: "Summarize the key points"
- **Specific information**: "Who are the stakeholders?"

## ⚡ **Performance**

### Typical Processing Times
- **Small documents** (1-5 pages): 5-15 seconds
- **Medium documents** (10-50 pages): 15-45 seconds  
- **Large documents** (50+ pages): 45-120 seconds

### Scaling Factors
- **Document size**: Linear with page count
- **Question count**: Linear with number of questions
- **Network speed**: Affects download time
- **API quotas**: Rate limiting may add delays

## 🔒 **Security & Reliability**

### Security Features
- **Temporary file handling**: Files deleted after processing
- **API key protection**: Stored in environment variables
- **Input validation**: Pydantic models for request validation
- **Error isolation**: Comprehensive exception handling

### Reliability Features
- **Multi-library fallbacks**: PDF parsing redundancy
- **Timeout handling**: Prevents hung requests
- **Health checks**: Server status monitoring
- **Graceful degradation**: Continues processing despite partial failures

## 🚨 **Error Handling**

### Common Issues & Solutions

**API Key Missing**
```json
{"detail": "GEMINI_API_KEY environment variable is required"}
```
*Solution*: Set GEMINI_API_KEY in .env file

**Document Download Failed**
```json
{"detail": "Failed to download document: HTTP 404"}
```
*Solution*: Verify document URL is accessible

**Parsing Failed**
```json
{"detail": "Failed to parse document: No PDF parsing libraries available"}
```
*Solution*: Install PDF libraries with `pip install PyMuPDF pdfplumber PyPDF2`

**Quota Exceeded**
```json
{"detail": "Failed to generate embeddings: Quota exceeded"}
```
*Solution*: Wait for quota reset or upgrade API plan

## 📊 **Monitoring**

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2025-08-08T03:30:45.123456",
  "api_key_status": "configured",
  "components": {
    "document_parser": "ready",
    "gemini_embedder": "ready", 
    "faiss_vector_store": "ready",
    "gemini_answer_engine": "ready"
  },
  "endpoints": {
    "/api/v1/hackrx/run": "operational"
  }
}
```

### Processing Info
Each response includes detailed processing information:
- Document processing stats
- Embedding generation metrics  
- Total processing time
- Component status

## 🏆 **HackRX Competition Ready**

This implementation provides:
- ✅ **Complete pipeline** as specified
- ✅ **Professional API** with documentation
- ✅ **Robust error handling** for competition reliability
- ✅ **Performance optimization** for fast responses
- ✅ **Comprehensive testing** suite
- ✅ **Easy deployment** with setup scripts

## 🚀 **Quick Start**

```bash
# 1. Install dependencies
install_hackrx.bat

# 2. Start server  
python start_hackrx_server.py

# 3. Test API
python test_hackrx_api.py

# 4. View documentation
# Open: http://localhost:8000/docs
```

**Your HackRX Document Q&A API is ready for competition! 🏆**
