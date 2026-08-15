from pathlib import Path


REQUIRED_GANA = [
    "が", "ぎ", "ぐ", "げ", "ご",
    "ざ", "じ", "ず", "ぜ", "ぞ",
    "だ", "ぢ", "づ", "で", "ど",
    "ば", "び", "ぶ", "べ", "ぼ",
    "ぱ", "ぴ", "ぷ", "ぺ", "ぽ",
]


def test_missing_gana_present_in_network_page():
    index_html = Path(__file__).resolve().parents[1] / "docs" / "index.html"
    text = index_html.read_text(encoding="utf-8")
    missing = [char for char in REQUIRED_GANA if char not in text]
    assert not missing, f"Missing kana in vocabulary network: {missing}"
