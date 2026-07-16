from pydantic import Field
from app.schemas.base import StrictModel

class InvestmentCreateRequest(StrictModel):
    asset_type: str = Field(min_length=1, max_length=128)
    ticker_symbol: str = Field(default="", max_length=32)
    quantity: float = Field(default=0, ge=0)
    avg_buy_price: float = Field(default=0, ge=0)
    current_value: float = Field(default=0, ge=0)

class InvestmentUpdateRequest(StrictModel):
    asset_type: str | None = Field(default=None, min_length=1, max_length=128)
    ticker_symbol: str | None = Field(default=None, max_length=32)
    quantity: float | None = Field(default=None, ge=0)
    avg_buy_price: float | None = Field(default=None, ge=0)
    current_value: float | None = Field(default=None, ge=0)

class InvestmentResponse(StrictModel):
    id: str
    asset_type: str
    ticker_symbol: str
    quantity: float
    avg_buy_price: float
    amount: float  # invested amount = qty * avg_buy_price
    current_value: float
    avg_return_pct: float
    risk_profile: str
