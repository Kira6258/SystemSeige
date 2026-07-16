"""Deterministic Fairness Score engine. Pure math — no LLM involvement — so the
same document always produces the same score, verified by the reproducibility
acceptance test in the build spec."""

from app.schemas.loan import LoanExtraction

TYPICAL_FEE_RANGES_PCT: dict[str, tuple[float, float]] = {
    "processing_fee": (0.5, 2.5),
    "prepayment_penalty": (0.0, 2.0),
    "foreclosure_charge": (0.0, 4.0),
    "late_payment_fee": (0.0, 3.0),
}

# Compliance rule: penal/late interest more than 2x the base annual rate is a red flag.
PENAL_RATE_MULTIPLIER_THRESHOLD = 2.0


def verify_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    r = (annual_rate / 12) / 100
    if r == 0:
        return principal / tenure_months
    return principal * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)


def compute_emi_deviation(stated_emi: float | None, verified_emi: float) -> float:
    if not stated_emi or verified_emi == 0:
        return 0.0
    return abs(stated_emi - verified_emi) / verified_emi * 100


def score_fees(fees: list, principal: float) -> tuple[float, list[dict]]:
    penalty = 0.0
    flags: list[dict] = []
    for fee in fees:
        fee_type = fee.type if hasattr(fee, "type") else fee["type"]
        amount = fee.amount if hasattr(fee, "amount") else fee["amount"]
        is_percentage = fee.is_percentage if hasattr(fee, "is_percentage") else fee["is_percentage"]

        amount_pct = amount if is_percentage else (amount / principal * 100 if principal else 0)
        typical = TYPICAL_FEE_RANGES_PCT.get(fee_type)
        if typical and not (typical[0] <= amount_pct <= typical[1]):
            excess = amount_pct - typical[1]
            severity_penalty = min(15, excess * 5)
            penalty += severity_penalty
            flags.append(
                {
                    "fee_type": fee_type,
                    "found_pct": round(amount_pct, 2),
                    "typical_range_pct": [typical[0], typical[1]],
                    "severity": "high" if excess > 1 else "medium",
                }
            )
    return penalty, flags


def check_compliance(extraction: LoanExtraction) -> tuple[float, list[dict]]:
    """Rule-engine compliance checks — deterministic, not LLM judgment."""
    penalty = 0.0
    flags: list[dict] = []

    for fee in extraction.fees:
        if fee.type in ("late_payment_fee", "penal_interest"):
            rate_pct = fee.amount if fee.is_percentage else (fee.amount / extraction.principal * 100)
            if rate_pct > extraction.annual_interest_rate_pct * PENAL_RATE_MULTIPLIER_THRESHOLD:
                penalty += 10
                flags.append({"rule_violated": "penal_rate_exceeds_2x_base_rate", "severity": "high"})

    return penalty, flags


def compute_fairness_score(emi_deviation_pct: float, fee_penalty: float, compliance_penalty: float) -> float:
    score = 100 - min(40, emi_deviation_pct * 2) - fee_penalty - compliance_penalty
    return max(0.0, min(100.0, round(score, 1)))


def run_fairness_engine(extraction: LoanExtraction) -> dict:
    verified_emi = verify_emi(extraction.principal, extraction.annual_interest_rate_pct, extraction.tenure_months)
    emi_deviation_pct = compute_emi_deviation(extraction.stated_emi, verified_emi)
    fee_penalty, fee_flags = score_fees(extraction.fees, extraction.principal)
    compliance_penalty, compliance_flags = check_compliance(extraction)
    fairness_score = compute_fairness_score(emi_deviation_pct, fee_penalty, compliance_penalty)

    return {
        "verified_emi": round(verified_emi, 2),
        "stated_emi": extraction.stated_emi,
        "emi_deviation_pct": round(emi_deviation_pct, 2),
        "fee_flags": fee_flags,
        "compliance_flags": compliance_flags,
        "fairness_score": fairness_score,
    }
