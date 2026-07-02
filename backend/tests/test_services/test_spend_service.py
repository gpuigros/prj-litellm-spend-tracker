"""Test spend service."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key_validator import hash_token
from app.models.litellm import LiteLLMSpendLog, LiteLLMVirtualKeys
from app.models.spend import Period
from app.services.spend_service import SpendService

_TEST_KEY = "sk-test-key-12345"
_HASHED_KEY = hash_token(_TEST_KEY)


@pytest.mark.asyncio
async def test_spend_service_get_summary(db_session: AsyncSession) -> None:
    """Test spend service get_summary method."""
    await _seed_key(db_session)
    service = SpendService(db_session)
    result = await service.get_summary("test-user-1", _TEST_KEY, Period.MONTH)

    assert result.user_id == "test-user-1"
    assert result.period == Period.MONTH
    assert result.currency == "EUR"
    assert result.spend >= 0
    assert result.budget > 0
    assert result.remaining == result.budget - result.spend


@pytest.mark.asyncio
async def test_spend_service_get_by_model(db_session: AsyncSession) -> None:
    """Test spend service get_by_model method."""
    await _seed_key(db_session)
    service = SpendService(db_session)
    result = await service.get_by_model("test-user-1", _TEST_KEY, Period.MONTH)

    assert result.period == Period.MONTH
    assert result.currency == "EUR"
    assert isinstance(result.models, list)


@pytest.mark.asyncio
async def test_spend_service_get_by_project(db_session: AsyncSession) -> None:
    """Test spend service get_by_project method."""
    await _seed_key(db_session)
    service = SpendService(db_session)
    result = await service.get_by_project("test-user-1", _TEST_KEY, Period.MONTH)

    assert result.period == Period.MONTH
    assert result.currency == "EUR"
    assert isinstance(result.projects, list)


@pytest.mark.asyncio
async def test_spend_service_get_daily(db_session: AsyncSession) -> None:
    """Test spend service get_daily method."""
    await _seed_key(db_session)
    service = SpendService(db_session)
    result = await service.get_daily("test-user-1", _TEST_KEY, Period.MONTH)

    assert result.period == Period.MONTH
    assert result.currency == "EUR"
    assert isinstance(result.days, list)


async def _seed_key(db_session: AsyncSession) -> None:
    """Insert a verification token with a flat max_budget so the service
    can resolve a budget without a budget_limits window.
    """
    from datetime import datetime

    db_session.add(
        LiteLLMVirtualKeys(
            token=_HASHED_KEY,
            key_alias="test-key",
            spend=0.0,
            max_budget=100.0,
            user_id="test-user-1",
            created_at=datetime.utcnow(),
        )
    )
    await db_session.commit()
