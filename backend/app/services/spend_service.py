"""Spend service for aggregating and calculating spend data."""

from typing import List

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
from app.repositories.budget_repository import BudgetRepository
from app.repositories.spend_repository import SpendRepository
from app.utils.date_utils import get_period_range


class SpendService:
    """Service for spend data aggregation and calculations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.spend_repo = SpendRepository(db)
        self.budget_repo = BudgetRepository(db)

    async def get_summary(self, user_id: str, period: Period) -> SpendSummaryResponse:
        """Get spend summary for user and period.

        Args:
            user_id: User identifier
            period: Time period

        Returns:
            Spend summary with budget information
        """
        start_date, end_date = get_period_range(period)

        # Get total spend
        total_spend = await self.spend_repo.get_total_spend(user_id, start_date, end_date)

        # Get budget
        budget = await self.budget_repo.get_user_budget(user_id)

        # Calculate remaining and percentage
        remaining = budget.monthly_budget - total_spend
        percentage = (
            (total_spend / budget.monthly_budget * 100) if budget.monthly_budget > 0 else 0
        )

        return SpendSummaryResponse(
            user_id=user_id,
            period=period,
            currency=budget.currency,
            spend=total_spend,
            budget=budget.monthly_budget,
            remaining=remaining,
            budget_used_percent=percentage,
        )

    async def get_by_model(self, user_id: str, period: Period) -> SpendByModelResponse:
        """Get spend breakdown by model.

        Args:
            user_id: User identifier
            period: Time period

        Returns:
            Spend breakdown by model with percentages
        """
        start_date, end_date = get_period_range(period)

        # Get spend by model from repository
        model_data = await self.spend_repo.get_spend_by_model(user_id, start_date, end_date)

        # Calculate total for percentages
        total_spend = sum(item.spend for item in model_data)

        # Build response with percentages
        models: List[ModelSpend] = []
        for item in model_data:
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

        # Sort by spend descending
        models.sort(key=lambda x: x.spend, reverse=True)

        budget = await self.budget_repo.get_user_budget(user_id)

        return SpendByModelResponse(
            period=period,
            currency=budget.currency,
            models=models,
        )

    async def get_by_project(self, user_id: str, period: Period) -> SpendByProjectResponse:
        """Get spend breakdown by project.

        Args:
            user_id: User identifier
            period: Time period

        Returns:
            Spend breakdown by project with percentages
        """
        start_date, end_date = get_period_range(period)

        # Get spend by project from repository
        project_data = await self.spend_repo.get_spend_by_project(user_id, start_date, end_date)

        # Calculate total for percentages
        total_spend = sum(item.spend for item in project_data)

        # Build response with percentages
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

        # Sort by spend descending
        projects.sort(key=lambda x: x.spend, reverse=True)

        budget = await self.budget_repo.get_user_budget(user_id)

        return SpendByProjectResponse(
            period=period,
            currency=budget.currency,
            projects=projects,
        )

    async def get_daily(self, user_id: str, period: Period) -> SpendDailyResponse:
        """Get daily spend trend.

        Args:
            user_id: User identifier
            period: Time period

        Returns:
            Daily spend data sorted by date (most recent first)
        """
        start_date, end_date = get_period_range(period)

        # Get daily spend from repository
        daily_data = await self.spend_repo.get_daily_spend(user_id, start_date, end_date)

        # Build response
        days = [
            DailySpend(
                date=item.date,
                spend=item.spend,
                requests=item.requests,
                tokens=item.tokens,
            )
            for item in daily_data
        ]

        # Sort by date descending (most recent first)
        days.sort(key=lambda x: x.date, reverse=True)

        budget = await self.budget_repo.get_user_budget(user_id)

        return SpendDailyResponse(
            period=period,
            currency=budget.currency,
            days=days,
        )
