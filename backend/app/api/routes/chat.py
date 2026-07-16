import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.rate_limit import AI_LIMIT, GENERAL_LIMIT, limiter
from app.db.session import get_db
from app.models.models import ChatHistory, FinancialProfile, User, AgentLog
from app.schemas.chat import AdvisorResponse, BoardChatResponse, ChatHistoryItem, ChatRequest
from app.agents.orchestrator import hydrate_context, dispatch_to_agent
from app.services.translate import detect_language, translate_from_english, translate_to_english

logger = logging.getLogger("clearfinance")
router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("", response_model=BoardChatResponse)
@limiter.limit(AI_LIMIT)
async def chat(
    request: Request,
    body: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        detected_lang = detect_language(body.message, fallback=user.preferred_language)
        english_message = translate_to_english(body.message, detected_lang)

        # 1. Hydrate the shared context for all agents
        prof_res = await db.execute(select(FinancialProfile).where(FinancialProfile.user_id == user.id))
        profile = prof_res.scalar_one_or_none()
        
        from app.models.models import Goal, Investment, Transaction
        goals_res = await db.execute(select(Goal).where(Goal.user_id == user.id, Goal.status == 'active'))
        inv_res = await db.execute(select(Investment).where(Investment.user_id == user.id))
        exp_res = await db.execute(select(Transaction).where(Transaction.user_id == user.id).order_by(Transaction.txn_date.desc()).limit(10))
        
        context = {
            "income": float(profile.monthly_income) if profile else 0.0,
            "expenses": float(profile.monthly_expenses) if profile else 0.0,
            "liquid_savings": float(profile.liquid_savings) if profile else 0.0,
            "total_debt": float(profile.total_debt) if profile else 0.0,
            "family_status": profile.family_status if profile else "single",
            "active_goals": [{"title": g.title, "target": float(g.target_amount), "saved": float(g.current_amount)} for g in goals_res.scalars().all()],
            "investments": [{"asset": i.asset_type, "value": float(i.current_value)} for i in inv_res.scalars().all()],
            "recent_expenses": [{"category": e.category, "amount": float(e.amount)} for e in exp_res.scalars().all()]
        }
        
        # 2. Call Groq for multi-agent advice
        from app.services.llm import run_board_chat
        llm_response = run_board_chat(english_message, context, language=detected_lang)

        advisors = []
        for adv in llm_response.get("advisors", []):
            conf = adv.get("confidence")
            if conf is None or conf == "":
                conf = 0.8
            else:
                try:
                    conf = float(conf)
                except (ValueError, TypeError):
                    conf = 0.8
                    
            advisors.append(
                AdvisorResponse(
                    role=adv.get("role", "Advisor"),
                    advice=adv.get("advice", "No advice provided."),
                    confidence=conf,
                    evidence=["Analyzed user profile context", "Applied financial heuristics"],
                    reasoning="Synthesized via Groq Multi-Agent Simulator.",
                    formula_used=None
                )
            )
        
    except HTTPException:
        raise
    except Exception:
        logger.exception("[ERROR] board chat failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    try:
        history = ChatHistory(
            user_id=user.id,
            message=body.message,
            agent_response={"advisors": [a.model_dump() for a in advisors]},
            language=detected_lang,
        )
        db.add(history)
        await db.commit()
        await db.refresh(history)
    except Exception:
        await db.rollback()
        logger.exception("[ERROR] persisting chat history failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    return BoardChatResponse(
        id=str(history.id),
        advisors=advisors,
        language=detected_lang,
        created_at=history.created_at.isoformat(),
    )

@router.get("/history", response_model=list[ChatHistoryItem])
@limiter.limit(GENERAL_LIMIT)
async def chat_history(request: Request, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatHistory).where(ChatHistory.user_id == user.id).order_by(ChatHistory.created_at.desc()).limit(100)
    )
    items = result.scalars().all()
    return [
        ChatHistoryItem(
            id=str(h.id),
            message=h.message,
            board_response=h.board_response,
            language=h.language,
            created_at=h.created_at.isoformat(),
        )
        for h in items
    ]
