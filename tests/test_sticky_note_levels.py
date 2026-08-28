from pathlib import Path

from src.create_sticky_notes import load_note_data


def test_load_note_data_filters_by_level():
    notes = load_note_data(level="N4")

    assert len(notes) == 149
    assert {note["level"] for note in notes} == {"n4"}
    assert notes[0]["hiragana"] == "てーぶる"
    assert notes[0]["sentence"] == "家族とテーブルで晩ご飯を食べます。"


def test_n5_notes_use_n5_sentences():
    notes = load_note_data(level="N5")

    assert len(notes) == 149
    assert notes[0]["sentence"] == "このテーブルは私の家にあります。とても便利です。"


def test_load_note_data_rejects_unknown_level():
    try:
        load_note_data(level="N3")
    except ValueError as error:
        assert "N3" in str(error)
    else:
        raise AssertionError("Expected an error for a level with no manifest entries")