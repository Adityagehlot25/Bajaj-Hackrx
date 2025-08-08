"""
Test configuration and shared fixtures for the Document AI Q&A System

This file contains pytest configuration, shared fixtures, and utilities
that are used across multiple test modules.
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Import the FastAPI app
from main import app

# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings"""
    # Add custom markers
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line("markers", "integration: Integration tests for API endpoints")
    config.addinivalue_line("markers", "performance: Performance and timing tests")
    config.addinivalue_line("markers", "security: Security and authentication tests")
    config.addinivalue_line("markers", "explainability: Tests for AI explainability")
    config.addinivalue_line("markers", "slow: Tests that take longer to run")
    config.addinivalue_line("markers", "network: Tests that make network calls")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on test file names and test names
        if "performance" in item.name.lower():
            item.add_marker(pytest.mark.performance)
        if "security" in item.name.lower():
            item.add_marker(pytest.mark.security)
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        if "explainability" in item.name.lower() or "explanation" in item.name.lower():
            item.add_marker(pytest.mark.explainability)

# =============================================================================
# SHARED FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def test_client():
    """Create a FastAPI test client for the entire test session"""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def temp_directory():
    """Create a temporary directory for each test function"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(scope="function")
def mock_gemini_api():
    """Mock Gemini API responses to avoid actual API calls"""
    with patch('httpx.AsyncClient') as mock_client:
        # Configure mock client for Gemini API responses
        mock_instance = Mock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        mock_client.return_value.__aexit__.return_value = None
        
        # Default successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": '{"answer": "Mock answer", "rationale": "Mock rationale", "source_chunks": ["Mock source"]}'
                    }]
                },
                "finishReason": "STOP"
            }],
            "usageMetadata": {"totalTokenCount": 100}
        }
        mock_instance.post.return_value = mock_response
        
        yield mock_client

@pytest.fixture(scope="function")
def mock_document_content():
    """Provide sample document content for testing"""
    return {
        "pdf": {
            "success": True,
            "content": "Sample PDF content about machine learning and AI applications.",
            "pages": 1,
            "metadata": {"filename": "sample.pdf"}
        },
        "docx": {
            "success": True,
            "content": "Sample DOCX content about data privacy and GDPR compliance.",
            "pages": 1,
            "metadata": {"filename": "sample.docx"}
        },
        "txt": {
            "success": True,
            "content": "Sample text file content for testing purposes.",
            "pages": 1,
            "metadata": {"filename": "sample.txt"}
        }
    }

@pytest.fixture(scope="function")
def sample_embeddings():
    """Provide sample embedding vectors for testing"""
    embedding_dim = 1280
    return {
        "query": [0.1 + i * 0.001 for i in range(embedding_dim)],
        "chunk1": [0.2 + i * 0.001 for i in range(embedding_dim)],
        "chunk2": [0.3 + i * 0.001 for i in range(embedding_dim)],
        "chunk3": [0.4 + i * 0.001 for i in range(embedding_dim)]
    }

@pytest.fixture(scope="function")
def sample_chunks():
    """Provide sample text chunks for testing"""
    return [
        {
            "content": "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
            "metadata": {"filename": "ml_guide.pdf", "page": 1, "chunk_id": "chunk_1"}
        },
        {
            "content": "Deep learning uses neural networks with multiple layers to process complex patterns in data.",
            "metadata": {"filename": "dl_guide.pdf", "page": 2, "chunk_id": "chunk_2"}
        },
        {
            "content": "Natural language processing enables computers to understand and generate human language.",
            "metadata": {"filename": "nlp_guide.pdf", "page": 3, "chunk_id": "chunk_3"}
        }
    ]

# =============================================================================
# TEST UTILITIES
# =============================================================================

class TestDataGenerator:
    """Utility class for generating test data"""
    
    @staticmethod
    def create_test_pdf_file(temp_dir: str, content: str = None) -> str:
        """Create a test PDF file"""
        if content is None:
            content = "Test PDF content for document processing pipeline testing."
        
        pdf_path = os.path.join(temp_dir, "test_document.pdf")
        with open(pdf_path, "w") as f:
            f.write(f"%PDF-1.4\n{content}")
        return pdf_path
    
    @staticmethod
    def create_test_docx_file(temp_dir: str, content: str = None) -> str:
        """Create a test DOCX file"""
        if content is None:
            content = "Test DOCX content for document processing pipeline testing."
        
        docx_path = os.path.join(temp_dir, "test_document.docx")
        # Create minimal DOCX structure (ZIP file)
        with open(docx_path, "wb") as f:
            f.write(b"PK\x03\x04")  # ZIP signature
        return docx_path
    
    @staticmethod
    def create_test_txt_file(temp_dir: str, content: str = None) -> str:
        """Create a test text file"""
        if content is None:
            content = """
            Test Document for AI Q&A System
            
            This is a comprehensive test document that contains multiple paragraphs
            of text to verify the document processing pipeline functionality.
            
            The document includes information about machine learning, artificial
            intelligence, and natural language processing to test the question
            answering capabilities of the system.
            
            Key topics covered:
            1. Machine learning algorithms and applications
            2. Deep learning neural network architectures  
            3. Natural language processing techniques
            4. AI ethics and responsible deployment
            """
        
        txt_path = os.path.join(temp_dir, "test_document.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(content)
        return txt_path

# =============================================================================
# ASSERTION HELPERS
# =============================================================================

def assert_valid_embedding(embedding, expected_dim=1280):
    """Assert that an embedding vector is valid"""
    assert isinstance(embedding, list)
    assert len(embedding) == expected_dim
    assert all(isinstance(val, (int, float)) for val in embedding)

def assert_valid_chunk(chunk):
    """Assert that a document chunk has valid structure"""
    assert isinstance(chunk, dict)
    assert "content" in chunk
    assert "metadata" in chunk
    assert isinstance(chunk["content"], str)
    assert len(chunk["content"].strip()) > 0
    assert isinstance(chunk["metadata"], dict)

def assert_valid_api_response(response, expected_fields=None):
    """Assert that an API response has valid structure"""
    if expected_fields is None:
        expected_fields = ["success"]
    
    assert isinstance(response, dict)
    for field in expected_fields:
        assert field in response

def assert_valid_ai_answer(answer_response):
    """Assert that an AI answer response has valid structure"""
    required_fields = ["success", "answer", "rationale", "source_chunks"]
    assert_valid_api_response(answer_response, required_fields)
    
    if answer_response["success"]:
        assert isinstance(answer_response["answer"], str)
        assert isinstance(answer_response["rationale"], str)
        assert isinstance(answer_response["source_chunks"], list)
        assert len(answer_response["answer"].strip()) > 0
        assert len(answer_response["rationale"].strip()) > 0

# =============================================================================
# MOCK HELPERS
# =============================================================================

class MockHelpers:
    """Helper functions for creating consistent mocks"""
    
    @staticmethod
    def mock_successful_embedding_response(embedding_data):
        """Create mock successful embedding API response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"embedding": embedding_data}
        return mock_response
    
    @staticmethod
    def mock_api_error_response(status_code, error_message):
        """Create mock API error response"""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"error": {"message": error_message}}
        return mock_response
    
    @staticmethod
    def mock_vector_search_results(num_results=3):
        """Create mock vector search results"""
        results = []
        for i in range(num_results):
            result = Mock()
            result.page_content = f"Mock search result content {i+1}"
            result.metadata = {
                "filename": f"document_{i+1}.pdf",
                "page": i+1,
                "similarity_score": 0.9 - (i * 0.1)
            }
            results.append(result)
        return results

# =============================================================================
# TEST ENVIRONMENT SETUP
# =============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup and teardown test environment for the entire test session"""
    print("🔧 Setting up comprehensive test environment...")
    
    # Create necessary directories
    test_dirs = ["temp_test_files", "test_outputs", "coverage_reports"]
    for dir_name in test_dirs:
        os.makedirs(dir_name, exist_ok=True)
    
    # Set environment variables for testing
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    yield
    
    # Cleanup after all tests
    print("🧹 Cleaning up test environment...")
    for dir_name in test_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name, ignore_errors=True)
    
    # Clean up environment variables
    os.environ.pop("TESTING", None)
    os.environ.pop("LOG_LEVEL", None)
