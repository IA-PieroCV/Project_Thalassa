"""
Authentication dependencies for FastAPI endpoints.

This module provides FastAPI dependency injection for authentication
using Bearer tokens.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config import settings
from ..services.auth import AuthService

# Initialize HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)

# Initialize auth service with configured token
auth_service = AuthService(bearer_token=settings.bearer_token)


async def get_authorization_header(
    request: Request,
) -> str | None:
    """
    Extract Authorization header from request.

    Args:
        request: FastAPI request object

    Returns:
        Authorization header value or None
    """
    return request.headers.get("authorization")


async def verify_bearer_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> None:
    """
    FastAPI dependency to verify Bearer token authentication.

    Args:
        credentials: HTTP Bearer credentials from FastAPI security

    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not auth_service.validate_bearer_token(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_authentication(
    authorization: Annotated[str | None, Depends(get_authorization_header)],
) -> None:
    """
    FastAPI dependency that requires valid Bearer token authentication.

    This is an alternative to verify_bearer_token that works directly with
    the Authorization header for more control over error handling.

    Args:
        authorization: Authorization header from request

    Raises:
        HTTPException: If authentication fails
    """
    auth_service.authenticate_request(authorization)


# Dependency for protecting endpoints that require authentication
RequireAuth = Annotated[None, Depends(verify_bearer_token)]
