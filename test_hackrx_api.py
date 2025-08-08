#!/usr/bin/env python3
"""
Pytest test module for HackRx API endpoint `/api/v1/hackrx/run`.

This module contains comprehensive tests for the HackRx FastAPI application,
including success cases, authentication failures, and validation errors.

Tests cover:
- Successful API requests with proper authentication
- Missing authentication scenarios  
- Invalid authentication scenarios
- Invalid payload validation
- Response structure validation
"""

import pytest
import json
from fastapi.testclient import TestClient
from typing import Dict, Any, List

# Import the FastAPI app instance
from hackrx_api_fixed import app


class TestHackRxAPI:
    """Test suite for the HackRx API endpoint."""

    @pytest.fixture
    def client(self) -> TestClient:
        """
        Initialize FastAPI TestClient with the app under test.
        
        Returns:
            TestClient: Configured test client for API testing
        """
        return TestClient(app)

    @pytest.fixture
    def valid_auth_header(self) -> Dict[str, str]:
        """
        Provide valid authorization header for authenticated requests.
        
        Returns:
            Dict[str, str]: Headers with valid Bearer token
        """
        return {
            "Authorization": "Bearer 38b55709d56bfa29e00fe840d84c0d2cc0b092396ba148b8f535262a4b3894e0"
        }

    @pytest.fixture
    def invalid_auth_header(self) -> Dict[str, str]:
        """
        Provide invalid authorization header for negative testing.
        
        Returns:
            Dict[str, str]: Headers with invalid Bearer token
        """
        return {
            "Authorization": "Bearer invalid_token_12345"
        }

    @pytest.fixture
    def sample_request_payload(self) -> Dict[str, Any]:
        """
        Provide sample request payload with document URL and questions.
        
        Note: The API expects 'document_url' (singular), not 'documents'.
        
        Returns:
            Dict[str, Any]: Valid request payload structure
        """
        return {
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

    def test_hackrx_run_success(self, client: TestClient, valid_auth_header: Dict[str, str], 
                               sample_request_payload: Dict[str, Any]) -> None:
        """
        Test successful HackRx API request with valid authentication and payload.
        
        This test verifies:
        - POST request to /api/v1/hackrx/run succeeds with proper authentication
        - Response status is 200 OK
        - Response contains 'answers' key with list of strings
        - Response list has same number of answers as questions (10)
        - Answers contain relevant insurance policy information
        
        Args:
            client: FastAPI test client
            valid_auth_header: Headers with valid Bearer token
            sample_request_payload: Valid request body with document URL and questions
        """
        # Send POST request to the HackRx endpoint
        response = client.post(
            "/api/v1/hackrx/run",
            json=sample_request_payload,
            headers=valid_auth_header
        )
        
        # Assert response status is 200 OK
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Parse response JSON
        response_json = response.json()
        
        # Assert response contains 'answers' key
        assert "answers" in response_json, f"Response missing 'answers' key: {response_json}"
        
        # Assert answers is a list
        assert isinstance(response_json["answers"], list), f"Answers should be a list: {type(response_json['answers'])}"
        
        # Assert we have 10 answers (one for each question)
        answers = response_json["answers"]
        assert len(answers) == 10, f"Expected 10 answers, got {len(answers)}"
        
        # Assert all answers are strings
        for i, answer in enumerate(answers):
            assert isinstance(answer, str), f"Answer {i} should be string: {type(answer)}"
            assert len(answer.strip()) > 0, f"Answer {i} should not be empty"
        
        # Optional: Assert certain key phrases are present in corresponding answers
        expected_keywords = [
            ("thirty days", "grace period"),  # Grace period question
            ("waiting period", "pre-existing"),  # PED waiting period  
            ("maternity", "pregnancy"),  # Maternity coverage
            ("cataract", "waiting"),  # Cataract waiting period
            ("organ donor", "medical expenses"),  # Organ donor coverage
            ("claim discount", "NCD"),  # No Claim Discount
            ("preventive", "health check"),  # Preventive health check-ups
            ("hospital", "definition"),  # Hospital definition
            ("AYUSH", "treatment"),  # AYUSH coverage
            ("room rent", "sub-limit")  # Room rent sub-limits
        ]
        
        # Check if relevant keywords appear in answers (case-insensitive)
        for i, (keyword1, keyword2) in enumerate(expected_keywords):
            answer_lower = answers[i].lower()
            keyword_found = keyword1.lower() in answer_lower or keyword2.lower() in answer_lower
            # Note: This is optional verification - answers may vary based on document content
            if not keyword_found:
                print(f"Warning: Answer {i} may not contain expected keywords '{keyword1}' or '{keyword2}': {answers[i][:100]}...")

    def test_hackrx_run_missing_auth(self, client: TestClient, 
                                   sample_request_payload: Dict[str, Any]) -> None:
        """
        Test HackRx API request without authentication header.
        
        This test verifies:
        - POST request without Authorization header is rejected
        - Response status is 401 Unauthorized
        - Error message indicates authentication is required
        
        Args:
            client: FastAPI test client
            sample_request_payload: Valid request body (auth is the issue)
        """
        # Send POST request without Authorization header
        response = client.post(
            "/api/v1/hackrx/run",
            json=sample_request_payload
            # Note: No headers parameter = no authentication
        )
        
        # Assert response status is 401 Unauthorized
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        
        # Parse response JSON to check error message
        response_json = response.json()
        assert "detail" in response_json, f"Response should contain error detail: {response_json}"
        
        # Verify error message indicates authentication issue
        detail = response_json["detail"].lower()
        assert "authorization" in detail or "token" in detail, f"Error should mention authorization: {response_json['detail']}"

    def test_hackrx_run_invalid_auth(self, client: TestClient, invalid_auth_header: Dict[str, str],
                                   sample_request_payload: Dict[str, Any]) -> None:
        """
        Test HackRx API request with invalid authentication token.
        
        This test verifies:
        - POST request with invalid Bearer token is rejected
        - Response status is 401 Unauthorized  
        - Error message indicates invalid token
        
        Args:
            client: FastAPI test client
            invalid_auth_header: Headers with invalid Bearer token
            sample_request_payload: Valid request body (auth token is the issue)
        """
        # Send POST request with invalid Authorization header
        response = client.post(
            "/api/v1/hackrx/run", 
            json=sample_request_payload,
            headers=invalid_auth_header
        )
        
        # Assert response status is 401 Unauthorized
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        
        # Parse response JSON to check error message
        response_json = response.json()
        assert "detail" in response_json, f"Response should contain error detail: {response_json}"
        
        # Verify error message indicates invalid token
        detail = response_json["detail"].lower()
        assert "invalid" in detail or "authorization" in detail, f"Error should mention invalid auth: {response_json['detail']}"

    def test_hackrx_run_missing_document_url(self, client: TestClient, 
                                           valid_auth_header: Dict[str, str]) -> None:
        """
        Test HackRx API request with missing 'document_url' field.
        
        This test verifies:
        - POST request without required document_url field is rejected
        - Response status is 422 Unprocessable Entity (validation error)
        - Error indicates missing required field
        
        Args:
            client: FastAPI test client
            valid_auth_header: Valid authentication (payload is the issue)
        """
        # Create payload missing 'document_url' field
        invalid_payload = {
            "questions": [
                "What is the grace period for premium payment?",
                "What is the waiting period for pre-existing diseases?"
            ]
            # Missing 'document_url' field
        }
        
        # Send POST request with invalid payload
        response = client.post(
            "/api/v1/hackrx/run",
            json=invalid_payload,
            headers=valid_auth_header
        )
        
        # Assert response status is 422 Unprocessable Entity
        assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"
        
        # Parse response JSON to check validation error
        response_json = response.json()
        assert "detail" in response_json, f"Response should contain validation details: {response_json}"
        
        # Verify error mentions missing field (FastAPI validation format)
        detail_str = str(response_json["detail"])
        assert "document_url" in detail_str, f"Error should mention missing document_url: {response_json['detail']}"

    def test_hackrx_run_missing_questions(self, client: TestClient,
                                        valid_auth_header: Dict[str, str]) -> None:
        """
        Test HackRx API request with missing 'questions' field.
        
        This test verifies:
        - POST request without required questions field is rejected  
        - Response status is 422 Unprocessable Entity (validation error)
        - Error indicates missing required field
        
        Args:
            client: FastAPI test client
            valid_auth_header: Valid authentication (payload is the issue)
        """
        # Create payload missing 'questions' field
        invalid_payload = {
            "document_url": "https://example.com/test-document.pdf"
            # Missing 'questions' field
        }
        
        # Send POST request with invalid payload
        response = client.post(
            "/api/v1/hackrx/run",
            json=invalid_payload,
            headers=valid_auth_header
        )
        
        # Assert response status is 422 Unprocessable Entity
        assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"
        
        # Parse response JSON to check validation error
        response_json = response.json()
        assert "detail" in response_json, f"Response should contain validation details: {response_json}"
        
        # Verify error mentions missing field
        detail_str = str(response_json["detail"])
        assert "questions" in detail_str, f"Error should mention missing questions: {response_json['detail']}"

    def test_hackrx_run_invalid_document_url(self, client: TestClient,
                                           valid_auth_header: Dict[str, str]) -> None:
        """
        Test HackRx API request with invalid document URL format.
        
        This test verifies:
        - POST request with malformed URL is rejected
        - Response status is 422 Unprocessable Entity (validation error)
        - Error indicates URL validation failure
        
        Args:
            client: FastAPI test client  
            valid_auth_header: Valid authentication (URL format is the issue)
        """
        # Create payload with invalid URL format
        invalid_payload = {
            "document_url": "not-a-valid-url-format",  # Invalid URL
            "questions": ["What is covered in this policy?"]
        }
        
        # Send POST request with invalid URL
        response = client.post(
            "/api/v1/hackrx/run",
            json=invalid_payload,
            headers=valid_auth_header
        )
        
        # Assert response status is 422 Unprocessable Entity
        assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"
        
        # Parse response JSON to check validation error
        response_json = response.json()
        assert "detail" in response_json, f"Response should contain validation details: {response_json}"
        
        # Verify error mentions URL validation (FastAPI/Pydantic HttpUrl validation)
        detail_str = str(response_json["detail"]).lower()
        url_error_indicators = ["url", "invalid", "scheme", "format"]
        assert any(indicator in detail_str for indicator in url_error_indicators), \
            f"Error should mention URL validation issue: {response_json['detail']}"

    def test_hackrx_run_empty_questions_list(self, client: TestClient,
                                           valid_auth_header: Dict[str, str]) -> None:
        """
        Test HackRx API request with empty questions list.
        
        This test verifies API behavior when questions list is empty.
        Depending on business logic, this might be:
        - 422 validation error (if questions must not be empty)
        - 200 with empty answers list (if empty questions are allowed)
        
        Args:
            client: FastAPI test client
            valid_auth_header: Valid authentication
        """
        # Create payload with empty questions list
        payload_empty_questions = {
            "document_url": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
            "questions": []  # Empty list
        }
        
        # Send POST request with empty questions
        response = client.post(
            "/api/v1/hackrx/run",
            json=payload_empty_questions,
            headers=valid_auth_header
        )
        
        # The API might handle empty questions in different ways:
        if response.status_code == 200:
            # If API accepts empty questions and returns empty answers
            response_json = response.json()
            assert "answers" in response_json, "Response should contain answers key"
            assert len(response_json["answers"]) == 0, "Should return empty answers list"
        elif response.status_code == 422:
            # If API validates that questions list must not be empty
            response_json = response.json()
            assert "detail" in response_json, "Should contain validation error details"
        else:
            # Unexpected status code
            pytest.fail(f"Unexpected status code for empty questions: {response.status_code}")

    def test_hackrx_api_health_endpoint(self, client: TestClient) -> None:
        """
        Test the health check endpoint to verify API is operational.
        
        This test verifies:
        - Health endpoint is accessible without authentication
        - Returns 200 OK status
        - Contains expected health information
        
        Args:
            client: FastAPI test client
        """
        # Send GET request to health endpoint
        response = client.get("/api/v1/hackrx/health")
        
        # Assert response status is 200 OK
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Parse response JSON
        response_json = response.json()
        
        # Verify response structure (based on typical health check format)
        assert "status" in response_json, f"Health response should contain status: {response_json}"
        assert response_json["status"] in ["healthy", "ok", "operational"], \
            f"Status should indicate healthy state: {response_json['status']}"


if __name__ == "__main__":
    """
    Run tests directly with pytest if this file is executed.
    
    Usage:
        python test_hackrx_api.py
        
    Or run with pytest command:
        pytest test_hackrx_api.py -v
        pytest test_hackrx_api.py::TestHackRxAPI::test_hackrx_run_success -v
    """
    pytest.main([__file__, "-v"])
