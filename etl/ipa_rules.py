"""
IPA Rules - Phase 2
Deterministic Spanish grapheme-to-phoneme module.
Implements stress rules, digraphs ch/ll/rr, c/z/qu/gu/gue, b/v, silent h, x, n-tilde.
Variants: es-ES (distincion) and es-419 (seseo).
"""
import re
import unicodedata


class SpanishIPA:
    """Convert Spanish text to IPA transcription."""

    def __init__(self, variant="es-ES"):
        self.variant = variant  # es-ES or es-419

    def normalize(self, text):
        """Normalize text: lowercase, NFC."""
        text = unicodedata.normalize("NFC", text.lower())
        return text

    def apply_stress_rules(self, syllables):
        """Apply Spanish stress rules to syllables."""
        vowels = set("aeiouáéíóúü")
        strong_vowels = set("aeoáéó")
        weak_vowels = set("iuíú")

        if not syllables:
            return syllables

        # Check for written accent
        for i, syl in enumerate(syllables):
            if any(c in syl for c in "áéíóú"):
                # Has written accent - stressed
                return syllables

        # Default stress rules
        last_syl = syllables[-1]
        # If ends in vowel, n, or s -> stress on penultimate
        if last_syl[-1] in vowels or last_syl[-1] in "ns":
            if len(syllables) >= 2:
                syllables[-2] = "\u02c8" + syllables[-2]
        else:
            # Otherwise stress on last syllable
            syllables[-1] = "\u02c8" + syllables[-1]

        return syllables

    def syllabify(self, text):
        """Simple syllabification."""
        vowels = "aeiouáéíóúü"
        syllables = []
        current = ""
        for char in text:
            current += char
            if char in vowels:
                syllables.append(current)
                current = ""
        if current:
            if syllables:
                syllables[-1] += current
            else:
                syllables.append(current)
        return syllables

    def grapheme_to_phoneme(self, text):
        """Convert graphemes to phonemes."""
        text = self.normalize(text)

        # Digraphs first
        text = re.sub(r"ch", "t\u0283", text)
        text = re.sub(r"ll", "\u029d", text)
        text = re.sub(r"rr", "r", text)

        # c/z/qu/gu rules
        if self.variant == "es-ES":
            text = re.sub(r"c([ei])", r"T\1", text)
            text = re.sub(r"z", "T", text)
        else:
            text = re.sub(r"c([ei])", r"s\1", text)
            text = re.sub(r"z", "s", text)

        text = re.sub(r"qu", "k", text)
        text = re.sub(r"g([ei])", r"x\1", text)
        text = re.sub(r"gu([ei])", r"g\1", text)
        text = re.sub(r"gü", "g", text)

        # b/v -> /b/
        text = re.sub(r"[bv]", "b", text)

        # silent h
        text = re.sub(r"h", "", text)

        # x -> /ks/
        text = re.sub(r"x", "ks", text)

        # n-tilde -> /n/
        text = re.sub(r"\u00f1", "n", text)

        # Single letters
        text = re.sub(r"c([aou])", r"k\1", text)
        text = re.sub(r"g([aou])", r"g\1", text)
        text = re.sub(r"j", "x", text)
        text = re.sub(r"y", "\u029d", text)
        text = re.sub(r"r(?!r)", "\u027e", text)

        # Diphthongs
        text = re.sub(r"ue", "we", text)
        text = re.sub(r"ie", "je", text)
        text = re.sub(r"ui", "wi", text)
        text = re.sub(r"iu", "ju", text)

        return text

    def transcribe(self, text):
        """Full transcription pipeline."""
        text = self.normalize(text)
        syllables = self.syllabify(text)
        syllables = self.apply_stress_rules(syllables)
        ipa = "".join(syllables)
        ipa = self.grapheme_to_phoneme(ipa)
        return ipa


# Test words covering every stress pattern
TEST_WORDS = {
    "camion": "ka\u02c8mjon",
    "feliz": "fe\u02c8lis",
    "reloj": "re\u02c8lox",
    "casa": "\u02c8kasa",
    "arbol": "a\u02c8rbol",
    "lapiz": "la\u02c8pis",
    "musica": "\u02c8musika",
    "pelicula": "pe\u02c8likula",
    "chico": "\u02c8t\u0283iko",
    "llave": "\u02c8\u029dabe",
    "perro": "\u02c8pero",
    "zapato": "\u02c8sapato",
    "queso": "\u02c8keso",
    "guerra": "\u02c8gera",
    "baca": "\u02c8baka",
    "vaca": "\u02c8baka",
    "hola": "\u02c8ola",
    "hotel": "o\u02c8tel",
    "examen": "e\u02c8ksamen",
    "nino": "\u02c8nino",
}


def test_ipa():
    """Test IPA transcription."""
    ipa = SpanishIPA(variant="es-ES")
    for word, expected in TEST_WORDS.items():
        result = ipa.transcribe(word)
        # ASCII-safe output for Windows console
        print(f"{word} -> {ascii(result)} (expected: {ascii(expected)})")
    print("IPA tests complete.")


if __name__ == "__main__":
    test_ipa()
