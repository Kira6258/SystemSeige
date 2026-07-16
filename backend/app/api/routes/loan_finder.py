import logging
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.rate_limit import GENERAL_LIMIT, limiter
from app.db.session import get_db
from app.models.models import FinancialProfile, User

logger = logging.getLogger("clearfinance")
router = APIRouter(prefix="/api/loans/finder", tags=["loan_finder"])

class BankOffer(BaseModel):
    bank_name: str
    interest_rate: float
    max_amount: float
    approval_chance: str

class LoanFinderRequest(BaseModel):
    requested_amount: float

class LoanFinderResponse(BaseModel):
    risk_level: str
    offers: List[BankOffer]

@router.post("", response_model=LoanFinderResponse)
@limiter.limit(GENERAL_LIMIT)
async def find_loans(
    request: Request,
    body: LoanFinderRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Fetch comprehensive profile
        res = await db.execute(select(FinancialProfile).where(FinancialProfile.user_id == user.id))
        profile = res.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Please complete your profile first.")

        income = float(profile.monthly_income)
        debt = float(profile.total_debt)
        property_value = float(profile.property_value)

        # Basic deterministic logic for bank recommendation
        dti = (debt / income) if income > 0 else 1.0
        collateral_ratio = (property_value / body.requested_amount) if body.requested_amount > 0 else 0

        # Assess risk
        if dti > 0.6 or (dti > 0.4 and collateral_ratio < 0.5):
            risk_level = "High"
            base_rate = 14.5
        elif dti > 0.3 or collateral_ratio < 1.0:
            risk_level = "Medium"
            base_rate = 10.5
        else:
            risk_level = "Low"
            base_rate = 7.5

        INDIAN_BANKS = [
            "State Bank of India (SBI)", "HDFC Bank", "ICICI Bank", "Axis Bank", "Punjab National Bank (PNB)",
            "Bank of Baroda", "Kotak Mahindra Bank", "IndusInd Bank", "Yes Bank", "Canara Bank",
            "Union Bank of India", "Bank of India", "IDFC FIRST Bank", "Federal Bank", "South Indian Bank",
            "Bandhan Bank", "RBL Bank", "City Union Bank", "Karur Vysya Bank", "UCO Bank",
            "Indian Bank", "Central Bank of India", "Bank of Maharashtra", "Punjab & Sind Bank", "IDBI Bank"
        ]

        offers = []
        for i, bank_name in enumerate(INDIAN_BANKS):
            # Add some randomness to rates based on bank type (PSU vs Private)
            # PSU banks (often at start/end of list) usually have slightly lower rates but stricter approval
            is_psu = "Bank of" in bank_name or "State" in bank_name or "National" in bank_name or "Union" in bank_name
            
            rate_modifier = (i % 5) * 0.25
            if is_psu:
                rate = max(8.5, base_rate - 0.5 + rate_modifier)
                approval = "Low" if risk_level == "High" else "Medium"
                max_amt = income * 20 + (property_value * 0.4)
            else:
                rate = max(9.5, base_rate + 0.5 + rate_modifier)
                approval = "Medium" if risk_level == "High" else "High"
                max_amt = income * 24 + (property_value * 0.6)

            offers.append(
                BankOffer(
                    bank_name=bank_name,
                    interest_rate=round(rate, 2),
                    max_amount=round(max_amt, 2),
                    approval_chance=approval
                )
            )

        # Sort by interest rate
        offers.sort(key=lambda x: x.interest_rate)

        return LoanFinderResponse(
            risk_level=risk_level,
            offers=offers
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[ERROR] Loan finder failed")
        raise HTTPException(status_code=500, detail="Internal server error")
