from datetime import date
from pydantic import Field
from app.schemas.base import StrictModel

class ExpenseCreateRequest(StrictModel):
    amount: float = Field(gt=0)
    category: str = Field(pattern="^(emergency|leisure|family|food|transport|bills|health|education|other)$")
    txn_date: date
    description: str = Field(default="", max_length=255)

class ExpenseResponse(StrictModel):
    id: str
    amount: float
    category: str
    txn_date: date
    description: str

class ExpenseSummaryItem(StrictModel):
    category: str
    total_amount: float
    percentage: float
