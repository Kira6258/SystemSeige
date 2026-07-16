"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { api, ApiError } from "@/lib/api";
import { use } from "react";

export default function GoalDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const router = useRouter();
  const [goal, setGoal] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  
  const [form, setForm] = useState({
    title: "", target_amount: "", current_amount: "", target_date: "", status: "", priority: "3", description: ""
  });

  useEffect(() => {
    async function load() {
      try {
        const data = await api.get<any>(`/api/goals/${resolvedParams.id}`);
        setGoal(data);
        setForm({
          title: data.title,
          target_amount: String(data.target_amount),
          current_amount: String(data.current_amount),
          target_date: data.target_date,
          status: data.status,
          priority: String(data.priority),
          description: data.description || ""
        });
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) router.replace("/login");
        else router.replace("/goals");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [resolvedParams.id, router]);

  async function onSave(e: React.FormEvent) {
    e.preventDefault();
    try {
      const updated = await api.put<any>(`/api/goals/${resolvedParams.id}`, {
        title: form.title,
        target_amount: Number(form.target_amount),
        current_amount: Number(form.current_amount),
        target_date: form.target_date,
        status: form.status,
        priority: Number(form.priority),
        description: form.description
      });
      setGoal(updated);
      setEditing(false);
    } catch (err) {
      alert("Failed to update goal");
    }
  }

  if (loading) return <div className="container">Loading...</div>;
  if (!goal) return null;

  const progress = Math.min(100, (goal.current_amount / goal.target_amount) * 100);

  return (
    <div className="container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 32 }}>
        <div>
          <button className="secondary sm" onClick={() => router.push("/goals")} style={{marginBottom: 16}}>← Back to Goals</button>
          <h1>{goal.title}</h1>
          <p className="muted">{goal.goal_type} • Target Date: {goal.target_date}</p>
        </div>
        <button className="secondary" onClick={() => setEditing(!editing)}>
          {editing ? "Cancel" : "Edit Goal"}
        </button>
      </div>

      <div className="grid-2">
        <div>
          {/* Progress Card */}
          <div className="card" style={{display: "flex", flexDirection: "column", alignItems: "center", padding: "48px 24px"}}>
            <div style={{position: "relative", width: 200, height: 200, display: "flex", alignItems: "center", justifyContent: "center"}}>
              <svg width="200" height="200" viewBox="0 0 200 200" style={{position: "absolute"}}>
                <circle cx="100" cy="100" r="90" fill="none" stroke="rgba(128,128,128,0.2)" strokeWidth="12" />
                <circle cx="100" cy="100" r="90" fill="none" stroke="var(--primary)" strokeWidth="12" 
                  strokeDasharray={`${2 * Math.PI * 90}`} 
                  strokeDashoffset={`${2 * Math.PI * 90 * (1 - progress/100)}`}
                  strokeLinecap="round"
                  style={{transition: "stroke-dashoffset 1s ease-out", transform: "rotate(-90deg)", transformOrigin: "center"}}
                />
              </svg>
              <div style={{textAlign: "center"}}>
                <div style={{fontSize: "2.5rem", fontWeight: 700, lineHeight: 1}}>{Math.round(progress)}%</div>
                <div className="muted" style={{fontSize: "0.9rem"}}>Complete</div>
              </div>
            </div>
            
            <div style={{marginTop: 32, width: "100%", textAlign: "center"}}>
              <div style={{display: "flex", justifyContent: "space-between", marginBottom: 8}}>
                <span className="muted">Currently Saved</span>
                <strong>₹{goal.current_amount.toLocaleString()}</strong>
              </div>
              <div style={{display: "flex", justifyContent: "space-between"}}>
                <span className="muted">Target Amount</span>
                <strong>₹{goal.target_amount.toLocaleString()}</strong>
              </div>
            </div>
          </div>
          
          {editing && (
            <div className="card" style={{border: "1px solid var(--primary)", marginTop: "24px"}}>
              <h3>Edit Goal Details</h3>
              <form onSubmit={onSave} style={{marginTop: 24}}>
                <div>
                  <label>Goal Title</label>
                  <input type="text" required value={form.title} onChange={e => setForm({...form, title: e.target.value})} />
                </div>
                <div className="grid-2" style={{marginTop: 16}}>
                  <div>
                    <label>Target Amount (₹)</label>
                    <input type="number" required min={1} value={form.target_amount} onChange={e => setForm({...form, target_amount: e.target.value})} />
                  </div>
                  <div>
                    <label>Currently Saved (₹)</label>
                    <input type="number" required min={0} value={form.current_amount} onChange={e => setForm({...form, current_amount: e.target.value})} />
                  </div>
                </div>
                <div className="grid-3" style={{marginTop: 16}}>
                  <div>
                    <label>Target Date</label>
                    <input type="date" required value={form.target_date} onChange={e => setForm({...form, target_date: e.target.value})} />
                  </div>
                  <div>
                    <label>Priority (1-5)</label>
                    <input type="number" required min={1} max={5} value={form.priority} onChange={e => setForm({...form, priority: e.target.value})} />
                  </div>
                  <div>
                    <label>Status</label>
                    <select value={form.status} onChange={e => setForm({...form, status: e.target.value})}>
                      <option value="active">Active</option>
                      <option value="completed">Completed</option>
                      <option value="paused">Paused</option>
                    </select>
                  </div>
                </div>
                <div style={{marginTop: 16}}>
                  <label>Description / Motivation</label>
                  <textarea rows={3} value={form.description} onChange={e => setForm({...form, description: e.target.value})} />
                </div>
                <button type="submit" style={{marginTop: 24}}>Save Changes</button>
              </form>
            </div>
          )}
        </div>

        <div>
          {/* AI Advice Card */}
          <div className="card advisor-card">
            <h3 style={{display: "flex", alignItems: "center", gap: 12}}>
              <span>✨</span> AI Action Plan
            </h3>
            <p className="muted" style={{marginBottom: 24}}>
              Based on your full financial profile, income, and existing debts.
            </p>
            
            <div className="reasoning-content" style={{padding: 0, fontSize: "1.05rem", lineHeight: 1.6}}>
              {goal.llm_advice ? (
                <ReactMarkdown>{goal.llm_advice}</ReactMarkdown>
              ) : (
                <p>Generating advice... Please complete your financial profile if you haven&apos;t already.</p>
              )}
            </div>
          </div>
          
          <div className="card">
            <h3>Motivation</h3>
            <p style={{marginTop: 16}}>{goal.description || <span className="muted">No description provided.</span>}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
