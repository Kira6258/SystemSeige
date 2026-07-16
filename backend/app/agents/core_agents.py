from pydantic import BaseModel, ConfigDict
from typing import Literal, Any

class ExplainableOutput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    evidence: list[str]          
    reasoning: str                
    confidence_score: float       
    risk_level: Literal["low", "medium", "high"]
    relevant_clause: str | None   
    formula_used: str | None      
    recommendation: str
    reproducible: bool = True

def compute_confidence(schema_fields_total: int, schema_fields_populated: int, sanity_checks_passed: int, sanity_checks_total: int) -> float:
    if schema_fields_total == 0 or sanity_checks_total == 0:
        return 0.0
    completeness = schema_fields_populated / schema_fields_total
    validity = sanity_checks_passed / sanity_checks_total
    return round(0.5 * completeness + 0.5 * validity, 2)
