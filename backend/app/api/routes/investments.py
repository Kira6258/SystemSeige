import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.deps import get_current_user
from app.core.rate_limit import GENERAL_LIMIT, limiter
from app.db.session import get_db
from app.models.models import Investment, User
from app.schemas.investments import InvestmentCreateRequest, InvestmentUpdateRequest, InvestmentResponse

logger = logging.getLogger("clearfinance")
router = APIRouter(prefix="/api/investments", tags=["investments"])

@router.post("", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(GENERAL_LIMIT)
async def create_investment(request: Request, body: InvestmentCreateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    amount = body.quantity * body.avg_buy_price
    # Simple default for avg_return_pct based on current value vs cost
    avg_return = 0.0
    if amount > 0 and body.current_value > 0:
        avg_return = ((body.current_value - amount) / amount) * 100

    investment = Investment(
        user_id=user.id,
        asset_type=body.asset_type,
        ticker_symbol=body.ticker_symbol,
        quantity=body.quantity,
        avg_buy_price=body.avg_buy_price,
        amount=amount,
        current_value=body.current_value,
        avg_return_pct=avg_return
    )
    db.add(investment)
    try:
        await db.commit()
        await db.refresh(investment)
    except Exception:
        await db.rollback()
        logger.exception("[ERROR] investment creation failed")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    return InvestmentResponse(
        id=str(investment.id), asset_type=investment.asset_type, ticker_symbol=investment.ticker_symbol,
        quantity=float(investment.quantity), avg_buy_price=float(investment.avg_buy_price),
        amount=float(investment.amount), current_value=float(investment.current_value),
        avg_return_pct=float(investment.avg_return_pct), risk_profile=investment.risk_profile
    )

@router.get("", response_model=List[InvestmentResponse])
@limiter.limit(GENERAL_LIMIT)
async def list_investments(request: Request, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Investment).where(Investment.user_id == user.id))
    investments = result.scalars().all()
    return [
        InvestmentResponse(
            id=str(i.id), asset_type=i.asset_type, ticker_symbol=i.ticker_symbol,
            quantity=float(i.quantity), avg_buy_price=float(i.avg_buy_price),
            amount=float(i.amount), current_value=float(i.current_value),
            avg_return_pct=float(i.avg_return_pct), risk_profile=i.risk_profile
        ) for i in investments
    ]

@router.delete("/{investment_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(GENERAL_LIMIT)
async def delete_investment(request: Request, investment_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Investment).where(Investment.id == investment_id, Investment.user_id == user.id))
    investment = result.scalar_one_or_none()
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
        
    try:
        await db.delete(investment)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Delete failed")
