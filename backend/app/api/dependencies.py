"""FastAPI dependencies for database and authentication."""

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key_validator import APIKeyValidator
from app.auth.models import User
from app.config import settings
from app.database.connection import get_db

# Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from API key.

    Args:
        credentials: HTTP Bearer credentials from the request.
        db: Database session.

    Returns:
        Authenticated User object.

    Raises:
        HTTPException: If authentication fails.
    """
    validator = APIKeyValidator(db)
    user_info = await validator.validate_key(credentials.credentials)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return User(**user_info)


async def require_master_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> bool:
    """Validate that the request is authenticated with the LiteLLM master key.

    Unlike ``get_current_user``, this dependency does NOT look up the
    token in the virtual keys table. It compares the provided token
    against the ``LITELLM_MASTER_KEY`` environment variable using a
    constant-time comparison to prevent timing attacks.

    A regular virtual API key will never match the master key and is
    therefore rejected with 403 Forbidden.

    Raises:
        HTTPException: 401 if no token is provided, 403 if the token is
            not the configured master key.

    Returns:
        ``True`` when the master key is valid.
    """
    configured = settings.litellm_master_key
    if not configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Master key is not configured on the server",
        )

    provided = credentials.credentials
    if not provided:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing master key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not secrets.compare_digest(provided, configured):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Master key required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True
