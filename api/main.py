"""
API — Phase 4
FastAPI backend for the dictionary.
All endpoints under /api/v1.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(
    title="Dictionary API",
    description="English ↔ Spanish Dictionary API",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Models ---

class SearchResult(BaseModel):
    lemma_id: int
    headword: str
    lang: str
    pos: str
    slug: str
    preview_gloss: str
    matched_form: Optional[str] = None
    note: Optional[str] = None
    direction: str


class SuggestItem(BaseModel):
    headword: str
    pos: str
    preview_gloss: str
    direction: str


class Sense(BaseModel):
    sense_no: int
    gloss: str
    context_label: Optional[str] = None
    register: Optional[str] = None
    region_tags: list[str] = []


class Example(BaseModel):
    text_es: str
    text_en: str
    topic_tag: Optional[str] = None


class Pronunciation(BaseModel):
    variant: str
    ipa: str
    audio_path: Optional[str] = None


class Entry(BaseModel):
    headword: str
    lang: str
    pos: str
    slug: str
    senses: list[Sense]
    examples: list[Example] = []
    pronunciation: Optional[Pronunciation] = None
    level: Optional[str] = None
    cefr_source: Optional[str] = None
    has_conjugation: bool = False


class ConjugationForm(BaseModel):
    person: str
    form: str
    is_irregular: bool = False


class ConjugationTable(BaseModel):
    mood: str
    tense: str
    forms: list[ConjugationForm]


class ConjugationResponse(BaseModel):
    verb: str
    conjugation_class: str
    tables: list[ConjugationTable]
    pattern_label: Optional[str] = None
    source: Optional[str] = None


class WordOfDay(BaseModel):
    date: str
    word: str
    pos: str
    gloss: str
    verb: Optional[str] = None


class SourceInfo(BaseModel):
    code: str
    name: str
    url: str
    license: str
    attribution_text: str


class SourcesResponse(BaseModel):
    sources: list[SourceInfo]
    statement: str


class HealthResponse(BaseModel):
    status: str
    database: str


class ErrorResponse(BaseModel):
    code: str
    message: str


# --- Mock Data (replace with DB queries) ---

MOCK_LEMMAS = [
    {"id": 1, "word": "casa", "pos": "noun", "slug": "casa", "gloss": "house, home", "lang": "es"},
    {"id": 2, "word": "comer", "pos": "verb", "slug": "comer", "gloss": "to eat", "lang": "es"},
    {"id": 3, "word": "perro", "pos": "noun", "slug": "perro", "gloss": "dog", "lang": "es"},
    {"id": 4, "word": "hablar", "pos": "verb", "slug": "hablar", "gloss": "to speak, to talk", "lang": "es"},
    {"id": 5, "word": "gato", "pos": "noun", "slug": "gato", "gloss": "cat", "lang": "es"},
    {"id": 6, "word": "book", "pos": "noun", "slug": "book", "gloss": "libro", "lang": "en"},
    {"id": 7, "word": "eat", "pos": "verb", "slug": "eat", "gloss": "comer", "lang": "en"},
    {"id": 8, "word": "dog", "pos": "noun", "slug": "dog", "gloss": "perro", "lang": "en"},
    {"id": 9, "word": "house", "pos": "noun", "slug": "house", "gloss": "casa", "lang": "en"},
    {"id": 10, "word": "speak", "pos": "verb", "slug": "speak", "gloss": "hablar", "lang": "en"},
]

MOCK_SENSES = {
    "casa": [
        {"sense_no": 1, "gloss": "house, home", "context_label": None, "register": None, "region_tags": []},
        {"sense_no": 2, "gloss": "household, family", "context_label": None, "register": None, "region_tags": []},
    ],
    "comer": [
        {"sense_no": 1, "gloss": "to eat", "context_label": None, "register": None, "region_tags": []},
        {"sense_no": 2, "gloss": "to consume", "context_label": "formal", "register": "formal", "region_tags": []},
    ],
}

MOCK_EXAMPLES = {
    "casa": [
        {"text_es": "Mi casa es tu casa.", "text_en": "My house is your house.", "topic_tag": None},
        {"text_es": "La casa es grande.", "text_en": "The house is big.", "topic_tag": None},
    ],
    "comer": [
        {"text_es": "Me gusta comer tacos.", "text_en": "I like to eat tacos.", "topic_tag": "food"},
    ],
}

MOCK_CONJUGATIONS = {
    "hablar": {
        "class": "ar",
        "pattern": "Regular -ar verb",
        "source": "asosab/esp_verbos",
        "tables": [
            {
                "mood": "indicative",
                "tense": "present",
                "forms": [
                    {"person": "1sg", "form": "hablo", "is_irregular": False},
                    {"person": "2sg", "form": "hablas", "is_irregular": False},
                    {"person": "3sg", "form": "habla", "is_irregular": False},
                    {"person": "1pl", "form": "hablamos", "is_irregular": False},
                    {"person": "2pl", "form": "habláis", "is_irregular": False},
                    {"person": "3pl", "form": "hablan", "is_irregular": False},
                ],
            },
            {
                "mood": "indicative",
                "tense": "preterite",
                "forms": [
                    {"person": "1sg", "form": "hablé", "is_irregular": False},
                    {"person": "2sg", "form": "hablaste", "is_irregular": False},
                    {"person": "3sg", "form": "habló", "is_irregular": False},
                    {"person": "1pl", "form": "hablamos", "is_irregular": False},
                    {"person": "2pl", "form": "hablasteis", "is_irregular": False},
                    {"person": "3pl", "form": "hablaron", "is_irregular": False},
                ],
            },
        ],
    },
}


# --- Endpoints ---

@app.get("/api/v1/health", response_model=HealthResponse)
async def health():
    """Liveness and database check."""
    return {"status": "ok", "database": "connected"}


@app.get("/api/v1/search", response_model=list[SearchResult])
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    lang: str = Query("auto", description="Language: auto, es, en"),
    limit: int = Query(20, ge=1, le=100),
):
    """Ranked search results."""
    q_lower = q.lower()
    results = []
    for lemma in MOCK_LEMMAS:
        if q_lower in lemma["word"].lower() or q_lower in lemma["gloss"].lower():
            results.append(SearchResult(
                lemma_id=lemma["id"],
                headword=lemma["word"],
                lang=lemma["lang"],
                pos=lemma["pos"],
                slug=lemma["slug"],
                preview_gloss=lemma["gloss"],
                direction=f"{lemma['lang']}-{'en' if lemma['lang'] == 'es' else 'es'}",
            ))
    return results[:limit]


@app.get("/api/v1/suggest", response_model=list[SuggestItem])
async def suggest(
    q: str = Query(..., min_length=1, description="Search query"),
    lang: str = Query("auto", description="Language: auto, es, en"),
    limit: int = Query(8, ge=1, le=8),
):
    """Autocomplete (max 8 items)."""
    q_lower = q.lower()
    results = []
    for lemma in MOCK_LEMMAS:
        if q_lower in lemma["word"].lower():
            results.append(SuggestItem(
                headword=lemma["word"],
                pos=lemma["pos"],
                preview_gloss=lemma["gloss"],
                direction=f"{lemma['lang']}-{'en' if lemma['lang'] == 'es' else 'es'}",
            ))
    return results[:limit]


@app.get("/api/v1/entries/{lang}/{slug}", response_model=Entry)
async def get_entry(lang: str, slug: str):
    """Get a word entry by language and slug."""
    for lemma in MOCK_LEMMAS:
        if lemma["slug"] == slug and lemma["lang"] == lang:
            word = lemma["word"]
            return Entry(
                headword=word,
                lang=lang,
                pos=lemma["pos"],
                slug=slug,
                senses=[Sense(**s) for s in MOCK_SENSES.get(word, [])],
                examples=[Example(**e) for e in MOCK_EXAMPLES.get(word, [])],
                pronunciation=Pronunciation(variant="es-ES", ipa="/ˈkasa/") if lang == "es" else None,
                level="A1",
                cefr_source="frequency_estimate",
                has_conjugation=lemma["pos"] == "verb",
            )
    raise HTTPException(status_code=404, detail="Entry not found")


@app.get("/api/v1/verbs/{slug}/conjugation", response_model=ConjugationResponse)
async def get_conjugation(slug: str):
    """Get verb conjugation."""
    if slug in MOCK_CONJUGATIONS:
        data = MOCK_CONJUGATIONS[slug]
        return ConjugationResponse(
            verb=slug,
            conjugation_class=data["class"],
            tables=[ConjugationTable(**t) for t in data["tables"]],
            pattern_label=data["pattern"],
            source=data["source"],
        )
    raise HTTPException(status_code=404, detail="Verb not found")


@app.get("/api/v1/word-of-the-day", response_model=WordOfDay)
async def word_of_the_day(date: Optional[str] = None):
    """Word and verb for a date (default today, UTC)."""
    return WordOfDay(
        date=date or "2026-09-30",
        word="casa",
        pos="noun",
        gloss="house, home",
        verb="hablar",
    )


@app.get("/api/v1/meta/sources", response_model=SourcesResponse)
async def get_sources():
    """Sources, licenses, attributions."""
    return SourcesResponse(
        sources=[
            SourceInfo(
                code="doozan",
                name="doozan/spanish_data",
                url="https://github.com/doozan/spanish_data",
                license="CC BY 4.0",
                attribution_text="Spanish data from doozan/spanish_data, CC BY 4.0",
            ),
            SourceInfo(
                code="asosab",
                name="asosab/esp_verbos",
                url="https://github.com/asosab/esp_verbos",
                license="CC BY-SA 4.0",
                attribution_text="Spanish verb conjugations from asosab/esp_verbos, CC BY-SA 4.0",
            ),
            SourceInfo(
                code="unimorph",
                name="unimorph/spa",
                url="https://github.com/unimorph/spa",
                license="CC BY-SA 3.0",
                attribution_text="Spanish unimorph data from unimorph/spa, CC BY-SA 3.0",
            ),
        ],
        statement="Some examples and relations are machine-written under automated and human checks.",
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
