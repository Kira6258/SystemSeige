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
      <Nav />
      <div className="container">
        <h1>Board of Directors Chat</h1>
        <p className="muted">Debt · Savings · Investment · Insurance · Tax · Legal/Compliance — one question, six perspectives.</p>

        {error && <div className="error">{error}</div>}

        {responses.map((r) => (
          <div className="card" key={r.id}>
            {r.advisors.map((a, i) => (
              <div className="advisor" key={i}>
                <strong>{a.role}</strong> <span className="muted">({(a.confidence * 100).toFixed(0)}% confidence)</span>
                <p>{a.advice}</p>
              </div>
            ))}
          </div>
        ))}
        <div ref={bottomRef} />

        <form onSubmit={onSend} className="card">
          <label>Ask the board</label>
          <textarea
            rows={3}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            maxLength={4000}
            placeholder="e.g. How should I prioritize paying off debt vs. building savings?"
          />
          <button type="submit" disabled={sending}>{sending ? "Consulting the board..." : "Send"}</button>
        </form>
      </div>
    </>
  );
}
