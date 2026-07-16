import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.rate_limit import GENERAL_LIMIT, limiter
from app.db.session import get_db
from app.models.models import FinancialProfile, User
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.services.health_score import compute_financial_health_score

logger = logging.getLogger("clearfinance")
router = APIRouter(prefix="/api/profile", tags=["profile"])


async def _get_owned_profile(db: AsyncSession, user_id) -> FinancialProfile:
    # Ownership scoped: always filtered by user_id, never fetched by profile id alone.
    result = await db.execute(select(FinancialProfile).where(FinancialProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return profile


@router.get("", response_model=ProfileResponse)
@limiter.limit(GENERAL_LIMIT)
async def get_profile(request: Request, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    profile = await _get_owned_profile(db, user.id)
    return ProfileResponse(
        monthly_income=float(profile.monthly_income),
        total_debt=float(profile.total_debt),
        savings=float(profile.savings),
        financial_health_score=profile.financial_health_score,
    )


@router.put("", response_model=ProfileResponse)
@limiter.limit(GENERAL_LIMIT)
async def update_profile(
    request: Request,
    body: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_owned_profile(db, user.id)
    try:
        profile.monthly_income = body.monthly_income
        profile.total_debt = body.total_debt
        profile.savings = body.savings
        profile.financial_health_score = compute_financial_health_score(
            body.monthly_income, body.total_debt, body.savings
        )
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("[ERROR] profile update failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    return ProfileResponse(
        monthly_income=float(profile.monthly_income),
        total_debt=float(profile.total_debt),
        savings=float(profile.savings),
        financial_health_score=profile.financial_health_score,
    )
