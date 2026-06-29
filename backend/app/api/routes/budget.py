"""Budget API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.auth.models import User
from app.models.budget import BudgetResponse
from app.services.budget_service import BudgetService

router = APIRouter()


@router.get("/budget", response_model=BudgetResponse)
async def get_budget(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BudgetResponse:
    """Get budget information for the current user.

    Returns monthly budget, spent amount, remaining budget,
    usage percentage, and budget state (normal/warning/exceeded).
    """
    service = BudgetService(db)
    return await service.get_budget(current_user.id)
