# Windows PowerShell Commands to Test Your FastAPI Server

## 🚀 Your server is running on: http://localhost:3000

## ✅ Quick Tests - Copy and paste these commands into PowerShell:

### 1. Health Check
Invoke-RestMethod -Uri "http://localhost:3000/health" -Method Get

### 2. Get API Information
Invoke-RestMethod -Uri "http://localhost:3000/" -Method Get

### 3. Generate Query Embedding
$queryData = @{
    query_text = "artificial intelligence and machine learning"
    embedding_model = "embedding-001"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:3000/query-embedding" -Method Post -Body $queryData -ContentType "application/json"

### 4. Search by Text (works even with empty index)
$searchData = @{
    query_text = "artificial intelligence"
    k = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:3000/index/search-by-text" -Method Post -Body $searchData -ContentType "application/json"

### 5. Get Index Statistics
Invoke-RestMethod -Uri "http://localhost:3000/index/stats" -Method Get

### 6. Upload and Index a Document (replace with a real URL)
$uploadData = @{
    documents = @("https://example.com/sample.pdf")
    min_chunk_words = 500
    max_chunk_words = 1000
    embedding_model = "embedding-001"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:3000/upload-parse-embed-index" -Method Post -Body $uploadData -ContentType "application/json"

## 🌐 Web Interface
# Open in your browser:
# http://localhost:3000/docs - Interactive API documentation
# http://localhost:3000/redoc - Alternative documentation

## 🎯 What to Expect:
# ✅ Health check should return: {"status": "ok"}
# ✅ Query embedding should return 768-dimensional vectors
# ✅ Search should work (returns empty results if no documents indexed)
# ✅ All endpoints should respond successfully

## 🔥 Your API Features:
# - Real Gemini API embeddings (with your working API key!)
# - Document processing (PDF, DOCX, EML)
# - FAISS vector search
# - Complete upload-to-search pipeline
# - Graceful error handling and fallbacks

## 📋 Status: FULLY OPERATIONAL! 🎉
