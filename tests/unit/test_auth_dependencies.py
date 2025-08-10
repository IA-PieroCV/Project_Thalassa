"""
Unit tests for authentication dependencies.

This module tests the FastAPI authentication dependencies including
bearer token verification and request authentication.
"""

from unittest.mock import Mock, patch

from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
import pytest

from app.dependencies.auth import (
    get_authorization_header,
    require_authentication,
    verify_bearer_token,
)


class TestAuthDependencies:
    """Test cases for authentication dependencies."""

    @pytest.mark.asyncio
    async def test_get_authorization_header_present(self):
        """Test getting authorization header when present."""
        mock_request = Mock()
        mock_request.headers = {"authorization": "Bearer test-token"}

        result = await get_authorization_header(mock_request)
        assert result == "Bearer test-token"

    @pytest.mark.asyncio
    async def test_get_authorization_header_missing(self):
        """Test getting authorization header when missing."""
        mock_request = Mock()
        mock_request.headers = {}

        result = await get_authorization_header(mock_request)
        assert result is None

    @pytest.mark.asyncio
    async def test_verify_bearer_token_valid(self):
        """Test bearer token verification with valid credentials."""
        with patch("app.dependencies.auth.auth_service") as mock_auth_service:
            mock_auth_service.validate_bearer_token.return_value = True

            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer", credentials="test-token-123"
            )

            # Should not raise any exception
            await verify_bearer_token(credentials)
            mock_auth_service.validate_bearer_token.assert_called_once_with(
                "test-token-123"
            )

    @pytest.mark.asyncio
    async def test_verify_bearer_token_invalid(self):
        """Test bearer token verification with invalid credentials."""
        with patch("app.dependencies.auth.auth_service") as mock_auth_service:
            mock_auth_service.validate_bearer_token.return_value = False

            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer", credentials="invalid-token"
            )

            with pytest.raises(HTTPException) as exc_info:
                await verify_bearer_token(credentials)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid bearer token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_bearer_token_missing_credentials(self):
        """Test bearer token verification with missing credentials."""
        with pytest.raises(HTTPException) as exc_info:
            await verify_bearer_token(None)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Authorization header is required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_require_authentication_success(self):
        """Test require_authentication dependency with valid token."""
        with patch("app.dependencies.auth.auth_service") as mock_auth_service:
            mock_auth_service.authenticate_request.return_value = None

            # Should not raise any exception
            await require_authentication("Bearer test-token-123")
            mock_auth_service.authenticate_request.assert_called_once_with(
                "Bearer test-token-123"
            )

    @pytest.mark.asyncio
    async def test_require_authentication_failure(self):
        """Test require_authentication dependency with authentication failure."""
        with patch("app.dependencies.auth.auth_service") as mock_auth_service:
            mock_auth_service.authenticate_request.side_effect = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token"
            )

            with pytest.raises(HTTPException) as exc_info:
                await require_authentication("Bearer invalid-token")

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid bearer token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_require_authentication_missing_header(self):
        """Test require_authentication dependency with missing header."""
        with patch("app.dependencies.auth.auth_service") as mock_auth_service:
            mock_auth_service.authenticate_request.side_effect = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header is required",
            )

            with pytest.raises(HTTPException) as exc_info:
                await require_authentication(None)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_require_auth_annotation(self):
        """Test that RequireAuth annotation is properly configured."""
        from app.dependencies.auth import RequireAuth

        # RequireAuth should be an Annotated type
        assert RequireAuth is not None

        # We can't easily test the annotation structure without more complex introspection,
        # but we can verify it exists and can be imported
