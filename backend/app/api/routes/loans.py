import logging

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.rate_limit import AI_LIMIT, GENERAL_LIMIT, limiter
from app.db.session import get_db
from app.models.models import ComplianceFlag, FeeFlag, LoanAnalysis, User
from app.schemas.loan import (
    ComplianceFlagResponse,
    ComputationEnvelope,
    FeeFlagResponse,
    LoanAnalysisListItem,
    LoanAnalysisResponse,
)
from app.services.document_pipeline import extract_document_text, validate_upload
from app.services.llm import extract_loan_terms, generate_explanation
from app.services.translate import detect_language, translate_to_english
from app.engines.loan_engine import verify_emi, estimate_apr, loan_burden_ratio
from app.engines.compliance_engine import detect_predatory_patterns, run_compliance_checks
from app.engines.fairness_engine import calculate_fee_penalty, compute_fairness_score

logger = logging.getLogger("clearfinance")
router = APIRouter(prefix="/api/loans", tags=["loans"])

TYPICAL_FEE_RANGES_PCT = {
    "processing_fee": (0.5, 2.5),
    "prepayment_penalty": (0.0, 2.0),
    "foreclosure_charge": (0.0, 4.0),
    "late_payment_fee": (0.0, 3.0),
}

def _envelope_from_analysis(analysis: LoanAnalysis) -> LoanAnalysisResponse:
    return LoanAnalysisResponse(
        id=str(analysis.id),
        fairness_score=float(analysis.fairness_score),
        confidence=float(analysis.confidence_score),
        computation=ComputationEnvelope(
            verified_emi=float(analysis.verified_emi),
            stated_emi=float(analysis.loan.principal) if getattr(analysis, 'stated_emi', None) is not None else None, # quick fix
            emi_deviation_pct=float(analysis.emi_deviation_pct),
            fee_flags=[
                FeeFlagResponse(
                    fee_type=f.fee_type,
                    found_pct=f.found_pct,
                    typical_range_pct=list(TYPICAL_FEE_RANGES_PCT.get(f.fee_type, (0, 0))),
                    severity=f.severity,
                )
                for f in analysis.fee_flags
            ],
            compliance_flags=[
                ComplianceFlagResponse(rule_violated=c.rule_violated, severity=c.severity)
                for c in analysis.compliance_flags
            ],
        ),
        explanation=analysis.explanation or "",
        reproducible=True,
        created_at=analysis.created_at.isoformat(),
    )


@router.post("/analyze", response_model=LoanAnalysisResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(AI_LIMIT)
async def analyze_loan(
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    validate_upload(file.filename or "", content)

    try:
        raw_text = extract_document_text(content)
        detected_lang = detect_language(raw_text, fallback=user.preferred_language)
        english_text = translate_to_english(raw_text, detected_lang)

        extraction = extract_loan_terms(english_text)

        loan_data = {
            "principal": extraction.principal,
            "annual_interest_rate_pct": extraction.annual_interest_rate_pct,
            "tenure_months": extraction.tenure_months,
            "stated_emi": extraction.stated_emi,
            "fees": [{"type": f.type, "amount_pct": f.amount} for f in extraction.fees],
            "penal_interest_rate": 0,
            "foreclosure_notice_days": 30,
            "apr": 0,
            "cooling_off_days": 3,
        }

        verified_emi = verify_emi(extraction.principal, extraction.annual_interest_rate_pct, extraction.tenure_months)
        upfront_fees = sum([f.amount/100 * extraction.principal if f.is_percentage else f.amount for f in extraction.fees])
        apr = estimate_apr(extraction.principal, verified_emi, extraction.tenure_months, upfront_fees)
        loan_data["apr"] = apr

        emi_deviation_pct = abs(extraction.stated_emi - verified_emi) / verified_emi * 100 if extraction.stated_emi else 0.0

        predatory_signals = detect_predatory_patterns(loan_data)
        compliance_penalty, compliance_flags = run_compliance_checks(loan_data)
        total_fee_penalty, fee_flags = calculate_fee_penalty(loan_data["fees"], TYPICAL_FEE_RANGES_PCT)
        fairness_score = compute_fairness_score(emi_deviation_pct, total_fee_penalty, compliance_penalty, len(predatory_signals))

        result = {
            "verified_emi": verified_emi,
            "emi_deviation_pct": emi_deviation_pct,
            "fairness_score": fairness_score,
            "fee_flags": fee_flags,
            "compliance_flags": compliance_flags,
            "apr": apr,
            "predatory_signals": predatory_signals
        }

        # Need to generate explanation using old pipeline logic for now
        # Stub result object required by old generate_explanation signature
        legacy_result_stub = {
            "verified_emi": verified_emi,
            "emi_deviation_pct": emi_deviation_pct,
            "fairness_score": fairness_score,
            "fee_flags": [{"fee_type": f["fee_type"], "found_pct": f["found_pct"], "severity": f["severity"], "typical_range_pct": (0,0)} for f in fee_flags],
            "compliance_flags": compliance_flags
        }
        explanation = generate_explanation(legacy_result_stub, detected_lang)
    except HTTPException:
        raise
    except Exception:
        logger.exception("[ERROR] loan analysis pipeline failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    try:
        from app.models.models import Loan
        loan = Loan(
            user_id=user.id,
            lender_name="Unknown Lender",
            principal=extraction.principal,
            annual_interest_rate=extraction.annual_interest_rate_pct,
            tenure_months=extraction.tenure_months
        )
        db.add(loan)
        await db.flush()

        analysis = LoanAnalysis(
            loan_id=loan.id,
            verified_emi=verified_emi,
            emi_deviation_pct=emi_deviation_pct,
            apr=apr,
            loan_burden_ratio=0.0,
            fairness_score=fairness_score,
            confidence_score=extraction.extraction_confidence,
            risk_level="high" if len(predatory_signals) >= 2 else "medium",
            predatory_signals=predatory_signals,
            explanation=explanation,
        )
        db.add(analysis)
        await db.flush()

        for flag in fee_flags:
            db.add(
                FeeFlag(
                    loan_analysis_id=analysis.id,
                    fee_type=flag["fee_type"],
                    found_pct=flag["found_pct"],
                    severity=flag["severity"],
                )
            )
        for flag in compliance_flags:
            db.add(
                ComplianceFlag(
                    loan_analysis_id=analysis.id,
                    rule_violated=flag["rule_violated"],
                    severity=flag["severity"],
                )
            )
        await db.commit()
        await db.refresh(analysis, attribute_names=["fee_flags", "compliance_flags"])
    except Exception:
        await db.rollback()
        logger.exception("[ERROR] persisting loan analysis failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    return _envelope_from_analysis(analysis)


@router.get("", response_model=list[LoanAnalysisListItem])
@limiter.limit(GENERAL_LIMIT)
async def list_loans(request: Request, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LoanAnalysis).join(LoanAnalysis.loan).where(LoanAnalysis.loan.has(user_id=user.id)).order_by(LoanAnalysis.created_at.desc())
    )
    analyses = result.scalars().all()
    return [
        LoanAnalysisListItem(
            id=str(a.id),
            principal=float(a.loan.principal),
            fairness_score=a.fairness_score,
            created_at=a.created_at.isoformat(),
        )
        for a in analyses
    ]


@router.get("/{loan_id}", response_model=LoanAnalysisResponse)
@limiter.limit(GENERAL_LIMIT)
async def get_loan(
    request: Request,
    loan_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    forbidden = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        result = await db.execute(
            select(LoanAnalysis).join(LoanAnalysis.loan).where(LoanAnalysis.id == loan_id, LoanAnalysis.loan.has(user_id=user.id))
        )
        analysis = result.scalar_one_or_none()
    except Exception:
        raise forbidden
    if not analysis:
        raise forbidden

    await db.refresh(analysis, attribute_names=["fee_flags", "compliance_flags"])
    return _envelope_from_analysis(analysis)
