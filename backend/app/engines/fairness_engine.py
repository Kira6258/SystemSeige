# Phase 6: Fairness Engine

def compute_fairness_score(emi_deviation_pct: float, total_fee_penalty: float, compliance_penalty: float, predatory_signals_count: int) -> float:
    score = 100
    score -= min(40, emi_deviation_pct * 2)
    score -= total_fee_penalty
    score -= compliance_penalty
    
    if predatory_signals_count >= 2:
        score -= 10
    else:
        score -= (predatory_signals_count * 3)
        
    return max(0.0, min(100.0, round(score, 1)))

def calculate_fee_penalty(fees: list, typical_ranges: dict) -> tuple[float, list]:
    total_penalty = 0.0
    flags = []
    
    for fee in fees:
        fee_type = fee.get("type")
        amount_pct = fee.get("amount_pct", 0.0)
        
        if fee_type in typical_ranges:
            typical_min, typical_max = typical_ranges[fee_type]
            if amount_pct > typical_max:
                excess = amount_pct - typical_max
                severity_penalty = min(15, excess * 5)
                total_penalty += severity_penalty
                
                severity = "high" if severity_penalty > 10 else "medium" if severity_penalty > 5 else "low"
                
                flags.append({
                    "fee_type": fee_type,
                    "found_pct": amount_pct,
                    "severity": severity
                })
                
    return total_penalty, flags
