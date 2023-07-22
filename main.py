from enum import Enum
from pathlib import Path
from typing import Iterable, Iterator

from PIL import Image, ImageDraw, ImageFont

NUM_ROWS = 7
NUM_COLUMNS = 10

CARD_WIDTH = 600
CARD_HEIGHT = 900
MARGIN = 1
FONT_SIZE = 60
FOOTER_FONT_SIZE = 24
TEXT_GAP = FONT_SIZE

RGB_BLACK = (0, 0, 0)
RGB_WHITE = (255, 255, 255)

FONT_FILE = "arial.ttf"

OUTPUT_DIR = Path("output")
SETS_DIR = Path("sets")

TITLE = "Quips Against Sanity"


class CardType(Enum):
    WHITE = "white"
    BLACK = "black"


def main():
    override_font()
    OUTPUT_DIR.mkdir(exist_ok=True)

    for card_type in CardType:
        create_cardback(OUTPUT_DIR / f"back_{card_type.value}.png", card_type)

    for cat in SETS_DIR.iterdir():
        card_type = CardType(cat.stem.split("_")[-1])
        cards = cat.read_text().splitlines()
        for i, card_batch in enumerate(_batch(cards, NUM_ROWS * NUM_COLUMNS)):
            name = OUTPUT_DIR / f"{cat.stem}_{i}_{len(card_batch)}.png"
            create_cardsheet(name, card_type, card_batch)


def override_font() -> None:
    global FONT_FILE
    custom_font_files = list(Path.cwd().glob("*.ttf"))
    if custom_font_files:
        FONT_FILE = custom_font_files[0].name


def _batch(items: list, size: int) -> Iterator[list]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def create_cardsheet(name: Path, card_type: CardType, card_texts: Iterable[str]) -> None:
    sheet_width = NUM_COLUMNS * (CARD_WIDTH + MARGIN * 2)
    sheet_height = NUM_ROWS * (CARD_HEIGHT + MARGIN * 2)

    if card_type == CardType.WHITE:
        background_color = RGB_WHITE
        text_color = RGB_BLACK
    else:
        background_color = RGB_BLACK
        text_color = RGB_WHITE

    cardsheet = Image.new("RGB", (sheet_width, sheet_height), text_color)

    font = ImageFont.truetype(FONT_FILE, FONT_SIZE)
    font_height = font.getbbox("hg")[3]
    footer_text = TITLE
    footer_font = ImageFont.truetype(FONT_FILE, FOOTER_FONT_SIZE)

    footer_text_height = footer_font.getbbox(footer_text)[3]
    footer_text_position = (TEXT_GAP, CARD_HEIGHT - footer_text_height - TEXT_GAP)

    card_coords = [(row, col) for row in range(NUM_ROWS) for col in range(NUM_COLUMNS)]

    for text, (row, col) in zip(card_texts, card_coords):
        card = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), background_color)
        draw = ImageDraw.Draw(card)

        for i, line in enumerate(wrap_text_with_font(text.replace("_", "________"), CARD_WIDTH - 2 * TEXT_GAP, font)):
            draw.text((TEXT_GAP, TEXT_GAP + i * font_height), line, font=font, fill=text_color)

        draw.text(footer_text_position, footer_text, font=footer_font, fill=text_color)

        card_x = MARGIN + col * (CARD_WIDTH + 2 * MARGIN)
        card_y = MARGIN + row * (CARD_HEIGHT + 2 * MARGIN)
        card_position = (card_x, card_y)
        cardsheet.paste(card, card_position)

    cardsheet.save(name)


def create_cardback(name: Path, card_type: CardType) -> None:
    sheet_width = CARD_WIDTH + MARGIN * 2
    sheet_height = CARD_HEIGHT + MARGIN * 2

    if card_type == CardType.WHITE:
        background_color = RGB_WHITE
        text_color = RGB_BLACK
    else:
        background_color = RGB_BLACK
        text_color = RGB_WHITE

    card = Image.new("RGB", (sheet_width, sheet_height), background_color)
    draw = ImageDraw.Draw(card)

    font = ImageFont.truetype(FONT_FILE, FONT_SIZE * 2)
    font_height = font.getbbox("hg")[3]

    for i, line in enumerate(wrap_text_with_font(TITLE, CARD_WIDTH - 2 * TEXT_GAP, font)):
        draw.text((TEXT_GAP, TEXT_GAP + i * font_height), line, font=font, fill=text_color)

    card.save(name)


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


if __name__ == "__main__":
    main()
