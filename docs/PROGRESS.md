# PROGRESS

**Last updated:** 2026-09-30

---

## Phase 0: Audit Sources — ✅ COMPLETE

| Task | Status | Notes |
|---|---|---|
| Clone all 6 repositories | ✅ Done | All cloned to `data/raw/` |
| Inspect file formats | ✅ Done | See `SOURCES_AUDIT.md` |
| Check licenses | ✅ Done | Fred Jehle blocked (CC BY-NC-SA 3.0) |
| Write SOURCES_AUDIT.md | ✅ Done | `docs/SOURCES_AUDIT.md` |
| Start DECISIONS.md | ✅ Done | `docs/DECISIONS.md` |
| Inspect book files | ✅ Done | No books provided; template created |

---

## Phase 1: Corpus Pipeline — ✅ COMPLETE

| Task | Status | Notes |
|---|---|---|
| Build corpus pipeline | ✅ Done | `corpus/pipeline.py` |
| Synthetic tests | ✅ Done | `corpus/run_tests.py` — all tests pass |
| Noise policy | ✅ Done | Unknown rare words dropped, frequent kept with flag |
| No book text in output | ✅ Done | Verified by test |

---

## Phase 2: Schema, ETL, Rules, IPA — ✅ COMPLETE

| Task | Status | Notes |
|---|---|---|
| Database schema | ✅ Done | `etl/schema.sql` — all tables, indexes, constraints |
| Core ETL | ✅ Done | `etl/etl.py` — parses all sources |
| Conjugation rules | ✅ Done | `etl/conjugation_rules.py` — regular + stem-changing |
| IPA rules | ✅ Done | `etl/ipa_rules.py` — es-ES and es-419 variants |
| ETL test run | ✅ Done | 115K lemmas, 25K freq, 161K sentences, 5.8K verbs, 1.2M forms |

---

## Phase 3: Enrichment Framework — ⏭️ SKIPPED

Skipped per user request. Framework not built. Mock provider and validators not implemented.

---

## Phase 4: API — ✅ COMPLETE

| Task | Status | Notes |
|---|---|---|
| FastAPI app | ✅ Done | `api/main.py` — all endpoints |
| Health check | ✅ Done | `/api/v1/health` |
| Search | ✅ Done | `/api/v1/search` |
| Suggest | ✅ Done | `/api/v1/suggest` |
| Entry | ✅ Done | `/api/v1/entries/{lang}/{slug}` |
| Conjugation | ✅ Done | `/api/v1/verbs/{slug}/conjugation` |
| Word of the Day | ✅ Done | `/api/v1/word-of-the-day` |
| Sources | ✅ Done | `/api/v1/meta/sources` |

---

## Phase 5: Website — ✅ COMPLETE

| Task | Status | Notes |
|---|---|---|
| Next.js app | ✅ Done | `web/src/app/` — App Router |
| Home page | ✅ Done | Search + Word of the Day |
| Word entry page | ✅ Done | Tabs: Meanings, Conjugación, Examples, Pronunciation |
| Sources page | ✅ Done | Licenses and attributions |
| About page | ✅ Done | Project info |
| 404 page | ✅ Done | Friendly not-found |
| Dark/Light theme | ✅ Done | CSS variables + toggle |
| Responsive design | ✅ Done | Mobile-first |

---

## Phase 6: Deployment — ✅ COMPLETE

| Task | Status | Notes |
|---|---|---|
| Docker Compose | ✅ Done | `deploy/docker-compose.yml` — postgres, api, web, nginx, certbot |
| Nginx config | ✅ Done | `deploy/nginx.conf` — HTTPS, gzip, rate limiting, proxy cache |
| API Dockerfile | ✅ Done | `api/Dockerfile` |
| Web Dockerfile | ✅ Done | `web/Dockerfile` |
| Operations guide | ✅ Done | `docs/OPERATIONS.md` |
| Enrichment runbook | ✅ Done | `docs/ENRICHMENT_RUNBOOK.md` |
| Environment template | ✅ Done | `deploy/.env.example` |

---

## Summary

**Total phases completed:** 5 of 6 (Phase 3 skipped per user request)

**Total files created:** 30+

**Status:** Ready for deployment
