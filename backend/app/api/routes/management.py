"""Management API routes.

These endpoints are authenticated with the LiteLLM master key
(``LITELLM_MASTER_KEY``), not a regular virtual API key. They expose
aggregate spend data across all API keys for administrative purposes.
"""

from datetime import datetime, timedelta

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_master_key
from app.config import settings
from app.database.connection import get_db
from app.models.spend import ManagementSpendResponse
from app.services.spend_service import SpendService

logger = structlog.get_logger()

router = APIRouter()


def _default_range() -> tuple[datetime, datetime]:
    """Return the start and end datetimes for the current month.

    Mirrors the ``Period.MONTH`` semantics from
    ``app.utils.date_utils.get_period_range`` but is kept local to avoid
    coupling the management endpoint to the user-facing ``Period`` enum.
    """
    now = datetime.utcnow()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        next_month = now.replace(year=now.year + 1, month=1, day=1)
    else:
        next_month = now.replace(month=now.month + 1, day=1)
    end = (next_month - timedelta(days=1)).replace(
        hour=23, minute=59, second=59, microsecond=999999
    )
    return start, end


@router.get(
    "/spend",
    response_model=ManagementSpendResponse,
    dependencies=[Depends(require_master_key)],
)
async def get_management_spend(
    start_date: datetime = Query(
        default=None,
        description="Period start (inclusive). Defaults to the first day of the current month.",
    ),
    end_date: datetime = Query(
        default=None,
        description="Period end (inclusive). Defaults to the last day of the current month.",
    ),
    db: AsyncSession = Depends(get_db),
) -> ManagementSpendResponse:
    """Get spend for all API keys broken down by day and by model.

    Requires the LiteLLM master key (``LITELLM_MASTER_KEY``). A regular
    virtual API key will be rejected with 403 Forbidden.

    Each entry in the response is one (api_key, day, model) tuple, so
    the caller can pivot the data by key, by day, or by model.
    """
    default_start, default_end = _default_range()
    start = start_date or default_start
    end = end_date or default_end

    import time

    t0 = time.perf_counter()
    service = SpendService(db)
    response = await service.get_management_spend(
        start_date=start,
        end_date=end,
        currency=settings.default_currency,
    )
    logger.info(
        "management spend endpoint done",
        entries=len(response.entries),
        elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
    )
    return response
