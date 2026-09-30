# DECISIONS

**Date:** 2026-09-30

This document records all decisions made during the build. Each decision is one line.

---

## Phase 0 Decisions

1. **COMMERCIAL_MODE = true** (default) — Fred Jehle database (CC BY-NC-SA 3.0) is blocked from ingestion.
2. **ian-hamlin/verb-data license** — No explicit LICENSE file found; treated as blocked until owner confirms license.
3. **Conjugation priority** — With Fred Jehle blocked, priority becomes: 1. asosab/esp_verbos, 2. ian-hamlin/verb-data (if license confirmed).
4. **es-en.data format** — Wiktionary dump format with `_____` separators; parser must handle `pos:`, `gloss:`, `meta:`, `q:`, `etymology:` fields.
5. **sentences.tsv** — Tatoeba sentences with CC BY 2.0 license; acceptable for commercial use. Columns: EN, ES, license, word_count, es_word_count, tags.
6. **frequency.csv** — Columns: count, spanish, pos, flags, usage. The `usage` column contains pipe-separated inflected forms with counts.
7. **unimorph/spa format** — TSV with columns: lemma, form, tags. Tags follow UniMorph format (e.g., `V;IND;PRS;1;SG`).
8. **spanish-conjugator** — Used as build-time rule engine only. MIT license. Computes regular paradigms and detects irregularities.
