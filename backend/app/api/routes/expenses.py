import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date, timedelta

from app.core.deps import get_current_user
from app.core.rate_limit import GENERAL_LIMIT, limiter
from app.db.session import get_db
from app.models.models import Transaction, User
from app.schemas.expenses import ExpenseCreateRequest, ExpenseResponse, ExpenseSummaryItem

logger = logging.getLogger("clearfinance")
router = APIRouter(prefix="/api/expenses", tags=["expenses"])

@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(GENERAL_LIMIT)
async def create_expense(request: Request, body: ExpenseCreateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    expense = Transaction(
        user_id=user.id,
        amount=body.amount,
        category=body.category,
        txn_date=body.txn_date,
        description=body.description
    )
    db.add(expense)
    try:
        await db.commit()
        await db.refresh(expense)
    except Exception:
        await db.rollback()
        logger.exception("[ERROR] expense creation failed")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    return ExpenseResponse(
        id=str(expense.id), amount=float(expense.amount), category=expense.category,
        txn_date=expense.txn_date, description=expense.description
    )

@router.get("", response_model=List[ExpenseResponse])
@limiter.limit(GENERAL_LIMIT)
async def list_expenses(request: Request, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transaction).where(Transaction.user_id == user.id).order_by(Transaction.txn_date.desc()).limit(100))
    expenses = result.scalars().all()
    return [
        ExpenseResponse(
            id=str(e.id), amount=float(e.amount), category=e.category,
            txn_date=e.txn_date, description=e.description
        ) for e in expenses
    ]

@router.get("/summary", response_model=List[ExpenseSummaryItem])
@limiter.limit(GENERAL_LIMIT)
async def expenses_summary(request: Request, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Get current month start
    today = date.today()
    month_start = date(today.year, today.month, 1)
    
    # Get total for percentage calculation
    total_res = await db.execute(
        select(func.sum(Transaction.amount))
        .where(Transaction.user_id == user.id, Transaction.txn_date >= month_start)
    )
    total = float(total_res.scalar() or 0)
    
    if total == 0:
        return []
        
    # Get grouped by category
    cat_res = await db.execute(
        select(Transaction.category, func.sum(Transaction.amount))
        .where(Transaction.user_id == user.id, Transaction.txn_date >= month_start)
        .group_by(Transaction.category)
    )
    
    summary = []
    for cat, amount in cat_res:
        amt = float(amount or 0)
        summary.append(ExpenseSummaryItem(
            category=cat,
            total_amount=amt,
            percentage=round((amt / total) * 100, 1)
        ))
        
    # Sort by amount descending
    summary.sort(key=lambda x: x.total_amount, reverse=True)
    return summary

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(GENERAL_LIMIT)
async def delete_expense(request: Request, expense_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transaction).where(Transaction.id == expense_id, Transaction.user_id == user.id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
        
    try:
        await db.delete(expense)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Delete failed")
