"""Generates the placeholder assets of _2022/puzzles/subsets.py (the originals lived in Grant's Dropbox or
were not in the repo):

- raster_images/US_Flag.png (IMOLogo): US flag drawn with PIL (13 stripes, blue canton and 50
  stars).
- raster_images/BookQuestion.jpg (BookQuestionHighlight): placeholder photo of a book page, 16:9,
  with the problem statement (subsets of {1, ..., 2000} with sum divisible by 5) on the central
  line; the scene highlights a 5 x 0.55 rectangle centered at x = -0.2.
- svg_images/mines-of-moria-entrance.svg (MoriaEntrance): arched door with a ring and a star,
  placeholder (the original was the drawing of the entrance of the Mines of Moria).

Usage: python make_puzzles_assets.py"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]  # _lib/assets
sys.path.insert(0, str(ASSETS.parents[1] / "_tools"))
from placeholder import font


def star(cx, cy, r):
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.382
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return pts


def make_us_flag(out, w=1900, h=1000):
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    sh = h / 13
    for k in range(0, 13, 2):
        d.rectangle([0, k * sh, w, (k + 1) * sh], fill=(178, 34, 52))
    cw, ch = 0.4 * w, 7 * sh
    d.rectangle([0, 0, cw, ch], fill=(60, 59, 110))
    for row in range(9):
        n = 6 if row % 2 == 0 else 5
        for col in range(n):
            x = cw * ((2 * col + 1) / 12 if row % 2 == 0 else (2 * col + 2) / 12)
            y = ch * (row + 0.5) / 9
            d.polygon(star(x, y, 0.5 * 0.0616 * h), fill="white")
    img.save(out)


def make_book_question(out, w=1920, h=1080):
    img = Image.new("RGB", (w, h), (236, 228, 208))
    d = ImageDraw.Draw(img)
    f_big, f_small = font(46), font(34)
    d.text((w / 2, 70), "[foto de relleno de una página de libro]", font=f_small, fill=(120, 110, 95), anchor="mm")
    y = 170
    for k in range(5):
        d.rounded_rectangle([300, y, 300 + 1300 * (0.85 if k % 2 else 1.0), y + 14], radius=7, fill=(200, 192, 174))
        y += 46
    # center line: the statement, centered at x = -0.2 units (14.2-wide frame)
    cx = w / 2 - 0.2 * w / 14.2
    d.text((cx, h / 2), "How many subsets of {1, 2, ..., 2000} have a sum divisible by 5?",
           font=f_big, fill=(30, 30, 30), anchor="mm")
    y = h / 2 + 90
    for k in range(5):
        d.rounded_rectangle([300, y, 300 + 1300 * (0.9 if k % 2 else 1.0), y + 14], radius=7, fill=(200, 192, 174))
        y += 46
    img.save(out, quality=90)


def make_moria_svg(out):
    star_pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in star(50, 34, 12))
    out.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="100px" height="100px" viewBox="0 0 100 100">'
        '<!-- relleno: el original (entrada de las Minas de Moria) no es público -->'
        '<path d="M 8 98 L 8 46 A 42 42 0 0 1 92 46 L 92 98 Z" fill="#8a8f98" stroke="#d8dce2" stroke-width="1.5"/>'
        '<path d="M 26 98 L 26 50 A 24 24 0 0 1 74 50 L 74 98 Z" fill="#2a2d33" stroke="#d8dce2" stroke-width="1.5"/>'
        '<circle cx="50" cy="34" r="17" fill="none" stroke="#d8dce2" stroke-width="1.5"/>'
        f'<polygon points="{star_pts}" fill="#e8ecf2" stroke="#d8dce2" stroke-width="0.8"/>'
        '<path d="M 38 98 L 38 70 M 62 98 L 62 70 M 38 70 L 62 70" fill="none" stroke="#d8dce2" stroke-width="1.5"/>'
        '</svg>'
    )


if __name__ == "__main__":
    raster = ASSETS / "raster_images"
    raster.mkdir(parents=True, exist_ok=True)
    make_us_flag(raster / "US_Flag.png")
    make_book_question(raster / "BookQuestion.jpg")
    svgs = ASSETS / "svg_images"
    svgs.mkdir(parents=True, exist_ok=True)
    make_moria_svg(svgs / "mines-of-moria-entrance.svg")
