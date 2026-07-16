"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.post("/api/auth/login", { email, password });
      router.push("/dashboard");
    } catch (err) {
      // Backend already returns a generic message — surfaced as-is, no enumeration hints.
      setError(err instanceof ApiError ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container" style={{ maxWidth: 420 }}>
      <div className="card">
        <h1>Log in to ClearFinance</h1>
        {error && <div className="error">{error}</div>}
        <form onSubmit={onSubmit}>
          <label>Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required maxLength={255} />
          <label>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required maxLength={128} />
          <button type="submit" disabled={loading}>{loading ? "Logging in..." : "Log in"}</button>
        </form>
        <p className="muted" style={{ marginTop: 16 }}>
          No account? <Link href="/register">Register</Link>
        </p>
      </div>
    </div>
  );
}
