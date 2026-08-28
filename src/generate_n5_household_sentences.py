"""Generate N5 practice sentences for the canonical household vocabulary."""

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORDS_PATH = PROJECT_ROOT / "data" / "vocabulary" / "words.json"
OUTPUT_PATH = PROJECT_ROOT / "data" / "sentences" / "n5.json"


def sentence_record(index: int, word: dict[str, Any]) -> dict[str, Any]:
    """Create an N5 sentence record with one household word as the target."""
    written = str(word["written"])
    english = str(word["english"])
    templates = (
        (
            f"この{written}は私の家にあります。とても便利です。",
            f"This {english} is in my home. It is very useful.",
            [
                {"text": f"この{written}は", "meaning": f"this {english}", "function": "この modifies the noun; は marks the topic"},
                {"text": "私の家に", "meaning": "in my home", "function": "の links 私 and 家; に marks the location"},
                {"text": "あります", "meaning": "there is / is located", "function": "polite form of ある for an inanimate thing"},
                {"text": "とても便利です", "meaning": "is very useful", "function": "とても intensifies the な-adjective 便利"},
            ],
        ),
        (
            f"新しい{written}を買いました。家で毎日使います。",
            f"I bought a new {english}. I use it at home every day.",
            [
                {"text": f"新しい{written}を", "meaning": f"a new {english}", "function": "新しい modifies the noun; を marks the object"},
                {"text": "買いました", "meaning": "bought", "function": "polite past form of 買います"},
                {"text": "家で", "meaning": "at home", "function": "で marks the place of an action"},
                {"text": "毎日使います", "meaning": "use every day", "function": "毎日 is a time expression; 使います is a polite verb"},
            ],
        ),
        (
            f"母は{written}を使います。私はそばで見ます。",
            f"My mother uses the {english}. I watch nearby.",
            [
                {"text": "母は", "meaning": "my mother", "function": "は marks the topic"},
                {"text": f"{written}を", "meaning": f"the {english}", "function": "を marks the direct object of 使います"},
                {"text": "使います", "meaning": "uses", "function": "polite verb"},
                {"text": "私はそばで見ます", "meaning": "I watch nearby", "function": "は marks the topic; で marks where I watch"},
            ],
        ),
        (
            f"その{written}は小さいです。でもよく使います。",
            f"That {english} is small. But I use it often.",
            [
                {"text": f"その{written}は", "meaning": f"that {english}", "function": "その modifies the noun; は marks the topic"},
                {"text": "小さいです", "meaning": "is small", "function": "polite form of the い-adjective 小さい"},
                {"text": "でも", "meaning": "but", "function": "connects contrasting statements"},
                {"text": "よく使います", "meaning": "use often", "function": "よく is an adverb; 使います is a polite verb"},
            ],
        ),
        (
            f"私は{written}が好きです。色がきれいです。",
            f"I like this {english}. Its color is pretty.",
            [
                {"text": "私は", "meaning": "I", "function": "は marks the topic"},
                {"text": f"{written}が", "meaning": f"the {english}", "function": "が marks what is liked with 好きです"},
                {"text": "好きです", "meaning": "like", "function": "polite な-adjective expression"},
                {"text": "色がきれいです", "meaning": "the color is pretty", "function": "が marks the subject; きれい is a な-adjective"},
            ],
        ),
    )
    japanese, english_sentence, breakdown = templates[(index - 1) % len(templates)]
    breakdown.append(
        {
            "text": "Grammar note",
            "meaning": "This sentence uses N5 polite forms, basic particles, and simple adjective patterns.",
            "function": "learner grammar guidance",
        }
    )
    return {
        "id": f"n5-household-{index:03d}",
        "target_level": "N5",
        "word_id": word["id"],
        "japanese": japanese,
        "english": english_sentence,
        "breakdown": breakdown,
    }


def generate_n5_household_sentences() -> list[dict[str, Any]]:
    """Write one N5 practice sentence for every canonical household word."""
    words = json.loads(WORDS_PATH.read_text(encoding="utf-8"))
    if not isinstance(words, list):
        raise ValueError(f"Expected an array of word records in {WORDS_PATH}")
    records = [sentence_record(index, word) for index, word in enumerate(words, start=1)]
    OUTPUT_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return records


if __name__ == "__main__":
    records = generate_n5_household_sentences()
    print(f"Generated {len(records)} N5 household sentences.")