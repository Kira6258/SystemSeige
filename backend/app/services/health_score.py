def compute_financial_health_score(monthly_income: float, total_debt: float, savings: float) -> int:
    """Deterministic 0-100 score from debt-to-income and savings-to-income ratios."""
    if monthly_income <= 0:
        return 0

    annual_income = monthly_income * 12
    debt_to_income = total_debt / annual_income if annual_income > 0 else 1.0
    savings_to_income = savings / annual_income if annual_income > 0 else 0.0

    # Debt component: 0 debt -> 50 pts, debt >= 3x annual income -> 0 pts
    debt_score = max(0.0, 50.0 * (1 - min(debt_to_income / 3.0, 1.0)))

    # Savings component: savings >= 1x annual income -> 50 pts
    savings_score = min(50.0, 50.0 * min(savings_to_income / 1.0, 1.0))

    return max(0, min(100, round(debt_score + savings_score)))
