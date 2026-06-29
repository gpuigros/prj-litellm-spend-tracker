"""Custom exception classes for the API."""

from typing import Optional


class SpendAPIError(Exception):
    """Base exception for Spend API errors."""

    def __init__(self, message: str, status_code: int = 500, details: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(SpendAPIError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, status_code=401)


class AuthorizationError(SpendAPIError):
    """Raised when user lacks permission."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message, status_code=403)


class NotFoundError(SpendAPIError):
    """Raised when requested resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404)


class ValidationError(SpendAPIError):
    """Raised when request validation fails."""

    def __init__(self, message: str = "Validation error", details: Optional[dict] = None):
        super().__init__(message=message, status_code=422, details=details)


class DatabaseError(SpendAPIError):
    """Raised when database operations fail."""

    def __init__(self, message: str = "Database error"):
        super().__init__(message=message, status_code=500)
