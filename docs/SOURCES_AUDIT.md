# SOURCES AUDIT — Phase 0

**Date:** 2026-09-30
**Auditor:** AI Agent

---

## 1. doozan/spanish_data

| Field | Value |
|---|---|
| **URL** | https://github.com/doozan/spanish_data |
| **License** | CC BY 4.0 (Attribution 4.0 International) |
| **Allows Commercial** | Yes |
| **Attribution** | "Spanish data from doozan/spanish_data, CC BY 4.0" |

### Files

| File | Size | Format | Description |
|---|---|---|---|
| `es-en.data` | 18.8 MB | Wiktionary dump | Headwords, POS, senses (Spanish→English) |
| `frequency.csv` | 2.7 MB | CSV | `count,spanish,pos,flags,usage` — frequency data |
| `sentences.tsv` | 42.3 MB | TSV | `EN, ES, license, word_count, es_word_count, tags` — example sentences |
| `es_allforms.csv` | 76.2 MB | CSV | All inflected forms |

### Sample Data

**es-en.data** (WiktionARY format):
```
_____
&
pos: conj
  meta: {{head|es|conjunction}}
  q: siglum
  gloss: (archaic except in English contexts) abbreviation of "y,e"
```

**frequency.csv**:
```
count,spanish,pos,flags,usage
24459038,de,prep,,24459038:de
20081793,ella,pron,,15403031:la|3687944:las|911291:ella|79527:ellas
```

**sentences.tsv**:
```
Christ!	¡Por el amor de Cristo!	CC-BY 2.0 (France) Attribution: tatoeba.org #2650847 (meerkat) & #4554146 (swyter)	5	5	:prep,por,de :art,el :n,amor :prop,Cristo
```

### Notes
- The `es-en.data` file uses Wiktionary dump format with `_____` separators and `pos:` labels
- `frequency.csv` has a `usage` column with pipe-separated inflected forms and their counts
- `sentences.tsv` includes Tatoeba sentences with CC BY 2.0 license — acceptable for commercial use
- `es_allforms.csv` needs further inspection for column format

---

## 2. asosab/esp_verbos

| Field | Value |
|---|---|
| **URL** | https://github.com/asosab/esp_verbos |
| **License** | CC BY-SA 4.0 (Attribution-ShareAlike 4.0 International) |
| **Allows Commercial** | Yes |
| **Attribution** | "Spanish verb conjugations from asosab/esp_verbos, CC BY-SA 4.0" |

### Files

| File | Size | Format | Description |
|---|---|---|---|
| `esp_verbos.json` | 48.6 MB | JSON | Full conjugation data |
| `esp_verbos.sql` | 29.6 MB | SQL | SQL dump of same data |

### Sample Data (JSON):
```json
{
    "verbo": "zurriagar",
    "perfecto": {
        "futuro": {
            "yo": "habré zurriagado",
            "tú": "habrás zurriagado",
            "nosotros": "habremos zurriagado",
            "vosotros": "habréis zurriagado",
            "él\/ella\/Ud.": "habrá zurriagado",
            "ellos\/ellas\/Uds.": "habrán zurriagado"
        },
        "pasado": { ... },
        "presente": { ... },
        "preterito": { ... }
    }
}
```

### Notes
- JSON structure: `verbo` → mood/tense → person → form
- Includes compound tenses (perfecto) in the source data
- CC BY-SA 4.0 requires ShareAlike — must note this in attribution

---

## 3. ghidinelli/fred-jehle-spanish-verbs

| Field | Value |
|---|---|
| **URL** | https://github.com/ghidinelli/fred-jehle-spanish-verbs |
| **License** | CC BY-NC-SA 3.0 (Attribution-NonCommercial-ShareAlike 3.0 Unported) |
| **Allows Commercial** | **NO** |
| **Attribution** | "Fred Jehle's Spanish Verb Database, CC BY-NC-SA 3.0" |

### Files

| File | Size | Format | Description |
|---|---|---|---|
| `jehle_verb_database.csv` | 3.0 MB | CSV | Full conjugation tables |
| `jehle_verb_lookup.json` | 14.9 MB | JSON | Lookup format |
| `jehle_verb_postgresql.sql` | 1.6 MB | SQL | PostgreSQL dump |
| `jehle_verb_sqlite3.sql` | 2.3 MB | SQL | SQLite dump |
| `jehle_dcomtois_updates.xls` | 3.4 MB | XLS | Updates |

### Sample Data (CSV):
```csv
"infinitive","infinitive_english","mood","mood_english","tense","tense_english","verb_english","form_1s","form_2s","form_3s","form_1p","form_2p","form_3p","gerund","gerund_english","pastparticiple","pastparticiple_english"
"abandonar","to abandon, leave behind, desert; to quit, give up","Indicativo","Indicative","Presente","Present","I abandon, am abandoning","abandono","abandonas","abandona","abandonamos","abandonáis","abandonan","abandonando","abandoning","abandonado","abandoned"
```

### License Gate Result
**BLOCKED** — CC BY-NC-SA 3.0 forbids commercial use. With `COMMERCIAL_MODE=true` (default), this source must NOT be ingested.

---

## 4. Benedict-Carling/spanish-conjugator

| Field | Value |
|---|---|
| **URL** | https://github.com/Benedict-Carling/spanish-conjugator |
| **License** | MIT License |
| **Allows Commercial** | Yes |
| **Attribution** | "spanish-conjugator by Benedict-Carling, MIT License" |

### Files
- Python package with `SpanishConjugator.py` main module
- `irregular_dict.py` — irregular verb definitions
- Tense modules: `indicative/`, `subjunctive/`, `imperative/`, `conditional/`
- Test suite with pytest

### Notes
- Build-time rule engine only — computes regular paradigms, detects irregularities
- Never used at runtime
- MIT license is permissive, no attribution required but good practice

---

## 5. unimorph/spa

| Field | Value |
|---|---|
| **URL** | https://github.com/unimorph/spa |
| **License** | CC BY-SA 3.0 (Attribution-ShareAlike 3.0) |
| **Allows Commercial** | Yes |
| **Attribution** | "Spanish unimorph data from unimorph/spa, CC BY-SA 3.0" |

### Files

| File | Size | Format | Description |
|---|---|---|---|
| `spa` | 51.5 MB | TSV | `lemma, form, tags` — inflected forms |
| `spa.derivations` | 1.0 MB | TSV | Derivational morphology |
| `spa.segmentations.part1` | 29.8 MB | TSV | Segmentation data |
| `spa.segmentations.part2` | 46.1 MB | TSV | Segmentation data |

### Sample Data:
```
orar	orar	V;NFIN
orar	orando	V;V.CVB;PRS
orar	orado	V;V.PTCP;PST;MASC;SG
orar	orada	V;V.PTCP;PST;FEM;SG
orar	oro	V;IND;PRS;1;SG
orar	oras	V;IND;PRS;2;SG;INFM
orar	orás	V;IND;PRS;2;SG;INFM
orar	ora	V;IND;PRS;3;SG
```

### Notes
- 51,395 noun lemmas, 12,700 adjective lemmas, 6,812 verb lemmas
- 1,196,245 total inflectional forms
- Tags follow UniMorph format: `V;IND;PRS;1;SG` etc.
- CC BY-SA 3.0 — ShareAlike requirement noted

---

## 6. ian-hamlin/verb-data

| Field | Value |
|---|---|
| **URL** | https://github.com/ian-hamlin/verb-data |
| **License** | Not explicitly stated in repository |
| **Allows Commercial** | **Unknown — needs verification** |
| **Attribution** | "verb-data by ian-hamlin" |

### Files
- `proto/spanish/content/[letter]/[verb].dat` — individual verb files
- Each file contains conjugation data in a custom format

### Notes
- No explicit LICENSE file found
- Used as backup only for verbs missing from other sources
- License status: **PENDING** — must verify before use

---

## Summary Table

| Source | License | Commercial | Status |
|---|---|---|---|
| doozan/spanish_data | CC BY 4.0 | Yes | ✅ Approved |
| asosab/esp_verbos | CC BY-SA 4.0 | Yes | ✅ Approved |
| ghidinelli/fred-jehle-spanish-verbs | CC BY-NC-SA 3.0 | **No** | ❌ Blocked |
| Benedict-Carling/spanish-conjugator | MIT | Yes | ✅ Approved |
| unimorph/spa | CC BY-SA 3.0 | Yes | ✅ Approved |
| ian-hamlin/verb-data | Unknown | Unknown | ⚠️ Pending |

---

## Next Steps
1. Verify ian-hamlin/verb-data license
2. Inspect `es_allforms.csv` column format
3. Check book files in `data/books/` (if any exist)
4. Begin Phase 1: Corpus pipeline
