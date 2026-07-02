"""SQLAlchemy models for LiteLLM database tables."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


class LiteLLMSpendLog(Base):
    """Model for LiteLLM spend tracking logs.

    This table is managed by LiteLLM and contains spend attribution data.
    We read from this table but do not write to it.
    """

    __tablename__ = "LiteLLM_SpendLogs"

    request_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    api_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    user: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    model: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    spend: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    call_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    request_metadata: Mapped[Optional[str]] = mapped_column("metadata", Text, nullable=True)
    cache_hit: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    cache_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    startTime: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    endTime: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class LiteLLMVirtualKeys(Base):
    """Model for LiteLLM virtual API keys.

    This table contains the virtual keys issued to users.
    We use this for authentication and user identity resolution.
    """

    __tablename__ = "LiteLLM_VerificationToken"

    token: Mapped[str] = mapped_column(String(255), primary_key=True)
    key_alias: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    spend: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    team_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    models: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    key_metadata: Mapped[Optional[str]] = mapped_column("metadata", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # Budget window columns (LiteLLM stores the real budget here, not in max_budget).
    budget_duration: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    budget_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    budget_limits: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    budget_reset_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    model_max_budget: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    soft_budget_cooldown: Mapped[Optional[bool]] = mapped_column(nullable=True)
