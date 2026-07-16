"use client";

import { useState } from "react";
import Nav from "@/components/Nav";
import { api, ApiError } from "@/lib/api";

interface BankOffer {
  bank_name: string;
  interest_rate: number;
  max_amount: number;
  approval_chance: string;
}

interface LoanFinderResponse {
  risk_level: string;
  offers: BankOffer[];
}

export default function LoanFinderPage() {
  const [requestedAmount, setRequestedAmount] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState<LoanFinderResponse | null>(null);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setResults(null);
    setLoading(true);

    try {
      const data = await api.post<LoanFinderResponse>("/api/loans/finder", {
        requested_amount: Number(requestedAmount) || 0
      });
      setResults(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="container">
        <h1>Bank Loan Matcher</h1>
        <p className="muted" style={{marginBottom: '32px'}}>We use your financial profile, DTI ratio, and collateral to find the best interest rates.</p>

        <div className="card" style={{marginBottom: '32px'}}>
          <form onSubmit={handleSearch} style={{display: 'flex', gap: '16px', alignItems: 'flex-end'}}>
            <div style={{flex: 1}}>
              <label>How much do you want to borrow? (₹)</label>
              <input 
                type="number" 
                min={1} 
                required
                value={requestedAmount} 
                onChange={(e) => setRequestedAmount(e.target.value)} 
                placeholder="e.g. 50000"
              />
            </div>
            <button type="submit" disabled={loading} style={{padding: '14px 24px'}}>
              {loading ? "Searching..." : "Find Best Offers"}
            </button>
          </form>
          {error && <div className="error-banner" style={{marginTop: '16px'}}>⚠️ {error}</div>}
        </div>

        {results && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h2>Matched Offers</h2>
              <div style={{ padding: '8px 16px', borderRadius: '20px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--panel-border)' }}>
                Your Risk Tier: 
                <strong style={{ 
                  marginLeft: '8px',
                  color: results.risk_level === 'Low' ? 'var(--success)' : results.risk_level === 'Medium' ? 'var(--warning)' : 'var(--danger)'
                }}>
                  {results.risk_level}
                </strong>
              </div>
            </div>

            <div className="grid-3">
              {results.offers.map((offer, idx) => (
                <div key={idx} className="card" style={{ borderTop: `4px solid ${idx === 0 ? 'var(--primary)' : 'var(--panel-border)'}` }}>
                  {idx === 0 && <span style={{ background: 'var(--primary)', color: '#000', fontSize: '0.8rem', padding: '4px 8px', borderRadius: '4px', fontWeight: 'bold', display: 'inline-block', marginBottom: '12px' }}>BEST MATCH</span>}
                  <h3 style={{fontSize: '1.2rem'}}>{offer.bank_name}</h3>
                  <div style={{ marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{display: 'flex', justifyContent: 'space-between'}}>
                      <span className="muted">Interest Rate</span>
                      <strong style={{fontSize: '1.1rem'}}>{offer.interest_rate.toFixed(2)}%</strong>
                    </div>
                    <div style={{display: 'flex', justifyContent: 'space-between'}}>
                      <span className="muted">Max Eligible</span>
                      <strong>₹{offer.max_amount.toLocaleString()}</strong>
                    </div>
                    <div style={{display: 'flex', justifyContent: 'space-between'}}>
                      <span className="muted">Approval Odds</span>
                      <strong style={{
                        color: offer.approval_chance === 'High' || offer.approval_chance === 'Very High' ? 'var(--success)' : 
                               offer.approval_chance === 'Medium' ? 'var(--warning)' : 'var(--danger)'
                      }}>{offer.approval_chance}</strong>
                    </div>
                  </div>
                  <a href={`https://www.google.com/search?q=${encodeURIComponent(offer.bank_name)}+personal+loan+apply`} target="_blank" rel="noopener noreferrer" style={{textDecoration: 'none'}}>
                    <button style={{width: '100%', marginTop: '24px', background: 'transparent', border: '1px solid var(--primary)', color: 'var(--primary)', cursor: 'pointer'}}>
                      Apply Now
                    </button>
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
