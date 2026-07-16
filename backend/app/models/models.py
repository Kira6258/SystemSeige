import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Numeric, String, Text, JSON, Integer, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = _uuid_pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    profile: Mapped["FinancialProfile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    loan_analyses: Mapped[list["LoanAnalysis"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    chat_history: Mapped[list["ChatHistory"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    monthly_income: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_debt: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    savings: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    financial_health_score: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship(back_populates="profile")


class LoanAnalysis(Base):
    __tablename__ = "loan_analyses"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    document_s3_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=True)

    principal: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    annual_interest_rate: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)
    tenure_months: Mapped[int] = mapped_column(Integer, nullable=False)
    stated_emi: Mapped[float] = mapped_column(Numeric(14, 2), nullable=True)
    verified_emi: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    emi_deviation_pct: Mapped[float] = mapped_column(Float, default=0.0)
    fairness_score: Mapped[float] = mapped_column(Float, nullable=False)
    extraction_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="loan_analyses")
    fee_flags: Mapped[list["FeeFlag"]] = relationship(back_populates="loan_analysis", cascade="all, delete-orphan")
    compliance_flags: Mapped[list["ComplianceFlag"]] = relationship(back_populates="loan_analysis", cascade="all, delete-orphan")


class FeeFlag(Base):
    __tablename__ = "fee_flags"

    id: Mapped[uuid.UUID] = _uuid_pk()
    loan_analysis_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("loan_analyses.id"), nullable=False)
    fee_type: Mapped[str] = mapped_column(String(64), nullable=False)
    found_pct: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)

    loan_analysis: Mapped["LoanAnalysis"] = relationship(back_populates="fee_flags")


class ComplianceFlag(Base):
    __tablename__ = "compliance_flags"

    id: Mapped[uuid.UUID] = _uuid_pk()
    loan_analysis_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("loan_analyses.id"), nullable=False)
    rule_violated: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)

    loan_analysis: Mapped["LoanAnalysis"] = relationship(back_populates="compliance_flags")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    board_response: Mapped[dict] = mapped_column(JSON, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="chat_history")
