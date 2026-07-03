"""Budget repository for budget data access.

Reads the per-key budget from LiteLLM's ``max_budget`` column on
``LiteLLM_VerificationToken``. If the key is missing or has no
``max_budget`` set, falls back to the global default configured in
``settings.default_monthly_budget``.
"""

from dataclasses import dataclass

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.litellm import LiteLLMVirtualKeys

logger = structlog.get_logger()


@dataclass
class BudgetData:
    """Budget configuration data resolved for a key."""

    max_budget: float
    currency: str


class BudgetRepository:
    """Repository for budget data.

    The cap is always the key's flat ``max_budget`` column — the same
    value LiteLLM enforces. The ``budget_limits`` JSONB window is
    intentionally NOT consulted: the user budget panel should show
    progress against the key's hard cap, not against an arbitrary
    rolling window.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_key_budget(self, api_key: str) -> BudgetData:
        """Get budget configuration for the given API key.

        Args:
            api_key: The user's API key (hashed internally to match
                LiteLLM's storage format).

        Returns:
            Budget configuration for the key, or the global default if
            the key has no ``max_budget`` configured.
        """
        from app.auth.api_key_validator import hash_token

        hashed_key = hash_token(api_key) if api_key.startswith("sk-") else api_key

        query = select(LiteLLMVirtualKeys.max_budget).where(
            LiteLLMVirtualKeys.token == hashed_key
        )
        result = await self.db.execute(query)
        row = result.one_or_none()

        if row is None:
            logger.info("Using default budget (key not found)", key_prefix=api_key[:10])
            return self._default_budget()

        max_budget = row.max_budget
        if max_budget is not None and max_budget > 0:
            logger.info("Using key max_budget", max_budget=max_budget)
            return BudgetData(
                max_budget=float(max_budget),
                currency=settings.default_currency,
            )

        logger.info("Using default budget (no max_budget configured for key)")
        return self._default_budget()

    def _default_budget(self) -> BudgetData:
        return BudgetData(
            max_budget=settings.default_monthly_budget,
            currency=settings.default_currency,
        )
