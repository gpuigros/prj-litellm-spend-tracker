"""Pydantic models for spend data."""

from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class Period(str, Enum):
    """Time period for spend queries."""

    TODAY = "today"
    WEEK = "week"
    MONTH = "month"


class SpendSummaryResponse(BaseModel):
    """Response model for spend summary."""

    user_id: str = Field(..., description="User identifier")
    period: Period = Field(..., description="Time period")
    currency: str = Field(..., description="Currency code (e.g., EUR, USD)")
    spend: float = Field(..., ge=0, description="Total spend amount")
    budget: float = Field(..., ge=0, description="Budget limit")
    remaining: float = Field(..., description="Remaining budget")
    budget_used_percent: float = Field(..., ge=0, description="Percentage of budget used")


class ModelSpend(BaseModel):
    """Spend breakdown for a single model."""

    model: str = Field(..., description="Model name")
    spend: float = Field(..., ge=0, description="Spend amount")
    percentage: float = Field(..., ge=0, le=100, description="Percentage of total spend")
    requests: int = Field(..., ge=0, description="Number of requests")
    tokens: int = Field(..., ge=0, description="Total tokens used")


class SpendByModelResponse(BaseModel):
    """Response model for spend by model."""

    period: Period = Field(..., description="Time period")
    currency: str = Field(..., description="Currency code")
    models: List[ModelSpend] = Field(..., description="Spend by model")


class ProjectSpend(BaseModel):
    """Spend breakdown for a single project."""

    project: str = Field(..., description="Project/repository name")
    spend: float = Field(..., ge=0, description="Spend amount")
    percentage: float = Field(..., ge=0, le=100, description="Percentage of total spend")
    requests: int = Field(..., ge=0, description="Number of requests")


class SpendByProjectResponse(BaseModel):
    """Response model for spend by project."""

    period: Period = Field(..., description="Time period")
    currency: str = Field(..., description="Currency code")
    projects: List[ProjectSpend] = Field(..., description="Spend by project")


class DailySpend(BaseModel):
    """Spend data for a single day."""

    date: datetime = Field(..., description="Date")
    spend: float = Field(..., ge=0, description="Spend amount")
    requests: int = Field(..., ge=0, description="Number of requests")
    tokens: int = Field(..., ge=0, description="Total tokens used")


class SpendDailyResponse(BaseModel):
    """Response model for daily spend."""

    period: Period = Field(..., description="Time period")
    currency: str = Field(..., description="Currency code")
    days: List[DailySpend] = Field(..., description="Daily spend data")
