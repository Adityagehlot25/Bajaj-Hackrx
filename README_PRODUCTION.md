# 🏆 HackRX Document Q&A API

> **Bajaj HackRX Competition Entry** - A production-ready document processing and question-answering API powered by Google Gemini AI and FAISS vector search.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Gemini](https://img.shields.io/badge/Google-Gemini%201.5%20Flash-orange)](https://ai.google.dev/)
[![FAISS](https://img.shields.io/badge/Meta-FAISS-red)](https://github.com/facebookresearch/faiss)

## 🚀 **Live API**: https://bajaj-hackrx-bnm2.onrender.com/

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#-architecture) 
- [📚 API Documentation](#-api-documentation)
- [🔐 Authentication](#-authentication)
- [🛠️ Local Development](#-local-development)
- [📊 Testing](#-testing)
- [🚀 Deployment](#-deployment)
- [📝 Usage Examples](#-usage-examples)

---

## ✨ Features

### 🎯 **Core Capabilities**
- **📄 Document Processing**: PDF and DOCX support with intelligent parsing
- **🧠 AI-Powered Q&A**: Context-aware answers using Gemini 1.5 Flash  
- **🔍 Vector Search**: FAISS-based semantic search for relevant content retrieval
- **⚡ Async Processing**: High-performance async/await implementation
- **🔐 Secure Authentication**: Bearer token authentication with validation
- **📊 Comprehensive Logging**: Production-ready logging and error handling

### 🏆 **Production Features**
- **🌐 CORS Support**: Cross-origin requests enabled
- **📖 Auto Documentation**: Interactive API docs at `/docs`
- **💾 Memory Efficient**: Optimized chunking and vector storage
- **🔧 Health Monitoring**: Health check endpoints for uptime monitoring
- **⚙️ Configurable**: Environment variable configuration

---

## 🏗️ Architecture

```mermaid
graph TD
    A[Client Request] --> B[FastAPI Authentication]
    B --> C[Document Download]
    C --> D[Document Parsing]
    D --> E[Text Chunking]
    E --> F[Gemini Embeddings]
    F --> G[FAISS Indexing]
    G --> H[Question Processing]
    H --> I[Similarity Search]
    I --> J[Context Retrieval]
    J --> K[Gemini Answer Generation]
    K --> L[Response Formatting]
    L --> M[JSON Response]
```

### **Technology Stack**
- **API Framework**: FastAPI with Pydantic validation
- **AI Engine**: Google Gemini 1.5 Flash for embeddings and text generation
- **Vector Database**: FAISS for high-performance similarity search
- **Document Processing**: PyPDF2, python-docx for multi-format support
- **Async HTTP**: aiohttp for non-blocking document downloads
- **Authentication**: HTTPBearer with custom token validation

---

## 📚 API Documentation

### **🔗 Base URLs**
- **Production**: `https://bajaj-hackrx-bnm2.onrender.com`
- **Local**: `http://localhost:8000`
- **Documentation**: `https://bajaj-hackrx-bnm2.onrender.com/docs`

### **📍 Endpoints**

#### **GET /** - API Information
```bash
curl https://bajaj-hackrx-bnm2.onrender.com/
```

**Response:**
```json
{
  "message": "HackRX Document Q&A API",
  "version": "1.1.0",
  "status": "operational",
  "endpoints": {
    "main": "/api/v1/hackrx/run",
    "health": "/api/v1/hackrx/health",
    "docs": "/docs"
  }
}
```

#### **POST /api/v1/hackrx/run** - Main Q&A Endpoint 🎯

**Complete document processing and question answering workflow:**

**Request:**
```json
{
  "document_url": "https://example.com/document.pdf",
  "questions": [
    "What is the main topic of this document?",
    "What are the key requirements mentioned?"
  ]
}
```

**Headers:**
```
Authorization: Bearer your_token_here_min_10_chars
Content-Type: application/json
```

**Response:**
```json
{
  "answers": [
    "The main topic of the document is...",
    "The key requirements mentioned are..."
  ]
}
```

**Processing Steps:**
1. **Download** document from URL
2. **Parse** content (PDF/DOCX support)  
3. **Chunk** text intelligently (100-2000 tokens)
4. **Generate** embeddings with Gemini
5. **Index** using FAISS vector search
6. **Answer** each question using retrieval-augmented generation

#### **GET /api/v1/hackrx/health** - Health Check
```bash
curl https://bajaj-hackrx-bnm2.onrender.com/api/v1/hackrx/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-08T12:34:56.789Z",
  "api_key_status": "configured",
  "components": {
    "document_parser": "ready",
    "gemini_embedder": "ready", 
    "faiss_vector_store": "ready",
    "gemini_answer_engine": "ready"
  }
}
```

---

## 🔐 Authentication

### **Bearer Token Authentication**

All API endpoints require Bearer token authentication:

```bash
# Valid token (≥10 characters)
Authorization: Bearer hackrx_competition_token_2024

# Invalid examples:
Authorization: Bearer short     # ❌ Too short (<10 chars) → 401
# Missing Authorization header   # ❌ No auth → 403
```

### **Response Codes**
- **✅ 200**: Success with valid token
- **❌ 401**: Invalid token (too short or malformed)
- **❌ 403**: Missing Authorization header
- **❌ 422**: Invalid request format

---

## 🛠️ Local Development

### **Prerequisites**
- Python 3.8+
- pip package manager
- Git

### **Quick Start**

1. **Clone repository:**
```bash
git clone https://github.com/Adityagehlot25/Bajaj-Hackrx.git
cd Bajaj-Hackrx
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set environment variables:**
```bash
# Windows
set GEMINI_API_KEY=your_gemini_api_key_here

# Linux/Mac  
export GEMINI_API_KEY=your_gemini_api_key_here
```

4. **Run the API:**
```bash
python hackrx_api.py
```

5. **Access the API:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/hackrx/health

### **Dependencies**
```
fastapi>=0.104.1
uvicorn>=0.24.0
aiohttp>=3.9.0
google-generativeai>=0.3.0
faiss-cpu>=1.7.4
PyPDF2>=3.0.1
python-docx>=1.1.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
pydantic>=2.5.0
```

---

## 📊 Testing

### **🧪 Local Testing**

**Test API key functionality:**
```bash
python test_api_key.py
```

**Run authentication tests:**
```bash
python test_hackrx_api.py
```

### **🌐 Production Testing**

**Valid request example:**
```bash
curl -X POST https://bajaj-hackrx-bnm2.onrender.com/api/v1/hackrx/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer hackrx_test_token_2024" \
  -d '{
    "document_url": "https://example.com/sample.pdf",
    "questions": ["What is this document about?"]
  }'
```

**Authentication tests:**
```bash
# Test invalid token (should return 401)
curl -X POST https://bajaj-hackrx-bnm2.onrender.com/api/v1/hackrx/run \
  -H "Authorization: Bearer short" \
  -H "Content-Type: application/json" \
  -d '{"document_url": "https://example.com/test.pdf", "questions": ["test"]}'

# Test missing auth (should return 403)  
curl -X POST https://bajaj-hackrx-bnm2.onrender.com/api/v1/hackrx/run \
  -H "Content-Type: application/json" \
  -d '{"document_url": "https://example.com/test.pdf", "questions": ["test"]}'
```

### **📋 Test Scripts Available**
- `test_api_key.py` - Validate Gemini API key
- `test_hackrx_api.py` - Comprehensive API testing  
- `test_render_deployment.py` - Production deployment tests
- `quick_test.py` - Zero-dependency API test
- `test_deployed_api.sh` - Bash testing script
- `test_deployed_api.ps1` - PowerShell testing script

---

## 🚀 Deployment

### **🌐 Production Deployment (Render.com)**

1. **Deploy to Render:**
   - Connect GitHub repository
   - Set environment variables
   - Deploy with automatic builds

2. **Environment Variables:**
```bash
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000
```

3. **Build Command:**
```bash
pip install -r requirements.txt
```

4. **Start Command:**
```bash
python hackrx_api.py
```

### **🐳 Docker Deployment**

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "hackrx_api.py"]
```

---

## 📝 Usage Examples

### **🎯 Basic Document Q&A**

```python
import requests

url = "https://bajaj-hackrx-bnm2.onrender.com/api/v1/hackrx/run"
headers = {
    "Authorization": "Bearer hackrx_competition_token_2024",
    "Content-Type": "application/json"
}

payload = {
    "document_url": "https://example.com/policy.pdf",
    "questions": [
        "What is the coverage amount?",
        "What are the exclusions?",
        "How do I file a claim?"
    ]
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

print("Answers:")
for i, answer in enumerate(result["answers"], 1):
    print(f"{i}. {answer}")
```

### **💻 JavaScript/Node.js**

```javascript
const axios = require('axios');

const processDocument = async () => {
  try {
    const response = await axios.post(
      'https://bajaj-hackrx-bnm2.onrender.com/api/v1/hackrx/run',
      {
        document_url: 'https://example.com/document.pdf',
        questions: ['What is the main topic?']
      },
      {
        headers: {
          'Authorization': 'Bearer hackrx_test_token_2024',
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log('Answers:', response.data.answers);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
};

processDocument();
```

### **🔧 PowerShell**

```powershell
$headers = @{
    'Authorization' = 'Bearer hackrx_competition_token_2024'
    'Content-Type' = 'application/json'
}

$body = @{
    document_url = 'https://example.com/sample.pdf'
    questions = @('What is this document about?')
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri 'https://bajaj-hackrx-bnm2.onrender.com/api/v1/hackrx/run' -Method Post -Headers $headers -Body $body

Write-Output "Answers:"
$response.answers | ForEach-Object { Write-Output "- $_" }
```

---

## 🎯 **Performance Metrics**

- **Document Processing**: ~20-30 seconds
- **Question Answering**: ~2-3 seconds per question  
- **Concurrent Requests**: Supported via async processing
- **Memory Usage**: Optimized chunking and vector storage
- **Supported File Size**: Up to 50MB documents

---

## 🏆 **Competition Ready**

This API is **production-ready** for the Bajaj HackRX competition with:

- ✅ **Robust Authentication**: Bearer token security
- ✅ **Professional Documentation**: Comprehensive API docs  
- ✅ **Error Handling**: Graceful failure management
- ✅ **Performance Optimized**: Async processing and efficient algorithms
- ✅ **Scalable Architecture**: Ready for high-load scenarios
- ✅ **Industry Standards**: FastAPI best practices

---

## 📞 **Support**

- **GitHub**: [Adityagehlot25/Bajaj-Hackrx](https://github.com/Adityagehlot25/Bajaj-Hackrx)
- **API Docs**: [Live Documentation](https://bajaj-hackrx-bnm2.onrender.com/docs)
- **Issues**: Report bugs and feature requests via GitHub Issues

---

**Built with ❤️ for Bajaj HackRX 2025**
