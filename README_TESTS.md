# 🧪 Comprehensive Test Suite Documentation

## Overview

This comprehensive Python test suite provides complete testing coverage for the LLM-powered Document AI Q&A System using pytest. The test suite includes unit tests, integration tests, performance tests, security tests, and explainability tests with proper mocking to avoid external API calls.

## 📁 Test Suite Structure

```
e:\final try\
├── test_comprehensive_suite.py    # Main comprehensive test suite
├── conftest.py                    # Pytest configuration and shared fixtures
├── pytest.ini                    # Pytest settings and configuration
├── run_tests.py                  # Test runner script with categories
├── validate_tests.py             # Quick test validation script
└── README_TESTS.md               # This documentation file
```

## 🔧 Setup and Installation

### Prerequisites

```bash
# Install testing dependencies
pip install pytest pytest-asyncio pytest-mock pytest-cov

# Install FastAPI testing support
pip install httpx

# Verify installation
python -m pytest --version
```

### Quick Validation

```bash
# Validate test suite setup
python validate_tests.py
```

## 🚀 Running Tests

### Basic Test Execution

```bash
# Run all tests
python run_tests.py --all

# Run specific test categories
python run_tests.py --unit           # Unit tests only
python run_tests.py --integration    # Integration tests only
python run_tests.py --performance    # Performance tests only
python run_tests.py --security       # Security tests only
python run_tests.py --explainability # Explainability tests only

# Quick development testing
python run_tests.py --quick          # Fast tests only
python run_tests.py --coverage       # With coverage report
```

### Advanced Test Execution

```bash
# Run specific test file
python -m pytest test_comprehensive_suite.py -v

# Run specific test class
python -m pytest test_comprehensive_suite.py::TestDocumentIngestion -v

# Run specific test function
python -m pytest test_comprehensive_suite.py::TestDocumentIngestion::test_pdf_text_extraction_success -v

# Run with markers
python -m pytest -m unit            # Unit tests only
python -m pytest -m "not slow"      # Exclude slow tests
python -m pytest -m "integration or performance"  # Multiple markers
```

### Coverage Analysis

```bash
# Generate HTML coverage report
python -m pytest --cov=main --cov=gemini_answer --cov-report=html

# View coverage report
# Open htmlcov/index.html in your browser

# Terminal coverage report
python -m pytest --cov=main --cov-report=term-missing
```

## 📋 Test Categories

### 1. Unit Tests (`@pytest.mark.unit`)

**Document Ingestion Module:**
- ✅ PDF text extraction with PyMuPDF
- ✅ DOCX text extraction with python-docx  
- ✅ Plain text file processing
- ✅ Email file parsing and content extraction
- ✅ Error handling for corrupted/missing files

**Document Chunking Module:**
- ✅ Intelligent text chunking with word limits
- ✅ Semantic boundary preservation
- ✅ Metadata preservation and chunk ID assignment
- ✅ Empty text and edge case handling

**Embedding Generation Module:**
- ✅ Batch embedding generation with Gemini API
- ✅ Query embedding creation for search
- ✅ API error handling (401, 429, 500 errors)
- ✅ Embedding dimension validation (1280-dim vectors)

**Vector Search Module:**
- ✅ FAISS vector indexing and similarity search
- ✅ MMR (Maximal Marginal Relevance) search strategy
- ✅ Similarity threshold filtering
- ✅ Metadata-based search filtering
- ✅ Empty vector store handling

**LLM Integration Module:**
- ✅ Gemini API prompt formatting
- ✅ Structured JSON response parsing
- ✅ Malformed response handling
- ✅ API error scenarios (rate limiting, authentication)

### 2. Integration Tests (`@pytest.mark.integration`)

**FastAPI Endpoint Testing:**
- ✅ Complete `/hackrx/run` pipeline with document processing
- ✅ `/ask` endpoint with vector search + AI answering
- ✅ `/answer` endpoint for direct AI responses
- ✅ API request validation and error responses
- ✅ Health check endpoint functionality

**End-to-End Workflows:**
- ✅ Document upload → parsing → chunking → embedding → indexing
- ✅ Query processing → vector search → AI answer generation
- ✅ Multi-question processing with source attribution

### 3. Performance Tests (`@pytest.mark.performance`)

**Response Time Testing:**
- ✅ Direct answer endpoint latency (< 5 seconds)
- ✅ Health check response time (< 1 second)  
- ✅ Vector search performance with large result sets
- ✅ Batch processing performance monitoring

### 4. Security Tests (`@pytest.mark.security`)

**Authentication and Authorization:**
- ✅ HackRX endpoint Bearer token validation
- ✅ Invalid token rejection (401/403 responses)
- ✅ Missing authorization header handling
- ✅ Malformed authorization header validation

**Input Validation and Sanitization:**
- ✅ XSS prevention in API responses
- ✅ SQL injection attempt handling
- ✅ Oversized input validation
- ✅ Control character filtering

**Rate Limiting and Security:**
- ✅ API key validation and protection
- ✅ Rate limiting simulation and handling

### 5. Explainability Tests (`@pytest.mark.explainability`)

**AI Response Transparency:**
- ✅ Answer rationale inclusion and quality
- ✅ Source chunk attribution and references
- ✅ Document source tracking with page numbers
- ✅ Confidence and uncertainty indication

## 🔍 Mock Usage

### External Dependencies Mocked

**Network Calls:**
```python
@patch('main.httpx.AsyncClient')  # Document downloads
@patch('gemini_answer.httpx.AsyncClient')  # Gemini API calls
```

**File System Operations:**
```python
@patch('main.fitz.open')  # PDF parsing
@patch('main.Document')   # DOCX parsing
@patch('builtins.open')   # File operations
```

**Vector Store Operations:**
```python
@patch('main.get_vector_store')  # FAISS operations
```

### Mock Response Examples

**Gemini API Response:**
```python
mock_llm_response = {
    "candidates": [{
        "content": {
            "parts": [{
                "text": '{"answer": "...", "rationale": "...", "source_chunks": [...]}'
            }]
        },
        "finishReason": "STOP"
    }],
    "usageMetadata": {"totalTokenCount": 234}
}
```

**Embedding API Response:**
```python
mock_embedding_response = {
    "embedding": [0.1, 0.2, 0.3, ...] * 1280  # 1280-dimensional vector
}
```

## 📊 Test Data and Fixtures

### Shared Fixtures (conftest.py)

```python
@pytest.fixture
def test_client():
    """FastAPI test client"""
    
@pytest.fixture  
def temp_directory():
    """Temporary directory for test files"""
    
@pytest.fixture
def sample_embeddings():
    """Mock embedding vectors (1280-dim)"""
    
@pytest.fixture
def sample_chunks():
    """Sample document chunks with metadata"""
```

### Test Data Generation

```python
class TestDataGenerator:
    @staticmethod
    def create_test_pdf_file(temp_dir, content=None)
    
    @staticmethod
    def create_test_docx_file(temp_dir, content=None)
    
    @staticmethod
    def create_test_txt_file(temp_dir, content=None)
```

## ✅ Assertion Helpers

### Validation Functions

```python
def assert_valid_embedding(embedding, expected_dim=1280):
    """Validate embedding structure and dimensions"""
    
def assert_valid_chunk(chunk):
    """Validate document chunk structure"""
    
def assert_valid_api_response(response, expected_fields=None):
    """Validate API response structure"""
    
def assert_valid_ai_answer(answer_response):
    """Validate AI answer response structure"""
```

## 🏃‍♂️ Example Test Runs

### Run Unit Tests Only
```bash
$ python run_tests.py --unit

🚀 Unit Tests
============================================================
Running: python -m pytest -m unit test_comprehensive_suite.py --tb=line
========================= test session starts =========================
collected 25 items

test_comprehensive_suite.py::TestDocumentIngestion::test_pdf_text_extraction_success PASSED
test_comprehensive_suite.py::TestDocumentIngestion::test_docx_text_extraction_success PASSED
test_comprehensive_suite.py::TestDocumentChunking::test_intelligent_chunking_basic_functionality PASSED
test_comprehensive_suite.py::TestEmbeddingGeneration::test_generate_embeddings_success PASSED
test_comprehensive_suite.py::TestVectorSearch::test_faiss_indexing_and_search PASSED

========================= 25 passed in 2.34s =========================
✅ Unit Tests - PASSED
```

### Run Integration Tests with Coverage
```bash
$ python run_tests.py --integration --coverage

🚀 Integration Tests
============================================================
Running: python -m pytest -m integration test_comprehensive_suite.py --cov=main --cov=gemini_answer --cov-report=html
========================= test session starts =========================
collected 8 items

test_comprehensive_suite.py::TestFastAPIIntegration::test_hackrx_endpoint_full_pipeline PASSED
test_comprehensive_suite.py::TestFastAPIIntegration::test_hackrx_authentication_required PASSED

---------- coverage: platform win32, python 3.12.5 -----------
Coverage HTML written to dir htmlcov

========================= 8 passed in 5.67s =========================
✅ Integration Tests - PASSED
📋 Coverage report generated in htmlcov/index.html
```

## 🔧 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Solution: Ensure all dependencies are installed
pip install pytest pytest-asyncio pytest-mock pytest-cov httpx
```

**2. Module Not Found**
```bash
# Solution: Run tests from project root directory
cd "e:\final try"
python run_tests.py --unit
```

**3. Async Test Issues**
```bash
# Solution: Ensure pytest-asyncio is configured
# Check pytest.ini has: asyncio_mode = auto
```

**4. Mock Import Errors**
```bash
# Solution: Install pytest-mock
pip install pytest-mock
```

### Debug Mode

```bash
# Run with debug logging
python run_tests.py --debug --verbose

# Run specific test with maximum verbosity
python -m pytest test_comprehensive_suite.py::TestDocumentIngestion::test_pdf_text_extraction_success -vvv --log-cli --log-cli-level=DEBUG
```

## 📈 Coverage Goals

### Target Coverage Metrics

- **Overall Coverage:** > 90%
- **Unit Test Coverage:** > 95%
- **Integration Test Coverage:** > 85%
- **Critical Path Coverage:** 100%

### Coverage Reports

```bash
# Generate all coverage formats
python -m pytest --cov=main --cov=gemini_answer \
    --cov-report=html:htmlcov \
    --cov-report=xml:coverage.xml \
    --cov-report=term-missing \
    --cov-report=json:coverage.json
```

## 🎯 Best Practices

### Writing Tests

1. **Use descriptive test names** that explain what is being tested
2. **Follow Arrange-Act-Assert pattern** for clear test structure
3. **Mock external dependencies** to avoid network calls and costs
4. **Use fixtures** for reusable test data and setup
5. **Test both success and failure scenarios**
6. **Include edge cases** and boundary conditions

### Test Organization

1. **Group related tests** in classes (TestDocumentIngestion, etc.)
2. **Use markers** to categorize tests (@pytest.mark.unit)
3. **Keep tests independent** - no shared state between tests
4. **Use meaningful assertions** with clear error messages

### Performance Considerations

1. **Use session-scoped fixtures** for expensive setup operations
2. **Mock external API calls** to avoid network latency
3. **Run unit tests frequently**, integration tests less frequently
4. **Use --quick flag** for rapid development testing

## 🚦 Continuous Integration

### GitHub Actions Example

```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.12
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    - name: Run test suite
      run: python run_tests.py --all
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio)
- [Coverage.py](https://coverage.readthedocs.io/)

---

**🎉 Happy Testing!**

This comprehensive test suite ensures your Document AI Q&A System is robust, reliable, and ready for production deployment.
