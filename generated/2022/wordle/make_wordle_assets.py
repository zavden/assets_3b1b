"""Placeholders for the _2022/wordle images that are not in the public repo:

- raster_images/wordle-phone.png and svg_images/wordle-phone.svg: the phone with the game on screen
  (in the original, a drawing by Grant). Here: a phone with an example Wordle grid.
- raster_images/WordleThumbnail.png: the thumbnail of the video that HeresTheThing holds in its hand
  (the original was `<output folder>/2022/wordle/images/Thumbnail`). Here: a placeholder thumbnail
  with a Wordle grid and the word "WORDLE".

Everything is visibly marked as a placeholder.  Usage: python make_wordle_assets.py"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]  # _lib/assets
RASTER = ASSETS / "raster_images"
SVG = ASSETS / "svg_images"

GREY, YELLOW, GREEN = "#797C7E", "#C6B566", "#538D4E"
GRID = [  # example patterns (0 gray, 1 yellow, 2 green) for each row
    [0, 0, 1, 0, 2],
    [0, 0, 1, 1, 0],
    [2, 2, 2, 2, 2],
]
COLORS = {0: GREY, 1: YELLOW, 2: GREEN}


def font(size):
    for p in ["/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf"]:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def make_phone_svg(path):
    w, h = 300, 600
    parts = [
        f'<rect x="4" y="4" width="{w - 8}" height="{h - 8}" rx="36" ry="36"/>',
        f'<rect x="24" y="64" width="{w - 48}" height="{h - 128}" rx="8" ry="8"/>',
        f'<rect x="{w / 2 - 30}" y="30" width="60" height="10" rx="5" ry="5"/>',
        f'<circle cx="{w / 2}" cy="{h - 32}" r="14"/>',
    ]
    size, gap = 36, 8
    x0 = (w - (5 * size + 4 * gap)) / 2
    for r in range(6):
        for c in range(5):
            parts.append(f'<rect x="{x0 + c * (size + gap)}" y="{96 + r * (size + gap)}" '
                         f'width="{size}" height="{size}" rx="3" ry="3"/>')
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'fill="none" stroke="#ffffff" stroke-width="3">\n  ' + "\n  ".join(parts) + "\n</svg>\n"
    )


def draw_grid(d, x0, y0, size, gap, rows, rng_letters="TRACE"):
    for r in range(6):
        for c in range(5):
            x, y = x0 + c * (size + gap), y0 + r * (size + gap)
            if r < len(rows):
                d.rounded_rectangle([x, y, x + size, y + size], radius=size // 12, fill=COLORS[rows[r][c]])
                d.text((x + size / 2, y + size / 2), rng_letters[(r + c) % 5], font=font(int(size * 0.6)),
                       fill="white", anchor="mm")
            else:
                d.rounded_rectangle([x, y, x + size, y + size], radius=size // 12, outline="#3a3a3c", width=3)


def make_phone_png(path):
    w, h = 600, 1200
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([8, 8, w - 8, h - 8], radius=72, fill="#2b2b2e", outline="#888888", width=6)
    d.rounded_rectangle([48, 128, w - 48, h - 128], radius=16, fill="#121213")
    d.rounded_rectangle([w / 2 - 60, 60, w / 2 + 60, 80], radius=10, fill="#555555")
    d.ellipse([w / 2 - 28, h - 92, w / 2 + 28, h - 36], outline="#555555", width=5)
    draw_grid(d, 90, 190, 72, 16, GRID)
    d.text((w / 2, h - 170), "[imagen de relleno]", font=font(26), fill="#999999", anchor="mm")
    img.save(path)


def make_thumbnail_png(path):
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), "#121213")
    d = ImageDraw.Draw(img)
    draw_grid(d, 120, 150, 120, 20, GRID + [[0, 1, 0, 0, 0]] * 2)
    d.text((1390, 420), "WORDLE", font=font(150), fill="white", anchor="mm")
    d.text((1390, 580), "Information theory", font=font(56), fill=YELLOW, anchor="mm")
    d.text((w / 2, h - 60), "[miniatura de relleno]", font=font(36), fill="#888888", anchor="mm")
    img.save(path)


def main():
    RASTER.mkdir(parents=True, exist_ok=True)
    SVG.mkdir(parents=True, exist_ok=True)
    make_phone_svg(SVG / "wordle-phone.svg")
    make_phone_png(RASTER / "wordle-phone.png")
    make_thumbnail_png(RASTER / "WordleThumbnail.png")
    print("rellenos de wordle escritos")


if __name__ == "__main__":
    main()
