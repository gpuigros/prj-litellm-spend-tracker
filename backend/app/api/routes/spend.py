"""Spend API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.auth.models import User
from app.models.spend import (
    Period,
    SpendByModelResponse,
    SpendByProjectResponse,
    SpendDailyResponse,
    SpendSummaryResponse,
)
from app.services.spend_service import SpendService

router = APIRouter()


@router.get("/summary", response_model=SpendSummaryResponse)
async def get_spend_summary(
    period: Period = Query(default=Period.MONTH, description="Time period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SpendSummaryResponse:
    """Get spend summary for the current user.

    Returns total spend, budget, remaining budget, and usage percentage
    for the specified period (today, week, or month).
    """
    service = SpendService(db)
    return await service.get_summary(current_user.id, current_user.api_key, period)


@router.get("/by-model", response_model=SpendByModelResponse)
async def get_spend_by_model(
    period: Period = Query(default=Period.MONTH, description="Time period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SpendByModelResponse:
    """Get spend breakdown by model for the current user.

    Returns spend, percentage, request count, and token count
    for each model used during the specified period.
    """
    service = SpendService(db)
    return await service.get_by_model(current_user.id, current_user.api_key, period)


@router.get("/by-project", response_model=SpendByProjectResponse)
async def get_spend_by_project(
    period: Period = Query(default=Period.MONTH, description="Time period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SpendByProjectResponse:
    """Get spend breakdown by project/repository for the current user.

    Returns spend, percentage, and request count for each project
    during the specified period.
    """
    service = SpendService(db)
    return await service.get_by_project(current_user.id, current_user.api_key, period)


@router.get("/daily", response_model=SpendDailyResponse)
async def get_spend_daily(
    period: Period = Query(default=Period.MONTH, description="Time period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SpendDailyResponse:
    """Get daily spend trend for the current user.

    Returns spend, request count, and token count for each day
    during the specified period.
    """
    service = SpendService(db)
    return await service.get_daily(current_user.id, current_user.api_key, period)
