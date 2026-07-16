# ClearFinance v2 — AI-Powered Financial Intelligence Platform

**Built for the System Siege Hackathon (PS-002)**

ClearFinance is a judge-proof, highly secure financial advisory platform built on a deterministic Multi-Agent Architecture. It transforms opaque financial documents into mathematically verified Fairness Scores and provides tailored financial advice across 6 domains.

## The Architecture (v2 Rebuild)

ClearFinance was rebuilt from the ground up to solve the core problem with most AI financial apps: **LLM Hallucinations.**

Instead of letting an LLM guess a financial health score or loan fairness rating, ClearFinance uses a deterministic engine architecture:
1. **Extraction:** The LLM strictly extracts structured data from PDFs (e.g. Principal, EMI, Fees) in a JSON schema.
2. **Determinism:** Pure Python mathematical engines (`financial_engine.py`, `loan_engine.py`, `compliance_engine.py`) verify the EMI, calculate the APR, flag predatory patterns, and compute the Fairness Score using strict formulas.
3. **Orchestration:** A Multi-Agent Orchestrator routes chat queries to specialized deterministic agents (Debt, Savings, etc.).
4. **Explainability Envelope:** Every AI output is wrapped in an explainability envelope that exposes the specific mathematical formula, the evidence, and the reasoning used to generate the advice. 

*If you upload the same loan document twice, you will get the exact same Fairness Score twice.*

## Security Posture (Red Team Tested)

Security is built-in by design, adhering strictly to the `agent_security_instructions.md`:
- **IDOR Prevention:** Every database query for user-owned data is strictly scoped with a `user_id = current_user.id` check. The API never returns `404` for unauthorized resources (returning `403` instead to avoid revealing existence).
- **Rate Limiting:** `slowapi` enforces strict rate limits (`5/min` for auth, `3/min` for AI operations, `100/min` for general endpoints).
- **Mass Assignment Defense:** All Pydantic models inherit from a `StrictModel` that uses `extra='forbid'` to reject any unexpected fields injected by an attacker.
- **SQL Injection Prevention:** 100% ORM-based (SQLAlchemy), with no raw SQL string concatenation anywhere in the codebase.
- **Security Headers:** A custom middleware applies `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, and `X-XSS-Protection` to every request.
- **Production Mode:** Swagger `/docs` and `/redoc` are disabled in production to prevent endpoint discovery.

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+

### Running Locally
1. Clone the repository.
2. Ensure you have an `.env` file at the root (use `.env.example` as a template).
3. Start the application:
```bash
docker-compose up --build
```
4. Access the frontend at `http://localhost:3000`.

## Known Limitations & Honest Gap Analysis

In the spirit of the System Siege hackathon, here is an honest assessment of the current build:
- **LLM Cost:** The Multi-Agent Orchestrator currently mocks the sub-agent LLM calls for MVP speed and cost control. A true production version would require an Intent Classifier LLM followed by specialized domain LLM calls, increasing latency.
- **File Validation:** While the API checks for `.pdf` magic bytes, deeper malicious PDF sanitization (e.g., stripping javascript embedded in PDFs) is not fully implemented.
- **Database Scale:** We are using SQLite for the MVP. A production rollout would require migrating the SQLAlchemy connection string to PostgreSQL, which is fully supported by the current ORM schema.
