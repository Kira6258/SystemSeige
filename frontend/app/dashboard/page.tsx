"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [expenses, setExpenses] = useState<any[]>([]);
  const [goals, setGoals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [p, exp, g] = await Promise.all([
          api.get<any>("/api/profile").catch(() => null),
          api.get<any[]>("/api/expenses").catch(() => []),
          api.get<any[]>("/api/goals").catch(() => [])
        ]);
        setProfile(p);
        setExpenses(exp.slice(0, 5));
        setGoals(g.slice(0, 3));
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) router.replace("/login");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [router]);

  if (loading) return <div className="container">Loading...</div>;

  // Calculate current month expenses
  const currentMonth = new Date().getMonth();
  const currentYear = new Date().getFullYear();
  const monthlyExpenses = expenses
    .filter(e => {
      const d = new Date(e.txn_date);
      return d.getMonth() === currentMonth && d.getFullYear() === currentYear;
    })
    .reduce((sum, e) => sum + e.amount, 0);

  const savingsRate = profile && profile.monthly_income > 0 
    ? ((profile.monthly_income - profile.monthly_expenses) / profile.monthly_income * 100).toFixed(1)
    : "0.0";

  const dti = profile && profile.monthly_income > 0
    ? ((profile.total_debt / 12) / profile.monthly_income * 100).toFixed(1)
    : "0.0";

  return (
    <div className="container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 32 }}>
        <div>
          <h1>Command Center</h1>
          <p className="muted">Welcome back. Here is your financial overview.</p>
        </div>
        {profile && profile.health_score !== null && (
          <div style={{textAlign: "right"}}>
            <div className="stat-label">Health Score</div>
            <div className={`score-badge ${profile.health_score > 70 ? "score-good" : profile.health_score > 40 ? "score-mid" : "score-bad"}`}>
              {profile.health_score}
            </div>
          </div>
        )}
      </div>

      {(!profile || profile.monthly_income === 0) && (
        <div className="error-banner" style={{marginBottom: 32}}>
          <p>Your financial profile is incomplete. We need this data to power our AI engines.</p>
          <Link href="/profile"><button className="sm">Complete Profile</button></Link>
        </div>
      )}

      {/* Quick Stats Row */}
      <div className="grid-4" style={{marginBottom: 32}}>
        <div className="stat-card">
          <div className="stat-label">Monthly Income</div>
          <div className="stat-value text-success">₹{profile?.monthly_income?.toLocaleString() || "0"}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Recent Expenses</div>
          <div className="stat-value text-warning">₹{monthlyExpenses.toLocaleString()}</div>
          <div className="stat-sub muted">This month</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Savings Rate</div>
          <div className="stat-value">{savingsRate}%</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">DTI Ratio</div>
          <div className="stat-value">{dti}%</div>
        </div>
      </div>

      <div className="grid-2">
        {/* Goals Widget */}
        <div className="card">
          <div style={{display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24}}>
            <h3>Active Goals</h3>
            <Link href="/goals"><button className="secondary sm">View All</button></Link>
          </div>
          
          {goals.length === 0 ? (
            <div style={{textAlign: "center", padding: "32px 0"}}>
              <p className="muted" style={{marginBottom: 16}}>No active financial goals.</p>
              <Link href="/goals"><button className="sm">Create Goal</button></Link>
            </div>
          ) : (
            <div style={{display: "flex", flexDirection: "column", gap: 20}}>
              {goals.map(g => (
                <div key={g.id}>
                  <div style={{display: "flex", justifyContent: "space-between", marginBottom: 8}}>
                    <Link href={`/goals/${g.id}`} style={{textDecoration: "none", color: "inherit"}}>
                      <strong>{g.title}</strong>
                    </Link>
                    <span className="muted">₹{g.current_amount} / ₹{g.target_amount}</span>
                  </div>
                  <div className="progress-container">
                    <div 
                      className="progress-bar primary" 
                      style={{width: `${Math.min(100, (g.current_amount / g.target_amount) * 100)}%`}}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Expenses Widget */}
        <div className="card">
          <div style={{display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24}}>
            <h3>Recent Expenses</h3>
            <Link href="/expenses"><button className="secondary sm">Tracker</button></Link>
          </div>

          {expenses.length === 0 ? (
            <p className="muted">No recent expenses.</p>
          ) : (
            <div style={{display: "flex", flexDirection: "column", gap: 12}}>
              {expenses.map(e => (
                <div key={e.id} style={{display: "flex", justifyContent: "space-between", alignItems: "center", padding: 12, background: "rgba(128,128,128,0.05)", borderRadius: 8}}>
                  <div style={{display: "flex", alignItems: "center", gap: 12}}>
                    <span className="badge neutral">{e.category}</span>
                    <span style={{fontSize: "0.9rem"}}>{e.description || e.category}</span>
                  </div>
                  <strong>₹{e.amount}</strong>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

    </div>
  );
}
