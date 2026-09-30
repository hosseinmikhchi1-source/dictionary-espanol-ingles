"use client";

import Link from "next/link";

export default function AboutPage() {
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

      <section className="sources-section" style={{ paddingTop: "2rem" }}>
        <h1 style={{ fontSize: "1.75rem", fontWeight: 700, marginBottom: "1rem" }}>About</h1>

        <div style={{ background: "var(--card)", border: "1px solid var(--border)", borderRadius: "10px", padding: "1.5rem", marginBottom: "1rem" }}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>What is Diccionario?</h3>
          <p style={{ color: "var(--ink-light)" }}>
            Diccionario is a bilingual English ↔ Spanish dictionary for learners, translators, and people living in Spanish-speaking countries.
            It features multiple meanings with context, complete verb conjugation, natural example sentences, and pronunciation guides.
          </p>
        </div>

        <div style={{ background: "var(--card)", border: "1px solid var(--border)", borderRadius: "10px", padding: "1.5rem", marginBottom: "1rem" }}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>Features</h3>
          <ul style={{ color: "var(--ink-light)", paddingLeft: "1.25rem" }}>
            <li>Bidirectional search with autocomplete</li>
            <li>Multiple meanings with context, register, and region labels</li>
            <li>Full verb conjugation tables</li>
            <li>Example sentences grouped by sense</li>
            <li>Pronunciation (IPA + audio)</li>
            <li>Word of the Day</li>
            <li>Mobile-first, fast, and privacy-respecting</li>
          </ul>
        </div>

        <div style={{ background: "var(--card)", border: "1px solid var(--border)", borderRadius: "10px", padding: "1.5rem", marginBottom: "1rem" }}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>Privacy</h3>
          <p style={{ color: "var(--ink-light)" }}>
            This dictionary runs entirely on our own servers. No data is sent to third parties.
            No user accounts, no tracking, no ads. Your search history stays on your device.
          </p>
        </div>

        <div style={{ background: "var(--card)", border: "1px solid var(--border)", borderRadius: "10px", padding: "1.5rem" }}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>Technology</h3>
          <p style={{ color: "var(--ink-light)" }}>
            Built with PostgreSQL, FastAPI, Next.js, and Docker. All data is self-hosted.
            No external API calls at runtime.
          </p>
        </div>
      </section>

      <footer className="footer">
        <p>Diccionario — A Spanish to English Dictionary</p>
      </footer>
    </>
  );
}
