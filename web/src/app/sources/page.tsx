"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface SourceInfo {
  code: string;
  name: string;
  url: string;
  license: string;
  attribution_text: string;
}

interface SourcesResponse {
  sources: SourceInfo[];
  statement: string;
}

export default function SourcesPage() {
  const [sources, setSources] = useState<SourcesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const saved = localStorage.getItem("theme") as "light" | "dark" | null;
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initial = saved || (prefersDark ? "dark" : "light");
    setTheme(initial);
    document.documentElement.setAttribute("data-theme", initial);
  }, []);

  useEffect(() => {
    fetchSources();
  }, []);

  async function fetchSources() {
    try {
      const res = await fetch("/api/v1/meta/sources");
      if (res.ok) {
        const data = await res.json();
        setSources(data);
      }
    } catch (e) {
      console.error("Failed to fetch sources:", e);
    }
    setLoading(false);
  }

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

      <section className="sources-section" style={{ paddingTop: "2rem" }}>
        <h1 style={{ fontSize: "1.75rem", fontWeight: 700, marginBottom: "1rem" }}>Sources & Licenses</h1>
        <p style={{ color: "var(--ink-light)", marginBottom: "1.5rem" }}>
          This dictionary is built from open-source data. We respect all licenses and provide attribution below.
        </p>

        {loading && <div className="loading">Loading...</div>}

        {sources && (
          <>
            {sources.sources.map((source) => (
              <div key={source.code} className="source-item">
                <div className="source-name">{source.name}</div>
                <div className="source-license">License: {source.license}</div>
                <div className="source-attribution">{source.attribution_text}</div>
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: "var(--english)", fontSize: "0.85rem", marginTop: "0.25rem", display: "inline-block" }}
                >
                  View source →
                </a>
              </div>
            ))}

            <div style={{ marginTop: "2rem", padding: "1rem", background: "var(--card)", border: "1px solid var(--border)", borderRadius: "10px" }}>
              <h3 style={{ fontSize: "1rem", marginBottom: "0.5rem" }}>Machine-Written Content</h3>
              <p style={{ color: "var(--ink-light)", fontSize: "0.9rem" }}>
                {sources.statement}
              </p>
            </div>
          </>
        )}
      </section>

      <footer className="footer">
        <p>Diccionario — A Spanish to English Dictionary</p>
      </footer>
    </>
  );
}
