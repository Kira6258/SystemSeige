"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Nav from "@/components/Nav";
import { api, ApiError } from "@/lib/api";
import type { BoardChatResponse } from "@/lib/types";

export default function ChatPage() {
  const router = useRouter();
  const [message, setMessage] = useState("");
  const [responses, setResponses] = useState<BoardChatResponse[]>([]);
  const [error, setError] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [responses]);

  async function onSend(e: React.FormEvent) {
    e.preventDefault();
    if (!message.trim()) return;
    setError("");
    setSending(true);
    try {
      const response = await api.post<BoardChatResponse>("/api/chat", { message });
      setResponses((prev) => [...prev, response]);
      setMessage("");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.replace("/login");
        return;
      }
      setError(err instanceof ApiError ? err.message : "Could not reach the board");
    } finally {
      setSending(false);
    }
  }

  return (
    <>
      <div className="container" style={{maxWidth: '900px'}}>
        <h1>Board of Directors</h1>
        <p className="muted" style={{fontSize: '1.1rem', marginBottom: '40px'}}>
          Debt · Savings · Investment · Insurance · Tax · Compliance
        </p>

        {error && <div className="error-banner">⚠️ {error}</div>}

        <div style={{display: 'flex', flexDirection: 'column', gap: '32px'}}>
          {responses.map((r, responseIdx) => (
            <div key={r.id} style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
              {/* User Message Bubble */}
              <div style={{alignSelf: 'flex-end', background: 'var(--primary)', padding: '16px 24px', borderRadius: '24px 24px 4px 24px', maxWidth: '80%'}}>
                <p style={{margin: 0}}>{responses.length === 0 && responseIdx === 0 ? "" : r.advisors[0] ? "..." : ""}
                </p>
              </div>

              {/* Board's Multi-Agent Response */}
              <div className="card" style={{padding: '0', overflow: 'hidden'}}>
                <div style={{padding: '16px 24px', background: 'rgba(255,255,255,0.02)', borderBottom: '1px solid var(--panel-border)', display: 'flex', alignItems: 'center', gap: '12px'}}>
                  <div style={{width: '8px', height: '8px', borderRadius: '50%', background: 'var(--success)'}}></div>
                  <strong style={{letterSpacing: '1px'}}>BOARD RESPONSE</strong>
                </div>
                
                <div style={{padding: '24px'}}>
                  {r.advisors.map((a, i) => (
                    <div className="advisor-card" key={i}>
                      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px'}}>
                        <strong style={{fontSize: '1.1rem', color: 'var(--text-main)'}}>{a.role}</strong>
                        <div style={{display: 'flex', gap: '12px'}}>
                          <span style={{background: 'rgba(255,255,255,0.1)', padding: '4px 12px', borderRadius: '12px', fontSize: '0.8rem'}}>
                            Confidence: {(a.confidence * 100).toFixed(0)}%
                          </span>
                          <span style={{background: a.risk_level === 'high' ? 'rgba(244,63,94,0.2)' : 'rgba(16,185,129,0.2)', color: a.risk_level === 'high' ? 'var(--danger)' : 'var(--success)', padding: '4px 12px', borderRadius: '12px', fontSize: '0.8rem'}}>
                            {a.risk_level.toUpperCase()} RISK
                          </span>
                        </div>
                      </div>
                      <p style={{fontSize: '1.05rem', lineHeight: '1.7'}}>{a.advice}</p>
                      
                      <details className="reasoning-box">
                        <summary>Explainability Envelope</summary>
                        <div className="reasoning-content">
                          <strong>Evidence Cited:</strong>
                          <ul>
                            {a.evidence.map((ev, idx) => <li key={idx}>{ev}</li>)}
                          </ul>
                          <strong>Deterministic Reasoning:</strong>
                          <p>{a.reasoning}</p>
                          {a.formula_used && (
                            <>
                              <strong>Mathematical Formula Applied:</strong>
                              <p><code>{a.formula_used}</code></p>
                            </>
                          )}
                        </div>
                      </details>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div ref={bottomRef} style={{height: '100px'}} />

        <div style={{position: 'fixed', bottom: 0, left: 0, right: 0, background: 'linear-gradient(to top, var(--bg-dark) 60%, transparent)', padding: '40px 24px 24px 24px', zIndex: 10}}>
          <div style={{maxWidth: '900px', margin: '0 auto'}}>
            <form onSubmit={onSend} style={{position: 'relative', display: 'flex', gap: '12px'}}>
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                maxLength={4000}
                placeholder="Ask your board for financial guidance..."
                style={{margin: 0, padding: '20px 24px', borderRadius: '16px', background: 'var(--panel-bg)', backdropFilter: 'blur(16px)', flexGrow: 1, fontSize: '1.05rem', boxShadow: '0 10px 30px rgba(0,0,0,0.5)'}}
              />
              <button type="submit" disabled={sending} style={{borderRadius: '16px', padding: '0 32px'}}>
                {sending ? "Processing..." : "Send"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </>
  );
}
