"""Create a printable 8 x 10 inch sheet of household-object sticky notes."""

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    from .vocab_objects_data import HOUSEHOLD_OBJECTS
except ImportError:
    from vocab_objects_data import HOUSEHOLD_OBJECTS


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
DEFAULT_OUTPUT = PROJECT_ROOT / "docs" / "household_objects" / "sticky_notes_12"
FONT_PATH = Path("C:/Windows/Fonts/YuGothM.ttc")


def load_note_data(hash_csv: Path = HASH_CSV) -> list[dict[str, str]]:
    """Load word/hash rows and attach their source sentences."""
    entries_by_word = {str(entry["word"]): entry for entry in HOUSEHOLD_OBJECTS}
    with hash_csv.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError(f"No word/hash rows found in {hash_csv}")

    notes = []
    for row in rows:
        word = row["word"]
        word_hash = row["hash"]
        if word not in entries_by_word:
            raise KeyError(f"No sentence found for word: {word}")
        qr_path = QR_DIRECTORY / f"{word_hash}_qr.png"
        if not qr_path.exists():
            raise FileNotFoundError(f"QR code not found: {qr_path}")
        entry = entries_by_word[word]
        notes.append({
            "word": word,
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
    output_base: str | Path = DEFAULT_OUTPUT,
) -> tuple[Path, Path]:
    """Render one 8 x 10 PNG and PDF containing up to 12 sticky notes."""
    output_base = Path(output_base)
    output_base.parent.mkdir(parents=True, exist_ok=True)
    page = Image.new("RGB", PAGE_SIZE, "white")
    draw = ImageDraw.Draw(page)
    word_font_size = 70
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
        english_word = next(entry["english_word"] for entry in HOUSEHOLD_OBJECTS if str(entry["word"]) == note["word"])
        english_font = fit_font(draw, english_word, english_font_size, text_width)
        english_lines = wrap_text(draw, english_word, english_font, text_width)
        english_y = y + 115
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

    png_path = output_base.with_suffix(".png")
    pdf_path = output_base.with_suffix(".pdf")
    page.save(png_path, dpi=(DPI, DPI))
    page.save(pdf_path, "PDF", resolution=DPI)
    return png_path, pdf_path


def create_sticky_notes_pages(
    output_base: str | Path = DEFAULT_OUTPUT,
    hash_csv: str | Path = HASH_CSV,
) -> list[tuple[Path, Path]]:
    """Create printable sheets for every word/hash pair in the CSV."""
    output_base = Path(output_base)
    notes = load_note_data(Path(hash_csv))
    output_paths = []
    for page_number in range(0, len(notes), NOTE_COUNT):
        page_notes = notes[page_number:page_number + NOTE_COUNT]
        page_base = output_base.parent / f"{output_base.name}_{page_number // NOTE_COUNT + 1:02d}"
        output_paths.append(render_sticky_notes_sheet(page_notes, page_base))
    return output_paths


if __name__ == "__main__":
    for png_path, pdf_path in create_sticky_notes_pages():
        print(f"Created {png_path}")
        print(f"Created {pdf_path}")
