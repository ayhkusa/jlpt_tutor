from src.vocabulary_repository import load_household_objects


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