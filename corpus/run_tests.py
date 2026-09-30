"""
Simple test runner for Corpus Pipeline — no external dependencies.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from corpus.pipeline import CorpusPipeline, create_synthetic_fixture, create_synthetic_lexicon_checker


def test_extract_text_removes_page_numbers():
    pipeline = CorpusPipeline()
    text = "Hola mundo\n42\nAdiós mundo"
    result = pipeline.extract_text(text)
    assert "42" not in result, "Page number not removed"
    assert "Hola" in result, "Text lost"
    print("✓ test_extract_text_removes_page_numbers")


def test_should_drop_asterisk_sentences():
    pipeline = CorpusPipeline()
    assert pipeline.should_drop_sentence("*Este es incorrecto") is True
    assert pipeline.should_drop_sentence("Texto normal") is False
    print("✓ test_should_drop_asterisk_sentences")


def test_should_drop_sentences_with_digits():
    pipeline = CorpusPipeline()
    assert pipeline.should_drop_sentence("Tengo 5 años") is True
    assert pipeline.should_drop_sentence("Tengo cinco años") is False
    print("✓ test_should_drop_sentences_with_digits")


def test_is_spanish():
    pipeline = CorpusPipeline()
    assert pipeline.is_spanish("El gato come pescado") is True
    assert pipeline.is_spanish("The cat eats fish") is False
    print("✓ test_is_spanish")


def test_tokenize():
    pipeline = CorpusPipeline()
    tokens = pipeline.tokenize("El gato come pescado")
    assert "gato" in tokens
    assert "come" in tokens
    print("✓ test_tokenize")


def test_lemmatize():
    pipeline = CorpusPipeline()
    lemma, pos = pipeline.lemmatize("corriendo")
    assert pos == "verb"
    lemma, pos = pipeline.lemmatize("casas")
    assert pos == "noun"
    print("✓ test_lemmatize")


def test_process_book_counts():
    pipeline = CorpusPipeline(lexicon_checker=create_synthetic_lexicon_checker())
    text = "El gato come. El gato duerme. El gato juega."
    pipeline.process_book("book1", text, level="A1")
    entries = pipeline.finalize()
    gato_entries = [e for e in entries if e.lemma == "gato"]
    assert len(gato_entries) > 0, "No gato entries found"
    assert gato_entries[0].total_count >= 3, f"Expected >= 3, got {gato_entries[0].total_count}"
    print("✓ test_process_book_counts")


def test_noise_policy_drops_unknown_rare():
    pipeline = CorpusPipeline(lexicon_checker=create_synthetic_lexicon_checker())
    text = "El gato come. xyzabc duerme."
    pipeline.process_book("book1", text, level="A1")
    entries = pipeline.finalize()
    xyz_entries = [e for e in entries if e.lemma == "xyzabc"]
    assert len(xyz_entries) == 0, "Unknown rare word should be dropped"
    print("✓ test_noise_policy_drops_unknown_rare")


def test_noise_policy_keeps_unknown_frequent():
    pipeline = CorpusPipeline(lexicon_checker=create_synthetic_lexicon_checker())
    text = "xyzabc duerme. xyzabc come. xyzabc juega. xyzabc corre."
    pipeline.process_book("book1", text, level="A1")
    entries = pipeline.finalize()
    xyz_entries = [e for e in entries if e.lemma == "xyzabc"]
    assert len(xyz_entries) == 1, "Unknown frequent word should be kept"
    assert "unknown_word" in xyz_entries[0].flags
    print("✓ test_noise_policy_keeps_unknown_frequent")


def test_min_level_tracking():
    pipeline = CorpusPipeline(lexicon_checker=create_synthetic_lexicon_checker())
    text = "El gato come."
    pipeline.process_book("book1", text, level="B1")
    pipeline.process_book("book2", text, level="A2")
    entries = pipeline.finalize()
    gato_entries = [e for e in entries if e.lemma == "gato"]
    assert gato_entries[0].min_level == "A2", f"Expected A2, got {gato_entries[0].min_level}"
    print("✓ test_min_level_tracking")


def test_no_book_text_in_output():
    pipeline = CorpusPipeline(lexicon_checker=create_synthetic_lexicon_checker())
    text = "El gato come pescado. La casa es grande."
    pipeline.process_book("book1", text, level="A1")
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        output_path = f.name
    pipeline.write_csv(output_path)
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    os.unlink(output_path)
    assert "El gato come pescado" not in content, "Book text leaked into output!"
    assert "gato" in content
    print("✓ test_no_book_text_in_output")


def test_write_csv():
    pipeline = CorpusPipeline(lexicon_checker=create_synthetic_lexicon_checker())
    text = "El gato come pescado."
    pipeline.process_book("book1", text, level="A1")
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        output_path = f.name
    pipeline.write_csv(output_path)
    assert os.path.exists(output_path)
    with open(output_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    assert len(lines) > 1, "CSV should have header + data"
    assert 'lemma' in lines[0]
    os.unlink(output_path)
    print("✓ test_write_csv")


def run_all_tests():
    tests = [
        test_extract_text_removes_page_numbers,
        test_should_drop_asterisk_sentences,
        test_should_drop_sentences_with_digits,
        test_is_spanish,
        test_tokenize,
        test_lemmatize,
        test_process_book_counts,
        test_noise_policy_drops_unknown_rare,
        test_noise_policy_keeps_unknown_frequent,
        test_min_level_tracking,
        test_no_book_text_in_output,
        test_write_csv,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {type(e).__name__}: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    return failed == 0


if __name__ == "__main__":
    import os
    success = run_all_tests()
    sys.exit(0 if success else 1)
