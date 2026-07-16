from datetime import date
from pydantic import Field
from app.schemas.base import StrictModel

class GoalCreateRequest(StrictModel):
    title: str = Field(min_length=1, max_length=255)
    goal_type: str = Field(min_length=1, max_length=128)
    description: str = Field(default="")
    target_amount: float = Field(gt=0)
    target_date: date
    priority: int = Field(default=3, ge=1, le=5)

class GoalUpdateRequest(StrictModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None)
    target_amount: float | None = Field(default=None, gt=0)
    current_amount: float | None = Field(default=None, ge=0)
    target_date: date | None = Field(default=None)
    status: str | None = Field(default=None, pattern="^(active|completed|paused)$")
    priority: int | None = Field(default=None, ge=1, le=5)

class GoalResponse(StrictModel):
    id: str
    title: str
    goal_type: str
    description: str
    target_amount: float
    current_amount: float
    target_date: date
    status: str
    priority: int
    llm_advice: str | None
    created_at: str

class GoalListResponse(StrictModel):
    id: str
    title: str
    goal_type: str
    target_amount: float
    current_amount: float
    target_date: date
    status: str
    priority: int
    created_at: str
