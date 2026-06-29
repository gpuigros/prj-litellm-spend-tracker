"""Authentication models."""

from pydantic import BaseModel, Field


class User(BaseModel):
    """Authenticated user model."""

    id: str = Field(..., description="User identifier (from API key)")
    email: str = Field(..., description="User email address")
    api_key: str = Field(..., description="LiteLLM virtual API key")
