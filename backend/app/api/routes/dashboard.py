import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.rate_limit import GENERAL_LIMIT, limiter
from app.db.session import get_db
from app.models.models import FinancialProfile, User, Recommendation
from pydantic import BaseModel
from typing import List
from app.engines.financial_engine import compute_health

logger = logging.getLogger("clearfinance")
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

class DashboardResponse(BaseModel):
    overall_score: int
    sub_scores: dict
    recent_recommendations: List[dict]

@router.get("", response_model=DashboardResponse)
@limiter.limit(GENERAL_LIMIT)
async def get_dashboard(request: Request, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        profile_res = await db.execute(select(FinancialProfile).where(FinancialProfile.user_id == user.id))
        profile = profile_res.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
            
        health_data = compute_health(
            monthly_income=float(profile.monthly_income),
            monthly_expenses=float(profile.monthly_expenses),
            liquid_savings=float(profile.liquid_savings),
            total_monthly_debt_payments=float(profile.total_debt) * 0.05, 
            existing_life_cover=0.0,
            years_to_retirement=30,
            deductions_claimed=0.0,
            max_eligible_deductions=0.0,
            total_credit_used=float(profile.total_debt),
            total_credit_limit=float(profile.total_debt) * 2
        )
        
        rec_res = await db.execute(select(Recommendation).where(Recommendation.user_id == user.id).order_by(Recommendation.priority.desc()).limit(3))
        recommendations = [{"domain": r.domain, "text": r.recommendation, "priority": r.priority} for r in rec_res.scalars().all()]
        
        return DashboardResponse(
            overall_score=int(health_data["overall_wellness_score"]),
            sub_scores=health_data["sub_scores"],
            recent_recommendations=recommendations
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("[ERROR] dashboard failed")
        raise HTTPException(status_code=500, detail="Internal server error")
