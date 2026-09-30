-- Database Schema — Phase 2
-- PostgreSQL 16 with unaccent and pg_trgm extensions

CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Sources table
CREATE TABLE sources (
    id BIGSERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    url TEXT,
    license TEXT NOT NULL,
    allows_commercial BOOLEAN NOT NULL DEFAULT false,
    attribution_text TEXT,
    version_or_commit TEXT,
    ingested_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enrichment runs
CREATE TABLE enrichment_runs (
    id BIGSERIAL PRIMARY KEY,
    run_uid TEXT UNIQUE NOT NULL,
    task TEXT NOT NULL,
    model_name TEXT NOT NULL,
    model_params JSONB,
    prompt_version TEXT NOT NULL,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    items_total INTEGER DEFAULT 0,
    items_ok INTEGER DEFAULT 0,
    items_failed INTEGER DEFAULT 0,
    notes TEXT
);

-- Lemmas table
CREATE TABLE lemmas (
    id BIGSERIAL PRIMARY KEY,
    lang TEXT NOT NULL CHECK (lang IN ('es', 'en')),
    lemma TEXT NOT NULL,
    lemma_key TEXT NOT NULL,
    search_key TEXT NOT NULL,
    pos TEXT NOT NULL,
    gender TEXT CHECK (gender IN ('m', 'f', 'm/f', NULL)),
    frequency_rank INTEGER,
    frequency_band TEXT,
    cefr_level TEXT CHECK (cefr_level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2', NULL)),
    cefr_source TEXT CHECK (cefr_source IN ('books', 'frequency_estimate', NULL)),
    slug TEXT NOT NULL,
    is_reflexive_only BOOLEAN DEFAULT false,
    UNIQUE (lang, lemma_key, pos)
);

-- Corpus lexicon (internal, never exposed)
CREATE TABLE corpus_lexicon (
    id BIGSERIAL PRIMARY KEY,
    lemma_key TEXT NOT NULL,
    pos_guess TEXT,
    total_count INTEGER DEFAULT 0,
    book_count INTEGER DEFAULT 0,
    min_level TEXT DEFAULT 'unknown',
    known_in_lexicons BOOLEAN DEFAULT false
);

-- Senses table
CREATE TABLE senses (
    id BIGSERIAL PRIMARY KEY,
    lemma_id BIGINT NOT NULL REFERENCES lemmas(id) ON DELETE CASCADE,
    sense_no INTEGER NOT NULL,
    gloss TEXT NOT NULL,
    context_label TEXT,
    register TEXT CHECK (register IN ('formal', 'informal', 'slang', 'literary', 'vulgar', 'dated', NULL)),
    region_tags TEXT[],
    definition_note TEXT,
    sense_hash TEXT NOT NULL,
    content_origin TEXT NOT NULL DEFAULT 'repo' CHECK (content_origin IN ('repo', 'rule', 'curated', 'ai')),
    review_status TEXT NOT NULL DEFAULT 'approved' CHECK (review_status IN ('pending', 'auto_passed', 'approved', 'rejected')),
    run_id BIGINT REFERENCES enrichment_runs(id),
    item_key TEXT UNIQUE NOT NULL,
    source_id BIGINT REFERENCES sources(id),
    UNIQUE (lemma_id, sense_no)
);

-- Sense translations
CREATE TABLE sense_translations (
    id BIGSERIAL PRIMARY KEY,
    sense_id BIGINT NOT NULL REFERENCES senses(id) ON DELETE CASCADE,
    target_lang TEXT NOT NULL,
    term TEXT NOT NULL,
    term_key TEXT NOT NULL,
    search_key TEXT NOT NULL,
    position INTEGER NOT NULL DEFAULT 1,
    is_primary BOOLEAN DEFAULT false
);

-- Examples table
CREATE TABLE examples (
    id BIGSERIAL PRIMARY KEY,
    lemma_id BIGINT NOT NULL REFERENCES lemmas(id) ON DELETE CASCADE,
    sense_id BIGINT REFERENCES senses(id),
    text_es TEXT NOT NULL,
    text_en TEXT NOT NULL,
    topic_tag TEXT,
    level_target TEXT,
    length_chars INTEGER,
    content_origin TEXT NOT NULL DEFAULT 'repo' CHECK (content_origin IN ('repo', 'rule', 'curated', 'ai')),
    review_status TEXT NOT NULL DEFAULT 'approved' CHECK (review_status IN ('pending', 'auto_passed', 'approved', 'rejected')),
    run_id BIGINT REFERENCES enrichment_runs(id),
    item_key TEXT UNIQUE NOT NULL,
    source_id BIGINT REFERENCES sources(id),
    UNIQUE (text_es, text_en)
);

-- Verbs table
CREATE TABLE verbs (
    id BIGSERIAL PRIMARY KEY,
    lemma_id BIGINT UNIQUE NOT NULL REFERENCES lemmas(id) ON DELETE CASCADE,
    conjugation_class TEXT CHECK (conjugation_class IN ('ar', 'er', 'ir')),
    is_reflexive BOOLEAN DEFAULT false,
    auxiliary BOOLEAN DEFAULT false,
    irregularity_signature TEXT,
    irregularity_pattern_label TEXT,
    conjugation_source TEXT
);

-- Conjugations table
CREATE TABLE conjugations (
    id BIGSERIAL PRIMARY KEY,
    verb_id BIGINT NOT NULL REFERENCES verbs(id) ON DELETE CASCADE,
    mood TEXT NOT NULL,
    tense TEXT NOT NULL,
    person TEXT NOT NULL,
    form TEXT NOT NULL,
    is_irregular BOOLEAN DEFAULT false,
    alt_form TEXT,
    source_id BIGINT REFERENCES sources(id),
    UNIQUE (verb_id, mood, tense, person)
);

-- Word forms table
CREATE TABLE word_forms (
    id BIGSERIAL PRIMARY KEY,
    form TEXT NOT NULL,
    form_key TEXT NOT NULL,
    search_key TEXT NOT NULL,
    lemma_id BIGINT NOT NULL REFERENCES lemmas(id) ON DELETE CASCADE,
    pos TEXT,
    tense_or_tags TEXT,
    is_verb_form BOOLEAN DEFAULT false
);

-- Pronunciations table
CREATE TABLE pronunciations (
    id BIGSERIAL PRIMARY KEY,
    lemma_id BIGINT NOT NULL REFERENCES lemmas(id) ON DELETE CASCADE,
    variant TEXT NOT NULL CHECK (variant IN ('es-ES', 'es-419')),
    ipa TEXT NOT NULL,
    ipa_source TEXT NOT NULL CHECK (ipa_source IN ('source', 'rules')),
    audio_path TEXT,
    audio_duration_ms INTEGER,
    audio_provider TEXT
);

-- Related table
CREATE TABLE related (
    id BIGSERIAL PRIMARY KEY,
    lemma_id BIGINT NOT NULL REFERENCES lemmas(id) ON DELETE CASCADE,
    related_lemma_id BIGINT NOT NULL REFERENCES lemmas(id) ON DELETE CASCADE,
    relation TEXT NOT NULL CHECK (relation IN ('similar_verb', 'synonym', 'antonym')),
    rank INTEGER DEFAULT 1,
    content_origin TEXT NOT NULL DEFAULT 'repo' CHECK (content_origin IN ('repo', 'rule', 'curated', 'ai')),
    review_status TEXT NOT NULL DEFAULT 'approved' CHECK (review_status IN ('pending', 'auto_passed', 'approved', 'rejected')),
    run_id BIGINT REFERENCES enrichment_runs(id),
    item_key TEXT UNIQUE NOT NULL,
    source_id BIGINT REFERENCES sources(id)
);

-- Collocations table
CREATE TABLE collocations (
    id BIGSERIAL PRIMARY KEY,
    lemma_id BIGINT NOT NULL REFERENCES lemmas(id) ON DELETE CASCADE,
    sense_id BIGINT REFERENCES senses(id),
    phrase_es TEXT NOT NULL,
    phrase_en TEXT NOT NULL,
    content_origin TEXT NOT NULL DEFAULT 'repo' CHECK (content_origin IN ('repo', 'rule', 'curated', 'ai')),
    review_status TEXT NOT NULL DEFAULT 'approved' CHECK (review_status IN ('pending', 'auto_passed', 'approved', 'rejected')),
    run_id BIGINT REFERENCES enrichment_runs(id),
    item_key TEXT UNIQUE NOT NULL,
    source_id BIGINT REFERENCES sources(id)
);

-- False friends table
CREATE TABLE false_friends (
    id BIGSERIAL PRIMARY KEY,
    lemma_id BIGINT NOT NULL REFERENCES lemmas(id) ON DELETE CASCADE,
    english_word TEXT NOT NULL,
    explanation_en TEXT NOT NULL,
    content_origin TEXT NOT NULL DEFAULT 'repo' CHECK (content_origin IN ('repo', 'rule', 'curated', 'ai')),
    review_status TEXT NOT NULL DEFAULT 'approved' CHECK (review_status IN ('pending', 'auto_passed', 'approved', 'rejected')),
    run_id BIGINT REFERENCES enrichment_runs(id),
    item_key TEXT UNIQUE NOT NULL,
    source_id BIGINT REFERENCES sources(id)
);

-- Word of the day
CREATE TABLE word_of_day (
    id BIGSERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    lemma_id BIGINT REFERENCES lemmas(id),
    verb_lemma_id BIGINT REFERENCES lemmas(id)
);

-- Indexes
CREATE INDEX idx_lemmas_search_key ON lemmas USING gin (search_key gin_trgm_ops);
CREATE INDEX idx_lemmas_lemma_key ON lemmas (lemma_key);
CREATE INDEX idx_lemmas_slug ON lemmas (slug);
CREATE INDEX idx_lemmas_frequency_rank ON lemmas (frequency_rank);
CREATE INDEX idx_sense_translations_search_key ON sense_translations USING gin (search_key gin_trgm_ops);
CREATE INDEX idx_word_forms_form_key ON word_forms (form_key);
CREATE INDEX idx_word_forms_search_key ON word_forms USING gin (search_key gin_trgm_ops);
CREATE INDEX idx_senses_item_key ON senses (item_key);
CREATE INDEX idx_examples_item_key ON examples (item_key);
CREATE INDEX idx_related_item_key ON related (item_key);
CREATE INDEX idx_collocations_item_key ON collocations (item_key);
CREATE INDEX idx_false_friends_item_key ON false_friends (item_key);
CREATE INDEX idx_senses_review_status ON senses (review_status);
CREATE INDEX idx_examples_review_status ON examples (review_status);
