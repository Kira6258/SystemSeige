"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Nav from "@/components/Nav";
import { api, ApiError } from "@/lib/api";
import type { LoanAnalysis } from "@/lib/types";

export default function LoanDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [analysis, setAnalysis] = useState<LoanAnalysis | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<LoanAnalysis>(`/api/loans/${params.id}`)
      .then(setAnalysis)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) {
          router.replace("/login");
        } else if (err instanceof ApiError && err.status === 403) {
          setError("You don't have access to this analysis.");
        } else {
          setError("Could not load this analysis.");
        }
      });
  }, [params.id, router]);

  if (error) {
    return (
      <>
        <Nav />
        <div className="container">
          <div className="error">{error}</div>
        </div>
      </>
    );
  }

  if (!analysis) {
    return (
      <>
        <Nav />
        <div className="container">Loading...</div>
      </>
    );
  }

  const scoreClass =
    analysis.fairness_score >= 70 ? "score-good" : analysis.fairness_score >= 40 ? "score-mid" : "score-bad";

  return (
    <>
      <Nav />
      <div className="container">
        <h1>Loan Analysis</h1>

        <div className="card">
          <h3>Fairness Score</h3>
          <span className={`score-badge ${scoreClass}`}>{analysis.fairness_score}</span>
          <p className="muted">Confidence: {(analysis.confidence * 100).toFixed(0)}% · Reproducible: {analysis.reproducible ? "Yes" : "No"}</p>
        </div>

        <div className="card">
          <h3>Explanation</h3>
          <p>{analysis.explanation}</p>
        </div>

        <div className="card">
          <h3>Computation</h3>
          <div className="grid-2">
            <p><strong>Verified EMI:</strong> {analysis.computation.verified_emi}</p>
            <p><strong>Stated EMI:</strong> {analysis.computation.stated_emi ?? "N/A"}</p>
          </div>
          <p><strong>EMI Deviation:</strong> {analysis.computation.emi_deviation_pct}%</p>

          {analysis.computation.fee_flags.length > 0 && (
            <>
              <h4>Fee Flags</h4>
              {analysis.computation.fee_flags.map((f, i) => (
                <div key={i} className="advisor">
                  <strong>{f.fee_type}</strong> — {f.found_pct}% found, typical range [{f.typical_range_pct[0]}%–{f.typical_range_pct[1]}%], severity: {f.severity}
                </div>
              ))}
            </>
          )}

          {analysis.computation.compliance_flags.length > 0 && (
            <>
              <h4>Compliance Flags</h4>
              {analysis.computation.compliance_flags.map((f, i) => (
                <div key={i} className="advisor">
                  <strong>{f.rule_violated}</strong> — severity: {f.severity}
                </div>
              ))}
            </>
          )}
        </div>
      </div>
    </>
  );
}
