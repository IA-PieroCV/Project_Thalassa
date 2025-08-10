"""
Authentication service for Bearer Token validation.

This module provides functionality for validating Bearer tokens
according to the project's security requirements.
"""

import logging

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling Bearer Token authentication."""

    def __init__(self, bearer_token: str | None = None):
        """
        Initialize the authentication service.

        Args:
            bearer_token: The valid bearer token for authentication
        """
        self.bearer_token = bearer_token

        if not bearer_token:
            logger.warning(
                "No bearer token configured - authentication will reject all requests"
            )

    def validate_bearer_token(self, token: str) -> bool:
        """
        Validate a bearer token against the configured token.

        Args:
            token: The token to validate

        Returns:
            True if token is valid, False otherwise
        """
        if not self.bearer_token:
            logger.warning("Authentication attempted but no bearer token configured")
            return False

        if not token:
            return False

        # Simple constant-time comparison for bearer token
        return token == self.bearer_token

    def extract_bearer_token(self, authorization_header: str) -> str:
        """
        Extract bearer token from Authorization header.

        Args:
            authorization_header: The Authorization header value

        Returns:
            The extracted bearer token

        Raises:
            HTTPException: If header format is invalid
        """
        if not authorization_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header is required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if header starts with "Bearer "
        if not authorization_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Expected 'Bearer <token>'",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract token part after "Bearer "
        token = authorization_header[7:]  # len("Bearer ") = 7

        if not token.strip():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer token is required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return token.strip()

    def authenticate_request(self, authorization_header: str | None) -> None:
        """
        Authenticate a request using the Authorization header.

        Args:
            authorization_header: The Authorization header value

        Raises:
            HTTPException: If authentication fails
        """
        if not authorization_header:
            logger.info("Authentication failed: No Authorization header provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header is required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            token = self.extract_bearer_token(authorization_header)

            if not self.validate_bearer_token(token):
                logger.info("Authentication failed: Invalid bearer token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid bearer token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            logger.debug("Authentication successful")

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error",
            ) from e
