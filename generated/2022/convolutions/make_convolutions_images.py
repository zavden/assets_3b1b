"""Generates the placeholder sprites of _2022/convolutions (discrete.py and supplements.py). The originals
(Grant's pixel-art images, in his Dropbox) are not in the public repo; here small sprites of our own
are drawn, so that the image convolution scenes (each pixel is a square) have
something to filter:

- PixelArtCat.png  (24x24): sitting orange cat, light sky-blue background.
- MarioSmall.png   (20x20): plumber with a red cap and blue overalls (own design, not Nintendo's sprite).
- KirbySmall.png   (32x32): pink ball with eyes, cheeks, red arms and feet, cream background.
- BitRandy.png     (32x32): pixelated blue pi creature (Randolph), dark gray background.

They are written to _lib/assets/raster_images/ (the scene asks for them by name: image_name = "PixelArtCat", ...).

Usage: python make_convolutions_images.py"""
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / "raster_images"


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def from_ascii(rows, palette):
    h, w = len(rows), len(rows[0])
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y, row in enumerate(rows):
        assert len(row) == w, (y, len(row), w)
        for x, ch in enumerate(row):
            arr[y, x] = hex_rgb(palette[ch])
    return arr


# ------------------------------------------------------------------ cat
CAT = [
    "........................",
    "........................",
    "......KK........KK......",
    ".....KOOK......KOOK.....",
    ".....KOPOK....KOPOK.....",
    ".....KOPOKKKKKKOPOK.....",
    ".....KOOOOOOOOOOOOK.....",
    "....KOOODOOOOOODOOOK....",
    "....KOOODOOOOOODOOOK....",
    "....KOOOOOOOOOOOOOOK....",
    "....KOGGOOOOOOOOGGOK....",
    "....KOGKOOOPPOOOKGOK....",
    ".....KOOOOOOOOOOOOK.....",
    "......KOOOOWWOOOOK......",
    ".....KKOOOOOOOOOOKKK....",
    "....KOOOOOOOOOOOOOOOK...",
    "....KOOWWOOOOOOWWOOOK.K.",
    "....KOOWWOOOOOOWWOOOKOK.",
    "....KOOWWOOOOOOWWOOOKOK.",
    ".....KOOOOOOOOOOOOOOKOK.",
    ".....KWWKKKKKKKKWWKKOK..",
    "......KK........KK.KK...",
    "........................",
    "........................",
]
CAT_PAL = {
    ".": "#bfe3f2", "K": "#2b1d14", "O": "#e8923a", "D": "#a85a1a", "P": "#f2a6a6",
    "W": "#fff4e6", "G": "#7bd05a",
}

# ------------------------------------------------------------------ plumber
MARIO = [
    "....................",
    "......RRRRRR........",
    "....RRRRRRRRRRR.....",
    "....BBBSSSSSS.......",
    "...BSBSSSSBSSS......",
    "...BSBBSSSSBSSSS....",
    "...BBSSSSSBBBB......",
    ".....SSSSSSSSS......",
    "....RRTRRRRTRR......",
    "...RRRTRRRRTRRRR....",
    "..RRRRTTTTTTRRRR....",
    "..SSRTYTTTTYTRSS....",
    "..SSSTTTTTTTTSSS....",
    "..SSTTTTTTTTTTSS....",
    "....TTTT..TTTT......",
    "...BBBB....BBBB.....",
    "..BBBBB....BBBBB....",
    "....................",
    "....................",
    "....................",
]
MARIO_PAL = {
    ".": "#6ba8ff", "R": "#d8281c", "S": "#f3b88a", "B": "#6b3b17", "T": "#2848c8", "Y": "#f5d033",
}

# ------------------------------------------------------------------ Kirby y Randy


def ellipse_mask(shape, cx, cy, rx, ry):
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w]
    return ((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2 <= 1.0


def paint(arr, mask, color):
    arr[mask] = hex_rgb(color)


def paint_outlined(arr, cx, cy, rx, ry, fill, outline="#4a2038", width=1.0):
    shape = arr.shape[:2]
    paint(arr, ellipse_mask(shape, cx, cy, rx + width, ry + width), outline)
    paint(arr, ellipse_mask(shape, cx, cy, rx, ry), fill)


def make_kirby(n=32):
    arr = np.zeros((n, n, 3), dtype=np.uint8)
    arr[:] = hex_rgb("#fff3d6")
    shape = (n, n)
    # Feet (red, behind the body) and arms
    paint_outlined(arr, 8.5, 28, 5.5, 2.5, "#e0405a")
    paint_outlined(arr, 23.5, 28, 5.5, 2.5, "#e0405a")
    paint_outlined(arr, 4.0, 17.5, 3.0, 3.6, "#ffa6c4")
    paint_outlined(arr, 28.0, 14.5, 3.0, 3.6, "#ffa6c4")
    # Body
    paint_outlined(arr, 16, 16.5, 11.5, 11.0, "#ffa6c4")
    # Cheeks
    paint(arr, ellipse_mask(shape, 8.5, 19.5, 2.4, 1.6), "#ff6f93")
    paint(arr, ellipse_mask(shape, 23.5, 19.5, 2.4, 1.6), "#ff6f93")
    # Eyes: dark blue with a highlight
    for cx in (12.0, 20.0):
        paint(arr, ellipse_mask(shape, cx, 14.0, 1.9, 3.4), "#1b2a7a")
        paint(arr, ellipse_mask(shape, cx, 12.4, 1.3, 1.8), "#2e5fe0")
        paint(arr, ellipse_mask(shape, cx, 10.9, 1.2, 1.3), "#ffffff")
    # Mouth
    paint(arr, ellipse_mask(shape, 16, 20.5, 1.7, 1.2), "#a8203c")
    return arr


def make_randy(n=32):
    arr = np.zeros((n, n, 3), dtype=np.uint8)
    arr[:] = hex_rgb("#2a2f3a")
    shape = (n, n)
    blue = "#3f78c4"
    dark = "#1c3a66"
    # Arms
    paint_outlined(arr, 4.5, 21, 2.6, 4.2, blue, dark)
    paint_outlined(arr, 27.5, 21, 2.6, 4.2, blue, dark)
    # Body
    paint_outlined(arr, 16, 18.5, 10.5, 11.5, blue, dark)
    # White eyes
    for cx in (11.5, 20.5):
        paint(arr, ellipse_mask(shape, cx, 12.0, 4.0, 4.6), "#dfe6ee")
    # Pupils (looking slightly to the right) and highlights
    for cx in (12.8, 21.8):
        paint(arr, ellipse_mask(shape, cx, 12.6, 1.9, 2.1), "#10131a")
        paint(arr, ellipse_mask(shape, cx + 0.5, 11.4, 0.6, 0.6), "#ffffff")
    # Mouth (smile)
    yy, xx = np.mgrid[0:n, 0:n]
    smile = (np.abs(((xx + 0.5 - 16) / 5.5) ** 2 + ((yy + 0.5 - 20) / 3.0) ** 2 - 1) < 0.45) & (yy + 0.5 > 21)
    arr[smile] = hex_rgb("#10131a")
    # Pies
    paint_outlined(arr, 11.5, 30, 3.6, 1.4, dark, "#10131a", 0.5)
    paint_outlined(arr, 20.5, 30, 3.6, 1.4, dark, "#10131a", 0.5)
    return arr


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    images = {
        "PixelArtCat.png": from_ascii(CAT, CAT_PAL),
        "MarioSmall.png": from_ascii(MARIO, MARIO_PAL),
        "KirbySmall.png": make_kirby(),
        "BitRandy.png": make_randy(),
    }
    for name, arr in images.items():
        Image.fromarray(arr, "RGB").save(OUT / name)
        print("escrito", OUT / name, arr.shape[:2])


if __name__ == "__main__":
    main()
