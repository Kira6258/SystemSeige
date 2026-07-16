"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Nav from "@/components/Nav";
import { api, ApiError } from "@/lib/api";

interface Profile {
  monthly_income: number;
  total_debt: number;
  savings: number;
  financial_health_score: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [form, setForm] = useState({ monthly_income: "", total_debt: "", savings: "" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api
      .get<Profile>("/api/profile")
      .then((p) => {
        setProfile(p);
        setForm({
          monthly_income: String(p.monthly_income),
          total_debt: String(p.total_debt),
          savings: String(p.savings),
        });
      })
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) router.replace("/login");
      });
  }, [router]);

  async function onSave(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      const updated = await api.put<Profile>("/api/profile", {
        monthly_income: Number(form.monthly_income) || 0,
        total_debt: Number(form.total_debt) || 0,
        savings: Number(form.savings) || 0,
      });
      setProfile(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save profile");
    } finally {
      setSaving(false);
    }
  }

  const scoreClass =
    profile && profile.financial_health_score >= 70
      ? "score-good"
      : profile && profile.financial_health_score >= 40
      ? "score-mid"
      : "score-bad";

  return (
    <>
      <Nav />
      <div className="container">
        <h1>Financial Health Dashboard</h1>

        {profile && (
          <div className="card">
            <h3>Financial Health Score</h3>
            <span className={`score-badge ${scoreClass}`}>{profile.financial_health_score}</span>
            <p className="muted">Computed from your debt-to-income and savings-to-income ratios.</p>
          </div>
        )}

        <div className="card">
          <h3>Your Financial Profile</h3>
          {error && <div className="error">{error}</div>}
          <form onSubmit={onSave}>
            <div className="grid-2">
              <div>
                <label>Monthly Income</label>
                <input
                  type="number"
                  min={0}
                  value={form.monthly_income}
                  onChange={(e) => setForm({ ...form, monthly_income: e.target.value })}
                />
              </div>
              <div>
                <label>Total Debt</label>
                <input
                  type="number"
                  min={0}
                  value={form.total_debt}
                  onChange={(e) => setForm({ ...form, total_debt: e.target.value })}
                />
              </div>
            </div>
            <label>Savings</label>
            <input
              type="number"
              min={0}
              value={form.savings}
              onChange={(e) => setForm({ ...form, savings: e.target.value })}
            />
            <button type="submit" disabled={saving}>{saving ? "Saving..." : "Save Profile"}</button>
          </form>
        </div>
      </div>
    </>
  );
}
