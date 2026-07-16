from pydantic import Field
from typing import Literal

from app.schemas.base import StrictModel

class ChatRequest(StrictModel):
    message: str = Field(min_length=1, max_length=4000)

class AdvisorResponse(StrictModel):
    role: str
    advice: str
    evidence: list[str] = []
    reasoning: str = ""
    confidence: float = Field(ge=0, le=1)
    risk_level: Literal["low", "medium", "high"] = "low"
    formula_used: str | None = None
    reproducible: bool = True

class BoardChatResponse(StrictModel):
    id: str
    advisors: list[AdvisorResponse]
    language: str
    created_at: str

class ChatHistoryItem(StrictModel):
    id: str
    message: str
    board_response: dict
    language: str
    created_at: str
