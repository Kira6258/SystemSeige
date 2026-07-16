"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";

export default function ExpensesPage() {
  const router = useRouter();
  const [expenses, setExpenses] = useState<any[]>([]);
  const [summary, setSummary] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [form, setForm] = useState({
    amount: "", category: "food", txn_date: new Date().toISOString().split("T")[0], description: ""
  });

  useEffect(() => {
    fetchData();
  }, [router]);

  async function fetchData() {
    try {
      const [exp, sum] = await Promise.all([
        api.get<any[]>("/api/expenses"),
        api.get<any[]>("/api/expenses/summary")
      ]);
      setExpenses(exp);
      setSummary(sum);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) router.replace("/login");
    } finally {
      setLoading(false);
    }
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post("/api/expenses", {
        amount: Number(form.amount),
        category: form.category,
        txn_date: form.txn_date,
        description: form.description
      });
      setForm({ ...form, amount: "", description: "" });
      fetchData(); // Refresh list and summary
    } catch (err) {
      alert("Failed to add expense");
    }
  }

  async function onDelete(id: string) {
    try {
      await api.delete(`/api/expenses/${id}`);
      fetchData();
    } catch (err) {
      alert("Delete failed");
    }
  }

  if (loading) return <div className="container">Loading...</div>;

  return (
    <div className="container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 32 }}>
        <div>
          <h1>Income & Expense Tracker</h1>
          <p className="muted">Track your daily spending and view monthly breakdowns.</p>
        </div>
      </div>

      <div className="grid-2">
        {/* Add Expense Form */}
        <div className="card" style={{height: "fit-content"}}>
          <h3>Log New Expense</h3>
          <form onSubmit={onSubmit} style={{marginTop: 24}}>
            <div className="grid-2">
              <div>
                <label>Amount (₹)</label>
                <input type="number" required min={0.01} step="0.01" value={form.amount} onChange={e => setForm({...form, amount: e.target.value})} />
              </div>
              <div>
                <label>Date</label>
                <input type="date" required value={form.txn_date} onChange={e => setForm({...form, txn_date: e.target.value})} />
              </div>
            </div>
            
            <div>
              <label>Category</label>
              <select value={form.category} onChange={e => setForm({...form, category: e.target.value})} required>
                <option value="emergency">Emergency</option>
                <option value="leisure">Leisure / Entertainment</option>
                <option value="family">Family / Home</option>
                <option value="food">Food / Dining</option>
                <option value="transport">Transportation</option>
                <option value="bills">Bills / Utilities</option>
                <option value="health">Health / Medical</option>
                <option value="education">Education</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label>Description / Note</label>
              <input type="text" value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="e.g. Groceries at Whole Foods" />
            </div>

            <button type="submit" style={{width: "100%"}}>Add Expense</button>
          </form>
        </div>

        {/* Monthly Summary */}
        <div className="card">
          <h3>This Month&apos;s Breakdown</h3>
          
          {summary.length === 0 ? (
            <p className="muted" style={{marginTop: 24}}>No expenses recorded this month.</p>
          ) : (
            <div style={{marginTop: 24, display: "flex", flexDirection: "column", gap: 16}}>
              {summary.map(item => (
                <div key={item.category}>
                  <div style={{display: "flex", justifyContent: "space-between", marginBottom: 8}}>
                    <span style={{textTransform: "capitalize"}}>{item.category}</span>
                    <strong>₹{item.total_amount.toLocaleString()} ({item.percentage}%)</strong>
                  </div>
                  <div className="progress-container">
                    <div 
                      className="progress-bar primary" 
                      style={{width: `${item.percentage}%`}}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Expense List */}
      <div className="card">
        <h3>Recent Transactions</h3>
        {expenses.length === 0 ? (
          <p className="muted" style={{marginTop: 24}}>No expenses found.</p>
        ) : (
          <div className="table-container" style={{marginTop: 24}}>
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Category</th>
                  <th>Description</th>
                  <th>Amount</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {expenses.map(exp => (
                  <tr key={exp.id}>
                    <td>{exp.txn_date}</td>
                    <td><span className="badge neutral">{exp.category}</span></td>
                    <td>{exp.description}</td>
                    <td><strong>₹{exp.amount.toLocaleString()}</strong></td>
                    <td>
                      <button className="danger sm" onClick={() => onDelete(exp.id)}>Del</button>
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
