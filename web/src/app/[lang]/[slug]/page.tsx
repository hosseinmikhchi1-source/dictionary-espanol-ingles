"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

interface Sense {
  sense_no: number;
  gloss: string;
  context_label: string | null;
  register: string | null;
  region_tags: string[];
}

interface Example {
  text_es: string;
  text_en: string;
  topic_tag: string | null;
}

interface Pronunciation {
  variant: string;
  ipa: string;
  audio_path: string | null;
}

interface Entry {
  headword: string;
  lang: string;
  pos: string;
  slug: string;
  senses: Sense[];
  examples: Example[];
  pronunciation: Pronunciation | null;
  level: string | null;
  cefr_source: string | null;
  has_conjugation: boolean;
}

interface ConjugationForm {
  person: string;
  form: string;
  is_irregular: boolean;
}

interface ConjugationTable {
  mood: string;
  tense: string;
  forms: ConjugationForm[];
}

interface ConjugationResponse {
  verb: string;
  conjugation_class: string;
  tables: ConjugationTable[];
  pattern_label: string | null;
  source: string | null;
}

export default function WordPage() {
  const params = useParams();
  const lang = params.lang as string;
  const slug = params.slug as string;

  const [entry, setEntry] = useState<Entry | null>(null);
  const [conjugation, setConjugation] = useState<ConjugationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"meanings" | "conjugation" | "examples" | "pronunciation">("meanings");
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const saved = localStorage.getItem("theme") as "light" | "dark" | null;
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initial = saved || (prefersDark ? "dark" : "light");
    setTheme(initial);
    document.documentElement.setAttribute("data-theme", initial);
  }, []);

  useEffect(() => {
    fetchEntry();
  }, [lang, slug]);

  async function fetchEntry() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/v1/entries/${lang}/${slug}`);
      if (!res.ok) throw new Error("Entry not found");
      const data = await res.json();
      setEntry(data);

      if (data.has_conjugation) {
        fetchConjugation(slug);
      }
    } catch (e) {
      setError("Word not found. Try searching for something else.");
    }
    setLoading(false);
  }

  async function fetchConjugation(verbSlug: string) {
    try {
      const res = await fetch(`/api/v1/verbs/${verbSlug}/conjugation`);
      if (res.ok) {
        const data = await res.json();
        setConjugation(data);
      }
    } catch (e) {
      console.error("Failed to fetch conjugation:", e);
    }
  }

  function toggleTheme() {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
  }

  if (loading) {
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
        <div className="loading">Loading...</div>
      </>
    );
  }

  if (error || !entry) {
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
        <div className="error">
          <p>{error}</p>
          <Link href="/" style={{ color: "var(--spanish)" }}>Go back home</Link>
        </div>
      </>
    );
  }

  const tabs = [
    { id: "meanings", label: "Meanings", show: entry.senses.length > 0 },
    { id: "conjugation", label: "Conjugación", show: entry.has_conjugation },
    { id: "examples", label: "Examples", show: entry.examples.length > 0 },
    { id: "pronunciation", label: "Pronunciation", show: entry.pronunciation !== null },
  ].filter(t => t.show);

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

      <div className="entry-header">
        <div className="entry-word">{entry.headword}</div>
        <span className="entry-pos">{entry.pos}</span>
        {entry.pronunciation && (
          <div className="entry-ipa">{entry.pronunciation.ipa}</div>
        )}
        {entry.level && (
          <span className="entry-level">
            Level {entry.level} {entry.cefr_source === "frequency_estimate" && "(estimated)"}
          </span>
        )}
      </div>

      <div style={{ maxWidth: "800px", margin: "0 auto", padding: "0 1rem 1rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as typeof activeTab)}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "8px",
              fontSize: "0.85rem",
              fontWeight: 600,
              background: activeTab === tab.id ? "var(--ink)" : "var(--card)",
              color: activeTab === tab.id ? "var(--card)" : "var(--ink)",
              border: "1px solid var(--border)",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "meanings" && (
        <section className="senses-section">
          <h2 className="senses-title">Meanings</h2>
          {entry.senses.map((sense) => (
            <div key={sense.sense_no} className="sense-item">
              <span className="sense-number">{sense.sense_no}.</span>
              <span className="sense-gloss">{sense.gloss}</span>
              {sense.context_label && (
                <div className="sense-context">Context: {sense.context_label}</div>
              )}
              {sense.register && (
                <div className="sense-context">Register: {sense.register}</div>
              )}
            </div>
          ))}
        </section>
      )}

      {activeTab === "conjugation" && conjugation && (
        <section className="conjugation-section">
          <h2 className="senses-title">Conjugación</h2>
          <p style={{ marginBottom: "1rem", color: "var(--ink-light)" }}>
            {conjugation.pattern_label} • Source: {conjugation.source}
          </p>
          {conjugation.tables.map((table, i) => (
            <div key={i} style={{ marginBottom: "1.5rem" }}>
              <h3 style={{ fontSize: "1rem", marginBottom: "0.5rem" }}>
                {table.mood} — {table.tense}
              </h3>
              <table className="conjugation-table">
                <thead>
                  <tr>
                    <th>Person</th>
                    <th>Form</th>
                  </tr>
                </thead>
                <tbody>
                  {table.forms.map((f, j) => (
                    <tr key={j}>
                      <td>{f.person}</td>
                      <td className={f.is_irregular ? "irregular" : ""}>{f.form}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </section>
      )}

      {activeTab === "examples" && (
        <section className="examples-section">
          <h2 className="senses-title">Examples</h2>
          {entry.examples.map((ex, i) => (
            <div key={i} className="example-item">
              <div className="example-es">{ex.text_es}</div>
              <div className="example-en">{ex.text_en}</div>
            </div>
          ))}
        </section>
      )}

      {activeTab === "pronunciation" && entry.pronunciation && (
        <section className="senses-section">
          <h2 className="senses-title">Pronunciation</h2>
          <div className="sense-item">
            <div><strong>Variant:</strong> {entry.pronunciation.variant}</div>
            <div><strong>IPA:</strong> {entry.pronunciation.ipa}</div>
            {entry.pronunciation.audio_path && (
              <div style={{ marginTop: "0.5rem" }}>
                <audio controls src={entry.pronunciation.audio_path}>
                  Your browser does not support the audio element.
                </audio>
              </div>
            )}
          </div>
        </section>
      )}

      <footer className="footer">
        <p>Diccionario — A Spanish to English Dictionary</p>
      </footer>
    </>
  );
}
