from enum import Enum
from pathlib import Path


from cardsheet import Colour, batch, create_cardsheet


OUTPUT_DIR = Path("output")
SETS_DIR = Path("sets")

TITLE = "Quips Against Sanity"


class CardType(Enum):
    WHITE = (Colour.WHITE, Colour.BLACK)
    BLACK = (Colour.BLACK, Colour.WHITE)

    @property
    def background(self) -> Colour:
        return self.value[0]

    @property
    def foreground(self) -> Colour:
        return self.value[1]


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    for card_type in CardType:
        create_cardsheet(
            OUTPUT_DIR / f"back_{card_type.name.lower()}.png",
            card_type.background,
            card_type.foreground,
            [TITLE],
            rows=1,
            columns=1,
            margin=0,
            font_size=120,
            text_gap=60,
        )

    for cat in SETS_DIR.iterdir():
        card_type = CardType[cat.stem.split("_")[-1].upper()]
        cards = [word.replace("_", "________") for word in cat.read_text().splitlines()]
        for i, card_batch in enumerate(batch(cards, 70)):
            name = OUTPUT_DIR / f"{cat.stem}_{i}_{len(card_batch)}.png"
            create_cardsheet(name, card_type.background, card_type.foreground, card_batch, footer=TITLE)


if __name__ == "__main__":
    main()
