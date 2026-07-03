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
from datetime import date, datetime
from typing import List, Optional

import structlog
from sqlalchemy import String, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key_validator import hash_token
from app.models.litellm import LiteLLMSpendLog, LiteLLMVirtualKeys

logger = structlog.get_logger()


@dataclass
class ModelSpendData:
    """Raw model spend data from database."""

    model: str
    spend: float
    requests: int
    tokens: int
    prompt_tokens: int
    completion_tokens: int


@dataclass
class ProjectSpendData:
    """Raw project spend data from database."""

    project: str
    spend: float
    requests: int
    tokens: int
    prompt_tokens: int
    completion_tokens: int


@dataclass
class DailySpendData:
    """Raw daily spend data from database."""

    date: datetime
    spend: float
    requests: int
    tokens: int


@dataclass
class ManagementModelDailyData:
    """Raw (api_key, day, model) spend row for management reports."""

    api_key: str
    key_alias: Optional[str]
    date: date
    model: str
    spend: float
    requests: int
    tokens: int
    prompt_tokens: int
    completion_tokens: int


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
                func.sum(LiteLLMSpendLog.prompt_tokens).label("prompt_tokens"),
                func.sum(LiteLLMSpendLog.completion_tokens).label("completion_tokens"),
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
                    prompt_tokens=int(row.prompt_tokens or 0),
                    completion_tokens=int(row.completion_tokens or 0),
                )
            else:
                existing.spend += float(row.total_spend or 0)
                existing.requests += int(row.request_count or 0)
                existing.tokens += int(row.total_tokens or 0)
                existing.prompt_tokens += int(row.prompt_tokens or 0)
                existing.completion_tokens += int(row.completion_tokens or 0)

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
                func.sum(LiteLLMSpendLog.total_tokens).label("total_tokens"),
                func.sum(LiteLLMSpendLog.prompt_tokens).label("prompt_tokens"),
                func.sum(LiteLLMSpendLog.completion_tokens).label("completion_tokens"),
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
                tokens=int(row.total_tokens or 0),
                prompt_tokens=int(row.prompt_tokens or 0),
                completion_tokens=int(row.completion_tokens or 0),
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

    async def get_management_spend_by_key_day_model(
        self, start_date: datetime, end_date: datetime
    ) -> List[ManagementModelDailyData]:
        """Get spend for ALL api keys grouped by key, day and model.

        Unlike the user-scoped queries, this does NOT filter by a single
        api key — it aggregates across every key in ``LiteLLM_SpendLogs``
        within the given date range. Intended for the management endpoint
        authenticated with the LiteLLM master key.

        Model normalisation (stripping the LiteLLM provider prefix, e.g.
        ``openai/qwen3.7-max`` → ``qwen3.7-max``) is pushed into the SQL
        query so Postgres merges equivalent models into a single group
        before returning rows. This keeps the result set small and avoids
        a second merge pass in Python.

        The query is unordered: the API response is an aggregate list
        with no required ordering, so we avoid the cost of sorting the
        full grouped result set.

        Args:
            start_date: Period start (inclusive).
            end_date: Period end (inclusive).

        Returns:
            List of (api_key, day, model) spend rows with normalised
            model names.
        """
        # Strip the provider prefix in SQL: if the model contains a '/',
        # take the part after the first '/'; otherwise keep it as-is.
        # COALESCE guards against NULL models (filtered out below, but
        # defensive against expression evaluation order).
        slash_pos = func.position(func.cast("/", String).op("IN")(LiteLLMSpendLog.model))
        normalized_model = func.coalesce(
            func.nullif(
                func.substr(LiteLLMSpendLog.model, slash_pos + 1),
                "",
            ),
            LiteLLMSpendLog.model,
        ).label("model")

        # LEFT JOIN keeps spend rows whose hashed api_key no longer
        # exists in LiteLLM_VerificationToken (e.g. deleted key, or a
        # log written by a non-virtual flow). For those rows, key_alias
        # resolves to NULL and the response surfaces the raw api_key.
        query = (
            select(
                LiteLLMSpendLog.api_key,
                LiteLLMVirtualKeys.key_alias.label("key_alias"),
                func.date(LiteLLMSpendLog.startTime).label("date"),
                normalized_model,
                func.sum(LiteLLMSpendLog.spend).label("total_spend"),
                func.count(LiteLLMSpendLog.request_id).label("request_count"),
                func.sum(LiteLLMSpendLog.total_tokens).label("total_tokens"),
                func.sum(LiteLLMSpendLog.prompt_tokens).label("prompt_tokens"),
                func.sum(LiteLLMSpendLog.completion_tokens).label("completion_tokens"),
            )
            .select_from(LiteLLMSpendLog)
            .outerjoin(
                LiteLLMVirtualKeys,
                LiteLLMVirtualKeys.token == LiteLLMSpendLog.api_key,
            )
            .where(
                LiteLLMSpendLog.startTime >= start_date,
                LiteLLMSpendLog.startTime <= end_date,
                LiteLLMSpendLog.model.isnot(None),
                LiteLLMSpendLog.model != "",
            )
            .group_by(
                LiteLLMSpendLog.api_key,
                LiteLLMVirtualKeys.key_alias,
                func.date(LiteLLMSpendLog.startTime),
                normalized_model,
            )
        )

        import time

        t0 = time.perf_counter()
        result = await self.db.execute(query)
        t1 = time.perf_counter()
        rows = result.all()
        t2 = time.perf_counter()
        logger.info(
            "management spend db query",
            execute_ms=round((t1 - t0) * 1000, 2),
            fetch_ms=round((t2 - t1) * 1000, 2),
            rows=len(rows),
        )

        return [
            ManagementModelDailyData(
                api_key=row.api_key,
                key_alias=row.key_alias,
                date=self._parse_date(row.date).date(),
                model=row.model,
                spend=float(row.total_spend or 0),
                requests=int(row.request_count or 0),
                tokens=int(row.total_tokens or 0),
                prompt_tokens=int(row.prompt_tokens or 0),
                completion_tokens=int(row.completion_tokens or 0),
            )
            for row in rows
        ]
