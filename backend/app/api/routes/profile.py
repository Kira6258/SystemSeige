import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.rate_limit import GENERAL_LIMIT, limiter
from app.db.session import get_db
from app.models.models import FinancialProfile, User
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.engines.financial_engine import compute_health

logger = logging.getLogger("clearfinance")
router = APIRouter(prefix="/api/profile", tags=["profile"])

async def _get_owned_profile(db: AsyncSession, user_id) -> FinancialProfile:
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
        monthly_expenses=float(profile.monthly_expenses),
        liquid_savings=float(profile.liquid_savings),
        total_debt=float(profile.total_debt),
        family_status=profile.family_status,
        past_loans=profile.past_loans,
        property_value=float(profile.property_value),
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
        profile.monthly_expenses = body.monthly_expenses
        profile.liquid_savings = body.liquid_savings
        profile.total_debt = body.total_debt
        profile.family_status = body.family_status
        profile.past_loans = body.past_loans
        profile.property_value = body.property_value
        
        # Calculate new health score using the deterministic engine
        # We pass 0 for fields we don't have yet (insurance, taxes, credit) to prevent crashes
        health_data = compute_health(
            monthly_income=body.monthly_income,
            monthly_expenses=body.monthly_expenses,
            liquid_savings=body.liquid_savings,
            total_monthly_debt_payments=body.total_debt * 0.05, # rough estimate
            existing_life_cover=0.0,
            years_to_retirement=30,
            deductions_claimed=0.0,
            max_eligible_deductions=0.0,
            total_credit_used=body.total_debt,
            total_credit_limit=body.total_debt * 2
        )
        profile.financial_health_score = int(health_data["overall_wellness_score"])
        
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("[ERROR] profile update failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    return ProfileResponse(
        monthly_income=float(profile.monthly_income),
        monthly_expenses=float(profile.monthly_expenses),
        liquid_savings=float(profile.liquid_savings),
        total_debt=float(profile.total_debt),
        family_status=profile.family_status,
        past_loans=profile.past_loans,
        property_value=float(profile.property_value),
        financial_health_score=profile.financial_health_score,
    )
