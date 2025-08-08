# 🔄 OpenAI to Google Gemini Migration Guide

## Overview
This document explains how to migrate from OpenAI embeddings to Google Gemini embeddings in your FastAPI document search system.

## 🚀 What Was Changed

### 1. **Core Embedding Module**
- **Old**: `vector_embedder.py` (OpenAI-based)
- **New**: `gemini_vector_embedder.py` (Gemini-based)

### 2. **API Integration Method**
- **Old**: OpenAI Python library (`openai`)
- **New**: HTTP requests using `aiohttp` and `requests`

### 3. **Authentication**
- **Old**: `OPENAI_API_KEY` environment variable
- **New**: `GEMINI_API_KEY` environment variable

### 4. **Default Model**
- **Old**: `text-embedding-3-small` (1536 dimensions)
- **New**: `text-embedding-004` (768 dimensions)

## 📊 Key Differences

| Feature | OpenAI | Gemini |
|---------|--------|--------|
| **Dimensions** | 1536 | 768 |
| **API Method** | Python SDK | HTTP Requests |
| **Cost** | $0.00002/1K tokens | Free tier available |
| **Rate Limits** | 3000 RPM | Varies by tier |
| **Max Context** | 8191 tokens | 2048 tokens |

## 🔧 Implementation Details

### **HTTP Request Structure (Gemini)**

```python
import aiohttp
import requests

# Async version
async def generate_embedding_async(text: str, api_key: str):
    url = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    payload = {
        "content": {
            "parts": [{"text": text}]
        },
        "taskType": "RETRIEVAL_DOCUMENT"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data["embedding"]["values"]
            else:
                raise Exception(f"API Error: {response.status}")

# Sync version
def generate_embedding_sync(text: str, api_key: str):
    url = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    payload = {
        "content": {
            "parts": [{"text": text}]
        },
        "taskType": "RETRIEVAL_DOCUMENT"
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        return data["embedding"]["values"]
    else:
        raise Exception(f"API Error: {response.status_code}")
```

### **Error Handling**

```python
# Common Gemini API errors and handling
try:
    embedding = await generate_embedding(text)
except Exception as e:
    error_msg = str(e)
    
    if "429" in error_msg or "rate limit" in error_msg.lower():
        # Rate limit exceeded - wait and retry
        await asyncio.sleep(1)
        # Retry logic here
    elif "403" in error_msg:
        # Invalid API key or insufficient permissions
        raise Exception("API key invalid or insufficient permissions")
    elif "400" in error_msg:
        # Bad request - check payload format
        raise Exception(f"Bad request: {error_msg}")
    else:
        # Other errors
        raise Exception(f"API error: {error_msg}")
```

## 🛠️ Migration Steps

### Step 1: Update Dependencies

**Old requirements.txt:**
```
openai>=1.0.0
```

**New requirements.txt:**
```
aiohttp>=3.8.0
requests>=2.28.0
```

### Step 2: Update Environment Variables

**Old .env:**
```
OPENAI_API_KEY=sk-proj-...
```

**New .env:**
```
GEMINI_API_KEY=your-gemini-api-key
```

### Step 3: Update Import Statements

**Old imports:**
```python
from vector_embedder import generate_embeddings, embed_document_chunks
```

**New imports:**
```python
from gemini_vector_embedder import generate_embeddings, embed_document_chunks
```

### Step 4: Update Model Parameters

**Old default model:**
```python
model: str = "text-embedding-3-small"
```

**New default model:**
```python
model: str = "text-embedding-004"
```

### Step 5: Update Mock Embedding Dimensions

**Old mock embeddings:**
```python
mock_embedding = np.random.randn(1536)  # OpenAI dimensions
```

**New mock embeddings:**
```python
mock_embedding = np.random.randn(768)   # Gemini dimensions
```

## 🧪 Testing the Migration

### 1. **Test Basic Functionality**
```bash
python gemini_integration_example.py
```

### 2. **Test API Endpoints**
```bash
# Start server
python main.py

# Test query embedding
curl -X POST "http://localhost:3000/query-embedding" \
  -H "Content-Type: application/json" \
  -d '{"query_text": "test query", "embedding_model": "text-embedding-004"}'
```

### 3. **Verify Dimensions**
The response should show 768 dimensions instead of 1536.

## 🔑 Getting Gemini API Key

1. **Go to Google AI Studio**: https://makersuite.google.com/app/apikey
2. **Create API Key**: Click "Create API Key"
3. **Copy Key**: Save the generated key
4. **Add to Environment**: Set `GEMINI_API_KEY=your-key-here`

## ⚠️ Important Notes

### **Dimension Compatibility**
- **Issue**: Existing FAISS indexes use 1536 dimensions (OpenAI)
- **Solution**: Either rebuild indexes or use dimension mapping

### **Rate Limits**
- Gemini has different rate limits than OpenAI
- Monitor your usage in Google Cloud Console

### **Model Availability**
- `text-embedding-004` is the recommended model
- `embedding-001` is also available but older

### **Token Limits**
- Gemini: 2048 tokens max per request
- OpenAI: 8191 tokens max per request
- Adjust chunking strategy if needed

## 🔄 Backward Compatibility

The refactored system maintains the same:
- ✅ Function signatures
- ✅ Response format
- ✅ Error handling patterns  
- ✅ Mock embedding fallback
- ✅ FastAPI endpoint structure

## 🚀 Benefits of Migration

### **Cost Savings**
- Gemini offers free tier
- No billing issues like OpenAI quota

### **Google Integration**
- Better integration with Google Cloud
- Enterprise-grade security

### **API Reliability**
- Direct HTTP requests (no SDK dependency)
- More control over request/response handling

## 🐛 Troubleshooting

### **"Module not found" errors**
```bash
pip install aiohttp requests
```

### **"API key invalid" errors**
- Check your `GEMINI_API_KEY` environment variable
- Verify the key is valid in Google AI Studio

### **Dimension mismatch in FAISS**
- Option 1: Rebuild FAISS index with 768-dim vectors
- Option 2: Use dimension reduction/expansion

### **Rate limit errors**
- Implement retry logic with exponential backoff
- Monitor usage in Google Cloud Console

## 📚 Additional Resources

- **Gemini API Documentation**: https://ai.google.dev/api/embeddings
- **Google AI Studio**: https://makersuite.google.com/
- **Rate Limits & Quotas**: https://ai.google.dev/api/embeddings#rate-limits

## 🎯 Next Steps

1. **Test the migration** with your specific use case
2. **Update documentation** to reflect Gemini usage  
3. **Monitor performance** compared to OpenAI
4. **Consider rebuilding FAISS indexes** for optimal performance

---

**Migration Complete!** 🎉 Your system now uses Google Gemini instead of OpenAI for embeddings.
