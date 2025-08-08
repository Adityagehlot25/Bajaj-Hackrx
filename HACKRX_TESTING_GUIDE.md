# HackRx API Testing Guide

## 🎯 Overview
This guide covers comprehensive testing for the HackRx FastAPI application using pytest and FastAPI TestClient.

## 📋 Test Module Structure

### `test_hackrx_api.py`
Complete test suite for the HackRx API endpoint `/api/v1/hackrx/run` covering:

- **Success scenarios** with valid authentication and payloads
- **Authentication failures** (missing/invalid tokens)  
- **Validation errors** (missing fields, invalid URLs)
- **Edge cases** (empty questions, malformed data)
- **Health check endpoint** verification

## 🚀 Quick Start

### 1. Install Testing Dependencies
```bash
# Install all testing requirements
pip install -r requirements_test.txt

# Or install individually
pip install pytest pytest-asyncio fastapi[all] httpx
```

### 2. Run All HackRx API Tests
```bash
# Using pytest directly
pytest test_hackrx_api.py -v

# Using the test runner script
python run_hackrx_tests.py
```

### 3. Run Specific Test Categories
```bash
# Authentication tests only
pytest test_hackrx_api.py -m auth -v

# Integration tests only  
pytest test_hackrx_api.py -m integration -v

# Single test function
pytest test_hackrx_api.py::TestHackRxAPI::test_hackrx_run_success -v
```

## 🧪 Test Categories

### ✅ Success Tests
- `test_hackrx_run_success`: Valid request with proper authentication
- `test_hackrx_api_health_endpoint`: Health check endpoint verification

### 🔐 Authentication Tests  
- `test_hackrx_run_missing_auth`: Request without Authorization header
- `test_hackrx_run_invalid_auth`: Request with invalid Bearer token

### 📋 Validation Tests
- `test_hackrx_run_missing_document_url`: Missing required document_url field
- `test_hackrx_run_missing_questions`: Missing required questions field  
- `test_hackrx_run_invalid_document_url`: Malformed URL validation
- `test_hackrx_run_empty_questions_list`: Empty questions array handling

## 📊 Expected Test Results

### ✅ Successful Test Run
```
test_hackrx_api.py::TestHackRxAPI::test_hackrx_run_success PASSED
test_hackrx_api.py::TestHackRxAPI::test_hackrx_run_missing_auth PASSED  
test_hackrx_api.py::TestHackRxAPI::test_hackrx_run_invalid_auth PASSED
test_hackrx_api.py::TestHackRxAPI::test_hackrx_run_missing_document_url PASSED
test_hackrx_api.py::TestHackRxAPI::test_hackrx_run_missing_questions PASSED
test_hackrx_api.py::TestHackRxAPI::test_hackrx_run_invalid_document_url PASSED
test_hackrx_api.py::TestHackRxAPI::test_hackrx_run_empty_questions_list PASSED
test_hackrx_api.py::TestHackRxAPI::test_hackrx_api_health_endpoint PASSED

============= 8 passed in 45.23s =============
```

## 🔧 Test Configuration

### Sample Request Payload
```json
{
  "document_url": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
  "questions": [
    "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
    "What is the waiting period for pre-existing diseases (PED) to be covered?",
    "Does this policy cover maternity expenses, and what are the conditions?",
    "What is the waiting period for cataract surgery?",
    "Are the medical expenses for an organ donor covered under this policy?",
    "What is the No Claim Discount (NCD) offered in this policy?",
    "Is there a benefit for preventive health check-ups?",
    "How does the policy define a 'Hospital'?",
    "What is the extent of coverage for AYUSH treatments?",
    "Are there any sub-limits on room rent and ICU charges for Plan A?"
  ]
}
```

### Valid Authorization Header
```
Authorization: Bearer 38b55709d56bfa29e00fe840d84c0d2cc0b092396ba148b8f535262a4b3894e0
```

## 🎨 Test Fixtures

### `client` - FastAPI TestClient
Initializes TestClient with the HackRx FastAPI app for making HTTP requests.

### `valid_auth_header` - Authentication Header
Provides valid Bearer token for authenticated requests.

### `invalid_auth_header` - Invalid Authentication  
Provides invalid Bearer token for negative testing.

### `sample_request_payload` - Request Body
Complete request payload with document URL and 10 insurance policy questions.

## 📈 Coverage Testing

### Run with Coverage Report
```bash
# Generate coverage report
pytest test_hackrx_api.py --cov=hackrx_api_fixed --cov-report=html --cov-report=term-missing

# Using test runner with coverage
python run_hackrx_tests.py --coverage --html-cov
```

### Coverage Report Location
- **HTML Report**: `htmlcov/index.html`
- **Terminal Report**: Displayed after test completion
- **XML Report**: `coverage.xml` (for CI/CD integration)

## 🐛 Debugging Tests

### Run Single Test with Verbose Output
```bash
pytest test_hackrx_api.py::TestHackRxAPI::test_hackrx_run_success -v -s --tb=long
```

### Debug API Response Issues
```bash
# Print response content for debugging
pytest test_hackrx_api.py -v -s --capture=no
```

### Check Environment Variables
```bash
# Verify environment setup before testing
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('GEMINI_API_KEY:', bool(os.getenv('GEMINI_API_KEY')))  
print('TEAM_TOKEN:', bool(os.getenv('TEAM_TOKEN')))
"
```

## ⚡ Advanced Test Scenarios

### Custom Test Markers
```bash
# Run only API endpoint tests
pytest -m api test_hackrx_api.py

# Run only authentication tests  
pytest -m auth test_hackrx_api.py

# Skip slow tests
pytest -m "not slow" test_hackrx_api.py
```

### Parallel Test Execution
```bash
# Install pytest-xdist for parallel execution
pip install pytest-xdist

# Run tests in parallel
pytest test_hackrx_api.py -n auto
```

## 🔍 Test Assertions

### Success Test Assertions
- ✅ Response status code is 200
- ✅ Response contains 'answers' key with list
- ✅ Number of answers matches number of questions (10)
- ✅ All answers are non-empty strings
- ✅ Optional keyword verification in answers

### Error Test Assertions  
- ✅ 401 status for authentication failures
- ✅ 422 status for validation errors
- ✅ Error messages contain relevant details
- ✅ Response structure follows FastAPI error format

## 🏆 Best Practices

### 1. Environment Isolation
```python
# Use environment variables for API keys
os.environ['GEMINI_API_KEY'] = 'test_key_value'
```

### 2. Mock External Services
```python
# Mock document download for faster tests
@pytest.fixture
def mock_document_download():
    with mock.patch('hackrx_api_fixed.download_document') as mock_dl:
        mock_dl.return_value = 'path/to/test/document.pdf'
        yield mock_dl
```

### 3. Test Data Management
```python
# Use fixtures for test data consistency
@pytest.fixture
def insurance_questions():
    return [
        "What is the grace period for premium payment?",
        "What is the waiting period for pre-existing diseases?"
    ]
```

## 📚 Related Files

- **`test_hackrx_api.py`**: Main test module
- **`requirements_test.txt`**: Testing dependencies
- **`run_hackrx_tests.py`**: Test runner script
- **`pytest.ini`**: Pytest configuration
- **`hackrx_api_fixed.py`**: Application under test

## 🎯 CI/CD Integration

### GitHub Actions Example
```yaml
name: HackRx API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements_test.txt
      - name: Run tests
        run: pytest test_hackrx_api.py --cov --junitxml=junit.xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

Your HackRx API now has comprehensive test coverage for all endpoints and scenarios! 🚀
