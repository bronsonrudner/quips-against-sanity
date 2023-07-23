from enum import Enum
from pathlib import Path
from typing import Iterator, Optional

from PIL import Image, ImageDraw, ImageFont


class Colour(Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)


OUTPUT_DIR = Path("output")
SETS_DIR = Path("sets")

TITLE = "Quips Against Sanity"


def create_cardsheet(
    name: Path,
    background: Colour,
    foreground: Colour,
    texts: list[str],
    footer: Optional[str] = None,
    rows: int = 7,
    columns: int = 10,
    card_width: int = 600,
    card_height: int = 900,
    margin: int = 1,
    font_size: int = 60,
    footer_font_size: int = 24,
    text_gap: Optional[int] = None,
    font_file: Optional[str] = None,
    paragraph_spacing: float = 0.65,  # of line height
) -> None:
    if text_gap is None:
        text_gap = font_size
    if font_file is None:
        custom_font_files = list(Path.cwd().glob("*.ttf"))
        if custom_font_files:
            font_file = custom_font_files[0].name
        else:
            font_file = "arial.ttf"

    sheet_width = columns * (card_width + margin * 2)
    sheet_height = rows * (card_height + margin * 2)

    cardsheet = Image.new("RGB", (sheet_width, sheet_height), foreground.value)

    font = ImageFont.truetype(font_file, font_size)
    font_height = font.getbbox("hg")[3]
    footer_text = TITLE
    footer_font = ImageFont.truetype(font_file, footer_font_size)

    footer_text_height = footer_font.getbbox(footer_text or "")[3]
    footer_text_position = (text_gap, card_height - footer_text_height - text_gap)

    card_coords = [(row, col) for row in range(rows) for col in range(columns)]

    for text, (row, col) in zip(texts, card_coords):
        card = Image.new("RGB", (card_width, card_height), background.value)
        draw = ImageDraw.Draw(card)

        x_offset = text_gap
        y_offset = text_gap
        for paragraph in text.split("\n"):
            for line in wrap_text_with_font(paragraph, card_width - 2 * text_gap, font):
                draw.text((x_offset, y_offset), line, font=font, fill=foreground.value)
                y_offset += font_height
            y_offset += int(font_height * paragraph_spacing)

        if footer:
            draw.text(footer_text_position, footer_text, font=footer_font, fill=foreground.value)

        card_x = margin + col * (card_width + 2 * margin)
        card_y = margin + row * (card_height + 2 * margin)
        card_position = (card_x, card_y)
        cardsheet.paste(card, card_position)

    cardsheet.save(name)


def wrap_text_with_font(text: str, line_width: int, font: ImageFont.FreeTypeFont) -> Iterator[str]:
    words = iter(text.split(" "))
    current_line = [next(words)]
    for word in words:
        width = font.getlength(" ".join(current_line + [word]))
        if width <= line_width:
            current_line.append(word)
        else:
            yield " ".join(current_line)
            current_line = [word]
    yield " ".join(current_line)


def batch(items: list, size: int) -> Iterator[list]:
    for i in range(0, len(items), size):
        yield items[i : i + size]
