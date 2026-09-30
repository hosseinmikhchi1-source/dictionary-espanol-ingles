"""
Corpus Pipeline — Phase 1
Turns book text into a clean word-level table (corpus_lexicon).
Never stores book text. Only derived word-level data.
"""
import csv
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


# --- Configuration ---
SPANISH_LETTERS = set("abcdefghijklmnñopqrstuvwxyzáéíóúü")
PROPER_NOUN_THRESHOLD = 0.7  # fraction of non-sentence-initial occurrences to flag


@dataclass
class CorpusEntry:
    lemma: str
    pos_guess: str
    total_count: int = 0
    book_count: int = 0
    min_level: str = "unknown"
    known_in_lexicons: bool = False
    flags: list = field(default_factory=list)


class CorpusPipeline:
    """Process book text into corpus_lexicon."""

    def __init__(self, lexicon_checker=None):
        self.lexicon_checker = lexicon_checker or (lambda lemma: False)
        self.entries: dict[tuple[str, str], CorpusEntry] = {}
        self._book_lemmas: dict[str, set] = {}  # book_id -> set of lemmas
        self._lemma_occurrences: dict[str, list[bool]] = defaultdict(list)  # lemma -> [is_sentence_initial]

    def extract_text(self, text: str) -> str:
        """Clean raw text: remove page numbers, headers/footers, fix hyphens."""
        # Remove page numbers (standalone numbers on a line)
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        # Remove headers/footers (lines that appear on multiple pages — simplified)
        # Fix words split by end-of-line hyphens
        text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
        return text

    def should_drop_sentence(self, sentence: str) -> bool:
        """Drop sentences starting with * or cross marks, or containing digits."""
        stripped = sentence.strip()
        if stripped.startswith('*') or stripped.startswith('✗') or stripped.startswith('×'):
            return True
        if re.search(r'\d', stripped):
            return True
        return False

    def is_spanish(self, sentence: str) -> bool:
        """Simple offline language detection: check for Spanish-specific characters and common words."""
        # Simplified: check for Spanish-specific characters and common Spanish words
        spanish_markers = set("áéíóúüñ¿¡")
        common_spanish = {"el", "la", "los", "las", "un", "una", "de", "en", "que", "y", "es", "por", "con"}
        tokens = sentence.lower().split()
        has_spanish_char = any(c in spanish_markers for c in sentence.lower())
        has_common_word = any(t in common_spanish for t in tokens)
        return has_spanish_char or has_common_word

    def tokenize(self, text: str) -> list[str]:
        """Tokenize and keep alphabetic tokens with Spanish letters."""
        tokens = re.findall(r'[a-záéíóúüñ]+', text.lower())
        return [t for t in tokens if any(c in SPANISH_LETTERS for c in t)]

    def is_sentence_initial(self, text: str, token_start: int) -> bool:
        """Check if a token is at the start of a sentence."""
        if token_start == 0:
            return True
        # Look backwards for sentence-ending punctuation
        before = text[:token_start].rstrip()
        return before.endswith(('.', '!', '?', '…'))

    def lemmatize(self, token: str) -> tuple[str, str]:
        """
        Offline lemmatizer (simplified).
        Returns (lemma, pos_guess).
        In production, use Simplemma or similar.
        """
        # Simplified rules for demonstration
        # Verb endings
        if token.endswith(('ar', 'er', 'ir')):
            return token, 'verb'
        if token.endswith(('ando', 'iendo')):
            return token[:-4] + ('ar' if token.endswith('ando') else 'er'), 'verb'
        if token.endswith(('ado', 'ido')):
            return token[:-2] + ('ar' if token.endswith('ado') else 'er'), 'verb'
        # Plural nouns/adjectives
        if token.endswith('es') and len(token) > 3:
            return token[:-2], 'noun'
        if token.endswith('s') and len(token) > 2:
            return token[:-1], 'noun'
        # Adverbs
        if token.endswith('mente'):
            return token[:-5], 'adverb'
        return token, 'other'

    def process_book(self, book_id: str, text: str, level: str = "unknown"):
        """Process a single book's text."""
        text = self.extract_text(text)
        sentences = re.split(r'[.!?…]+', text)

        book_lemmas = set()

        for sentence in sentences:
            if self.should_drop_sentence(sentence):
                continue
            if not self.is_spanish(sentence):
                continue

            tokens = self.tokenize(sentence)
            for token in tokens:
                lemma, pos_guess = self.lemmatize(token)
                key = (lemma, pos_guess)

                if key not in self.entries:
                    self.entries[key] = CorpusEntry(lemma=lemma, pos_guess=pos_guess)

                entry = self.entries[key]
                entry.total_count += 1
                book_lemmas.add(lemma)

                # Track sentence-initial occurrences for proper noun detection
                # (simplified — in production, track actual positions)

        self._book_lemmas[book_id] = book_lemmas

        # Update book_count and min_level
        for lemma in book_lemmas:
            for key, entry in self.entries.items():
                if entry.lemma == lemma:
                    entry.book_count += 1
                    if level != "unknown":
                        if entry.min_level == "unknown":
                            entry.min_level = level
                        else:
                            # Keep the lowest level
                            levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
                            if levels.index(level) < levels.index(entry.min_level):
                                entry.min_level = level

    def finalize(self) -> list[CorpusEntry]:
        """Finalize entries: apply noise policy and existence check."""
        results = []
        for key, entry in self.entries.items():
            entry.known_in_lexicons = self.lexicon_checker(entry.lemma)

            # Noise policy
            if not entry.known_in_lexicons and entry.total_count < 3:
                continue  # Drop

            if not entry.known_in_lexicons and entry.total_count >= 3:
                entry.flags.append("unknown_word")

            results.append(entry)

        return results

    def write_csv(self, output_path: Path):
        """Write corpus_lexicon.csv."""
        results = self.finalize()
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['lemma', 'pos_guess', 'total_count', 'book_count', 'min_level', 'known_in_lexicons', 'flags'])
            for entry in results:
                writer.writerow([
                    entry.lemma,
                    entry.pos_guess,
                    entry.total_count,
                    entry.book_count,
                    entry.min_level,
                    entry.known_in_lexicons,
                    '|'.join(entry.flags)
                ])


# --- Synthetic Fixtures for Tests ---

def create_synthetic_fixture() -> str:
    """Create synthetic Spanish text for testing."""
    return """
    El gato come pescado. El gato es muy rápido.
    La casa es grande. La casa tiene un jardín.
    *Este es un ejemplo incorrecto que debe ser eliminado.
    El perro corre en el parque. El perro es feliz.
    La niña juega con el gato. La niña tiene cinco años.
    Yo tengo un libro interesante. Tú tienes dos libros.
    Él come una manzana. Ella come una naranja.
    Nosotros vivimos en una ciudad grande.
    Ellos tienen una casa pequeña.
    ¿Dónde está el baño? ¿Cuánto cuesta esto?
    ¡Hola! ¿Cómo estás? Muy bien, gracias.
    El sol brilla en el cielo azul.
    La luna es blanca y redonda.
    Me gusta leer libros interesantes.
    El tren llega tarde hoy.
    La profesora explica la lección.
    Los estudiantes escuchan atentamente.
    Quiero aprender español todos los días.
    El restaurante sirve comida deliciosa.
    La música es muy bonita.
    """


def create_synthetic_lexicon_checker():
    """Create a simple lexicon checker for testing."""
    known_words = {"gato", "casa", "perro", "niña", "libro", "sol", "luna", "tren", "profesora", "estudiantes", "restaurante", "música", "comer", "correr", "jugar", "tener", "vivir", "gustar", "llegar", "explicar", "escuchar", "aprender", "servir", "brillar"}
    return lambda lemma: lemma in known_words


if __name__ == "__main__":
    # Test with synthetic data
    pipeline = CorpusPipeline(lexicon_checker=create_synthetic_lexicon_checker())
    fixture = create_synthetic_fixture()
    pipeline.process_book("test_book_1", fixture, level="A2")
    pipeline.write_csv(Path("data/derived/corpus_lexicon.csv"))
    print("Corpus pipeline test complete. Output: data/derived/corpus_lexicon.csv")
