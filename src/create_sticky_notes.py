"""Create a printable 8 x 10 inch sheet of household-object sticky notes."""

import csv
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    from .vocabulary_repository import load_household_objects
except ImportError:
    from vocabulary_repository import load_household_objects


PAGE_WIDTH_INCHES = 8
PAGE_HEIGHT_INCHES = 10
DPI = 300
PAGE_SIZE = (PAGE_WIDTH_INCHES * DPI, PAGE_HEIGHT_INCHES * DPI)
NOTE_COUNT = 12
COLUMNS = 3
ROWS = 4
NOTE_SIZE = 660
NOTE_GAP = 30

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HASH_CSV = Path(__file__).resolve().parent / "vocab_objects_hash.csv"
QR_DIRECTORY = Path(__file__).resolve().parent / "qrcodes"
DEFAULT_OUTPUT = PROJECT_ROOT / "docs" / "household_objects" / "sticky_notes"
FONT_PATH = Path("C:/Windows/Fonts/YuGothM.ttc")


def load_note_data(hash_csv: Path = HASH_CSV, level: str | None = None) -> list[dict[str, str]]:
    """Load level-aware word/hash rows and attach their source sentences."""
    with hash_csv.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError(f"No word/hash rows found in {hash_csv}")

    selected_level = level.lower() if level else None
    rows = [row for row in rows if selected_level is None or row.get("level", "n4").lower() == selected_level]
    if not rows:
        requested_level = level.upper() if level else "all levels"
        raise ValueError(f"No word/hash rows found for {requested_level} in {hash_csv}")

    entries_by_level = {}
    notes = []
    for row in rows:
        word = row["word"]
        word_hash = row["hash"]
        row_level = row.get("level", "n4")
        filename = row.get("filename", f"{word_hash}.html")
        if row_level not in entries_by_level:
            entries_by_level[row_level] = {
                str(entry["word"]): entry for entry in load_household_objects(row_level)
            }
        entries_by_word = entries_by_level[row_level]
        if word not in entries_by_word:
            raise KeyError(f"No {row_level.upper()} sentence found for word: {word}")
        qr_path = QR_DIRECTORY / row_level.upper() / f"{Path(filename).stem}_qr.png"
        if not qr_path.exists():
            raise FileNotFoundError(f"QR code not found: {qr_path}")
        entry = entries_by_word[word]
        notes.append({
            "word": word,
            "hiragana": str(entry["hiragana"]),
            "english_word": str(entry["english_word"]),
            "level": row_level,
            "hash": word_hash,
            "sentence": str(entry["sentence"]),
            "english_sentence": str(entry["english_sentence"]),
            "qr_path": str(qr_path),
        })
    return notes


def load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load a Japanese-capable font available on the Windows host."""
    candidates = [FONT_PATH, Path("C:/Windows/Fonts/msgothic.ttc")]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    raise FileNotFoundError("A Japanese-capable font was not found in C:/Windows/Fonts")


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap Japanese text by character so it fits within a note."""
    lines = []
    current = ""
    punctuation = "、。！？）」』】］〉》」』】》"
    for character in text:
        candidate = current + character
        if current and draw.textbbox((0, 0), candidate, font=font)[2] > max_width:
            if character in punctuation:
                current += character
            else:
                lines.append(current)
                current = character
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def wrap_english_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap English text at spaces without splitting words."""
    lines = []
    current = ""
    for word in text.split():
        candidate = word if not current else f"{current} {word}"
        if current and draw.textbbox((0, 0), candidate, font=font)[2] > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def fit_font(draw: ImageDraw.ImageDraw, text: str, size: int, max_width: int) -> ImageFont.FreeTypeFont:
    """Return the largest configured font size that fits one line."""
    while size > 20 and draw.textbbox((0, 0), text, font=load_font(size))[2] > max_width:
        size -= 2
    return load_font(size)


def render_sticky_notes_sheet(
    notes: list[dict[str, str]],
) -> Image.Image:
    """Render one 8 x 10 sticky-note sheet in memory."""
    page = Image.new("RGB", PAGE_SIZE, "white")
    draw = ImageDraw.Draw(page)
    word_font_size = 70
    hiragana_font = load_font(40)
    english_font_size = 50
    sentence_font = load_font(36)
    english_sentence_font = load_font(34)
    qr_size = 320
    note_colors = ["#fff2a8", "#d9f4ff", "#ffe0d2", "#e4f5d0"]
    total_width = COLUMNS * NOTE_SIZE + (COLUMNS - 1) * NOTE_GAP
    total_height = ROWS * NOTE_SIZE + (ROWS - 1) * NOTE_GAP
    left = (PAGE_SIZE[0] - total_width) // 2
    top = (PAGE_SIZE[1] - total_height) // 2

    for index, note in enumerate(notes):
        column = index % COLUMNS
        row = index // COLUMNS
        x = left + column * (NOTE_SIZE + NOTE_GAP)
        y = top + row * (NOTE_SIZE + NOTE_GAP)
        draw.rectangle((x, y, x + NOTE_SIZE, y + NOTE_SIZE), fill=note_colors[index % len(note_colors)], outline="#c5b96b", width=3)

        qr_x = x + NOTE_SIZE - qr_size - 25
        text_width = qr_x - x - 50
        word_font = fit_font(draw, note["word"], word_font_size, text_width)
        draw.text((x + 30, y + 25), note["word"], fill="#17202a", font=word_font)
        draw.text((x + 30, y + 115), note["hiragana"], fill="#425466", font=hiragana_font)
        english_font = fit_font(draw, note["english_word"], english_font_size, text_width)
        english_lines = wrap_text(draw, note["english_word"], english_font, text_width)
        english_y = y + 165
        for line in english_lines[:2]:
            draw.text((x + 30, english_y), line, fill="#425466", font=english_font)
            english_y += 58

        qr_image = Image.open(note["qr_path"]).convert("RGB")
        qr_image.thumbnail((qr_size, qr_size), Image.Resampling.LANCZOS)
        qr_x = x + NOTE_SIZE - qr_image.width - 25
        qr_y = y + 25
        page.paste(qr_image, (qr_x, qr_y))

        sentence_lines = wrap_text(draw, note["sentence"], sentence_font, NOTE_SIZE - 60)
        sentence_y = y + 375
        for line in sentence_lines[:4]:
            draw.text((x + 30, sentence_y), line, fill="#17202a", font=sentence_font)
            sentence_y += 52

        english_sentence_lines = wrap_english_text(draw, note["english_sentence"], english_sentence_font, NOTE_SIZE - 60)
        english_sentence_y = sentence_y + 12
        for line in english_sentence_lines[:3]:
            draw.text((x + 30, english_sentence_y), line, fill="#425466", font=english_sentence_font)
            english_sentence_y += 48

    return page


def create_sticky_notes_pdf(
    output_base: str | Path = DEFAULT_OUTPUT,
    hash_csv: str | Path = HASH_CSV,
    level: str | None = None,
) -> Path:
    """Create one multi-page PDF for the selected JLPT level."""
    output_base = Path(output_base)
    notes = load_note_data(Path(hash_csv), level)
    selected_level = level.lower() if level else "all"
    pages = []
    for page_number in range(0, len(notes), NOTE_COUNT):
        page_notes = notes[page_number:page_number + NOTE_COUNT]
        pages.append(render_sticky_notes_sheet(page_notes))

    pdf_path = output_base.parent / f"{output_base.name}_{selected_level}.pdf"
    pages[0].save(pdf_path, "PDF", resolution=DPI, save_all=True, append_images=pages[1:])
    for page in pages:
        page.close()
    return pdf_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a combined JLPT sticky-notes PDF.")
    parser.add_argument("--level", metavar="N", help="JLPT level to generate, for example N4")
    arguments = parser.parse_args()
    pdf_path = create_sticky_notes_pdf(level=arguments.level)
    print(f"Created {pdf_path}")
