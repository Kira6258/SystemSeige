from pydantic import Field

from app.schemas.base import StrictModel


class ChatRequest(StrictModel):
    message: str = Field(min_length=1, max_length=4000)


class AdvisorResponse(StrictModel):
    role: str
    advice: str
    confidence: float = Field(ge=0, le=1)


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
