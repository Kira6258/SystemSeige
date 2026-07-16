# Phase 6: Compliance and Predatory Pattern Detection

PREDATORY_SIGNALS = [
    ("apr_over_36pct", lambda d: d.get("apr", 0) > 36.0),
    ("prepayment_penalty_present", lambda d: any(f.get("type") == "prepayment_penalty" and f.get("amount_pct", 0) > 0 for f in d.get("fees", []))),
    ("balloon_payment", lambda d: d.get("final_payment_multiple", 1) > 1.5),
    ("mandatory_insurance_bundling", lambda d: d.get("bundled_insurance", False) and not d.get("insurance_optional_disclosed", False)),
    ("compounding_penal_interest", lambda d: d.get("penal_interest_compounds", False)),
    ("loan_burden_over_55pct", lambda d: d.get("loan_burden_ratio", 0) > 55.0),
]

def detect_predatory_patterns(loan_data: dict) -> list[str]:
    return [name for name, check in PREDATORY_SIGNALS if check(loan_data)]

COMPLIANCE_RULES = [
    {"id": "penal_interest_cap", "check": lambda d: d.get("penal_interest_rate", 0) <= d.get("annual_interest_rate_pct", 0) * 2,
     "violation": "Penal interest exceeds 2x the base rate", "severity": "high", "penalty": 15},
    {"id": "min_notice_period", "check": lambda d: d.get("foreclosure_notice_days", 30) >= 15,
     "violation": "Foreclosure notice period below 15 days", "severity": "medium", "penalty": 8},
    {"id": "apr_disclosure_present", "check": lambda d: d.get("apr") is not None,
     "violation": "APR not disclosed in agreement", "severity": "high", "penalty": 15},
    {"id": "cooling_off_period", "check": lambda d: d.get("cooling_off_days", 0) >= 3,
     "violation": "No cooling-off / free-look period stated", "severity": "low", "penalty": 5},
]

def run_compliance_checks(loan_data: dict) -> tuple[float, list]:
    penalty = 0.0
    flags = []
    for rule in COMPLIANCE_RULES:
        if not rule["check"](loan_data):
            penalty += rule["penalty"]
            flags.append({"rule_violated": rule["violation"], "severity": rule["severity"]})
    return penalty, flags
