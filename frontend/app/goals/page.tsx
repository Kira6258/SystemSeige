"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";

export default function GoalsPage() {
  const router = useRouter();
  const [goals, setGoals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  
  const [form, setForm] = useState({
    title: "", goal_type: "Emergency Fund", description: "", target_amount: "", target_date: "", priority: "3"
  });

  useEffect(() => {
    fetchGoals();
  }, []);

  async function fetchGoals() {
    try {
      const data = await api.get<any[]>("/api/goals");
      setGoals(data);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) router.replace("/login");
    } finally {
      setLoading(false);
    }
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post("/api/goals", {
        title: form.title,
        goal_type: form.goal_type,
        description: form.description,
        target_amount: Number(form.target_amount),
        target_date: form.target_date,
        priority: Number(form.priority)
      });
      setShowForm(false);
      setForm({ title: "", goal_type: "Emergency Fund", description: "", target_amount: "", target_date: "", priority: "3" });
      fetchGoals();
    } catch (err) {
      alert("Failed to create goal");
    }
  }

  if (loading) return <div className="container">Loading...</div>;

  return (
    <div className="container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 32 }}>
        <div>
          <h1>Financial Goals</h1>
          <p className="muted">Track your progress and get AI-driven advice to reach your targets.</p>
        </div>
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "+ New Goal"}
        </button>
      </div>

      {showForm && (
        <div className="card" style={{border: "1px solid var(--primary)", boxShadow: "0 0 20px var(--primary-glow)"}}>
          <h3>Create New Goal</h3>
          <form onSubmit={onSubmit} style={{marginTop: 24}}>
            <div className="grid-2">
              <div>
                <label>Goal Title</label>
                <input type="text" required value={form.title} onChange={e => setForm({...form, title: e.target.value})} placeholder="e.g. Save for a House" />
              </div>
              <div>
                <label>Goal Type</label>
                <select value={form.goal_type} onChange={e => setForm({...form, goal_type: e.target.value})} required>
                  <option value="Emergency Fund">Emergency Fund</option>
                  <option value="Debt Payoff">Debt Payoff</option>
                  <option value="Home Purchase">Home Purchase</option>
                  <option value="Retirement">Retirement</option>
                  <option value="Education">Education</option>
                  <option value="Vacation">Vacation</option>
                  <option value="Car Purchase">Car Purchase</option>
                  <option value="Custom">Custom</option>
                </select>
              </div>
            </div>
            
            <div className="grid-3">
              <div>
                <label>Target Amount (₹)</label>
                <input type="number" required min={1} value={form.target_amount} onChange={e => setForm({...form, target_amount: e.target.value})} />
              </div>
              <div>
                <label>Target Date</label>
                <input type="date" required value={form.target_date} onChange={e => setForm({...form, target_date: e.target.value})} />
              </div>
              <div>
                <label>Priority (1-High, 5-Low)</label>
                <input type="number" required min={1} max={5} value={form.priority} onChange={e => setForm({...form, priority: e.target.value})} />
              </div>
            </div>

            <div>
              <label>Description / Motivation</label>
              <textarea rows={3} value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Why is this important to you?"></textarea>
            </div>

            <div style={{display: "flex", justifyContent: "flex-end"}}>
              <button type="submit">Save Goal</button>
            </div>
          </form>
        </div>
      )}

      {goals.length === 0 ? (
        <div className="card" style={{textAlign: "center", padding: "64px 24px"}}>
          <h3 className="muted">You haven&apos;t set any goals yet.</h3>
          <p className="muted" style={{marginTop: 8, marginBottom: 24}}>Setting financial goals gives your AI Board of Directors a target to optimize for.</p>
          <button onClick={() => setShowForm(true)}>Create Your First Goal</button>
        </div>
      ) : (
        <div className="grid-3">
          {goals.map(g => {
            const progress = Math.min(100, (g.current_amount / g.target_amount) * 100);
            return (
              <Link href={`/goals/${g.id}`} key={g.id} style={{textDecoration: "none", color: "inherit"}}>
                <div className="card" style={{height: "100%", display: "flex", flexDirection: "column", transition: "transform 0.2s"}}>
                  <div style={{display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16}}>
                    <span className={`badge ${g.status === "completed" ? "success" : "primary"}`}>{g.status}</span>
                    <span className="badge neutral">P{g.priority}</span>
                  </div>
                  <h3 style={{marginBottom: 8}}>{g.title}</h3>
                  <p className="muted" style={{fontSize: "0.9rem", marginBottom: 24}}>{g.goal_type}</p>
                  
                  <div style={{marginTop: "auto"}}>
                    <div style={{display: "flex", justifyContent: "space-between", marginBottom: 8}}>
                      <strong>₹{g.current_amount.toLocaleString()}</strong>
                      <span className="muted">of ₹{g.target_amount.toLocaleString()}</span>
                    </div>
                    <div className="progress-container">
                      <div className={`progress-bar ${g.status === "completed" ? "success" : "primary"}`} style={{width: `${progress}%`}}></div>
                    </div>
                    <div style={{textAlign: "right", marginTop: 8, fontSize: "0.85rem", color: "var(--text-muted)"}}>
                      Target: {g.target_date}
                    </div>
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  );
}
