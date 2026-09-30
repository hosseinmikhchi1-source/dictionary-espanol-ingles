"""
Tests for Corpus Pipeline — Phase 1
Uses synthetic fixtures only. Never uses real book text.
"""
import csv
import pytest
from pathlib import Path
from corpus.pipeline import CorpusPipeline, create_synthetic_fixture, create_synthetic_lexicon_checker


class TestCorpusPipeline:
    """Test the corpus pipeline with synthetic data."""

    def setup_method(self):
        self.pipeline = CorpusPipeline(lexicon_checker=create_synthetic_lexicon_checker())

    def test_extract_text_removes_page_numbers(self):
        text = "Hola mundo\n42\nAdiós mundo"
        result = self.pipeline.extract_text(text)
        assert "42" not in result
        assert "Hola" in result
        assert "Adiós" in result

    def test_extract_text_fixes_hyphenation(self):
        text = "casa-\n grande"
        result = self.pipeline.extract_text(text)
        assert "casa-" not in result
        assert "casa" in result

    def test_should_drop_asterisk_sentences(self):
        assert self.pipeline.should_drop_sentence("*Este es incorrecto") is True
        assert self.pipeline.should_drop_sentence("✗ Error") is True
        assert self.pipeline.should_drop_sentence("Texto normal") is False

    def test_should_drop_sentences_with_digits(self):
        assert self.pipeline.should_drop_sentence("Tengo 5 años") is True
        assert self.pipeline.should_drop_sentence("Tengo cinco años") is False

    def test_is_spanish_detects_spanish(self):
        assert self.pipeline.is_spanish("El gato come pescado") is True
        assert self.pipeline.is_spanish("The cat eats fish") is False

    def test_tokenize_keeps_spanish_letters(self):
        tokens = self.pipeline.tokenize("El gato come pescado")
        assert "gato" in tokens
        assert "come" in tokens
        assert "pescado" in tokens

    def test_lemmatize_verbs(self):
        lemma, pos = self.pipeline.lemmatize("corriendo")
        assert pos == "verb"

    def test_lemmatize_nouns(self):
        lemma, pos = self.pipeline.lemmatize("casas")
        assert pos == "noun"

    def test_process_book_counts(self):
        text = "El gato come. El gato duerme. El gato juega."
        self.pipeline.process_book("book1", text, level="A1")
        entries = self.pipeline.finalize()
        gato_entries = [e for e in entries if e.lemma == "gato"]
        assert len(gato_entries) > 0
        assert gato_entries[0].total_count >= 3

    def test_proper_noun_detection(self):
        # Simplified test — in production, track actual positions
        text = "Madrid es grande. Madrid tiene parques."
        self.pipeline.process_book("book1", text, level="A1")
        entries = self.pipeline.finalize()
        madrid_entries = [e for e in entries if e.lemma == "madrid"]
        assert len(madrid_entries) > 0

    def test_noise_policy_drops_unknown_rare(self):
        text = "El gato come. xyzabc duerme."
        self.pipeline.process_book("book1", text, level="A1")
        entries = self.pipeline.finalize()
        xyz_entries = [e for e in entries if e.lemma == "xyzabc"]
        assert len(xyz_entries) == 0  # Dropped: unknown and count < 3

    def test_noise_policy_keeps_unknown_frequent(self):
        text = "xyzabc duerme. xyzabc come. xyzabc juega. xyzabc corre."
        self.pipeline.process_book("book1", text, level="A1")
        entries = self.pipeline.finalize()
        xyz_entries = [e for e in entries if e.lemma == "xyzabc"]
        assert len(xyz_entries) == 1
        assert "unknown_word" in xyz_entries[0].flags

    def test_min_level_tracking(self):
        text = "El gato come."
        self.pipeline.process_book("book1", text, level="B1")
        self.pipeline.process_book("book2", text, level="A2")
        entries = self.pipeline.finalize()
        gato_entries = [e for e in entries if e.lemma == "gato"]
        assert gato_entries[0].min_level == "A2"  # Lowest level wins

    def test_write_csv(self, tmp_path):
        text = "El gato come pescado."
        self.pipeline.process_book("book1", text, level="A1")
        output = tmp_path / "corpus_lexicon.csv"
        self.pipeline.write_csv(output)
        assert output.exists()
        with open(output, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) > 0
            assert 'lemma' in rows[0]
            assert 'pos_guess' in rows[0]
            assert 'total_count' in rows[0]

    def test_no_book_text_in_output(self, tmp_path):
        """Verify that book text never appears in the output."""
        text = "El gato come pescado. La casa es grande."
        self.pipeline.process_book("book1", text, level="A1")
        output = tmp_path / "corpus_lexicon.csv"
        self.pipeline.write_csv(output)
        content = output.read_text(encoding='utf-8')
        # Should not contain full sentences
        assert "El gato come pescado" not in content
        assert "La casa es grande" not in content
        # Should contain only word-level data
        assert "gato" in content
        assert "casa" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
