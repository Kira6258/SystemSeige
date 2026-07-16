import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.rate_limit import AI_LIMIT, GENERAL_LIMIT, limiter
from app.db.session import get_db
from app.models.models import ChatHistory, FinancialProfile, User
from app.schemas.chat import AdvisorResponse, BoardChatResponse, ChatHistoryItem, ChatRequest
from app.services.llm import run_board_chat
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
    result = await db.execute(select(FinancialProfile).where(FinancialProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    profile_json = (
        {
            "monthly_income": float(profile.monthly_income),
            "total_debt": float(profile.total_debt),
            "savings": float(profile.savings),
            "financial_health_score": profile.financial_health_score,
        }
        if profile
        else {}
    )

    try:
        detected_lang = detect_language(body.message, fallback=user.preferred_language)
        english_message = translate_to_english(body.message, detected_lang)

        # Profile data passed as DATA, never as instructions; injection attempts in the
        # user message are treated as data by the system prompt in llm.run_board_chat.
        board_result = run_board_chat(english_message, profile_json)

        advisors = [
            AdvisorResponse(
                role=a["role"],
                advice=translate_from_english(a["advice"], detected_lang),
                confidence=a["confidence"],
            )
            for a in board_result.get("advisors", [])
        ]
    except HTTPException:
        raise
    except Exception:
        logger.exception("[ERROR] board chat failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    try:
        history = ChatHistory(
            user_id=user.id,
            message=body.message,
            board_response={"advisors": [a.model_dump() for a in advisors]},
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
