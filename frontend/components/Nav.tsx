"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function Nav() {
  const router = useRouter();

  async function logout() {
    await api.post("/api/auth/logout");
    router.push("/login");
  }

  return (
    <nav className="topnav">
      <div>
        <Link href="/dashboard"><strong>ClearFinance</strong></Link>
        <Link href="/dashboard">Dashboard</Link>
        <Link href="/loans">Loan Scanner</Link>
        <Link href="/chat">Board Chat</Link>
      </div>
      <button className="secondary" onClick={logout}>Log out</button>
    </nav>
  );
}
