"""Load and validate the canonical JLPT vocabulary and sentence data."""

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VOCABULARY_PATH = PROJECT_ROOT / "data" / "vocabulary" / "words.json"
SENTENCES_DIRECTORY = PROJECT_ROOT / "data" / "sentences"


def read_records(path: Path) -> list[dict[str, Any]]:
    """Read a JSON array of object records."""
    with path.open(encoding="utf-8") as file:
        records = json.load(file)
    if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
        raise ValueError(f"Expected a JSON array of objects in {path}")
    return records


def load_household_objects(level: str = "N4") -> list[dict[str, Any]]:
    """Return household entries for a JLPT level in the generator-compatible shape."""
    normalized_level = level.upper()
    if normalized_level not in {"N5", "N4", "N3", "N2", "N1"}:
        raise ValueError(f"Unsupported JLPT level: {level}")
    words = read_records(VOCABULARY_PATH)
    sentences_path = SENTENCES_DIRECTORY / f"{normalized_level.lower()}.json"
    if not sentences_path.exists():
        raise FileNotFoundError(f"Sentence data is not available for {normalized_level}: {sentences_path}")
    sentences = read_records(sentences_path)
    words_by_id = {word["id"]: word for word in words}

    if len(words_by_id) != len(words):
        raise ValueError("Vocabulary word IDs must be unique")

    entries = []
    seen_word_ids = set()
    for sentence in sentences:
        if sentence.get("target_level") != normalized_level:
            raise ValueError(f"{normalized_level} sentence has an invalid target level: {sentence.get('id')}")
        word_id = sentence.get("word_id")
        if word_id not in words_by_id:
            raise ValueError(f"Sentence references an unknown word ID: {word_id}")
        if word_id in seen_word_ids:
            raise ValueError(f"Multiple {normalized_level} sentences reference word ID: {word_id}")
        seen_word_ids.add(word_id)
        word = words_by_id[word_id]
        entries.append(
            {
                "word": word["written"],
                "hiragana": word["reading"],
                "english_word": word["english"],
                "sentence": sentence["japanese"],
                "english_sentence": sentence["english"],
                "breakdown": sentence["breakdown"],
            }
        )

    return entries