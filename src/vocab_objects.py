"""Common household object vocabulary for Japanese learners."""

import hashlib
import html
from pathlib import Path


BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def sentence_to_base62_hash(sentence: str) -> str:
    """Return a deterministic 12-character Base62 hash for a sentence."""
    digest_number = int.from_bytes(hashlib.sha256(sentence.encode("utf-8")).digest(), "big")
    hash_number = digest_number % (62**12)
    characters = []

    for _ in range(12):
        hash_number, remainder = divmod(hash_number, 62)
        characters.append(BASE62_ALPHABET[remainder])

    return "".join(reversed(characters))


def build_household_object_html(entry: dict[str, object]) -> str:
        """Build one styled HTML page for a household-object vocabulary entry."""
        word = html.escape(str(entry["word"]))
        english_word = html.escape(str(entry["english_word"]))
        sentence = html.escape(str(entry["sentence"]))
        english_sentence = html.escape(str(entry["english_sentence"]))
        breakdown_rows = "".join(
                "<tr>"
                f"<td>{html.escape(str(component['text']))}</td>"
                f"<td>{html.escape(str(component['meaning']))}</td>"
                f"<td>{html.escape(str(component['function']))}</td>"
                "</tr>"
                for component in entry["breakdown"]
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{english_word} | Japanese Household Vocabulary</title>
    <style>
        :root {{
            --bg: #f7f8f3;
            --panel: #ffffff;
            --ink: #1f2937;
            --muted: #6b7280;
            --accent: #0f766e;
            --accent-soft: #ccfbf1;
            --line: #d1d5db;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            padding: 1rem;
            min-height: 100vh;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            color: var(--ink);
            background: var(--bg);
        }}
        .page-tabs, .app {{ width: min(980px, 100%); margin: 0 auto; }}
        .page-tabs {{
            display: flex;
            gap: 0.5rem;
            padding: 0.25rem;
            margin-bottom: 1rem;
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 12px;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
        }}
        .page-tab {{
            flex: 1;
            padding: 0.55rem 0.8rem;
            border: 1px solid #99f6e4;
            border-radius: 9px;
            color: #134e4a;
            background: #f0fdfa;
            text-align: center;
            text-decoration: none;
            font-weight: 700;
            font-size: 0.92rem;
        }}
        .page-tab.active {{
            color: #ffffff;
            background: linear-gradient(135deg, #0f766e, #0ea5a4);
            border-color: transparent;
        }}
        .app {{
            overflow: hidden;
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 16px;
            box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
        }}
        .header {{
            padding: 1.25rem;
            color: #f0fdfa;
            background: linear-gradient(135deg, #0f766e, #0ea5a4);
        }}
        h1 {{ margin: 0; font-size: 1.6rem; }}
        .japanese {{ margin: 0.65rem 0 0; font-size: 1.5rem; font-weight: 700; }}
        .content {{ display: grid; gap: 1rem; padding: 1rem; }}
        .panel {{ padding: 1rem; background: #fcfcfb; border: 1px solid var(--line); border-radius: 12px; }}
        .label {{
            display: block;
            margin-bottom: 0.35rem;
            color: #64748b;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}
        .sentence {{ font-size: 1.2rem; line-height: 1.7; }}
        .translation {{ color: #b45309; line-height: 1.6; }}
        .speak-button {{
            margin-top: 0.75rem;
            padding: 0.55rem 0.8rem;
            border: 0;
            border-radius: 10px;
            color: #ffffff;
            background: var(--accent);
            font-weight: 700;
            cursor: pointer;
        }}
        .speak-button:hover {{ filter: brightness(1.06); }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 0.65rem; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
        th {{ color: #134e4a; background: var(--accent-soft); }}
        tr:last-child td {{ border-bottom: 0; }}
        @media (max-width: 600px) {{
            .page-tabs {{ flex-wrap: wrap; }}
            .page-tab {{ min-width: 45%; }}
            th, td {{ padding: 0.5rem 0.35rem; font-size: 0.9rem; }}
        }}
    </style>
</head>
<body>
    <nav class="page-tabs" aria-label="Page tabs">
        <a class="page-tab" href="../hiragana_phase.html">Hiragana Phrases</a>
        <a class="page-tab active" href="#">Household Object</a>
    </nav>
    <main class="app">
        <header class="header">
            <h1>{english_word}</h1>
            <p class="japanese">{word}</p>
        </header>
        <section class="content">
            <article class="panel">
                <span class="label">Japanese sentence</span>
                <div class="sentence">{sentence}</div>
                <button class="speak-button" id="speakSentenceButton" type="button">Speak sentence</button>
            </article>
            <article class="panel">
                <span class="label">English sentence</span>
                <div class="translation">{english_sentence}</div>
            </article>
            <article class="panel">
                <span class="label">Sentence breakdown</span>
                <table>
                    <thead><tr><th>Japanese</th><th>Meaning</th><th>Function</th></tr></thead>
                    <tbody>{breakdown_rows}</tbody>
                </table>
            </article>
        </section>
    </main>
    <script>
        document.getElementById("speakSentenceButton").addEventListener("click", () => {{
            const sentence = document.querySelector(".sentence").textContent;
            const utterance = new SpeechSynthesisUtterance(sentence);
            utterance.lang = "ja-JP";
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(utterance);
        }});
    </script>
</body>
</html>
"""


def generate_household_object_pages(output_dir: Path | None = None) -> list[Path]:
        """Create one hash-named HTML file for each household-object sentence."""
        output_dir = output_dir or Path(__file__).resolve().parent.parent / "docs" / "household_objects"
        output_dir.mkdir(parents=True, exist_ok=True)
        generated_paths = []
        seen_hashes = {}

        for entry in HOUSEHOLD_OBJECTS:
                sentence = str(entry["sentence"])
                filename = f"{sentence_to_base62_hash(sentence)}.html"
                if filename in seen_hashes and seen_hashes[filename] != sentence:
                        raise ValueError(f"Hash collision for {filename}")
                seen_hashes[filename] = sentence
                output_path = output_dir / filename
                output_path.write_text(build_household_object_html(entry), encoding="utf-8")
                generated_paths.append(output_path)

        return generated_paths


HOUSEHOLD_OBJECTS = [
    {
        "word": "テーブル",
        "english_word": "table",
        "sentence": "家族とテーブルで晩ご飯を食べます。",
        "english_sentence": "I eat dinner at the table with my family.",
        "breakdown": [
            {"text": "家族と", "meaning": "with my family", "function": "companion phrase"},
            {"text": "テーブルで", "meaning": "at the table", "function": "location phrase"},
            {"text": "晩ご飯を", "meaning": "dinner", "function": "object"},
            {"text": "食べます", "meaning": "eat", "function": "polite verb"},
        ],
    },
    {
        "word": "いす",
        "english_word": "chair",
        "sentence": "このいすは長く座っても疲れません。",
        "english_sentence": "I do not get tired even after sitting in this chair for a long time.",
        "breakdown": [
            {"text": "この", "meaning": "this", "function": "determiner"},
            {"text": "いすは", "meaning": "chair", "function": "topic"},
            {"text": "長く", "meaning": "for a long time", "function": "adverb"},
            {"text": "座っても", "meaning": "even after sitting", "function": "concessive phrase"},
            {"text": "疲れません", "meaning": "do not get tired", "function": "polite negative verb"},
        ],
    },
    {
        "word": "つくえ",
        "english_word": "desk",
        "sentence": "つくえの上にノートパソコンを置きました。",
        "english_sentence": "I put my laptop on the desk.",
        "breakdown": [
            {"text": "つくえの上に", "meaning": "on the desk", "function": "destination phrase"},
            {"text": "ノートパソコンを", "meaning": "laptop", "function": "object"},
            {"text": "置きました", "meaning": "put", "function": "polite past verb"},
        ],
    },
    {
        "word": "ベッド",
        "english_word": "bed",
        "sentence": "疲れていたので、ベッドですぐ寝ました。",
        "english_sentence": "I was tired, so I fell asleep in bed right away.",
        "breakdown": [
            {"text": "疲れていたので", "meaning": "because I was tired", "function": "reason clause"},
            {"text": "ベッドで", "meaning": "in bed", "function": "location phrase"},
            {"text": "すぐ", "meaning": "right away", "function": "adverb"},
            {"text": "寝ました", "meaning": "slept", "function": "polite past verb"},
        ],
    },
    {
        "word": "まくら",
        "english_word": "pillow",
        "sentence": "旅行にまくらを持っていきます。",
        "english_sentence": "I take my pillow with me when I travel.",
        "breakdown": [
            {"text": "旅行に", "meaning": "on a trip", "function": "occasion phrase"},
            {"text": "まくらを", "meaning": "pillow", "function": "object"},
            {"text": "持っていきます", "meaning": "take along", "function": "polite verb"},
        ],
    },
    {
        "word": "かがみ",
        "english_word": "mirror",
        "sentence": "出かける前に、かがみで服を確認します。",
        "english_sentence": "I check my clothes in the mirror before going out.",
        "breakdown": [
            {"text": "出かける前に", "meaning": "before going out", "function": "time phrase"},
            {"text": "かがみで", "meaning": "in the mirror", "function": "means phrase"},
            {"text": "服を", "meaning": "clothes", "function": "object"},
            {"text": "確認します", "meaning": "check", "function": "polite verb"},
        ],
    },
    {
        "word": "れいぞうこ",
        "english_word": "refrigerator",
        "sentence": "買ってきた野菜をれいぞうこに入れました。",
        "english_sentence": "I put the vegetables I bought in the refrigerator.",
        "breakdown": [
            {"text": "買ってきた", "meaning": "bought and brought back", "function": "describes 野菜"},
            {"text": "野菜を", "meaning": "vegetables", "function": "object"},
            {"text": "れいぞうこに", "meaning": "into the refrigerator", "function": "destination phrase"},
            {"text": "入れました", "meaning": "put in", "function": "polite past verb"},
        ],
    },
    {
        "word": "せんたくき",
        "english_word": "washing machine",
        "sentence": "せんたくきが止まったので、電源を確認しました。",
        "english_sentence": "The washing machine stopped, so I checked the power.",
        "breakdown": [
            {"text": "せんたくきが", "meaning": "washing machine", "function": "subject"},
            {"text": "止まったので", "meaning": "because it stopped", "function": "reason clause"},
            {"text": "電源を", "meaning": "power", "function": "object"},
            {"text": "確認しました", "meaning": "checked", "function": "polite past verb"},
        ],
    },
    {
        "word": "そうじき",
        "english_word": "vacuum cleaner",
        "sentence": "私のそうじきが動かないので、床をほうきで掃きました。",
        "english_sentence": "My vacuum cleaner was not working, so I swept the floor with a broom.",
        "breakdown": [
            {"text": "私の", "meaning": "my", "function": "possessive phrase"},
            {"text": "そうじきが", "meaning": "vacuum cleaner", "function": "subject"},
            {"text": "動かないので", "meaning": "because it does not work", "function": "reason clause"},
            {"text": "床を", "meaning": "floor", "function": "object"},
            {"text": "ほうきで", "meaning": "with a broom", "function": "means phrase"},
            {"text": "掃きました", "meaning": "swept", "function": "polite past verb"},
        ],
    },
    {
        "word": "でんき",
        "english_word": "light",
        "sentence": "寝る前に、部屋のでんきを消してください。",
        "english_sentence": "Please turn off the room light before going to bed.",
        "breakdown": [
            {"text": "寝る前に", "meaning": "before going to bed", "function": "time phrase"},
            {"text": "部屋の", "meaning": "room's", "function": "possessive phrase"},
            {"text": "でんきを", "meaning": "light", "function": "object"},
            {"text": "消してください", "meaning": "please turn off", "function": "polite request"},
        ],
    },
]
