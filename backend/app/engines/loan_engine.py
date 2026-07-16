# Phase 6: Deterministic Loan Analysis

def estimate_apr(principal: float, emi: float, tenure_months: int, upfront_fees: float) -> float:
    """
    Newton-Raphson solve for the rate that equates disbursed amount (principal - upfront fees) to the EMI stream.
    """
    if principal <= 0 or emi <= 0 or tenure_months <= 0:
        return 0.0
        
    net_disbursed = principal - upfront_fees
    if net_disbursed <= 0:
        return 0.0

    r = 0.01  # initial guess, monthly
    for _ in range(100):
        try:
            pv = emi * (1 - (1 + r) ** -tenure_months) / r
            d_pv = emi * (
                tenure_months * (1 + r) ** (-tenure_months - 1) / r
                - (1 - (1 + r) ** -tenure_months) / r ** 2
            )
            if d_pv == 0:
                break
            r_new = r - (pv - net_disbursed) / d_pv
            if abs(r_new - r) < 1e-8:
                break
            r = r_new
        except OverflowError:
            break
            
    # clamp unreasonable rates and annualize
    r = max(0.0, min(r, 1.0))
    return round(r * 12 * 100, 2)  # annualized %

def loan_burden_ratio(new_emi: float, existing_emi_total: float, monthly_income: float) -> float:
    if monthly_income <= 0:
        return 0.0
    return round((new_emi + existing_emi_total) / monthly_income * 100, 1)

def verify_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    r = (annual_rate / 12) / 100
    if r == 0:
        return principal / tenure_months if tenure_months > 0 else 0
    return principal * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)
