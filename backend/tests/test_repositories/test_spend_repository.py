"""Test spend repository."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.spend_repository import SpendRepository


@pytest.mark.asyncio
async def test_spend_repository_get_total_spend(db_session: AsyncSession) -> None:
    """Test spend repository get_total_spend method."""
    repo = SpendRepository(db_session)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    result = await repo.get_total_spend("test-user-1", start_date, end_date)

    assert isinstance(result, float)
    assert result >= 0


@pytest.mark.asyncio
async def test_spend_repository_get_spend_by_model(db_session: AsyncSession) -> None:
    """Test spend repository get_spend_by_model method."""
    repo = SpendRepository(db_session)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    result = await repo.get_spend_by_model("test-user-1", start_date, end_date)

    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_spend_repository_get_spend_by_project(db_session: AsyncSession) -> None:
    """Test spend repository get_spend_by_project method."""
    repo = SpendRepository(db_session)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    result = await repo.get_spend_by_project("test-user-1", start_date, end_date)

    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_spend_repository_get_daily_spend(db_session: AsyncSession) -> None:
    """Test spend repository get_daily_spend method."""
    repo = SpendRepository(db_session)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    result = await repo.get_daily_spend("test-user-1", start_date, end_date)

    assert isinstance(result, list)
