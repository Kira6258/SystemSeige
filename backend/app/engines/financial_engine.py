# Phase 9: Financial Health Engine Formulas
# Deterministic math for financial wellness

FIN_HEALTH_WEIGHTS = {
    "savings": 0.20,
    "debt": 0.20,
    "emergency_fund": 0.15,
    "investment_readiness": 0.15,
    "insurance": 0.10,
    "tax_efficiency": 0.10,
    "credit_utilization": 0.10
}

def clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    return max(min_val, min(value, max_val))

def compute_health(
    monthly_income: float,
    monthly_expenses: float,
    liquid_savings: float,
    total_monthly_debt_payments: float,
    existing_life_cover: float,
    years_to_retirement: int,
    deductions_claimed: float,
    max_eligible_deductions: float,
    total_credit_used: float,
    total_credit_limit: float
) -> dict:
    
    # Savings Score
    savings_rate = ((monthly_income - monthly_expenses) / monthly_income * 100) if monthly_income > 0 else 0
    savings_score = clamp((savings_rate / 20) * 100)

    # Debt Score
    dti = (total_monthly_debt_payments / monthly_income * 100) if monthly_income > 0 else 0
    debt_score = clamp(100 - dti * 2)

    # Emergency Fund Score
    emergency_fund_score = clamp((liquid_savings / (monthly_expenses * 6)) * 100) if monthly_expenses > 0 else 0

    # Investment Readiness
    investment_readiness = clamp(emergency_fund_score * 0.4 + debt_score * 0.3 + savings_score * 0.3)

    # Insurance Score
    annual_income = monthly_income * 12
    human_life_value = annual_income * years_to_retirement * 0.7
    insurance_score = clamp((existing_life_cover / human_life_value) * 100) if human_life_value > 0 else 0

    # Tax Efficiency
    tax_efficiency = clamp((deductions_claimed / max_eligible_deductions) * 100) if max_eligible_deductions > 0 else 0

    # Credit Utilization
    credit_utilization = (total_credit_used / total_credit_limit * 100) if total_credit_limit > 0 else 0
    credit_utilization_score = clamp(100 - credit_utilization)

    # Future Risk Score
    future_risk_score = clamp(100 - (dti * 0.4 + (100 - emergency_fund_score) * 0.3 + (100 - insurance_score) * 0.3))

    # Overall Wellness
    overall_wellness = round(
        savings_score * FIN_HEALTH_WEIGHTS["savings"] +
        debt_score * FIN_HEALTH_WEIGHTS["debt"] +
        emergency_fund_score * FIN_HEALTH_WEIGHTS["emergency_fund"] +
        investment_readiness * FIN_HEALTH_WEIGHTS["investment_readiness"] +
        insurance_score * FIN_HEALTH_WEIGHTS["insurance"] +
        tax_efficiency * FIN_HEALTH_WEIGHTS["tax_efficiency"] +
        credit_utilization_score * FIN_HEALTH_WEIGHTS["credit_utilization"],
        1
    )

    return {
        "overall_wellness_score": overall_wellness,
        "sub_scores": {
            "savings_score": round(savings_score, 1),
            "debt_score": round(debt_score, 1),
            "emergency_fund_score": round(emergency_fund_score, 1),
            "investment_readiness": round(investment_readiness, 1),
            "insurance_score": round(insurance_score, 1),
            "tax_efficiency": round(tax_efficiency, 1),
            "credit_utilization_score": round(credit_utilization_score, 1),
            "future_risk_score": round(future_risk_score, 1)
        }
    }
