from kana_guide import pronunciation_guide as kana_pronunciation_guide

_katakana_to_hiragana = str.maketrans(
    {
        "ア": "あ",
        "イ": "い",
        "ウ": "う",
        "エ": "え",
        "オ": "お",
        "カ": "か",
        "キ": "き",
        "ク": "く",
        "ケ": "け",
        "コ": "こ",
        "サ": "さ",
        "シ": "し",
        "ス": "す",
        "セ": "せ",
        "ソ": "そ",
        "タ": "た",
        "チ": "ち",
        "ツ": "つ",
        "テ": "て",
        "ト": "と",
        "ナ": "な",
        "ニ": "に",
        "ヌ": "ぬ",
        "ネ": "ね",
        "ノ": "の",
        "ハ": "は",
        "ヒ": "ひ",
        "フ": "ふ",
        "ヘ": "へ",
        "ホ": "ほ",
        "マ": "ま",
        "ミ": "み",
        "ム": "む",
        "メ": "め",
        "モ": "も",
        "ヤ": "や",
        "ユ": "ゆ",
        "ヨ": "よ",
        "ラ": "ら",
        "リ": "り",
        "ル": "る",
        "レ": "れ",
        "ロ": "ろ",
        "ワ": "わ",
        "ヲ": "を",
        "ン": "ん",
    }
)


def _to_hiragana(value: str) -> str:
    return value.translate(_katakana_to_hiragana)


def _convert_entry(entry: dict[str, str]) -> dict[str, str]:
    converted = dict(entry)
    converted["label"] = _to_hiragana(entry.get("label", ""))
    converted["example"] = _to_hiragana(entry.get("example", ""))
    return converted


pronunciation_guide = {
    roman: _convert_entry(entry)
    for roman, entry in kana_pronunciation_guide.items()
}

pronunciation_guide.update(
    {
        "ga": {
            "label": "Ga (が)",
            "sound": '"gah" (g + a)',
            "example": "がくせい (Student)",
        },
        "gi": {
            "label": "Gi (ぎ)",
            "sound": '"gee" (g + i)',
            "example": "ぎんこう (Bank)",
        },
        "gu": {
            "label": "Gu (ぐ)",
            "sound": '"goo" (g + u)',
            "example": "ぐんたい (Army)",
        },
        "ge": {
            "label": "Ge (げ)",
            "sound": '"geh" (g + e)',
            "example": "げんき (Healthy, energetic)",
        },
    }
)
