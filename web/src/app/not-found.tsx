"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

export default function NotFound() {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const saved = localStorage.getItem("theme") as "light" | "dark" | null;
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initial = saved || (prefersDark ? "dark" : "light");
    setTheme(initial);
    document.documentElement.setAttribute("data-theme", initial);
  }, []);

  function toggleTheme() {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
  }

  return (
    <>
      <header className="header">
        <div className="header-inner">
          <Link href="/" className="logo">
            <span className="logo-icon">D</span>
            Diccionario
          </Link>
          <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === "light" ? "🌙" : "☀️"}
          </button>
        </div>
      </header>

      <div style={{ textAlign: "center", padding: "4rem 1rem" }}>
        <h1 style={{ fontSize: "4rem", fontWeight: 700, color: "var(--spanish)" }}>404</h1>
        <p style={{ color: "var(--ink-light)", margin: "1rem 0" }}>
          Word not found. Try searching for something else.
        </p>
        <Link
          href="/"
          style={{
            display: "inline-block",
            padding: "0.75rem 1.5rem",
            background: "var(--ink)",
            color: "var(--card)",
            borderRadius: "8px",
            fontWeight: 600,
          }}
        >
          Go back home
        </Link>
      </div>

      <footer className="footer">
        <p>Diccionario — A Spanish to English Dictionary</p>
      </footer>
    </>
  );
}
