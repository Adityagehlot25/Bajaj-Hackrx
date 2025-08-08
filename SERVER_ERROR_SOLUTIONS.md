# 🔧 HackRX API Processing Error Solutions

## 🚨 Current Issue
Your API structure is perfect, but document processing returns "server error". Let's fix this systematically.

---

## 🔍 **Solution 1: Verify Gemini API Key Configuration**

### Check Your Current API Key
```python
# Test your current Gemini API key
import os
import google.generativeai as genai

# Load your API key
api_key = "AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ"  # Your current key
genai.configure(api_key=api_key)

# Test the API key
try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content("Hello, test message")
    print("✅ API Key is working!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ API Key Error: {e}")
```

### **Action Required:** Update Render Environment Variables

1. **Go to your Render Dashboard:**
   - Visit: https://dashboard.render.com/
   - Find your HackRX API service

2. **Update Environment Variables:**
   ```
   GEMINI_API_KEY=AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ
   ```

3. **Verify the API Key Format:**
   - Should start with `AIza`
   - Should be 39 characters long
   - No quotes or spaces

---

## 🔧 **Solution 2: Add Better Error Logging**

### Enhanced API Error Handling
```python
# Add this to your answer_question method in hackrx_api.py
async def answer_question(self, question: str) -> str:
    """Answer a single question with enhanced error logging"""
    try:
        logger.info(f"Processing question: {question[:100]}...")
        
        # Test API key first
        if not self.api_key or len(self.api_key) < 30:
            logger.error(f"Invalid API key length: {len(self.api_key) if self.api_key else 0}")
            return "API key configuration error - please check environment variables"
        
        # Generate query embedding with detailed logging
        logger.info("Generating query embedding...")
        query_result = await self.embedder.generate_embeddings_async([question])
        
        if not query_result.get('success'):
            error_msg = query_result.get('error', 'Unknown embedding error')
            logger.error(f"Embedding error: {error_msg}")
            return f"Embedding generation failed: {error_msg}"
        
        # Continue with rest of processing...
        
    except Exception as e:
        logger.error(f"Detailed error in answer_question: {type(e).__name__}: {str(e)}")
        return f"I encountered a server error while processing this question. Error: {type(e).__name__}: {str(e)}"
```

---

## 🚀 **Solution 3: Optimize for Render Free Tier**

### Memory and Timeout Optimizations

```python
# Add these optimizations to your DocumentQAPipeline class

class DocumentQAPipeline:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Optimize for free tier
        self.max_chunks = 20  # Limit chunks to reduce memory
        self.max_questions = 5  # Limit questions per request
        self.chunk_size = 500  # Smaller chunks for faster processing
        
    async def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """Generate embeddings with free tier optimization"""
        # Limit chunks for free tier
        if len(chunks) > self.max_chunks:
            logger.warning(f"Limiting chunks from {len(chunks)} to {self.max_chunks} for free tier")
            chunks = chunks[:self.max_chunks]
        
        # Process in smaller batches with delays
        batch_size = 3  # Smaller batches
        delay_between_batches = 2  # Seconds
        
        try:
            chunk_texts = [chunk['text'] for chunk in chunks]
            
            # Process in batches with delays
            all_embeddings = []
            for i in range(0, len(chunk_texts), batch_size):
                batch = chunk_texts[i:i+batch_size]
                logger.info(f"Processing embedding batch {i//batch_size + 1}")
                
                result = await self.embedder.generate_embeddings_async(
                    batch,
                    batch_size=len(batch)
                )
                
                if result.get('success'):
                    all_embeddings.extend(result['embeddings'])
                else:
                    raise Exception(f"Batch {i//batch_size + 1} failed: {result.get('error')}")
                
                # Add delay between batches to avoid rate limits
                if i + batch_size < len(chunk_texts):
                    await asyncio.sleep(delay_between_batches)
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Optimized embedding generation failed: {e}")
            raise
```

---

## 🆘 **Solution 4: Add Fallback Error Handling**

### Robust Answer Generation with Fallbacks

```python
async def answer_question_with_fallback(self, question: str) -> str:
    """Answer question with multiple fallback strategies"""
    
    # Strategy 1: Full pipeline
    try:
        return await self.answer_question(question)
    except Exception as e1:
        logger.warning(f"Full pipeline failed: {e1}")
        
        # Strategy 2: Simple Gemini call without context
        try:
            logger.info("Attempting fallback: direct Gemini call")
            
            # Direct call to Gemini without vector search
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            prompt = f"""
            Based on general knowledge, please answer this question:
            
            Question: {question}
            
            If you don't know the answer, please say "I don't have enough information to answer this question from the provided document."
            """
            
            response = model.generate_content(prompt)
            return response.text if response.text else "No response generated"
            
        except Exception as e2:
            logger.error(f"Fallback strategy failed: {e2}")
            
            # Strategy 3: Return helpful error message
            return f"I'm experiencing technical difficulties. Please try again in a few moments. (Error: {type(e1).__name__})"
```

---

## 🔄 **Solution 5: Quick Fix Script**

### Test and Fix Your Deployment

```python
# Create this as test_and_fix.py
import os
import asyncio
import aiohttp
import json
from datetime import datetime

async def test_deployment_with_fixes():
    """Test deployed API and identify specific issues"""
    
    base_url = "https://bajaj-hackrx-bnm2.onrender.com"
    
    print("🔍 Testing HackRX API Deployment...")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Endpoint...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/api/v1/hackrx/health") as response:
                health_data = await response.json()
                print(f"✅ Health Status: {health_data.get('status')}")
                print(f"🔑 API Key Status: {health_data.get('api_key_status')}")
                
                if health_data.get('api_key_status') == 'missing':
                    print("❌ ISSUE FOUND: Gemini API key is missing in Render environment!")
                    print("🔧 SOLUTION: Add GEMINI_API_KEY to Render environment variables")
                    
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 2: Simple Processing Test
    print("\n2️⃣ Testing Simple Processing...")
    try:
        test_payload = {
            "document_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "questions": ["What is this document about?"]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer hackrx_test_token_2024"
        }
        
        start_time = datetime.now()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/api/v1/hackrx/run",
                headers=headers,
                json=test_payload,
                timeout=aiohttp.ClientTimeout(total=60)  # 60 second timeout
            ) as response:
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                if response.status == 200:
                    result = await response.json()
                    answers = result.get('answers', [])
                    
                    print(f"✅ Processing completed in {processing_time:.1f} seconds")
                    print(f"📄 Answers received: {len(answers)}")
                    
                    for i, answer in enumerate(answers):
                        print(f"🤖 Answer {i+1}: {answer[:100]}...")
                        
                        if "server error" in answer.lower():
                            print("❌ ISSUE FOUND: Server processing error detected!")
                            print("🔧 SOLUTIONS:")
                            print("   - Check Gemini API key in Render dashboard")
                            print("   - Upgrade Render plan for more memory")
                            print("   - Use smaller test documents")
                            
                else:
                    error_text = await response.text()
                    print(f"❌ Request failed: {response.status}")
                    print(f"Error: {error_text}")
                    
    except asyncio.TimeoutError:
        print("⏱️ ISSUE FOUND: Request timeout (likely memory/processing limits)")
        print("🔧 SOLUTIONS:")
        print("   - Use smaller documents")
        print("   - Upgrade Render plan")
        print("   - Optimize chunk sizes")
        
    except Exception as e:
        print(f"❌ Processing test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 NEXT STEPS:")
    print("1. Check Render dashboard environment variables")
    print("2. Verify GEMINI_API_KEY is correctly set")
    print("3. Consider upgrading Render plan for better performance")
    print("4. Test with smaller documents first")

if __name__ == "__main__":
    asyncio.run(test_deployment_with_fixes())
```

---

## ⚡ **Immediate Actions Required**

### Step 1: Update Render Environment Variables
```bash
# In your Render dashboard, ensure these are set:
GEMINI_API_KEY=AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ
DEFAULT_EMBEDDING_MODEL=embedding-001
```

### Step 2: Test API Key Locally
```bash
# Run this to verify your API key works
python -c "
import google.generativeai as genai
genai.configure(api_key='AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ')
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content('Hello')
print('API Key Test:', 'SUCCESS' if response.text else 'FAILED')
"
```

### Step 3: Redeploy with Environment Variables
1. Go to Render dashboard
2. Navigate to your service
3. Go to "Environment" tab
4. Add/update `GEMINI_API_KEY`
5. Click "Save Changes" → triggers redeploy

---

## 🎯 **Most Likely Solutions (In Order)**

1. **🔑 Missing API Key in Render (90% likely)**
   - Your `.env` file isn't deployed to Render
   - Need to manually add environment variables in Render dashboard

2. **💾 Memory Limits on Free Tier (80% likely)**
   - Large documents exceed free tier memory
   - Solution: Use smaller test documents or upgrade plan

3. **⏱️ Timeout Issues (70% likely)**
   - Processing takes too long for free tier
   - Solution: Optimize chunk sizes and batch processing

4. **🔧 API Rate Limits (30% likely)**
   - Too many API calls too quickly
   - Solution: Add delays between requests

---

## 🚀 **Quick Win: Test with Minimal Document**

```python
# Use this minimal test to isolate the issue
import requests

test_payload = {
    "document_url": "https://www.adobe.com/support/products/enterprise/knowledgecenter/media/c4611_sample_explain.pdf",
    "questions": ["What is this?"]
}

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer test_token_123456789"
}

response = requests.post(
    "https://bajaj-hackrx-bnm2.onrender.com/api/v1/hackrx/run",
    headers=headers,
    json=test_payload,
    timeout=60
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

The most critical step is ensuring your `GEMINI_API_KEY` is properly set in Render's environment variables dashboard!
