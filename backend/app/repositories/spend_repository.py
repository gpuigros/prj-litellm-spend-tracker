"""Spend repository for querying LiteLLM spend data."""

from dataclasses import dataclass
from datetime import datetime
from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.litellm import LiteLLMSpendLog


@dataclass
class ModelSpendData:
    """Raw model spend data from database."""

    model: str
    spend: float
    requests: int
    tokens: int


@dataclass
class ProjectSpendData:
    """Raw project spend data from database."""

    project: str
    spend: float
    requests: int


@dataclass
class DailySpendData:
    """Raw daily spend data from database."""

    date: datetime
    spend: float
    requests: int
    tokens: int


class SpendRepository:
    """Repository for spend data queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_total_spend(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> float:
        """Get total spend for user in date range.

        Args:
            user_id: User identifier
            start_date: Period start
            end_date: Period end

        Returns:
            Total spend amount
        """
        query = select(func.sum(LiteLLMSpendLog.spend)).where(
            LiteLLMSpendLog.user == user_id,
            LiteLLMSpendLog.startTime >= start_date,
            LiteLLMSpendLog.startTime <= end_date,
        )

        result = await self.db.execute(query)
        total = result.scalar()
        return float(total) if total else 0.0

    async def get_spend_by_model(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[ModelSpendData]:
        """Get spend breakdown by model.

        Args:
            user_id: User identifier
            start_date: Period start
            end_date: Period end

        Returns:
            List of model spend data
        """
        query = (
            select(
                LiteLLMSpendLog.model,
                func.sum(LiteLLMSpendLog.spend).label("total_spend"),
                func.count(LiteLLMSpendLog.request_id).label("request_count"),
                func.sum(LiteLLMSpendLog.total_tokens).label("total_tokens"),
            )
            .where(
                LiteLLMSpendLog.user == user_id,
                LiteLLMSpendLog.startTime >= start_date,
                LiteLLMSpendLog.startTime <= end_date,
            )
            .group_by(LiteLLMSpendLog.model)
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            ModelSpendData(
                model=row.model,
                spend=float(row.total_spend or 0),
                requests=int(row.request_count or 0),
                tokens=int(row.total_tokens or 0),
            )
            for row in rows
        ]

    async def get_spend_by_project(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[ProjectSpendData]:
        """Get spend breakdown by project.

        Note: Project attribution comes from metadata field in LiteLLM logs.
        For now, we use a simple extraction from metadata JSON.

        Args:
            user_id: User identifier
            start_date: Period start
            end_date: Period end

        Returns:
            List of project spend data
        """
        # For simplicity, we'll group by a placeholder "unknown" project
        # In production, you'd parse the metadata JSON field
        query = (
            select(
                func.sum(LiteLLMSpendLog.spend).label("total_spend"),
                func.count(LiteLLMSpendLog.request_id).label("request_count"),
            )
            .where(
                LiteLLMSpendLog.user == user_id,
                LiteLLMSpendLog.startTime >= start_date,
                LiteLLMSpendLog.startTime <= end_date,
            )
        )

        result = await self.db.execute(query)
        row = result.one_or_none()

        if not row or not row.total_spend:
            return []

        return [
            ProjectSpendData(
                project="unknown",
                spend=float(row.total_spend),
                requests=int(row.request_count or 0),
            )
        ]

    async def get_daily_spend(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[DailySpendData]:
        """Get daily spend breakdown.

        Args:
            user_id: User identifier
            start_date: Period start
            end_date: Period end

        Returns:
            List of daily spend data
        """
        query = (
            select(
                func.date(LiteLLMSpendLog.startTime).label("date"),
                func.sum(LiteLLMSpendLog.spend).label("total_spend"),
                func.count(LiteLLMSpendLog.request_id).label("request_count"),
                func.sum(LiteLLMSpendLog.total_tokens).label("total_tokens"),
            )
            .where(
                LiteLLMSpendLog.user == user_id,
                LiteLLMSpendLog.startTime >= start_date,
                LiteLLMSpendLog.startTime <= end_date,
            )
            .group_by(func.date(LiteLLMSpendLog.startTime))
            .order_by(func.date(LiteLLMSpendLog.startTime))
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            DailySpendData(
                date=datetime.combine(row.date, datetime.min.time()),
                spend=float(row.total_spend or 0),
                requests=int(row.request_count or 0),
                tokens=int(row.total_tokens or 0),
            )
            for row in rows
        ]
