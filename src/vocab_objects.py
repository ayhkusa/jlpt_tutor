"""Common household object vocabulary for Japanese learners."""

import csv
import hashlib
import html
import argparse
from pathlib import Path

try:
    from .vocab_objects_data import HOUSEHOLD_OBJECTS
except ImportError:
    from vocab_objects_data import HOUSEHOLD_OBJECTS


BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def create_qr_code(url: str, output_path: str | Path = "qr_code.png") -> Path:
    """Create a PNG QR code that opens ``url`` when scanned."""
    try:
        import qrcode
    except ImportError as error:
        raise RuntimeError("Install the QR-code dependency with: pip install 'qrcode[pil]'") from error

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    qr_code = qrcode.make(url)
    qr_code.save(output_path)
    return output_path


def sentence_to_base62_hash(word: str) -> str:
    """Return a deterministic 12-character Base62 hash for a word."""
    digest_number = int.from_bytes(hashlib.sha256(word.encode("utf-8")).digest(), "big")
    hash_number = digest_number % (62**12)
    characters = []

    for _ in range(12):
        hash_number, remainder = divmod(hash_number, 62)
        characters.append(BASE62_ALPHABET[remainder])

    return "".join(reversed(characters))


def build_breakdown_row(component: dict[str, str]) -> str:
    japanese_text = html.escape(str(component["text"]), quote=True)
    pronounce_button = ""
    if component["text"] != "Grammar note":
        pronounce_button = (
            f'<button class="speak-button row-speak-button" type="button" '
            f'data-japanese="{japanese_text}">Pronounce</button>'
        )
    return (
        "<tr>"
        f"<td>{japanese_text}</td>"
        f"<td>{pronounce_button}</td>"
        f"<td>{html.escape(str(component['meaning']))}</td>"
        f"<td>{html.escape(str(component['function']))}</td>"
        "</tr>"
    )


def build_household_object_html(entry: dict[str, object], next_page: str = "#") -> str:
        """Build one styled HTML page for a household-object vocabulary entry."""
        word = html.escape(str(entry["word"]))
        hiragana = html.escape(str(entry["hiragana"]))
        english_word = html.escape(str(entry["english_word"]))
        sentence = html.escape(str(entry["sentence"]))
        english_sentence = html.escape(str(entry["english_sentence"]))
        next_page = html.escape(next_page, quote=True)
        breakdown_rows = "".join(
            build_breakdown_row(component)
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
        h1 {{ margin: 0; font-size: 2rem; }}
        .japanese {{ margin: 0.65rem 0 0; font-size: 1.5rem; font-weight: 700; }}
        .hiragana {{ margin: 0.15rem 0 0; color: var(--muted); font-size: 1rem; }}
        .english.word {{ margin: 0.35rem 0 0; font-size: 1.2rem; }}
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
        <a class="page-tab" href="../index.html">Home</a>
        <a class="page-tab active" href="{next_page}">Next Word</a>
    </nav>
    <main class="app">
        <header class="header">
            <h1>{word} : {hiragana}</h1>
            <p class="english word">{english_word}</p>
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
                    <thead><tr><th>Japanese</th><th>Pronounce</th><th>Meaning</th><th>Function</th></tr></thead>
                    <tbody>{breakdown_rows}</tbody>
                </table>
                <button class="speak-button" id="speakBreakdownButton" type="button">Pronounce all</button>
            </article>
        </section>
    </main>
    <script>
        let speechRequestId = 0;

        function speakJapanese(text) {{
            const requestId = ++speechRequestId;
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "ja-JP";
            window.speechSynthesis.cancel();
            window.setTimeout(() => {{
                if (requestId === speechRequestId) {{
                    window.speechSynthesis.speak(utterance);
                }}
            }}, 0);
        }}

        document.getElementById("speakSentenceButton").addEventListener("click", () => {{
            const sentence = document.querySelector(".sentence").textContent;
            speakJapanese(sentence);
        }});

        document.getElementById("speakBreakdownButton").addEventListener("click", () => {{
            const breakdown = Array.from(document.querySelectorAll("table tbody tr td:first-child"))
                .filter((cell) => cell.textContent.trim() !== "Grammar note")
                .map((cell) => cell.textContent.trim())
                .join("、");
            speakJapanese(breakdown);
        }});

        document.querySelectorAll(".row-speak-button").forEach((button) => {{
            button.addEventListener("click", () => {{
                speakJapanese(button.dataset.japanese);
            }});
        }});
    </script>
</body>
</html>
"""


def generate_household_object_pages(
    output_dir: Path | None = None,
    limit: int | None = 1,
) -> list[Path]:
    """Create hash-named HTML files for a limited number of vocabulary entries."""
    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative or None")

    output_dir = output_dir or Path(__file__).resolve().parent.parent / "docs" / "household_objects"
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_paths = []
    seen_hashes = {}
    hash_pairs = {}
    site_url = "https://ayhkusa.github.io/jlpt_tutor/household_objects"
    qr_output_dir = Path(__file__).resolve().parent / "qrcodes"
    qr_output_dir.mkdir(parents=True, exist_ok=True)

    entries = HOUSEHOLD_OBJECTS if limit is None else HOUSEHOLD_OBJECTS[:limit]
    hash_by_word = {
        str(entry["word"]): sentence_to_base62_hash(str(entry["word"]))
        for entry in HOUSEHOLD_OBJECTS
    }
    for entry in entries:
        word = str(entry["word"])
        word_hash = hash_by_word[word]
        filename = f"{word_hash}.html"
        if filename in seen_hashes and seen_hashes[filename] != word:
            raise ValueError(f"Hash collision for {filename}")
        seen_hashes[filename] = word
        hash_pairs[word] = word_hash
        output_path = output_dir / filename
        entry_index = HOUSEHOLD_OBJECTS.index(entry)
        next_entry = HOUSEHOLD_OBJECTS[(entry_index + 1) % len(HOUSEHOLD_OBJECTS)]
        next_filename = f"{hash_by_word[str(next_entry['word'])]}.html"
        output_path.write_text(build_household_object_html(entry, next_filename), encoding="utf-8")
        qr_path = qr_output_dir / f"{output_path.stem}_qr.png"
        if not qr_path.exists():
            create_qr_code(f"{site_url}/{filename}", qr_path)
        generated_paths.append(output_path)

    hash_file = Path(__file__).resolve().parent / "vocab_objects_hash.csv"
    with hash_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["word", "hash"])
        writer.writerows(hash_pairs.items())

    return generated_paths


def main() -> None:
    """Generate one household-object page, or all pages when requested."""
    parser = argparse.ArgumentParser(description="Generate household-object vocabulary pages.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--all",
        action="store_true",
        help="generate pages for all household-object entries",
    )
    mode.add_argument(
        "--limit",
        type=int,
        metavar="N",
        help="generate pages for the first N entries",
    )
    arguments = parser.parse_args()
    limit = None if arguments.all else (arguments.limit if arguments.limit is not None else 1)
    generated_paths = generate_household_object_pages(limit=limit)
    print(f"Generated {len(generated_paths)} household-object page(s).")


if __name__ == "__main__":
    main()


