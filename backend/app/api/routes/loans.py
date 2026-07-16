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
from app.services.fairness_engine import run_fairness_engine
from app.services.llm import extract_loan_terms, generate_explanation
from app.services.translate import detect_language, translate_to_english

logger = logging.getLogger("clearfinance")
router = APIRouter(prefix="/api/loans", tags=["loans"])


def _envelope_from_analysis(analysis: LoanAnalysis) -> LoanAnalysisResponse:
    return LoanAnalysisResponse(
        id=str(analysis.id),
        fairness_score=analysis.fairness_score,
        confidence=analysis.extraction_confidence,
        computation=ComputationEnvelope(
            verified_emi=float(analysis.verified_emi),
            stated_emi=float(analysis.stated_emi) if analysis.stated_emi is not None else None,
            emi_deviation_pct=analysis.emi_deviation_pct,
            fee_flags=[
                FeeFlagResponse(
                    fee_type=f.fee_type,
                    found_pct=f.found_pct,
                    typical_range_pct=[0, 0],
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
        result = run_fairness_engine(extraction)

        explanation = generate_explanation(result, detected_lang)
    except HTTPException:
        raise
    except Exception:
        logger.exception("[ERROR] loan analysis pipeline failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    try:
        analysis = LoanAnalysis(
            user_id=user.id,
            extracted_text=raw_text[:50000],
            principal=extraction.principal,
            annual_interest_rate=extraction.annual_interest_rate_pct,
            tenure_months=extraction.tenure_months,
            stated_emi=extraction.stated_emi,
            verified_emi=result["verified_emi"],
            emi_deviation_pct=result["emi_deviation_pct"],
            fairness_score=result["fairness_score"],
            extraction_confidence=extraction.extraction_confidence,
            explanation=explanation,
            language=detected_lang,
        )
        db.add(analysis)
        await db.flush()

        for flag in result["fee_flags"]:
            db.add(
                FeeFlag(
                    loan_analysis_id=analysis.id,
                    fee_type=flag["fee_type"],
                    found_pct=flag["found_pct"],
                    severity=flag["severity"],
                )
            )
        for flag in result["compliance_flags"]:
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

    response = _envelope_from_analysis(analysis)
    # Restore the true typical_range_pct per flag (not persisted, recomputed from the rule table).
    from app.services.fairness_engine import TYPICAL_FEE_RANGES_PCT

    for i, flag in enumerate(result["fee_flags"]):
        response.computation.fee_flags[i].typical_range_pct = list(flag["typical_range_pct"])

    return response


@router.get("", response_model=list[LoanAnalysisListItem])
@limiter.limit(GENERAL_LIMIT)
async def list_loans(request: Request, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LoanAnalysis).where(LoanAnalysis.user_id == user.id).order_by(LoanAnalysis.created_at.desc())
    )
    analyses = result.scalars().all()
    return [
        LoanAnalysisListItem(
            id=str(a.id),
            principal=float(a.principal),
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
        # Ownership check baked into the query itself — WHERE id=:id AND user_id=:current_user_id.
        result = await db.execute(
            select(LoanAnalysis).where(LoanAnalysis.id == loan_id, LoanAnalysis.user_id == user.id)
        )
        analysis = result.scalar_one_or_none()
    except Exception:
        # Malformed UUID or any lookup error — still 403, never a stack trace or 404.
        raise forbidden
    if not analysis:
        # 403, never 404 — don't leak whether the resource exists for another user.
        raise forbidden

    await db.refresh(analysis, attribute_names=["fee_flags", "compliance_flags"])
    return _envelope_from_analysis(analysis)
