"""Common household object vocabulary for Japanese learners."""

import csv
import hashlib
import html
import argparse
from pathlib import Path

try:
    from .vocabulary_repository import load_household_objects
except ImportError:
    from vocabulary_repository import load_household_objects


BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
JLPT_LEVELS = ("n5", "n4", "n3", "n2", "n1")


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


def build_household_object_html(
    entry: dict[str, object],
    next_page: str = "#",
    home_page: str = "../index.html",
    level_pages: dict[str, str] | None = None,
    active_level: str | None = None,
) -> str:
        """Build one styled HTML page for a household-object vocabulary entry."""
        word = html.escape(str(entry["word"]))
        hiragana = html.escape(str(entry["hiragana"]))
        english_word = html.escape(str(entry["english_word"]))
        sentence = html.escape(str(entry["sentence"]))
        sentence = sentence.replace(word, f'<span class="target-word">{word}</span>')
        english_sentence = html.escape(str(entry["english_sentence"]))
        next_page = html.escape(next_page, quote=True)
        home_page = html.escape(home_page, quote=True)
        level_pages = level_pages or {}
        active_level = active_level.lower() if active_level else None
        level_buttons = "".join(
            (
                f'<button class="level-button{" active" if level == active_level else ""}" type="button" data-url="{html.escape(level_pages[level], quote=True)}">{level.upper()}</button>'
                if level in level_pages
                else f'<button class="level-button unavailable" type="button" data-level="{level.upper()}">{level.upper()}</button>'
            )
            for level in JLPT_LEVELS
        )
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
            padding: clamp(0.5rem, 2vw, 1rem);
            min-height: 100vh;
            overflow-x: hidden;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            color: var(--ink);
            background: var(--bg);
        }}
        .page-tabs, .app {{ width: 100%; max-width: 980px; margin: 0 auto; }}
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
        .target-word {{ text-decoration: underline; text-decoration-color: var(--accent); text-decoration-thickness: 0.14em; text-underline-offset: 0.16em; }}
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
        .sentence-actions {{ display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; margin-top: 0.75rem; }}
        .sentence-actions .speak-button {{ margin-top: 0; }}
        .level-button {{ min-width: 2.8rem; padding: 0.55rem 0.7rem; border: 1px solid #0f766e; border-radius: 8px; color: #134e4a; background: #f0fdfa; font-weight: 700; cursor: pointer; }}
        .level-button:hover {{ background: var(--accent-soft); }}
        .level-button.active {{ color: #ffffff; background: var(--accent); border-color: var(--accent); }}
        .level-button.unavailable {{ border-color: #cbd5e1; color: #64748b; background: #f8fafc; }}
        .level-message {{ min-height: 1.25rem; margin: 0.5rem 0 0; color: #b45309; font-size: 0.9rem; }}
        .table-wrap {{ overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 0.65rem; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
        th:first-child, td:first-child {{ width: 1%; white-space: nowrap; }}
        th {{ color: #134e4a; background: var(--accent-soft); }}
        tr:last-child td {{ border-bottom: 0; }}
        @media (max-width: 600px) {{
            .page-tabs {{ flex-wrap: wrap; }}
            .page-tab {{ min-width: 45%; }}
            .app {{ border-radius: 8px; }}
            .header, .content, .panel {{ padding: 0.75rem; }}
            h1 {{ font-size: 1.5rem; overflow-wrap: anywhere; }}
            .sentence {{ font-size: 1.1rem; }}
            .table-wrap {{ width: 100%; }}
            table {{ min-width: 620px; }}
            th, td {{ padding: 0.5rem 0.35rem; font-size: 0.9rem; }}
        }}
    </style>
</head>
<body>
    <nav class="page-tabs" aria-label="Page tabs">
        <a class="page-tab" href="{home_page}">Home</a>
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
                <div class="sentence-actions">
                    <button class="speak-button" id="speakSentenceButton" type="button">Speak sentence</button>
                    {level_buttons}
                </div>
                <p class="level-message" id="levelMessage" aria-live="polite"></p>
            </article>
            <article class="panel">
                <span class="label">English sentence</span>
                <div class="translation">{english_sentence}</div>
            </article>
            <article class="panel">
                <span class="label">Sentence breakdown</span>
                <div class="table-wrap">
                    <table>
                        <thead><tr><th>Japanese</th><th>Pronounce</th><th>Meaning</th><th>Function</th></tr></thead>
                        <tbody>{breakdown_rows}</tbody>
                    </table>
                </div>
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

        document.querySelectorAll(".level-button").forEach((button) => {{
            button.addEventListener("click", () => {{
                if (button.dataset.url) {{
                    window.location.assign(button.dataset.url);
                    return;
                }}
                document.getElementById("levelMessage").textContent = `${{button.dataset.level}} level sentence not available yet`;
            }});
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
    refresh_qr: bool = False,
    level: str = "N4",
) -> list[Path]:
    """Create level-prefixed household-object HTML pages and QR codes."""
    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative or None")

    level = level.lower()
    if level not in JLPT_LEVELS:
        raise ValueError(f"Unsupported JLPT level: {level}")
    topic = "household"
    output_dir = output_dir or Path(__file__).resolve().parent.parent / "docs" / "household_objects" / level
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_paths = []
    seen_hashes = {}
    site_url = f"https://ayhkusa.github.io/jlpt_tutor/household_objects/{level}"
    qr_output_dir = Path(__file__).resolve().parent / "qrcodes" / level.upper()
    qr_output_dir.mkdir(parents=True, exist_ok=True)

    all_entries = load_household_objects(level)
    entries = all_entries if limit is None else all_entries[:limit]
    hash_by_word = {
        str(entry["word"]): sentence_to_base62_hash(str(entry["word"]))
        for entry in all_entries
    }
    hash_pairs = dict(hash_by_word)
    page_root = output_dir.parent
    for entry in entries:
        word = str(entry["word"])
        word_hash = hash_by_word[word]
        filename = f"{level}-{topic}-{word_hash}.html"
        if filename in seen_hashes and seen_hashes[filename] != word:
            raise ValueError(f"Hash collision for {filename}")
        seen_hashes[filename] = word
        output_path = output_dir / filename
        entry_index = all_entries.index(entry)
        next_entry = all_entries[(entry_index + 1) % len(all_entries)]
        next_filename = f"{level}-{topic}-{hash_by_word[str(next_entry['word'])]}.html"
        level_pages = {}
        for candidate_level in JLPT_LEVELS:
            candidate_filename = f"{candidate_level}-{topic}-{word_hash}.html"
            candidate_path = page_root / candidate_level / candidate_filename
            if candidate_level == level or candidate_path.exists():
                level_pages[candidate_level] = f"../{candidate_level}/{candidate_filename}"
        output_path.write_text(
            build_household_object_html(entry, next_filename, "../../index.html", level_pages, level),
            encoding="utf-8",
        )
        qr_path = qr_output_dir / f"{output_path.stem}_qr.png"
        if refresh_qr or not qr_path.exists():
            create_qr_code(f"{site_url}/{filename}", qr_path)
        generated_paths.append(output_path)

    hash_file = Path(__file__).resolve().parent / "vocab_objects_hash.csv"
    existing_rows = []
    if hash_file.exists():
        with hash_file.open(newline="", encoding="utf-8") as file:
            existing_rows = [row for row in csv.DictReader(file) if row.get("level") != level]
    new_rows = [
        {
            "level": level,
            "topic": topic,
            "word": word,
            "hash": word_hash,
            "filename": f"{level}-{topic}-{word_hash}.html",
        }
        for word, word_hash in hash_pairs.items()
    ]
    with hash_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["level", "topic", "word", "hash", "filename"])
        writer.writerows(
            (row["level"], row["topic"], row["word"], row["hash"], row["filename"])
            for row in [*existing_rows, *new_rows]
        )

    return generated_paths


def main() -> None:
    """Generate one household-object page, or all pages when requested."""
    parser = argparse.ArgumentParser(description="Generate JLPT household-object vocabulary pages.")
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
    parser.add_argument(
        "--refresh-qr",
        action="store_true",
        help="regenerate QR codes for the current level-aware page URLs",
    )
    parser.add_argument(
        "--level",
        choices=[level.upper() for level in JLPT_LEVELS],
        default="N4",
        help="JLPT level to generate (default: N4)",
    )
    arguments = parser.parse_args()
    limit = None if arguments.all else (arguments.limit if arguments.limit is not None else 1)
    generated_paths = generate_household_object_pages(
        limit=limit,
        refresh_qr=arguments.refresh_qr,
        level=arguments.level,
    )
    print(f"Generated {len(generated_paths)} {arguments.level} household-object page(s).")


if __name__ == "__main__":
    main()


