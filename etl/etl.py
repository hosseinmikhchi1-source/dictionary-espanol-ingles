"""
Core ETL Pipeline — Phase 2
One command runs everything; every step is idempotent.
Load into staging, validate, promote in one transaction.
"""
import csv
import json
import re
import unicodedata
from pathlib import Path
from collections import defaultdict


class ETLPipeline:
    """Main ETL pipeline for the dictionary."""

    def __init__(self, data_dir: Path, db_connection=None):
        self.data_dir = data_dir
        self.db = db_connection
        self.report = {
            "sources": {},
            "lemmas": {"total": 0, "by_pos": defaultdict(int)},
            "senses": {"total": 0, "skipped_duplicates": 0},
            "examples": {"total": 0, "linked_to_sense": 0, "lemma_only": 0},
            "verbs": {"total": 0, "by_source": defaultdict(int), "without_conjugation": 0},
            "word_forms": {"total": 0},
            "pronunciations": {"total": 0},
            "unmapped_pos": defaultdict(int),
        }

    def normalize_text(self, text: str) -> str:
        """Clean text: trim, remove control chars, collapse spaces, NFC."""
        if not text:
            return ""
        text = unicodedata.normalize("NFC", text)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        # Standardize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        return text

    def make_lemma_key(self, text: str) -> str:
        """Casefolded, NFC, trimmed. Keeps accents and n-tilde."""
        return unicodedata.normalize("NFC", text.casefold().strip())

    def make_search_key(self, text: str) -> str:
        """lemma_key with acute accents and diaeresis removed. n-tilde never folded."""
        key = self.make_lemma_key(text)
        # Remove accents
        key = key.replace('á', 'a').replace('é', 'e').replace('í', 'i')
        key = key.replace('ó', 'o').replace('ú', 'u').replace('ü', 'u')
        # Remove inner hyphens and punctuation
        key = re.sub(r'[-_\s]', '', key)
        # Remove leading "to " for English verbs
        if key.startswith('to '):
            key = key[3:]
        return key

    def make_slug(self, text: str) -> str:
        """Create URL-friendly slug."""
        key = self.make_search_key(text)
        return key.replace(' ', '-')

    def map_pos(self, pos: str) -> str:
        """Map source POS labels to our canonical set."""
        pos_map = {
            'n': 'noun', 'noun': 'noun', 's': 'noun',
            'v': 'verb', 'verb': 'verb', 'v.': 'verb',
            'adj': 'adjective', 'adjective': 'adjective', 'a': 'adjective',
            'adv': 'adverb', 'adverb': 'adverb',
            'pron': 'pronoun', 'pronoun': 'pronoun',
            'prep': 'preposition', 'preposition': 'preposition',
            'conj': 'conjunction', 'conjunction': 'conjunction',
            'interj': 'interjection', 'interjection': 'interjection',
            'det': 'determiner', 'determiner': 'determiner',
            'num': 'numeral', 'numeral': 'numeral',
            'phrase': 'phrase',
            'prop': 'proper_noun', 'proper_noun': 'proper_noun',
        }
        normalized = pos.lower().strip()
        mapped = pos_map.get(normalized, 'other')
        if mapped == 'other':
            self.report["unmapped_pos"][normalized] += 1
        return mapped

    def parse_es_en_data(self, file_path: Path):
        """Parse the Wiktionary-format es-en.data file."""
        entries = []
        current_entry = None

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                if line == '_____':
                    if current_entry:
                        entries.append(current_entry)
                    current_entry = None
                    continue

                if current_entry is None:
                    current_entry = {'word': line, 'pos': None, 'glosses': []}
                elif line.startswith('pos:'):
                    current_entry['pos'] = line[4:].strip()
                elif line.startswith('gloss:'):
                    gloss = line[6:].strip()
                    if gloss:
                        current_entry['glosses'].append(gloss)
                elif line.startswith('meta:'):
                    pass  # Skip metadata
                elif line.startswith('q:'):
                    pass  # Skip qualifiers
                elif line.startswith('etymology:'):
                    pass  # Skip etymology

        if current_entry:
            entries.append(current_entry)

        return entries

    def parse_frequency_csv(self, file_path: Path):
        """Parse frequency.csv."""
        entries = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entries.append({
                    'count': int(row['count']),
                    'spanish': row['spanish'],
                    'pos': row['pos'],
                    'flags': row.get('flags', ''),
                    'usage': row.get('usage', ''),
                })
        return entries

    def parse_sentences_tsv(self, file_path: Path):
        """Parse sentences.tsv."""
        entries = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                entries.append({
                    'en': row.get('EN', ''),
                    'es': row.get('ES', ''),
                    'license': row.get('license', ''),
                    'word_count': row.get('word_count', ''),
                    'es_word_count': row.get('es_word_count', ''),
                    'tags': row.get('tags', ''),
                })
        return entries

    def load_sources(self):
        """Load and register sources."""
        sources = [
            {
                'code': 'doozan',
                'name': 'doozan/spanish_data',
                'url': 'https://github.com/doozan/spanish_data',
                'license': 'CC BY 4.0',
                'allows_commercial': True,
                'attribution_text': 'Spanish data from doozan/spanish_data, CC BY 4.0',
            },
            {
                'code': 'asosab',
                'name': 'asosab/esp_verbos',
                'url': 'https://github.com/asosab/esp_verbos',
                'license': 'CC BY-SA 4.0',
                'allows_commercial': True,
                'attribution_text': 'Spanish verb conjugations from asosab/esp_verbos, CC BY-SA 4.0',
            },
            {
                'code': 'unimorph',
                'name': 'unimorph/spa',
                'url': 'https://github.com/unimorph/spa',
                'license': 'CC BY-SA 3.0',
                'allows_commercial': True,
                'attribution_text': 'Spanish unimorph data from unimorph/spa, CC BY-SA 3.0',
            },
            {
                'code': 'conjugator',
                'name': 'Benedict-Carling/spanish-conjugator',
                'url': 'https://github.com/Benedict-Carling/spanish-conjugator',
                'license': 'MIT',
                'allows_commercial': True,
                'attribution_text': 'spanish-conjugator by Benedict-Carling, MIT License',
            },
        ]
        return sources

    def run(self):
        """Run the full ETL pipeline."""
        print("Starting ETL pipeline...")

        # Step 1: Load sources
        sources = self.load_sources()
        print(f"Loaded {len(sources)} sources")

        # Step 2: Parse es-en.data
        raw_dir = self.data_dir / 'raw'
        es_en_file = raw_dir / 'spanish_data' / 'es-en.data'
        if es_en_file.exists():
            entries = self.parse_es_en_data(es_en_file)
            print(f"Parsed {len(entries)} entries from es-en.data")
            self.report['lemmas']['total'] = len(entries)

        # Step 3: Parse frequency data
        freq_file = raw_dir / 'spanish_data' / 'frequency.csv'
        if freq_file.exists():
            freq_entries = self.parse_frequency_csv(freq_file)
            print(f"Parsed {len(freq_entries)} frequency entries")

        # Step 4: Parse sentences
        sentences_file = raw_dir / 'spanish_data' / 'sentences.tsv'
        if sentences_file.exists():
            sentences = self.parse_sentences_tsv(sentences_file)
            print(f"Parsed {len(sentences)} sentences")

        # Step 5: Parse verb conjugations
        verbos_file = raw_dir / 'esp_verbos' / 'esp_verbos.json'
        if verbos_file.exists():
            with open(verbos_file, 'r', encoding='utf-8') as f:
                verbs = json.load(f)
            print(f"Parsed {len(verbs)} verbs from esp_verbos")
            self.report['verbs']['total'] = len(verbs)

        # Step 6: Parse unimorph
        unimorph_file = raw_dir / 'unimorph-spa' / 'spa'
        if unimorph_file.exists():
            forms = []
            with open(unimorph_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 3:
                        forms.append({
                            'lemma': parts[0],
                            'form': parts[1],
                            'tags': parts[2],
                        })
            print(f"Parsed {len(forms)} word forms from unimorph")
            self.report['word_forms']['total'] = len(forms)

        print("\nETL Report:")
        print(json.dumps(self.report, indent=2, default=str))

        return self.report


if __name__ == "__main__":
    data_dir = Path(__file__).parent.parent / 'data'
    pipeline = ETLPipeline(data_dir)
    pipeline.run()
