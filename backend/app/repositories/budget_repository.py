"""Budget repository for budget data access."""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings


@dataclass
class BudgetData:
    """Budget configuration data."""

    monthly_budget: float
    currency: str


class BudgetRepository:
    """Repository for budget data.

    Budgets are currently configured via environment variables.
    Future versions may store per-user budgets in the database.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_budget(self, user_id: str) -> BudgetData:
        """Get budget configuration for user.

        Args:
            user_id: User identifier (currently unused, budgets are global)

        Returns:
            Budget configuration
        """
        # Use global defaults from settings
        # Future: query user-specific budget from database
        return BudgetData(
            monthly_budget=settings.default_monthly_budget,
            currency=settings.default_currency,
        )
