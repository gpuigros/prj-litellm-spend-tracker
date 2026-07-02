"""Budget repository for budget data access.

Reads the real budget configuration from LiteLLM's ``budget_limits`` JSONB
column on ``LiteLLM_VerificationToken``. LiteLLM stores the budget as an
array of objects, e.g.::

    [{"reset_at": "2026-08-01T00:00:00+00:00",
      "max_budget": 44.0,
      "budget_duration": "30d"}]

The ``budget_reset_at`` column is the **next** reset (a future timestamp),
so the current budget window is ``[reset_at - duration, reset_at)``.

If ``budget_limits`` is empty/missing, the repository falls back to the
flat ``max_budget`` column, and finally to the global default configured
in ``settings.default_monthly_budget``.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.litellm import LiteLLMVirtualKeys

logger = structlog.get_logger()


@dataclass
class BudgetWindow:
    """A single budget window resolved from LiteLLM configuration.

    ``start`` is inclusive, ``end`` is exclusive — matching the semantics
    used by LiteLLM's own enforcement.
    """

    max_budget: float
    start: datetime
    end: datetime
    duration_label: str


@dataclass
class BudgetData:
    """Budget configuration data resolved for a key."""

    max_budget: float
    currency: str
    window: Optional[BudgetWindow] = None


_DURATION_RE = re.compile(r"^(\d+)\s*([dhmw])$", re.IGNORECASE)
_DURATION_UNITS = {
    "d": "days",
    "h": "hours",
    "w": "weeks",
    "m": "days",  # LiteLLM "1m" means 30 days, not a calendar month
}
_MONTH_DAYS = 30


def parse_duration_to_timedelta(label: str) -> Optional[timedelta]:
    """Parse a LiteLLM duration label (e.g. ``"30d"``, ``"1h"``) into a timedelta.

    Returns ``None`` if the label cannot be parsed.
    """
    if not label:
        return None
    match = _DURATION_RE.match(label.strip())
    if not match:
        return None
    value = int(match.group(1))
    unit = match.group(2).lower()
    if unit == "m":
        return timedelta(days=value * _MONTH_DAYS)
    return timedelta(**{_DURATION_UNITS[unit]: value})


class BudgetRepository:
    """Repository for budget data.

    Resolves the active budget window for a given API key by reading
    ``budget_limits`` (preferred) or the flat ``max_budget`` column.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_key_budget(self, api_key: str) -> BudgetData:
        """Get budget configuration for the given API key.

        Args:
            api_key: The user's API key (hashed internally to match
                LiteLLM's storage format).

        Returns:
            Budget configuration with the active window if available.
        """
        from app.auth.api_key_validator import hash_token

        hashed_key = hash_token(api_key) if api_key.startswith("sk-") else api_key

        query = select(
            LiteLLMVirtualKeys.max_budget,
            LiteLLMVirtualKeys.budget_limits,
            LiteLLMVirtualKeys.budget_reset_at,
            LiteLLMVirtualKeys.budget_duration,
        ).where(LiteLLMVirtualKeys.token == hashed_key)
        result = await self.db.execute(query)
        row = result.one_or_none()

        if row is None:
            logger.info("Using default budget (key not found)", key_prefix=api_key[:10])
            return self._default_budget()

        window = self._resolve_window(
            budget_limits=row.budget_limits,
            budget_reset_at=row.budget_reset_at,
            budget_duration=row.budget_duration,
        )

        if window is not None and window.max_budget > 0:
            logger.info(
                "Using budget_limits window",
                max_budget=window.max_budget,
                duration=window.duration_label,
                start=window.start,
                end=window.end,
            )
            return BudgetData(
                max_budget=window.max_budget,
                currency=settings.default_currency,
                window=window,
            )

        if row.max_budget is not None and row.max_budget > 0:
            logger.info("Using flat max_budget", max_budget=row.max_budget)
            return BudgetData(
                max_budget=row.max_budget,
                currency=settings.default_currency,
            )

        logger.info("Using default budget (no key-specific budget configured)")
        return self._default_budget()

    def _resolve_window(
        self,
        budget_limits: Optional[list],
        budget_reset_at: Optional[datetime],
        budget_duration: Optional[str],
    ) -> Optional[BudgetWindow]:
        """Resolve the active budget window from the key's configuration.

        Priority:
        1. ``budget_limits`` JSONB array (LiteLLM's canonical store).
        2. Flat ``budget_reset_at`` + ``budget_duration`` columns.
        """
        if budget_limits:
            for entry in budget_limits:
                if not isinstance(entry, dict):
                    continue
                window = self._window_from_entry(entry)
                if window is not None:
                    return window

        if budget_reset_at is not None and budget_duration:
            delta = parse_duration_to_timedelta(budget_duration)
            if delta is not None:
                return BudgetWindow(
                    max_budget=0.0,  # unknown without budget_limits; caller falls back
                    start=budget_reset_at - delta,
                    end=budget_reset_at,
                    duration_label=budget_duration,
                )

        return None

    def _window_from_entry(self, entry: dict) -> Optional[BudgetWindow]:
        """Build a BudgetWindow from a single budget_limits entry."""
        max_budget = entry.get("max_budget")
        reset_at = entry.get("reset_at")
        duration = entry.get("budget_duration")

        if max_budget is None or reset_at is None or not duration:
            return None

        delta = parse_duration_to_timedelta(duration)
        if delta is None:
            return None

        end_dt = self._to_datetime(reset_at)
        if end_dt is None:
            return None

        return BudgetWindow(
            max_budget=float(max_budget),
            start=end_dt - delta,
            end=end_dt,
            duration_label=duration,
        )

    @staticmethod
    def _to_datetime(value) -> Optional[datetime]:
        """Coerce a reset_at value (str or datetime) into a naive UTC datetime."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
            if parsed.tzinfo is not None:
                parsed = parsed.astimezone(tz=None).replace(tzinfo=None)
            return parsed
        return None

    def _default_budget(self) -> BudgetData:
        return BudgetData(
            max_budget=settings.default_monthly_budget,
            currency=settings.default_currency,
        )
