from pydantic import BaseModel, ConfigDict, Field

class ProfileResponse(BaseModel):
    monthly_income: float
    monthly_expenses: float
    liquid_savings: float
    total_debt: float
    family_status: str
    past_loans: str
    property_value: float
    financial_health_score: int

class ProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    monthly_income: float = Field(ge=0)
    monthly_expenses: float = Field(ge=0)
    liquid_savings: float = Field(ge=0)
    total_debt: float = Field(ge=0)
    family_status: str = Field(default="single")
    past_loans: str = Field(default="")
    property_value: float = Field(ge=0, default=0)
