from pydantic import Field

from app.schemas.base import StrictModel


class ProfileUpdateRequest(StrictModel):
    monthly_income: float = Field(ge=0, le=100_000_000)
    total_debt: float = Field(ge=0, le=100_000_000)
    savings: float = Field(ge=0, le=100_000_000)


class ProfileResponse(StrictModel):
    monthly_income: float
    total_debt: float
    savings: float
    financial_health_score: int
