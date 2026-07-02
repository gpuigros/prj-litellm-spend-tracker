"""Budget service for budget calculations and state determination.

Uses the real LiteLLM budget window (from ``budget_limits``) when
available, falling back to the calendar month otherwise.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.budget import BudgetResponse, BudgetState
from app.models.spend import Period
from app.repositories.budget_repository import BudgetRepository
from app.repositories.spend_repository import SpendRepository
from app.utils.date_utils import get_period_range


class BudgetService:
    """Service for budget calculations and state management."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.spend_repo = SpendRepository(db)
        self.budget_repo = BudgetRepository(db)

    async def get_budget(self, user_id: str, api_key: str) -> BudgetResponse:
        """Get budget information for user.

        Args:
            user_id: User identifier
            api_key: User's API key (used to look up key-specific budget
                and to filter spend logs)

        Returns:
            Budget information with state (normal/warning/exceeded)
        """
        budget = await self.budget_repo.get_key_budget(api_key)

        # Spend is always measured over the current calendar month so the
        # budget panel reflects the same period the user selected. The
        # budget window from budget_limits only provides max_budget.
        start_date, end_date = get_period_range(Period.MONTH)
        spent = await self.spend_repo.get_total_spend(api_key, start_date, end_date)

        remaining = budget.max_budget - spent
        used_percent = (
            (spent / budget.max_budget * 100) if budget.max_budget > 0 else 0
        )

        state = self._determine_budget_state(used_percent)

        return BudgetResponse(
            user_id=user_id,
            monthly_budget=budget.max_budget,
            currency=budget.currency,
            spent=spent,
            remaining=remaining,
            used_percent=used_percent,
            state=state,
            warning_threshold=settings.budget_warning_threshold,
            exceeded_threshold=settings.budget_exceeded_threshold,
        )

    def _determine_budget_state(self, used_percent: float) -> BudgetState:
        """Determine budget state based on usage percentage.

        Args:
            used_percent: Percentage of budget used

        Returns:
            Budget state (normal, warning, or exceeded)
        """
        if used_percent >= settings.budget_exceeded_threshold:
            return BudgetState.EXCEEDED
        elif used_percent >= settings.budget_warning_threshold:
            return BudgetState.WARNING
        else:
            return BudgetState.NORMAL
