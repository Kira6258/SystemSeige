"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Nav from "@/components/Nav";
import { api, ApiError } from "@/lib/api";
import type { LoanListItem } from "@/lib/types";

export default function LoansPage() {
  const router = useRouter();
  const [loans, setLoans] = useState<LoanListItem[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  function loadLoans() {
    api
      .get<LoanListItem[]>("/api/loans")
      .then(setLoans)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) router.replace("/login");
      });
  }

  useEffect(loadLoans, [router]);

  async function onUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setError("");
    setUploading(true);
    try {
      const analysis = await api.upload<{ id: string }>("/api/loans/analyze", file);
      router.push(`/loans/${analysis.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Analysis failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <>
      <div className="container">
        <h1>Predatory Loan Scanner</h1>

        <div className="card">
          <h3>Upload a loan document</h3>
          <p className="muted">PDF only, up to 5MB. We extract the terms and compute a Fairness Score deterministically from the numbers — never guessed by the AI.</p>
          {error && <div className="error">{error}</div>}
          <form onSubmit={onUpload}>
            <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} />
            <button type="submit" disabled={!file || uploading}>{uploading ? "Analyzing..." : "Analyze Loan"}</button>
          </form>
        </div>

        <div className="card">
          <h3>Your Past Analyses</h3>
          {loans.length === 0 && <p className="muted">No analyses yet.</p>}
          {loans.map((l) => (
            <div key={l.id} className="advisor">
              <Link href={`/loans/${l.id}`}>
                Principal {l.principal.toLocaleString()} — Fairness Score {l.fairness_score}
              </Link>
              <p className="muted">{new Date(l.created_at).toLocaleString()}</p>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
