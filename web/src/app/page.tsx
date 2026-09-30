"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface SearchResult {
  lemma_id: number;
  headword: string;
  lang: string;
  pos: string;
  slug: string;
  preview_gloss: string;
  direction: string;
}

interface WordOfDay {
  date: string;
  word: string;
  pos: string;
  gloss: string;
  verb: string | null;
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [wotd, setWotd] = useState<WordOfDay | null>(null);
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const saved = localStorage.getItem("theme") as "light" | "dark" | null;
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initial = saved || (prefersDark ? "dark" : "light");
    setTheme(initial);
    document.documentElement.setAttribute("data-theme", initial);
  }, []);

  useEffect(() => {
    fetchWordOfDay();
  }, []);

  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      return;
    }
    setLoading(true);
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`/api/v1/suggest?q=${encodeURIComponent(query)}&limit=8`);
        if (res.ok) {
          const data = await res.json();
          setResults(data);
        }
      } catch (e) {
        console.error("Search failed:", e);
      }
      setLoading(false);
    }, 200);
    return () => clearTimeout(timer);
  }, [query]);

  async function fetchWordOfDay() {
    try {
      const res = await fetch("/api/v1/word-of-the-day");
      if (res.ok) {
        const data = await res.json();
        setWotd(data);
      }
    } catch (e) {
      console.error("Failed to fetch word of the day:", e);
    }
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

      <section className="hero">
        <h1>English ↔ Spanish Dictionary</h1>
        <p>Look up words, find translations, and learn with examples.</p>
        <div className="search-container">
          <svg className="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            className="search-box"
            placeholder="Search in English or Spanish..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
      </section>

      {results.length > 0 && (
        <div className="search-results">
          {results.map((r) => (
            <Link key={r.lemma_id} href={`/${r.lang}/${r.slug}`}>
              <div className="result-card">
                <span className="result-word">{r.headword}</span>
                <span className="result-pos">{r.pos}</span>
                <div className="result-gloss">{r.preview_gloss}</div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {loading && <div className="loading">Searching...</div>}

      {wotd && (
        <div className="wotd-card">
          <div className="wotd-inner">
            <div className="wotd-label">Word of the Day</div>
            <div className="wotd-word">{wotd.word}</div>
            <div className="wotd-gloss">{wotd.gloss}</div>
            {wotd.verb && (
              <div style={{ marginTop: "0.5rem", fontSize: "0.85rem", color: "var(--ink-light)" }}>
                Verb of the day: <strong>{wotd.verb}</strong>
              </div>
            )}
          </div>
        </div>
      )}

      <footer className="footer">
        <p>Diccionario — A Spanish to English Dictionary</p>
      </footer>
    </>
  );
}
