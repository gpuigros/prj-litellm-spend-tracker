"""Spend repository for querying LiteLLM spend data.

All queries filter by the **hashed API key** (``api_key`` column in
``LiteLLM_SpendLogs``) rather than the ``user`` column. LiteLLM writes
the key hash to ``api_key`` on every request, while the ``user`` column
may be ``default_user_id`` or NULL depending on how the key was created.
Filtering by ``api_key`` guarantees we attribute spend to the exact key
that made the request.

Model names are normalised by stripping the LiteLLM provider prefix
(e.g. ``openai/qwen3.7-max`` → ``qwen3.7-max``) so that the same
underlying model is grouped into a single entry regardless of whether
the request was routed through a provider alias.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key_validator import hash_token
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


def _hashed_key(api_key: str) -> str:
    """Return the hashed form of an API key as stored by LiteLLM."""
    return hash_token(api_key) if api_key.startswith("sk-") else api_key


def _normalize_model(model: str) -> str:
    """Strip the LiteLLM provider prefix from a model name.

    LiteLLM logs the same model as ``openai/qwen3.7-max`` (with provider
    prefix) and ``qwen3.7-max`` (without) depending on the request path.
    Normalising to the bare model name groups them into a single entry.
    """
    if not model:
        return model
    return model.split("/", 1)[1] if "/" in model else model


class SpendRepository:
    """Repository for spend data queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_total_spend(
        self, api_key: str, start_date: datetime, end_date: datetime
    ) -> float:
        """Get total spend for a key in a date range.

        Args:
            api_key: The user's API key (hashed internally).
            start_date: Period start (inclusive).
            end_date: Period end (inclusive).

        Returns:
            Total spend amount.
        """
        query = select(func.sum(LiteLLMSpendLog.spend)).where(
            LiteLLMSpendLog.api_key == _hashed_key(api_key),
            LiteLLMSpendLog.startTime >= start_date,
            LiteLLMSpendLog.startTime <= end_date,
        )

        result = await self.db.execute(query)
        total = result.scalar()
        return float(total) if total else 0.0

    async def get_spend_by_model(
        self, api_key: str, start_date: datetime, end_date: datetime
    ) -> List[ModelSpendData]:
        """Get spend breakdown by model.

        Args:
            api_key: The user's API key (hashed internally).
            start_date: Period start (inclusive).
            end_date: Period end (inclusive).

        Returns:
            List of model spend data, excluding rows with missing/empty
            model names (defensive against legacy LiteLLM rows that may
            contain NULL or empty strings).
        """
        query = (
            select(
                LiteLLMSpendLog.model,
                func.sum(LiteLLMSpendLog.spend).label("total_spend"),
                func.count(LiteLLMSpendLog.request_id).label("request_count"),
                func.sum(LiteLLMSpendLog.total_tokens).label("total_tokens"),
            )
            .where(
                LiteLLMSpendLog.api_key == _hashed_key(api_key),
                LiteLLMSpendLog.startTime >= start_date,
                LiteLLMSpendLog.startTime <= end_date,
                LiteLLMSpendLog.model.isnot(None),
                LiteLLMSpendLog.model != "",
            )
            .group_by(LiteLLMSpendLog.model)
        )

        result = await self.db.execute(query)
        rows = result.all()

        # Merge rows that normalise to the same model name (e.g.
        # "openai/qwen3.7-max" and "qwen3.7-max" → "qwen3.7-max").
        merged: dict[str, ModelSpendData] = {}
        for row in rows:
            name = _normalize_model(row.model)
            existing = merged.get(name)
            if existing is None:
                merged[name] = ModelSpendData(
                    model=name,
                    spend=float(row.total_spend or 0),
                    requests=int(row.request_count or 0),
                    tokens=int(row.total_tokens or 0),
                )
            else:
                existing.spend += float(row.total_spend or 0)
                existing.requests += int(row.request_count or 0)
                existing.tokens += int(row.total_tokens or 0)

        return list(merged.values())

    async def get_spend_by_project(
        self, api_key: str, start_date: datetime, end_date: datetime
    ) -> List[ProjectSpendData]:
        """Get spend breakdown by project.

        Note: Project attribution comes from metadata field in LiteLLM logs.
        For now, we use a simple extraction from metadata JSON.

        Args:
            api_key: The user's API key (hashed internally).
            start_date: Period start (inclusive).
            end_date: Period end (inclusive).

        Returns:
            List of project spend data.
        """
        # Project attribution comes from the metadata field in LiteLLM logs.
        # Until that is parsed, all spend is attributed to a single "global"
        # bucket so the UI shows a meaningful label instead of "unknown".
        query = (
            select(
                func.sum(LiteLLMSpendLog.spend).label("total_spend"),
                func.count(LiteLLMSpendLog.request_id).label("request_count"),
            )
            .where(
                LiteLLMSpendLog.api_key == _hashed_key(api_key),
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
                project="global",
                spend=float(row.total_spend),
                requests=int(row.request_count or 0),
            )
        ]

    async def get_daily_spend(
        self, api_key: str, start_date: datetime, end_date: datetime
    ) -> List[DailySpendData]:
        """Get daily spend breakdown.

        Args:
            api_key: The user's API key (hashed internally).
            start_date: Period start (inclusive).
            end_date: Period end (inclusive).

        Returns:
            List of daily spend data.
        """
        query = (
            select(
                func.date(LiteLLMSpendLog.startTime).label("date"),
                func.sum(LiteLLMSpendLog.spend).label("total_spend"),
                func.count(LiteLLMSpendLog.request_id).label("request_count"),
                func.sum(LiteLLMSpendLog.total_tokens).label("total_tokens"),
            )
            .where(
                LiteLLMSpendLog.api_key == _hashed_key(api_key),
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
                date=self._parse_date(row.date),
                spend=float(row.total_spend or 0),
                requests=int(row.request_count or 0),
                tokens=int(row.total_tokens or 0),
            )
            for row in rows
        ]

    @staticmethod
    def _parse_date(value) -> datetime:
        """Coerce a date result (str or date) into a datetime at midnight.

        SQLite returns ``func.date()`` as a string; PostgreSQL returns a
        ``date`` object. Both must be normalised so the service layer can
        treat them uniformly.
        """
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return datetime.combine(value, datetime.min.time())
