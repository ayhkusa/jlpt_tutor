import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_n5_sentences_cover_every_canonical_word_once():
    words = json.loads((PROJECT_ROOT / "data" / "vocabulary" / "words.json").read_text(encoding="utf-8"))
    sentences = json.loads((PROJECT_ROOT / "data" / "sentences" / "n5.json").read_text(encoding="utf-8"))

    assert len(sentences) == len(words)
    assert {sentence["word_id"] for sentence in sentences} == {word["id"] for word in words}
    assert {sentence["target_level"] for sentence in sentences} == {"N5"}