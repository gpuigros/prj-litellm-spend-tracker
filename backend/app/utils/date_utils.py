"""Date utility functions for period calculations."""

from datetime import datetime, timedelta
from typing import Tuple

from app.models.spend import Period


def get_period_range(period: Period) -> Tuple[datetime, datetime]:
    """Get start and end datetime for a given period.

    Args:
        period: Time period (today, week, month)

    Returns:
        Tuple of (start_datetime, end_datetime)
    """
    now = datetime.utcnow()

    if period == Period.TODAY:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == Period.WEEK:
        # Start of current week (Monday)
        days_since_monday = now.weekday()
        start = (now - timedelta(days=days_since_monday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:  # MONTH
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Last day of current month
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)
        end = (next_month - timedelta(days=1)).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

    return start, end
