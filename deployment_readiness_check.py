#!/usr/bin/env python3
"""
🔍 Comprehensive Deployment Readiness Check
Validates all components of the HackRX API for production deployment
"""

import requests
import json
import os
import sys
from pathlib import Path
import time

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def print_status(check, status, details=""):
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {check}: {details}")
    return status

def test_api_key():
    """Test if Gemini API key is working"""
    print_header("API KEY VALIDATION")
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyBH6ls3I80rOI3il-uX-7p8eUTSoox05cc')
        genai.configure(api_key=api_key)
        
        # Test text generation
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'API working'")
        text_gen = print_status("Text Generation", "API working" in response.text, response.text[:50])
        
        # Test embeddings
        result = genai.embed_content(
            model="models/text-embedding-004",
            content="Test embedding",
            task_type="RETRIEVAL_DOCUMENT"
        )
        embed_gen = print_status("Text Embedding", len(result['embedding']) > 0, f"{len(result['embedding'])} dimensions")
        
        return text_gen and embed_gen
        
    except Exception as e:
        print_status("API Key Test", False, f"Error: {str(e)}")
        return False

def test_local_imports():
    """Test if all required modules can be imported"""
    print_header("LOCAL DEPENDENCIES CHECK")
    
    modules = [
        ("FastAPI", "fastapi"),
        ("Uvicorn", "uvicorn"),
        ("Pydantic", "pydantic"),
        ("AIOHTTP", "aiohttp"),
        ("Google GenAI", "google.generativeai"),
        ("FAISS", "faiss"),
        ("PyPDF2", "PyPDF2"),
        ("Python-DOCX", "docx"),
        ("Python-dotenv", "dotenv"),
        ("Requests", "requests"),
    ]
    
    all_imported = True
    for name, module in modules:
        try:
            __import__(module)
            print_status(name, True, "Available")
        except ImportError as e:
            print_status(name, False, f"Missing: {e}")
            all_imported = False
    
    return all_imported

def test_local_api():
    """Test local API functionality"""
    print_header("LOCAL API FUNCTIONALITY")
    
    try:
        # Import the main modules
        from hackrx_api import pipeline
        
        # Test pipeline initialization
        pipeline_ok = print_status("Pipeline Initialization", 
                                 pipeline is not None, 
                                 "DocumentQAPipeline ready")
        
        # Test API key configuration
        api_key_ok = print_status("API Key Configuration",
                                pipeline.api_key is not None and len(pipeline.api_key) > 20,
                                f"Key: {pipeline.api_key[:20]}...")
        
        # Test component initialization
        parser_ok = print_status("Document Parser", 
                                pipeline.parser is not None,
                                "RobustDocumentParser ready")
        
        embedder_ok = print_status("Gemini Embedder",
                                 pipeline.embedder is not None,
                                 "GeminiVectorEmbedder ready")
        
        return all([pipeline_ok, api_key_ok, parser_ok, embedder_ok])
        
    except Exception as e:
        print_status("Local API Test", False, f"Error: {str(e)}")
        return False

def test_production_api():
    """Test production API endpoints"""
    print_header("PRODUCTION API TESTING")
    
    base_url = "https://bajaj-hackrx-bnm2.onrender.com"
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=30)
        root_ok = print_status("Root Endpoint", 
                             response.status_code == 200,
                             f"Status: {response.status_code}, Version: {response.json().get('version', 'Unknown')}")
    except Exception as e:
        root_ok = print_status("Root Endpoint", False, f"Error: {str(e)}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/hackrx/health", timeout=30)
        health_data = response.json()
        health_ok = print_status("Health Endpoint",
                                response.status_code == 200 and health_data.get('status') == 'healthy',
                                f"Status: {health_data.get('status')}, API Key: {health_data.get('api_key_status')}")
    except Exception as e:
        health_ok = print_status("Health Endpoint", False, f"Error: {str(e)}")
    
    # Test authentication - valid token
    headers = {
        'Authorization': 'Bearer hackrx_test_token_2024',
        'Content-Type': 'application/json'
    }
    payload = {
        'document_url': 'https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D',
        'questions': ['What is the grace period?']
    }
    
    try:
        print("⏳ Testing main endpoint (this may take 30+ seconds)...")
        response = requests.post(f"{base_url}/api/v1/hackrx/run", 
                               json=payload, headers=headers, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            answers = data.get('answers', [])
            if answers and answers[0] != "I encountered a server error while processing this question.":
                main_ok = print_status("Main Endpoint (Valid Auth)", True, 
                                     f"Real answer: {answers[0][:100]}...")
            else:
                main_ok = print_status("Main Endpoint (Valid Auth)", False, 
                                     "Server processing error - check API key on Render")
        else:
            main_ok = print_status("Main Endpoint (Valid Auth)", False, 
                                 f"Status: {response.status_code}, Error: {response.text[:100]}")
    except Exception as e:
        main_ok = print_status("Main Endpoint (Valid Auth)", False, f"Error: {str(e)}")
    
    # Test authentication - invalid token
    invalid_headers = {
        'Authorization': 'Bearer short',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/hackrx/run",
                               json=payload, headers=invalid_headers, timeout=30)
        invalid_auth_ok = print_status("Invalid Auth Test",
                                     response.status_code == 401,
                                     f"Expected 401, got {response.status_code}")
    except Exception as e:
        invalid_auth_ok = print_status("Invalid Auth Test", False, f"Error: {str(e)}")
    
    # Test missing authentication
    try:
        response = requests.post(f"{base_url}/api/v1/hackrx/run",
                               json=payload, timeout=30)
        missing_auth_ok = print_status("Missing Auth Test",
                                     response.status_code == 403,
                                     f"Expected 403, got {response.status_code}")
    except Exception as e:
        missing_auth_ok = print_status("Missing Auth Test", False, f"Error: {str(e)}")
    
    return all([root_ok, health_ok, invalid_auth_ok, missing_auth_ok])

def test_files_and_config():
    """Test if all required files exist"""
    print_header("FILE SYSTEM CHECK")
    
    required_files = [
        "hackrx_api.py",
        "robust_document_parser.py", 
        "gemini_vector_embedder.py",
        "faiss_store.py",
        "gemini_answer.py",
        "requirements.txt",
        "README_PRODUCTION.md"
    ]
    
    all_files = True
    for file in required_files:
        file_path = Path(file)
        exists = file_path.exists()
        print_status(f"File: {file}", exists, 
                   f"Size: {file_path.stat().st_size if exists else 0} bytes")
        all_files = all_files and exists
    
    # Check .env file
    env_exists = Path('.env').exists()
    print_status(".env file", env_exists, "Contains environment variables")
    
    return all_files

def main():
    """Run comprehensive deployment readiness check"""
    print("🏆 HackRX API - Comprehensive Deployment Readiness Check")
    print("=" * 60)
    
    checks = {
        "File System": test_files_and_config(),
        "Local Dependencies": test_local_imports(),
        "API Key": test_api_key(),
        "Local API": test_local_api(),
        "Production API": test_production_api()
    }
    
    print_header("DEPLOYMENT READINESS SUMMARY")
    
    all_passed = True
    for check_name, passed in checks.items():
        status_icon = "✅" if passed else "❌"
        print(f"{status_icon} {check_name}: {'PASS' if passed else 'FAIL'}")
        all_passed = all_passed and passed
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 DEPLOYMENT READY: All checks passed!")
        print("🏆 Your HackRX API is competition-ready!")
        print("🚀 Ready for final submission!")
    else:
        print("⚠️  ISSUES DETECTED: Some checks failed")
        print("🔧 Review the failed checks above")
        print("📞 Address issues before final deployment")
    
    print("="*60)
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
