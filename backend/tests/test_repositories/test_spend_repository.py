"""Test spend repository."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key_validator import hash_token
from app.models.litellm import LiteLLMSpendLog
from app.repositories.spend_repository import SpendRepository

# Static test key — its SHA-256 hash is inserted into the spend logs'
# api_key column so the repository can find the rows.
_TEST_KEY = "sk-test-key-12345"
_HASHED_KEY = hash_token(_TEST_KEY)


@pytest.mark.asyncio
async def test_spend_repository_get_total_spend(db_session: AsyncSession) -> None:
    """Test spend repository get_total_spend method."""
    await _seed_log(db_session, spend=0.5)
    repo = SpendRepository(db_session)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    result = await repo.get_total_spend(_TEST_KEY, start_date, end_date)

    assert isinstance(result, float)
    assert result >= 0


@pytest.mark.asyncio
async def test_spend_repository_get_spend_by_model(db_session: AsyncSession) -> None:
    """Test spend repository get_spend_by_model method."""
    await _seed_log(db_session, spend=0.5, model="gpt-4")
    repo = SpendRepository(db_session)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    result = await repo.get_spend_by_model(_TEST_KEY, start_date, end_date)

    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_spend_repository_get_spend_by_model_skips_empty_model_names(
    db_session: AsyncSession,
) -> None:
    """Rows with NULL or empty model names are excluded.

    Defensive test against legacy LiteLLM rows that may have a blank
    model field. They must not appear in the breakdown, otherwise the
    UI shows a phantom entry with just a colon.

    The bad rows are inserted via raw SQL to bypass the ORM's
    `nullable=False` constraint, simulating legacy data that bypassed
    the model definition.
    """
    now = datetime.utcnow()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S.%f")

    # Insert rows bypassing the ORM (legacy / malformed data).
    await db_session.execute(
        text(
            """
            INSERT INTO "LiteLLM_SpendLogs"
                (request_id, api_key, "user", model, spend,
                 total_tokens, prompt_tokens, completion_tokens,
                 "startTime", "endTime")
            VALUES
                (:rid_empty, :key, :user, :model_empty, :spend_empty,
                 :tt_empty, :pt_empty, :ct_empty, :ts, :ts),
                (:rid_null, :key, :user, :model_null, :spend_null,
                 :tt_null, :pt_null, :ct_null, :ts, :ts),
                (:rid_good, :key, :user, :model_good, :spend_good,
                 :tt_good, :pt_good, :ct_good, :ts, :ts)
            """
        ),
        {
            "rid_empty": "req-bad-empty",
            "rid_null": "req-bad-null",
            "rid_good": "req-good",
            "key": _HASHED_KEY,
            "user": "test-user-1",
            "model_empty": "",
            "model_null": None,
            "model_good": "gpt-4",
            "spend_empty": 1.23,
            "spend_null": 2.34,
            "spend_good": 0.5,
            "tt_empty": 10,
            "tt_null": 20,
            "tt_good": 100,
            "pt_empty": 5,
            "pt_null": 10,
            "pt_good": 50,
            "ct_empty": 5,
            "ct_null": 10,
            "ct_good": 50,
            "ts": now_str,
        },
    )
    await db_session.commit()

    repo = SpendRepository(db_session)
    result = await repo.get_spend_by_model(
        _TEST_KEY, now - timedelta(days=1), now + timedelta(days=1)
    )

    model_names = [item.model for item in result]
    assert "" not in model_names
    assert None not in model_names
    assert "gpt-4" in model_names


@pytest.mark.asyncio
async def test_spend_repository_get_spend_by_project(db_session: AsyncSession) -> None:
    """Test spend repository get_spend_by_project method."""
    await _seed_log(db_session, spend=0.5)
    repo = SpendRepository(db_session)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    result = await repo.get_spend_by_project(_TEST_KEY, start_date, end_date)

    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_spend_repository_get_daily_spend(db_session: AsyncSession) -> None:
    """Test spend repository get_daily_spend method."""
    await _seed_log(db_session, spend=0.5)
    repo = SpendRepository(db_session)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    result = await repo.get_daily_spend(_TEST_KEY, start_date, end_date)

    assert isinstance(result, list)


async def _seed_log(
    db_session: AsyncSession,
    *,
    spend: float = 0.1,
    model: str = "gpt-4",
) -> None:
    """Insert a single spend log row attributed to the test key hash."""
    now = datetime.utcnow()
    db_session.add(
        LiteLLMSpendLog(
            request_id=f"req-{now.timestamp()}",
            api_key=_HASHED_KEY,
            user="test-user-1",
            model=model,
            spend=spend,
            total_tokens=100,
            prompt_tokens=80,
            completion_tokens=20,
            startTime=now,
            endTime=now,
        )
    )
    await db_session.commit()
