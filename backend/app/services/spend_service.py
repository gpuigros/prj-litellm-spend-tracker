"""Spend service for aggregating and calculating spend data.

The ``period`` query parameter (today/week/month) selected in the
extension controls the date range for **all** spend queries — summary,
by-model, by-project, and daily. The budget window from
``budget_limits`` is used only to resolve the ``max_budget`` value for
the budget math (remaining, used percentage, state), never to override
the selected period.
"""

from datetime import datetime
from typing import List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.spend import (
    DailySpend,
    ModelSpend,
    Period,
    ProjectSpend,
    SpendByModelResponse,
    SpendByProjectResponse,
    SpendDailyResponse,
    SpendSummaryResponse,
)
from app.repositories.budget_repository import BudgetData, BudgetRepository
from app.repositories.spend_repository import SpendRepository
from app.utils.date_utils import get_period_range


class SpendService:
    """Service for spend data aggregation and calculations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.spend_repo = SpendRepository(db)
        self.budget_repo = BudgetRepository(db)

    async def _resolve_range(
        self, api_key: str, period: Period
    ) -> Tuple[BudgetData, datetime, datetime]:
        """Resolve the budget data and the date range to query.

        The date range always follows the selected ``period`` (today,
        week, month). The budget data is resolved separately so the
        summary can compute remaining/percentage against ``max_budget``.
        """
        budget = await self.budget_repo.get_key_budget(api_key)
        start_date, end_date = get_period_range(period)
        return budget, start_date, end_date

    async def get_summary(self, user_id: str, api_key: str, period: Period) -> SpendSummaryResponse:
        """Get spend summary for user and period.

        Args:
            user_id: User identifier
            api_key: User's API key for budget lookup and spend filtering
            period: Time period controlling the spend date range

        Returns:
            Spend summary with budget information
        """
        budget, start_date, end_date = await self._resolve_range(api_key, period)
        total_spend = await self.spend_repo.get_total_spend(api_key, start_date, end_date)

        remaining = budget.max_budget - total_spend
        percentage = (
            (total_spend / budget.max_budget * 100) if budget.max_budget > 0 else 0
        )

        return SpendSummaryResponse(
            user_id=user_id,
            period=period,
            currency=budget.currency,
            spend=total_spend,
            budget=budget.max_budget,
            remaining=remaining,
            budget_used_percent=percentage,
        )

    async def get_by_model(self, user_id: str, api_key: str, period: Period) -> SpendByModelResponse:
        """Get spend breakdown by model.

        Args:
            user_id: User identifier
            api_key: User's API key for budget lookup and spend filtering
            period: Time period controlling the spend date range

        Returns:
            Spend breakdown by model with percentages
        """
        budget, start_date, end_date = await self._resolve_range(api_key, period)
        model_data = await self.spend_repo.get_spend_by_model(api_key, start_date, end_date)

        total_spend = sum(item.spend for item in model_data)

        models: List[ModelSpend] = []
        for item in model_data:
            if not item.model:
                continue
            percentage = (item.spend / total_spend * 100) if total_spend > 0 else 0
            models.append(
                ModelSpend(
                    model=item.model,
                    spend=item.spend,
                    percentage=percentage,
                    requests=item.requests,
                    tokens=item.tokens,
                )
            )

        models.sort(key=lambda x: x.spend, reverse=True)

        return SpendByModelResponse(
            period=period,
            currency=budget.currency,
            models=models,
        )

    async def get_by_project(self, user_id: str, api_key: str, period: Period) -> SpendByProjectResponse:
        """Get spend breakdown by project.

        Args:
            user_id: User identifier
            api_key: User's API key for budget lookup and spend filtering
            period: Time period controlling the spend date range

        Returns:
            Spend breakdown by project with percentages
        """
        budget, start_date, end_date = await self._resolve_range(api_key, period)
        project_data = await self.spend_repo.get_spend_by_project(api_key, start_date, end_date)

        total_spend = sum(item.spend for item in project_data)

        projects: List[ProjectSpend] = []
        for item in project_data:
            percentage = (item.spend / total_spend * 100) if total_spend > 0 else 0
            projects.append(
                ProjectSpend(
                    project=item.project,
                    spend=item.spend,
                    percentage=percentage,
                    requests=item.requests,
                )
            )

        projects.sort(key=lambda x: x.spend, reverse=True)

        return SpendByProjectResponse(
            period=period,
            currency=budget.currency,
            projects=projects,
        )

    async def get_daily(self, user_id: str, api_key: str, period: Period) -> SpendDailyResponse:
        """Get daily spend trend.

        Args:
            user_id: User identifier
            api_key: User's API key for budget lookup and spend filtering
            period: Time period controlling the spend date range

        Returns:
            Daily spend data sorted by date (most recent first)
        """
        budget, start_date, end_date = await self._resolve_range(api_key, period)
        daily_data = await self.spend_repo.get_daily_spend(api_key, start_date, end_date)

        days = [
            DailySpend(
                date=item.date,
                spend=item.spend,
                requests=item.requests,
                tokens=item.tokens,
            )
            for item in daily_data
        ]

        days.sort(key=lambda x: x.date, reverse=True)

        return SpendDailyResponse(
            period=period,
            currency=budget.currency,
            days=days,
        )
