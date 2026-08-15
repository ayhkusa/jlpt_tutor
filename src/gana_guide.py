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
        "go": {
            "label": "Go (ご)",
            "sound": '"goh" (g + o)',
            "example": "ごはん (Meal)",
        },
        "za": {
            "label": "Za (ざ)",
            "sound": '"zah" (z + a)',
            "example": "ざっし (Magazine)",
        },
        "ji": {
            "label": "Ji (じ)",
            "sound": '"jee" (j + i)',
            "example": "じてんしゃ (Bicycle)",
        },
        "zu": {
            "label": "Zu (ず)",
            "sound": '"zoo" (z + u)',
            "example": "ずっと (All the time)",
        },
        "ze": {
            "label": "Ze (ぜ)",
            "sound": '"zeh" (z + e)',
            "example": "ぜんぶ (Everything)",
        },
        "zo": {
            "label": "Zo (ぞ)",
            "sound": '"zoh" (z + o)',
            "example": "ぞう (Elephant)",
        },
        "da": {
            "label": "Da (だ)",
            "sound": '"dah" (d + a)',
            "example": "だいがく (University)",
        },
        "de": {
            "label": "De (で)",
            "sound": '"deh" (d + e)',
            "example": "でんしゃ (Train)",
        },
        "do": {
            "label": "Do (ど)",
            "sound": '"doh" (d + o)',
            "example": "どこ (Where)",
        },
        "ba": {
            "label": "Ba (ば)",
            "sound": '"bah" (b + a)',
            "example": "ばか (Idiot)",
        },
        "bi": {
            "label": "Bi (び)",
            "sound": '"bee" (b + i)',
            "example": "びょういん (Hospital)",
        },
        "bu": {
            "label": "Bu (ぶ)",
            "sound": '"boo" (b + u)',
            "example": "ぶた (Pork)",
        },
        "be": {
            "label": "Be (べ)",
            "sound": '"beh" (b + e)',
            "example": "べんきょう (Study)",
        },
        "bo": {
            "label": "Bo (ぼ)",
            "sound": '"boh" (b + o)',
            "example": "ぼうし (Hat)",
        },
        "pa": {
            "label": "Pa (ぱ)",
            "sound": '"pah" (p + a)',
            "example": "ぱん (Bread)",
        },
        "pi": {
            "label": "Pi (ぴ)",
            "sound": '"pee" (p + i)',
            "example": "ぴかぴか (Shiny)",
        },
        "pu": {
            "label": "Pu (ぷ)",
            "sound": '"poo" (p + u)',
            "example": "ぷりん (Print)",
        },
        "pe": {
            "label": "Pe (ぺ)",
            "sound": '"peh" (p + e)',
            "example": "ぺん (Pen)",
        },
        "po": {
            "label": "Po (ぽ)",
            "sound": '"poh" (p + o)',
            "example": "ぽつぽつ (Dots)",
        },
    }
)
