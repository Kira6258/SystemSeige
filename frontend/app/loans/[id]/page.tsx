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
          <div className="error-banner">⚠️ {error}</div>
        </div>
      </>
    );
  }

  if (!analysis) {
    return (
      <>
        <Nav />
        <div className="container" style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh'}}>
          <div className="muted" style={{fontSize: '1.2rem', animation: 'pulse 2s infinite'}}>Running deterministic engines...</div>
        </div>
      </>
    );
  }

  const scoreClass =
    analysis.fairness_score >= 70 ? "score-good" : analysis.fairness_score >= 40 ? "score-mid" : "score-bad";

  return (
    <>
      <Nav />
      <div className="container">
        <h1 style={{marginBottom: '40px'}}>Loan Transparency Report</h1>

        <div className="grid-2" style={{alignItems: 'start'}}>
          <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', padding: '48px 24px' }}>
            <h3 className="muted" style={{textTransform: 'uppercase', letterSpacing: '2px', fontSize: '0.9rem'}}>Computed Fairness Score</h3>
            <div className={`score-badge ${scoreClass}`} style={{fontSize: '5rem', margin: '20px 0'}}>{analysis.fairness_score}</div>
            <div style={{display: 'flex', gap: '16px', marginTop: '16px'}}>
              <span style={{background: 'rgba(255,255,255,0.05)', padding: '6px 16px', borderRadius: '20px', fontSize: '0.85rem', border: '1px solid var(--panel-border)'}}>
                Confidence: {(analysis.confidence * 100).toFixed(0)}%
              </span>
              <span style={{background: 'rgba(255,255,255,0.05)', padding: '6px 16px', borderRadius: '20px', fontSize: '0.85rem', border: '1px solid var(--panel-border)', color: analysis.reproducible ? 'var(--success)' : 'var(--text)'}}>
                {analysis.reproducible ? "✓ Mathematically Verified" : "Unverified"}
              </span>
            </div>
          </div>

          <div className="card" style={{padding: '32px'}}>
            <h3 style={{marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '12px'}}>
              <span style={{background: 'var(--primary)', width: '32px', height: '32px', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', borderRadius: '8px', fontSize: '1rem'}}>i</span>
              Plain Language Explanation
            </h3>
            <p style={{fontSize: '1.1rem', lineHeight: '1.8', color: 'var(--text-muted)'}}>{analysis.explanation}</p>
          </div>
        </div>

        <div className="card" style={{marginTop: '16px'}}>
          <h3 style={{borderBottom: '1px solid var(--panel-border)', paddingBottom: '16px', marginBottom: '24px'}}>Deterministic Audit Trail</h3>
          
          <div className="grid-2">
            <div style={{background: 'rgba(255,255,255,0.02)', padding: '24px', borderRadius: '16px', border: '1px solid var(--panel-border)'}}>
              <p className="muted" style={{textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '1px'}}>Engine Calculation</p>
              <div style={{display: 'flex', justifyContent: 'space-between', marginTop: '12px'}}>
                <span>Verified EMI</span>
                <strong style={{fontSize: '1.2rem'}}>₹{analysis.computation.verified_emi.toFixed(2)}</strong>
              </div>
              <div style={{display: 'flex', justifyContent: 'space-between', marginTop: '12px'}}>
                <span>Stated EMI</span>
                <strong style={{fontSize: '1.2rem'}}>{analysis.computation.stated_emi ? `₹${analysis.computation.stated_emi.toFixed(2)}` : "N/A"}</strong>
              </div>
              <div style={{display: 'flex', justifyContent: 'space-between', marginTop: '12px'}}>
                <span>True APR</span>
                <strong style={{fontSize: '1.2rem', color: 'var(--warning)'}}>{analysis.computation.apr !== undefined ? `${analysis.computation.apr}%` : 'N/A'}</strong>
              </div>
              <div style={{display: 'flex', justifyContent: 'space-between', marginTop: '12px', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.1)'}}>
                <span>EMI Deviation</span>
                <strong style={{color: analysis.computation.emi_deviation_pct > 0 ? 'var(--danger)' : 'var(--success)'}}>{analysis.computation.emi_deviation_pct.toFixed(1)}%</strong>
              </div>
            </div>
            
            {analysis.computation.predatory_signals && analysis.computation.predatory_signals.length > 0 && (
              <div style={{background: 'rgba(244, 63, 94, 0.05)', padding: '24px', borderRadius: '16px', border: '1px solid rgba(244, 63, 94, 0.2)'}}>
                <h4 style={{color: "var(--danger)", display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px'}}>
                  <span style={{fontSize: '1.2rem'}}>⚠️</span> Predatory Signals Detected
                </h4>
                <ul style={{paddingLeft: '20px', color: 'var(--danger)', display: 'flex', flexDirection: 'column', gap: '8px'}}>
                  {analysis.computation.predatory_signals.map((sig, i) => (
                    <li key={i}>{sig}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {(analysis.computation.fee_flags.length > 0 || analysis.computation.compliance_flags.length > 0) && (
            <div style={{marginTop: "40px"}}>
              <h4 style={{marginBottom: '20px'}}>Rule Engine Violations</h4>
              
              {analysis.computation.fee_flags.map((f, i) => (
                <div key={i} className="advisor-card" style={{borderColor: f.severity === 'high' ? 'rgba(244, 63, 94, 0.3)' : 'rgba(245, 158, 11, 0.3)'}}>
                  <div style={{display: 'flex', justifyContent: 'space-between'}}>
                    <strong style={{textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-main)'}}>{f.fee_type.replace('_', ' ')}</strong>
                    <span style={{background: f.severity === 'high' ? 'rgba(244,63,94,0.15)' : 'rgba(245,158,11,0.15)', color: f.severity === 'high' ? 'var(--danger)' : 'var(--warning)', padding: '4px 12px', borderRadius: '12px', fontSize: '0.8rem'}}>
                      {f.severity.toUpperCase()} SEVERITY
                    </span>
                  </div>
                  <p style={{marginTop: '12px', color: 'var(--text-muted)'}}>
                    Found at <strong style={{color: 'var(--danger)'}}>{f.found_pct}%</strong>, which exceeds the typical industry range of [{f.typical_range_pct[0]}%–{f.typical_range_pct[1]}%].
                  </p>
                </div>
              ))}

              {analysis.computation.compliance_flags.map((f, i) => (
                <div key={i} className="advisor-card" style={{borderColor: 'rgba(244, 63, 94, 0.3)'}}>
                  <div style={{display: 'flex', justifyContent: 'space-between'}}>
                    <strong style={{color: 'var(--danger)'}}>Compliance Violation</strong>
                    <span style={{background: 'rgba(244,63,94,0.15)', color: 'var(--danger)', padding: '4px 12px', borderRadius: '12px', fontSize: '0.8rem'}}>
                      {f.severity.toUpperCase()} SEVERITY
                    </span>
                  </div>
                  <p style={{marginTop: '12px', color: 'var(--text-muted)'}}>{f.rule_violated}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
