"""LiteLLM virtual API key validator."""

import hashlib
import json
from typing import Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.litellm import LiteLLMVirtualKeys

logger = structlog.get_logger()


def hash_token(token: str) -> str:
    """Hash a token using SHA-256, matching LiteLLM's hash_token function."""
    return hashlib.sha256(token.encode()).hexdigest()


class APIKeyValidator:
    """Validates LiteLLM virtual API keys and extracts user identity."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate_key(self, api_key: str) -> Optional[dict[str, str]]:
        """Validate API key and return user information.

        Args:
            api_key: The LiteLLM virtual API key to validate.

        Returns:
            Dictionary with user_id and email if valid, None otherwise.
        """
        # Remove 'Bearer ' prefix if present
        if api_key.startswith("Bearer "):
            api_key = api_key[7:]

        # LiteLLM stores keys as SHA-256 hashes in the token column.
        # Keys starting with 'sk-' are hashed before lookup.
        if api_key.startswith("sk-"):
            hashed_key = hash_token(api_key)
        else:
            # Non-sk- tokens (e.g. master key, JWT) are used as-is
            hashed_key = api_key

        # Query the verification tokens table using the hashed key
        query = select(LiteLLMVirtualKeys).where(LiteLLMVirtualKeys.token == hashed_key)
        result = await self.db.execute(query)
        key_record = result.scalar_one_or_none()

        if not key_record:
            logger.warning("Invalid API key", key_prefix=api_key[:10] + "...")
            return None

        # Extract user information from metadata
        user_id = key_record.user_id or key_record.token[:16]
        email = self._extract_email_from_metadata(key_record.key_metadata) or f"{user_id}@unknown"

        logger.info("API key validated", user_id=user_id)

        return {
            "id": user_id,
            "email": email,
            "api_key": api_key,
        }

    def _extract_email_from_metadata(self, metadata_json: Optional[str]) -> Optional[str]:
        """Extract email from metadata JSON field."""
        if not metadata_json:
            return None

        try:
            metadata = json.loads(metadata_json)
            return metadata.get("email") or metadata.get("user_email")
        except (json.JSONDecodeError, AttributeError):
            return None
