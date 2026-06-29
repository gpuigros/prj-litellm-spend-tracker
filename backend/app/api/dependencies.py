"""FastAPI dependencies for database and authentication."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key_validator import APIKeyValidator
from app.auth.models import User
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
