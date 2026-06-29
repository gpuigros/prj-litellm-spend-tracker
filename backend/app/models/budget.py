"""Pydantic models for budget data."""

from enum import Enum

from pydantic import BaseModel, Field


class BudgetState(str, Enum):
    """Budget state based on usage percentage."""

    NORMAL = "normal"
    WARNING = "warning"
    EXCEEDED = "exceeded"


class BudgetResponse(BaseModel):
    """Response model for budget information."""

    user_id: str = Field(..., description="User identifier")
    monthly_budget: float = Field(..., ge=0, description="Monthly budget limit")
    currency: str = Field(..., description="Currency code (e.g., EUR, USD)")
    spent: float = Field(..., ge=0, description="Amount spent this month")
    remaining: float = Field(..., description="Remaining budget")
    used_percent: float = Field(..., ge=0, description="Percentage of budget used")
    state: BudgetState = Field(..., description="Budget state")
    warning_threshold: float = Field(..., ge=0, le=100, description="Warning threshold percentage")
    exceeded_threshold: float = Field(
        ..., ge=0, le=100, description="Exceeded threshold percentage"
    )
