"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";

export default function ProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [investments, setInvestments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    monthly_income: "",
    monthly_expenses: "",
    liquid_savings: "",
    total_debt: "",
    family_status: "single",
    past_loans: "",
    property_value: ""
  });

  const [invForm, setInvForm] = useState({
    asset_type: "", ticker_symbol: "", quantity: "", avg_buy_price: "", current_value: ""
  });
  const [showInvForm, setShowInvForm] = useState(false);

  useEffect(() => {
    fetchData();
  }, [router]);

  async function fetchData() {
    try {
      const p = await api.get<any>("/api/profile");
      setProfile(p);
      setForm({
        monthly_income: String(p.monthly_income),
        monthly_expenses: String(p.monthly_expenses),
        liquid_savings: String(p.liquid_savings),
        total_debt: String(p.total_debt),
        family_status: p.family_status || "single",
        past_loans: p.past_loans || "",
        property_value: String(p.property_value || 0),
      });

      const invs = await api.get<any[]>("/api/investments");
      setInvestments(invs);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) router.replace("/login");
    } finally {
      setLoading(false);
    }
  }

  async function onSaveProfile(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      const updated = await api.put<any>("/api/profile", {
        monthly_income: Number(form.monthly_income) || 0,
        monthly_expenses: Number(form.monthly_expenses) || 0,
        liquid_savings: Number(form.liquid_savings) || 0,
        total_debt: Number(form.total_debt) || 0,
        family_status: form.family_status,
        past_loans: form.past_loans,
        property_value: Number(form.property_value) || 0,
      });
      setProfile(updated);
      alert("Profile updated successfully");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save profile");
    } finally {
      setSaving(false);
    }
  }

  async function onAddInvestment(e: React.FormEvent) {
    e.preventDefault();
    try {
      const added = await api.post<any>("/api/investments", {
        asset_type: invForm.asset_type,
        ticker_symbol: invForm.ticker_symbol,
        quantity: Number(invForm.quantity) || 0,
        avg_buy_price: Number(invForm.avg_buy_price) || 0,
        current_value: Number(invForm.current_value) || 0
      });
      setInvestments([...investments, added]);
      setInvForm({ asset_type: "", ticker_symbol: "", quantity: "", avg_buy_price: "", current_value: "" });
      setShowInvForm(false);
    } catch (err) {
      alert("Could not add investment");
    }
  }

  async function onDeleteInvestment(id: string) {
    try {
      await api.delete(`/api/investments/${id}`);
      setInvestments(investments.filter((i: any) => i.id !== id));
    } catch (err) {
      alert("Delete failed");
    }
  }

  if (loading) return <div className="container">Loading...</div>;

  return (
    <div className="container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 32 }}>
        <div>
          <h1>Financial Profile</h1>
          <p className="muted">Your data powers the deterministic AI engines.</p>
        </div>
      </div>

      {error && <div className="error-banner">⚠️ {error}</div>}

      <div className="card">
        <h3>Base Financials</h3>
        <form onSubmit={onSaveProfile} style={{marginTop: 24}}>
          <div className="grid-3">
            <div>
              <label>Monthly Income (₹)</label>
              <input type="number" min={0} value={form.monthly_income} onChange={(e) => setForm({ ...form, monthly_income: e.target.value })} />
            </div>
            <div>
              <label>Monthly Expenses (₹)</label>
              <input type="number" min={0} value={form.monthly_expenses} onChange={(e) => setForm({ ...form, monthly_expenses: e.target.value })} />
            </div>
            <div>
              <label>Family Status</label>
              <select value={form.family_status} onChange={(e) => setForm({ ...form, family_status: e.target.value })}>
                <option value="single">Single</option>
                <option value="married">Married</option>
                <option value="family">Family (with dependents)</option>
              </select>
            </div>
          </div>
          
          <h4 style={{marginTop: 24, marginBottom: 16}}>Assets & Liabilities</h4>
          <div className="grid-3">
            <div>
              <label>Liquid Savings (₹)</label>
              <input type="number" min={0} value={form.liquid_savings} onChange={(e) => setForm({ ...form, liquid_savings: e.target.value })} />
            </div>
            <div>
              <label>Total Debt (₹)</label>
              <input type="number" min={0} value={form.total_debt} onChange={(e) => setForm({ ...form, total_debt: e.target.value })} />
            </div>
            <div>
              <label>Property Value (₹)</label>
              <input type="number" min={0} value={form.property_value} onChange={(e) => setForm({ ...form, property_value: e.target.value })} />
            </div>
          </div>
          
          <div>
            <label>Past Loans / Context</label>
            <input type="text" placeholder="e.g. Paid off 10k car loan in 2022" value={form.past_loans} onChange={(e) => setForm({ ...form, past_loans: e.target.value })} />
          </div>

          <div style={{display: "flex", justifyContent: "flex-end"}}>
            <button type="submit" disabled={saving}>{saving ? "Saving..." : "Save Profile Data"}</button>
          </div>
        </form>
      </div>

      <div className="card">
        <div style={{display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24}}>
          <h3>Investment Holdings</h3>
          <button className="sm" onClick={() => setShowInvForm(!showInvForm)}>+ Add Holding</button>
        </div>

        {showInvForm && (
          <div style={{background: "rgba(128,128,128,0.05)", padding: 24, borderRadius: 16, marginBottom: 24, border: "1px solid var(--panel-border)"}}>
            <form onSubmit={onAddInvestment} className="grid-4" style={{alignItems: "flex-end"}}>
              <div>
                <label>Asset Type</label>
                <select value={invForm.asset_type} onChange={e => setInvForm({...invForm, asset_type: e.target.value})} required>
                  <option value="">Select...</option>
                  <option value="Stock">Stock / Equity</option>
                  <option value="Crypto">Crypto</option>
                  <option value="Mutual Fund">Mutual Fund</option>
                  <option value="Bond">Bond</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div>
                <label>Ticker/Name</label>
                <input type="text" value={invForm.ticker_symbol} onChange={e => setInvForm({...invForm, ticker_symbol: e.target.value})} placeholder="e.g. AAPL" required />
              </div>
              <div>
                <label>Quantity</label>
                <input type="number" step="0.0001" value={invForm.quantity} onChange={e => setInvForm({...invForm, quantity: e.target.value})} required />
              </div>
              <div>
                <label>Avg Buy Price (₹)</label>
                <input type="number" step="0.01" value={invForm.avg_buy_price} onChange={e => setInvForm({...invForm, avg_buy_price: e.target.value})} required />
              </div>
              <div>
                <label>Current Value (₹)</label>
                <input type="number" step="0.01" value={invForm.current_value} onChange={e => setInvForm({...invForm, current_value: e.target.value})} required />
              </div>
              <button type="submit" className="sm" style={{marginBottom: 24}}>Save</button>
            </form>
          </div>
        )}

        {investments.length === 0 ? (
          <p className="muted">No investments recorded yet.</p>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Asset</th>
                  <th>Ticker</th>
                  <th>Qty</th>
                  <th>Avg Cost</th>
                  <th>Total Invested</th>
                  <th>Current Value</th>
                  <th>Return</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {investments.map(inv => (
                  <tr key={inv.id}>
                    <td>{inv.asset_type}</td>
                    <td><strong>{inv.ticker_symbol}</strong></td>
                    <td>{inv.quantity}</td>
                    <td>₹{inv.avg_buy_price.toLocaleString()}</td>
                    <td>₹{inv.amount.toLocaleString()}</td>
                    <td>₹{inv.current_value.toLocaleString()}</td>
                    <td>
                      <span className={`badge ${inv.avg_return_pct >= 0 ? "success" : "danger"}`}>
                        {inv.avg_return_pct >= 0 ? "+" : ""}{inv.avg_return_pct.toFixed(2)}%
                      </span>
                    </td>
                    <td>
                      <button className="danger sm" onClick={() => onDeleteInvestment(inv.id)}>Del</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
