"""Generate the application icon (assets/icon.ico + assets/icon.png).

Requires Pillow (dev dependency). The generated files are committed to the
repository, so routine builds do not need Pillow installed.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ICON_SIZE = 256
ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]

BACKGROUND_COLOR = "#1a1a2e"
TEXT_COLOR = "#ffffff"
TEXT = "KW"
CORNER_RADIUS = 48
# Text height as a fraction of the icon size.
TEXT_SCALE = 0.42

_FONT_CANDIDATES = ["arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"]

_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def generate() -> None:
    image = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        [(0, 0), (ICON_SIZE - 1, ICON_SIZE - 1)],
        radius=CORNER_RADIUS,
        fill=BACKGROUND_COLOR,
    )

    font = _load_font(int(ICON_SIZE * TEXT_SCALE))
    bbox = draw.textbbox((0, 0), TEXT, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (ICON_SIZE - text_width) / 2 - bbox[0]
    y = (ICON_SIZE - text_height) / 2 - bbox[1]
    draw.text((x, y), TEXT, font=font, fill=TEXT_COLOR)

    _ASSETS_DIR.mkdir(exist_ok=True)
    png_path = _ASSETS_DIR / "icon.png"
    ico_path = _ASSETS_DIR / "icon.ico"
    image.save(png_path)
    image.save(ico_path, sizes=[(s, s) for s in ICO_SIZES])
    print(f"Generated {png_path} and {ico_path}")


if __name__ == "__main__":
    generate()
