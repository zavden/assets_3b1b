"""Generates the placeholder images of _2022/visual_proofs/lies.py (the originals lived in Grant's Dropbox,
videos/2022/visual_proofs/lies/images/). They are written to _lib/assets/raster_images/, where
_lib/manim_imports_ext.py looks for them by name when the absolute path does not exist:

- SimpleSphereQuestion.png (2048x512): dark gray banner with the statement of the scene
  SimpleSphereQuestion (the SphereExample scene uses it as the texture of the sphere and of the banner).
- SquareApprox1..4.png and SquareApproxInf.png (300x300): "staircase" approximations of a circle
  (1, 2, 4 and 8 steps per quadrant; all measure 8) and the circle (length 2*pi).
- Fourier1..4.png and FourierInf.png (300x300): partial sums (1 to 4 odd harmonics) of the
  Fourier series of a square wave, and the square wave (discontinuous).

Usage: python make_lies_images.py"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / "raster_images"
BLUE, YELLOW, GREY = "#58c4dd", "#ffff00", "#888888"
FONT_PATHS = [
    "/usr/share/fonts/cm-unicode/cmunrm.otf",
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSerif.ttf",
]


def font(size):
    for p in FONT_PATHS:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def make_question():
    w, h = 2048, 512
    img = Image.new("RGB", (w, h), "#222222")
    d = ImageDraw.Draw(img)
    d.multiline_text(
        (w / 2, h / 2),
        "A “proof” of a formula for\nthe surface area of a sphere",
        font=font(110), fill="white", anchor="mm", align="center", spacing=20,
    )
    d.text((w / 2, h - 24), "[imagen de relleno]", font=font(26), fill="#777777", anchor="mm")
    img.save(OUT / "SimpleSphereQuestion.png")


def staircase(m):
    """Outer staircase of the unit circle with m steps per quadrant."""
    quarter = []
    th = np.linspace(0, np.pi / 2, m + 1)
    x, y = np.cos(th), np.sin(th)
    quarter.append((x[0], y[0]))
    for j in range(m):
        quarter.append((x[j], y[j + 1]))
        quarter.append((x[j + 1], y[j + 1]))
    quarter = np.array(quarter)
    pts = []
    for k in range(4):
        c, s = np.cos(k * np.pi / 2), np.sin(k * np.pi / 2)
        rot = np.array([[c, -s], [s, c]])
        pts.append(quarter @ rot.T)
    return np.vstack(pts + [pts[0][:1]])


def to_px(pts, size, scale, cx=0.0, cy=0.0):
    return [(size / 2 + (x - cx) * scale, size / 2 - (y - cy) * scale) for x, y in pts]


def make_square_approx():
    size = 300
    scale = size * 0.40
    th = np.linspace(0, 2 * np.pi, 400)
    circle = np.stack([np.cos(th), np.sin(th)], axis=1)
    for name, m in [("1", 1), ("2", 2), ("3", 4), ("4", 8)]:
        img = Image.new("RGB", (size, size), "black")
        d = ImageDraw.Draw(img)
        d.line(to_px(circle, size, scale), fill=BLUE, width=3)
        d.line(to_px(staircase(m), size, scale), fill=YELLOW, width=3, joint="curve")
        img.save(OUT / f"SquareApprox{name}.png")
    img = Image.new("RGB", (size, size), "black")
    d = ImageDraw.Draw(img)
    d.line(to_px(circle, size, scale), fill=YELLOW, width=4)
    img.save(OUT / "SquareApproxInf.png")


def make_fourier():
    size = 300
    xs = np.linspace(-np.pi, np.pi, 600)
    scale_x = size * 0.42 / np.pi
    scale_y = size * 0.28
    square = np.sign(np.sin(xs))
    for name, terms in [("1", 1), ("2", 2), ("3", 3), ("4", 4)]:
        ys = sum(4 / np.pi * np.sin((2 * k + 1) * xs) / (2 * k + 1) for k in range(terms))
        img = Image.new("RGB", (size, size), "black")
        d = ImageDraw.Draw(img)
        d.line([(0, size / 2), (size, size / 2)], fill=GREY, width=1)
        d.line([(size / 2 + x * scale_x, size / 2 - y * scale_y) for x, y in zip(xs, ys)], fill=BLUE, width=3)
        img.save(OUT / f"Fourier{name}.png")
    img = Image.new("RGB", (size, size), "black")
    d = ImageDraw.Draw(img)
    d.line([(0, size / 2), (size, size / 2)], fill=GREY, width=1)
    # Square wave: horizontal sections and vertical jumps (discontinuous)
    pts = []
    for x0, v in [(-np.pi, -1), (0, 1)]:
        x1 = x0 + np.pi
        pts.append([(size / 2 + x0 * scale_x, size / 2 - v * scale_y),
                    (size / 2 + x1 * scale_x, size / 2 - v * scale_y)])
    for seg in pts:
        d.line(seg, fill=YELLOW, width=4)
    d.line([(size / 2, size / 2 + scale_y), (size / 2, size / 2 - scale_y)], fill=YELLOW, width=2)
    img.save(OUT / "FourierInf.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    make_question()
    make_square_approx()
    make_fourier()
    print("escrito en", OUT)


if __name__ == "__main__":
    main()
