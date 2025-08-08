# How to Start the FastAPI Server (FIXED VERSION)

## ⚠️ IMPORTANT FIXES:

1. **Dependencies Issue**: Install setuptools first
2. **Port Conflict**: Use port 3000 instead of 8000

## Method 1: Using Fixed Batch File (RECOMMENDED)

Simply run:
```cmd
start_fixed.bat
```

## Method 2: Manual PowerShell Setup

1. **Open PowerShell in the project directory:**
   ```powershell
   cd "e:\final try"
   ```

2. **Fix dependencies first:**
   ```powershell
   python -m pip install --upgrade pip setuptools wheel
   ```

3. **Set the API key:**
   ```powershell
   $env:OPENAI_API_KEY = "your-openai-api-key-here"
   ```

4. **Install dependencies:**
   ```powershell
   pip install fastapi "uvicorn[standard]" python-dotenv openai httpx pydantic
   ```

5. **Start the server (on port 3000 to avoid conflicts):**
   ```powershell
   uvicorn main:app --reload --host 0.0.0.0 --port 3000
   ```

## Method 3: One-Line PowerShell Fix

```powershell
cd "e:\final try"; python -m pip install --upgrade pip setuptools wheel; $env:OPENAI_API_KEY = "your-openai-api-key-here"; pip install fastapi "uvicorn[standard]" python-dotenv openai httpx pydantic; uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

## Expected Output

When the server starts successfully, you should see:
```
INFO:     Will watch for changes in these directories: ['e:\\final try']
INFO:     Uvicorn running on http://0.0.0.0:3000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Access Your API

Once running, visit:
- **Interactive API Docs:** http://localhost:3000/docs
- **Health Check:** http://localhost:3000/health
- **Alternative Docs:** http://localhost:3000/redoc

## Test Your Endpoints

**Health Check:**
```bash
curl http://localhost:3000/health
```

**Generate Embeddings:**
```bash
curl -X POST "http://localhost:3000/embed" -H "Content-Type: application/json" -d '{"text_chunks": ["Test embedding generation"], "model": "text-embedding-3-small"}'
```

## Troubleshooting

**If you get "command not found" errors:**
1. Make sure Python is installed and in PATH
2. Install packages: `pip install fastapi uvicorn`
3. Try `python -m uvicorn` instead of just `uvicorn`

**If you get import errors:**
1. Install missing packages: `pip install -r requirements.txt`
2. Make sure you're in the correct directory: `cd "e:\final try"`

**If API calls fail:**
1. Verify API key is set correctly
2. Check internet connection
3. Verify OpenAI account has credits
