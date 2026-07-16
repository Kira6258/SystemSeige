import uuid
from datetime import datetime, date

from sqlalchemy import ForeignKey, Numeric, String, Text, JSON, Integer, Float, DateTime, Date
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
    role: Mapped[str] = mapped_column(String(32), default="user", nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    profile: Mapped["FinancialProfile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    budgets: Mapped[list["Budget"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    goals: Mapped[list["Goal"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    investments: Mapped[list["Investment"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    insurance: Mapped[list["Insurance"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    taxes: Mapped[list["Tax"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    loans: Mapped[list["Loan"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    agent_logs: Mapped[list["AgentLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    chat_history: Mapped[list["ChatHistory"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"
    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    monthly_income: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    monthly_expenses: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    liquid_savings: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_debt: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    family_status: Mapped[str] = mapped_column(String(32), default="single")
    past_loans: Mapped[str] = mapped_column(Text, default="")
    property_value: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    financial_health_score: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    user: Mapped["User"] = relationship(back_populates="profile")

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(128))
    amount: Mapped[float] = mapped_column(Numeric(14, 2))
    txn_date: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(Text, default="")
    note: Mapped[str] = mapped_column(Text, default="", nullable=True)
    user: Mapped["User"] = relationship(back_populates="transactions")

class Budget(Base):
    __tablename__ = "budgets"
    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(128))
    monthly_cap: Mapped[float] = mapped_column(Numeric(14, 2))
    user: Mapped["User"] = relationship(back_populates="budgets")

class Goal(Base):
    __tablename__ = "goals"
    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    goal_type: Mapped[str] = mapped_column(String(128))
    title: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    target_amount: Mapped[float] = mapped_column(Numeric(14, 2))
    current_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    target_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), default="active")
    priority: Mapped[int] = mapped_column(Integer, default=3)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    llm_advice: Mapped[str] = mapped_column(Text, nullable=True)
    user: Mapped["User"] = relationship(back_populates="goals")

class Investment(Base):
    __tablename__ = "investments"
    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(128))
    ticker_symbol: Mapped[str] = mapped_column(String(32), default="")
    quantity: Mapped[float] = mapped_column(Numeric(14, 4), default=0)
    avg_buy_price: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    amount: Mapped[float] = mapped_column(Numeric(14, 2))
    current_value: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    avg_return_pct: Mapped[float] = mapped_column(Float, default=0)
    risk_profile: Mapped[str] = mapped_column(String(64), default="medium")
    user: Mapped["User"] = relationship(back_populates="investments")

class Insurance(Base):
    __tablename__ = "insurance"
    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    policy_type: Mapped[str] = mapped_column(String(128))
    cover_amount: Mapped[float] = mapped_column(Numeric(14, 2))
    premium: Mapped[float] = mapped_column(Numeric(14, 2))
    user: Mapped["User"] = relationship(back_populates="insurance")

class Tax(Base):
    __tablename__ = "taxes"
    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    fiscal_year: Mapped[int] = mapped_column(Integer)
    income: Mapped[float] = mapped_column(Numeric(14, 2))
    deductions_claimed: Mapped[float] = mapped_column(Numeric(14, 2))
    regime: Mapped[str] = mapped_column(String(64))
    user: Mapped["User"] = relationship(back_populates="taxes")

class Loan(Base):
    __tablename__ = "loans"
    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    lender_name: Mapped[str] = mapped_column(String(255))
    principal: Mapped[float] = mapped_column(Numeric(14, 2))
    annual_interest_rate: Mapped[float] = mapped_column(Numeric(6, 3))
    tenure_months: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="loans")
    documents: Mapped[list["LoanDocument"]] = relationship(back_populates="loan", cascade="all, delete-orphan")
    analysis: Mapped["LoanAnalysis"] = relationship(back_populates="loan", uselist=False, cascade="all, delete-orphan")

class LoanDocument(Base):
    __tablename__ = "loan_documents"
    id: Mapped[uuid.UUID] = _uuid_pk()
    loan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("loans.id"), nullable=False)
    s3_url: Mapped[str] = mapped_column(String(1024))
    extracted_text: Mapped[str] = mapped_column(Text)
    detected_language: Mapped[str] = mapped_column(String(10))
    loan: Mapped["Loan"] = relationship(back_populates="documents")

class LoanAnalysis(Base):
    __tablename__ = "loan_analyses"
    id: Mapped[uuid.UUID] = _uuid_pk()
    loan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("loans.id"), unique=True, nullable=False)
    verified_emi: Mapped[float] = mapped_column(Numeric(14, 2))
    emi_deviation_pct: Mapped[float] = mapped_column(Float)
    apr: Mapped[float] = mapped_column(Numeric(6, 3))
    loan_burden_ratio: Mapped[float] = mapped_column(Float)
    fairness_score: Mapped[float] = mapped_column(Float)
    confidence_score: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(32))
    predatory_signals: Mapped[dict] = mapped_column(JSON)
    explanation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    loan: Mapped["Loan"] = relationship(back_populates="analysis")
    fee_flags: Mapped[list["FeeFlag"]] = relationship(back_populates="loan_analysis", cascade="all, delete-orphan")
    compliance_flags: Mapped[list["ComplianceFlag"]] = relationship(back_populates="loan_analysis", cascade="all, delete-orphan")

class FeeFlag(Base):
    __tablename__ = "fee_flags"
    id: Mapped[uuid.UUID] = _uuid_pk()
    loan_analysis_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("loan_analyses.id"), nullable=False)
    fee_type: Mapped[str] = mapped_column(String(64))
    found_pct: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String(16))
    loan_analysis: Mapped["LoanAnalysis"] = relationship(back_populates="fee_flags")

class ComplianceFlag(Base):
    __tablename__ = "compliance_flags"
    id: Mapped[uuid.UUID] = _uuid_pk()
    loan_analysis_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("loan_analyses.id"), nullable=False)
    rule_violated: Mapped[str] = mapped_column(String(128))
    severity: Mapped[str] = mapped_column(String(16))
    loan_analysis: Mapped["LoanAnalysis"] = relationship(back_populates="compliance_flags")

class Recommendation(Base):
    __tablename__ = "recommendations"
    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    domain: Mapped[str] = mapped_column(String(64))
    recommendation: Mapped[str] = mapped_column(Text)
    explainable_output: Mapped[dict] = mapped_column(JSON)
    priority: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    user: Mapped["User"] = relationship(back_populates="recommendations")

class AgentLog(Base):
    __tablename__ = "agent_logs"
    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(64))
    input_summary: Mapped[dict] = mapped_column(JSON)
    output_summary: Mapped[dict] = mapped_column(JSON)
    latency_ms: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    user: Mapped["User"] = relationship(back_populates="agent_logs")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    message: Mapped[str] = mapped_column(Text)
    agent_response: Mapped[dict] = mapped_column(JSON)
    language: Mapped[str] = mapped_column(String(10), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    user: Mapped["User"] = relationship(back_populates="chat_history")

class Report(Base):
    __tablename__ = "reports"
    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    report_type: Mapped[str] = mapped_column(String(64))
    s3_url: Mapped[str] = mapped_column(String(1024))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    user: Mapped["User"] = relationship(back_populates="reports")
