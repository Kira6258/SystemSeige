import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.deps import get_current_user
from app.core.rate_limit import GENERAL_LIMIT, limiter
from app.db.session import get_db
from app.models.models import Goal, User, FinancialProfile, Investment, Transaction, Loan
from app.schemas.goals import GoalCreateRequest, GoalUpdateRequest, GoalResponse, GoalListResponse
from app.services.llm import generate_goal_advice

logger = logging.getLogger("clearfinance")
router = APIRouter(prefix="/api/goals", tags=["goals"])

from fastapi import APIRouter, Depends, HTTPException, status, Request

@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(GENERAL_LIMIT)
async def create_goal(request: Request, body: GoalCreateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    goal = Goal(
        user_id=user.id,
        title=body.title,
        goal_type=body.goal_type,
        description=body.description,
        target_amount=body.target_amount,
        target_date=body.target_date,
        priority=body.priority
    )
    db.add(goal)
    try:
        await db.commit()
        await db.refresh(goal)
    except Exception:
        await db.rollback()
        logger.exception("[ERROR] goal creation failed")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    return GoalResponse(
        id=str(goal.id), title=goal.title, goal_type=goal.goal_type, description=goal.description,
        target_amount=float(goal.target_amount), current_amount=float(goal.current_amount),
        target_date=goal.target_date, status=goal.status, priority=goal.priority,
        llm_advice=goal.llm_advice, created_at=goal.created_at.isoformat()
    )

@router.get("", response_model=List[GoalListResponse])
@limiter.limit(GENERAL_LIMIT)
async def list_goals(request: Request, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Goal).where(Goal.user_id == user.id).order_by(Goal.priority.asc(), Goal.target_date.asc()))
    goals = result.scalars().all()
    return [
        GoalListResponse(
            id=str(g.id), title=g.title, goal_type=g.goal_type, target_amount=float(g.target_amount),
            current_amount=float(g.current_amount), target_date=g.target_date, status=g.status,
            priority=g.priority, created_at=g.created_at.isoformat()
        ) for g in goals
    ]

@router.get("/{goal_id}", response_model=GoalResponse)
@limiter.limit(GENERAL_LIMIT)
async def get_goal(request: Request, goal_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == user.id))
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    # Generate advice if not present
    if not goal.llm_advice:
        try:
            # Fetch context
            prof = await db.execute(select(FinancialProfile).where(FinancialProfile.user_id == user.id))
            profile = prof.scalar_one_or_none()
            
            # Use generate_goal_advice logic (which we will add to llm.py next)
            advice = generate_goal_advice(goal, profile, language=user.preferred_language)
            goal.llm_advice = advice
            await db.commit()
            await db.refresh(goal)
        except Exception:
            await db.rollback()
            logger.exception("[ERROR] LLM goal advice failed")
            # Don't fail the request, just return without advice
            
    return GoalResponse(
        id=str(goal.id), title=goal.title, goal_type=goal.goal_type, description=goal.description,
        target_amount=float(goal.target_amount), current_amount=float(goal.current_amount),
        target_date=goal.target_date, status=goal.status, priority=goal.priority,
        llm_advice=goal.llm_advice, created_at=goal.created_at.isoformat()
    )

@router.put("/{goal_id}", response_model=GoalResponse)
@limiter.limit(GENERAL_LIMIT)
async def update_goal(request: Request, goal_id: str, body: GoalUpdateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == user.id))
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    if body.title is not None: goal.title = body.title
    if body.description is not None: goal.description = body.description
    if body.target_amount is not None: goal.target_amount = body.target_amount
    if body.current_amount is not None: goal.current_amount = body.current_amount
    if body.target_date is not None: goal.target_date = body.target_date
    if body.status is not None: goal.status = body.status
    if body.priority is not None: goal.priority = body.priority
    
    # Recalculate advice if major fields changed
    if body.target_amount is not None or body.target_date is not None or body.current_amount is not None:
        try:
            prof = await db.execute(select(FinancialProfile).where(FinancialProfile.user_id == user.id))
            profile = prof.scalar_one_or_none()
            goal.llm_advice = generate_goal_advice(goal, profile, language=user.preferred_language)
        except Exception:
            logger.exception("Failed to update advice")

    try:
        await db.commit()
        await db.refresh(goal)
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Update failed")
        
    return GoalResponse(
        id=str(goal.id), title=goal.title, goal_type=goal.goal_type, description=goal.description,
        target_amount=float(goal.target_amount), current_amount=float(goal.current_amount),
        target_date=goal.target_date, status=goal.status, priority=goal.priority,
        llm_advice=goal.llm_advice, created_at=goal.created_at.isoformat()
    )
