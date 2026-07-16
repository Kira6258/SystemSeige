from pydantic import Field

from app.schemas.base import StrictModel


class FeeExtraction(StrictModel):
    type: str
    amount: float
    is_percentage: bool


class LoanExtraction(StrictModel):
    """Schema the LLM's structured output is validated against. Extraction only — never a score."""

    principal: float = Field(gt=0)
    annual_interest_rate_pct: float = Field(ge=0, le=100)
    tenure_months: int = Field(gt=0, le=600)
    stated_emi: float | None = None
    fees: list[FeeExtraction] = Field(default_factory=list)
    extraction_confidence: float = Field(ge=0, le=1)


class FeeFlagResponse(StrictModel):
    fee_type: str
    found_pct: float
    typical_range_pct: list[float]
    severity: str


class ComplianceFlagResponse(StrictModel):
    rule_violated: str
    severity: str


class ComputationEnvelope(StrictModel):
    verified_emi: float
    stated_emi: float | None
    emi_deviation_pct: float
    fee_flags: list[FeeFlagResponse]
    compliance_flags: list[ComplianceFlagResponse]


class LoanAnalysisResponse(StrictModel):
    id: str
    fairness_score: float
    confidence: float
    computation: ComputationEnvelope
    explanation: str
    reproducible: bool = True
    created_at: str


class LoanAnalysisListItem(StrictModel):
    id: str
    principal: float
    fairness_score: float
    created_at: str
