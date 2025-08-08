from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import tempfile
import os
from pathlib import Path
try:
    import httpx
except ImportError:
    httpx = None

app = FastAPI()

class UploadRequest(BaseModel):
    documents: List[str]  # Using str instead of HttpUrl for compatibility

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload_documents(request: UploadRequest):
    """
    Download files from provided URLs and save them temporarily.
    Requires httpx to be installed: pip install httpx
    """
    if httpx is None:
        raise HTTPException(
            status_code=500, 
            detail="httpx package is required. Install with: pip install httpx"
        )
    
    temp_dir = tempfile.mkdtemp()
    saved_files = []
    
    async with httpx.AsyncClient() as client:
        for url in request.documents:
            try:
                # Download the file
                response = await client.get(url)
                response.raise_for_status()
                
                # Generate a filename from the URL
                filename = Path(url).name or f"document_{len(saved_files)}.tmp"
                if not filename or filename == "/":
                    filename = f"document_{len(saved_files)}.tmp"
                
                # Save to temporary directory
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                saved_files.append({
                    "url": url,
                    "filename": filename,
                    "path": file_path,
                    "size": len(response.content)
                })
                
            except httpx.RequestError as e:
                raise HTTPException(status_code=400, detail=f"Failed to download {url}: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing {url}: {str(e)}")
    
    return {
        "status": "success",
        "temp_directory": temp_dir,
        "files": saved_files,
        "total_files": len(saved_files)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
