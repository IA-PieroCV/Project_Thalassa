"""
Unit tests for the authentication service.

This module tests the AuthService functionality including
bearer token validation, token extraction, and request authentication.
"""

from fastapi import HTTPException, status
import pytest

from app.services.auth import AuthService


class TestAuthService:
    """Test cases for AuthService."""

    @pytest.fixture
    def auth_service_with_token(self):
        """Create an auth service with a test token."""
        return AuthService(bearer_token="test-token-123")

    @pytest.fixture
    def auth_service_no_token(self):
        """Create an auth service without a token."""
        return AuthService(bearer_token=None)

    def test_validate_bearer_token_valid(self, auth_service_with_token):
        """Test bearer token validation with valid token."""
        assert auth_service_with_token.validate_bearer_token("test-token-123") is True

    def test_validate_bearer_token_invalid(self, auth_service_with_token):
        """Test bearer token validation with invalid token."""
        assert auth_service_with_token.validate_bearer_token("wrong-token") is False
        assert auth_service_with_token.validate_bearer_token("") is False
        assert auth_service_with_token.validate_bearer_token("test-token-124") is False

    def test_validate_bearer_token_no_configured_token(self, auth_service_no_token):
        """Test bearer token validation when no token is configured."""
        assert auth_service_no_token.validate_bearer_token("any-token") is False

    def test_extract_bearer_token_valid(self, auth_service_with_token):
        """Test token extraction from valid Authorization headers."""
        valid_headers = [
            "Bearer test-token-123",
            "Bearer   test-token-with-spaces   ",
            "Bearer abc123def456",
        ]

        expected_tokens = [
            "test-token-123",
            "test-token-with-spaces",
            "abc123def456",
        ]

        for header, expected in zip(valid_headers, expected_tokens, strict=False):
            token = auth_service_with_token.extract_bearer_token(header)
            assert token == expected

    def test_extract_bearer_token_missing_header(self, auth_service_with_token):
        """Test token extraction with missing Authorization header."""
        with pytest.raises(HTTPException) as exc_info:
            auth_service_with_token.extract_bearer_token("")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Authorization header is required" in exc_info.value.detail

    def test_extract_bearer_token_invalid_format(self, auth_service_with_token):
        """Test token extraction with invalid header formats."""
        invalid_headers = [
            "Basic dGVzdDp0ZXN0",  # Basic auth instead of Bearer
            "bearer token",  # lowercase bearer
            "Token test-token",  # Wrong scheme
            "Bearer",  # Missing token
            "Bearer ",  # Empty token
            "Bearer   ",  # Whitespace only token
        ]

        for header in invalid_headers:
            with pytest.raises(HTTPException) as exc_info:
                auth_service_with_token.extract_bearer_token(header)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticate_request_success(self, auth_service_with_token):
        """Test successful request authentication."""
        # Should not raise any exception
        auth_service_with_token.authenticate_request("Bearer test-token-123")

    def test_authenticate_request_missing_header(self, auth_service_with_token):
        """Test request authentication with missing header."""
        with pytest.raises(HTTPException) as exc_info:
            auth_service_with_token.authenticate_request(None)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Authorization header is required" in exc_info.value.detail

    def test_authenticate_request_invalid_token(self, auth_service_with_token):
        """Test request authentication with invalid token."""
        with pytest.raises(HTTPException) as exc_info:
            auth_service_with_token.authenticate_request("Bearer wrong-token")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid bearer token" in exc_info.value.detail

    def test_authenticate_request_invalid_format(self, auth_service_with_token):
        """Test request authentication with invalid header format."""
        with pytest.raises(HTTPException) as exc_info:
            auth_service_with_token.authenticate_request("Basic dGVzdA==")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticate_request_no_configured_token(self, auth_service_no_token):
        """Test request authentication when no token is configured."""
        with pytest.raises(HTTPException) as exc_info:
            auth_service_no_token.authenticate_request("Bearer any-token")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid bearer token" in exc_info.value.detail

    def test_www_authenticate_header_included(self, auth_service_with_token):
        """Test that WWW-Authenticate header is included in error responses."""
        with pytest.raises(HTTPException) as exc_info:
            auth_service_with_token.authenticate_request(None)

        assert exc_info.value.headers
        assert "WWW-Authenticate" in exc_info.value.headers
        assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"

    def test_case_sensitive_bearer_token(self, auth_service_with_token):
        """Test that bearer token comparison is case-sensitive."""
        # Token validation should be case-sensitive
        assert auth_service_with_token.validate_bearer_token("test-token-123") is True
        assert auth_service_with_token.validate_bearer_token("Test-Token-123") is False
        assert auth_service_with_token.validate_bearer_token("TEST-TOKEN-123") is False
