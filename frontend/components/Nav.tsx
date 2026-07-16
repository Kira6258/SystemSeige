"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useTheme } from "./ThemeProvider";

export default function Nav({ children }: { children?: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { theme, toggleTheme } = useTheme();
  const [email, setEmail] = useState("");

  useEffect(() => {
    // Only fetch if not on auth pages
    if (pathname !== "/login" && pathname !== "/register") {
      api.get<{email: string}>("/api/auth/me")
        .then(res => setEmail(res.email))
        .catch(() => {});
    }
  }, [pathname]);

  async function logout() {
    await api.post("/api/auth/logout");
    router.push("/login");
  }

  // Hide nav on login/register pages
  if (pathname === "/login" || pathname === "/register") {
    return <div className="app-shell">{children}</div>;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="avatar">CF</div>
          <h2>ClearFinance</h2>
        </div>

        <nav className="nav-links">
          <Link href="/dashboard" className={`nav-link ${pathname === "/dashboard" ? "active" : ""}`}>
            📊 Dashboard
          </Link>
          <Link href="/profile" className={`nav-link ${pathname === "/profile" ? "active" : ""}`}>
            👤 Financial Profile
          </Link>
          <Link href="/expenses" className={`nav-link ${pathname === "/expenses" ? "active" : ""}`}>
            💸 Expense Tracker
          </Link>
          <Link href="/goals" className={`nav-link ${pathname === "/goals" || pathname.startsWith("/goals/") ? "active" : ""}`}>
            🎯 Financial Goals
          </Link>
          <Link href="/loans" className={`nav-link ${pathname === "/loans" || pathname.startsWith("/loans/") ? "active" : ""}`}>
            📄 Loan Scanner
          </Link>
          <Link href="/loan-finder" className={`nav-link ${pathname === "/loan-finder" ? "active" : ""}`}>
            🏦 Loan Finder
          </Link>
          <Link href="/chat" className={`nav-link ${pathname === "/chat" ? "active" : ""}`}>
            💬 Board Chat
          </Link>
        </nav>

        <div className="sidebar-footer">
          <button className="theme-toggle-btn" onClick={toggleTheme}>
            {theme === "dark" ? "☀️ Light Mode" : "🌙 Dark Mode"}
          </button>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="user-profile-sm">
              <div className="avatar" style={{width: 32, height: 32, fontSize: '0.8rem'}}>
                {email ? email.substring(0, 2).toUpperCase() : "U"}
              </div>
              <div style={{fontSize: '0.8rem', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '120px'}} className="muted">
                {email || "Loading..."}
              </div>
            </div>
            <button className="danger sm" onClick={logout}>Log out</button>
          </div>
        </div>
      </aside>
      
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
