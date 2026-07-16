from typing import Any
from pydantic import BaseModel

class FinancialContext(BaseModel):
    user_id: str
    monthly_income: float
    total_debt: float
    savings: float
    # Other context data hydrated from the DB
    health_score: float | None = None
    sub_scores: dict | None = None

def hydrate_context(user_id: str, db_session: Any) -> FinancialContext:
    # In a real app, query the DB to fill this in
    # For now, return a stub
    return FinancialContext(
        user_id=user_id,
        monthly_income=5000.0,
        total_debt=1000.0,
        savings=10000.0,
    )

def dispatch_to_agent(agent_name: str, context: FinancialContext, query: str = "") -> dict:
    if agent_name == "debt":
        from app.engines.financial_engine import clamp
        # Call debt agent logic here
        return {"agent": "debt", "status": "ok"}
    elif agent_name == "savings":
        return {"agent": "savings", "status": "ok"}
    else:
        return {"error": "unknown agent"}
