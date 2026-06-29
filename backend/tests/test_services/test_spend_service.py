"""Test spend service."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.spend import Period
from app.services.spend_service import SpendService


@pytest.mark.asyncio
async def test_spend_service_get_summary(db_session: AsyncSession) -> None:
    """Test spend service get_summary method."""
    service = SpendService(db_session)
    result = await service.get_summary("test-user-1", Period.MONTH)

    assert result.user_id == "test-user-1"
    assert result.period == Period.MONTH
    assert result.currency == "EUR"
    assert result.spend >= 0
    assert result.budget > 0
    assert result.remaining == result.budget - result.spend


@pytest.mark.asyncio
async def test_spend_service_get_by_model(db_session: AsyncSession) -> None:
    """Test spend service get_by_model method."""
    service = SpendService(db_session)
    result = await service.get_by_model("test-user-1", Period.MONTH)

    assert result.period == Period.MONTH
    assert result.currency == "EUR"
    assert isinstance(result.models, list)


@pytest.mark.asyncio
async def test_spend_service_get_by_project(db_session: AsyncSession) -> None:
    """Test spend service get_by_project method."""
    service = SpendService(db_session)
    result = await service.get_by_project("test-user-1", Period.MONTH)

    assert result.period == Period.MONTH
    assert result.currency == "EUR"
    assert isinstance(result.projects, list)


@pytest.mark.asyncio
async def test_spend_service_get_daily(db_session: AsyncSession) -> None:
    """Test spend service get_daily method."""
    service = SpendService(db_session)
    result = await service.get_daily("test-user-1", Period.MONTH)

    assert result.period == Period.MONTH
    assert result.currency == "EUR"
    assert isinstance(result.days, list)
