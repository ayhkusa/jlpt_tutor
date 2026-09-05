from src.vocabulary_repository import (
    load_counting,
    load_grammar,
    load_household_objects,
    load_whisper_of_the_heart_vocab,
)


def test_n4_household_data_loads_as_legacy_entries():
    entries = load_household_objects()

    assert len(entries) == 149
    assert entries[0]["word"] == "テーブル"
    assert entries[0]["sentence"] == "家族とテーブルで晩ご飯を食べます。"
    assert entries[0]["breakdown"][-1]["text"] == "Grammar note"


def test_n5_household_data_loads_as_legacy_entries():
    entries = load_household_objects("N5")

    assert len(entries) == 149
    assert entries[0]["word"] == "テーブル"
    assert entries[0]["sentence"] == "このテーブルは私の家にあります。とても便利です。"


def test_whisper_of_the_heart_vocab_loads():
    entries = load_whisper_of_the_heart_vocab()

    assert len(entries) == 256
    assert entries[0]["japanese_reading"] == "牛乳"
    assert entries[0]["japanese_speaking"] == "ぎゅうにゅう"
    assert entries[0]["english"] == "milk"


def test_grammar_loads():
    data = load_grammar()

    assert "grammar_points" in data
    assert "speech_forms" in data
    assert len(data["grammar_points"]) == 6
    assert len(data["speech_forms"]) == 7
    assert data["grammar_points"][0]["grammar"] == "〜んだ / 〜んです"
    assert data["speech_forms"][0]["full_form"] == "〜のだ"


def test_counting_loads():
    entries = load_counting()

    assert len(entries) == 10
    assert entries[0]["number"] == 1
    assert entries[0]["english"] == "1 book"
    assert entries[0]["japanese"] == "一冊"
    assert entries[0]["reading"] == "いっさつ"


