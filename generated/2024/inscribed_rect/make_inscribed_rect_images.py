"""Generates the placeholder images of _2024/inscribed_rect (the originals lived in Grant's Dropbox):

- AntonChekhovPortrait.png  (supplements.ChekhovsGun)
- JoshuaGreene.png, AndrewLobb.png  (supplements.GreeneAndLobb)
  Boxes with the name, made with _tools/placeholder.py.
- TorusTexture.png, MobiusStripTexture.png, KleinBottleTexture.png  (loops.*)
  Square textures that TexturedSurface pastes on the parametrized surfaces (square ->
  tube -> torus / Möbius strip / Klein bottle). They are a diagonal gradient with a fine
  grid (so that you can see how the surface deforms) and the edges that get glued marked with
  colored stripes and arrows, just like the scene's diagrams:
    torus:   left/right edges blue (x = 0, 1) and top/bottom green (y = 0, 1)
    Möbius:  left/right edges teal
    Klein:   left/right edges pink (arrows pointing up) and top/bottom yellow
             (top to the right, bottom to the left), as in the ConstructKleinBottle diagram

The code looks for them by name with ImageMobject("...")/TexturedSurface(..., "..."), so they are
written here and copied to _lib/assets/raster_images/.

Usage: python make_inscribed_rect_images.py"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]  # _lib
sys.path.insert(0, str(LIB.parent / "_tools"))
from placeholder import make_image

# (file, label, size, background color)
PLACEHOLDERS = [
    ("AntonChekhovPortrait.png", "Anton Chekhov (retrato)", (800, 1000), "#4a3f33"),
    ("JoshuaGreene.png", "Joshua Greene (foto)", (800, 1000), "#2f4552"),
    ("AndrewLobb.png", "Andrew Lobb (foto)", (800, 1000), "#3d3a52"),
]

N = 1024  # side of the textures
BLUE, GREEN, TEAL, PINK, YELLOW = "#58C4DD", "#00FF00", "#5CD0B3", "#D147BD", "#FFFF00"


def gradient(c0, c1):
    """Diagonal gradient between two hex colors (the lower left corner is c0)."""
    a = np.array([int(c0[i:i + 2], 16) for i in (1, 3, 5)], dtype=float)
    b = np.array([int(c1[i:i + 2], 16) for i in (1, 3, 5)], dtype=float)
    u, v = np.meshgrid(np.linspace(0, 1, N), np.linspace(1, 0, N))  # v grows upward
    t = ((u + v) / 2)[..., None]
    return Image.fromarray((a * (1 - t) + b * t).astype(np.uint8), "RGB")


def draw_chevrons(d, x0, y0, x1, y1, color, n=3, size=46):
    """n arrowheads on the segment (x0, y0) -> (x1, y1), in the direction of the segment."""
    p0, p1 = np.array([x0, y0], float), np.array([x1, y1], float)
    t = (p1 - p0) / np.linalg.norm(p1 - p0)
    nrm = np.array([-t[1], t[0]])
    for k in range(n):
        c = p0 + (p1 - p0) * (k + 1) / (n + 1)
        tip, b1, b2 = c + t * size / 2, c - t * size / 2 + nrm * size / 2, c - t * size / 2 - nrm * size / 2
        d.polygon([tuple(tip), tuple(b1), tuple(b2)], fill=color)


def edge_texture(grad, side_colors, top_colors, flips=(False, False, False, False)):
    """Texture with a grid and borders colored with arrows.

    side_colors: colors of (left, right); top_colors: of (bottom, top).
    flips: reverses the direction of the arrows of (left, right, bottom, top)."""
    img = grad.copy()
    d = ImageDraw.Draw(img)
    for k in range(1, 16):
        w = 4 if k % 2 == 0 else 2
        p = k * N / 16
        d.line([p, 0, p, N], fill=(255, 255, 255), width=w)
        d.line([0, p, N, p], fill=(255, 255, 255), width=w)
    th = 26
    left, right = side_colors
    bottom, top = top_colors
    d.rectangle([0, 0, th, N], fill=left)
    d.rectangle([N - th, 0, N, N], fill=right)
    d.rectangle([0, N - th, N, N], fill=bottom)  # in the image, down is y = N
    d.rectangle([0, 0, N, th], fill=top)
    fl, fr, fb, ft = flips
    c = th + 36
    dark = (20, 20, 20)
    draw_chevrons(d, c, N - 60 if not fl else 60, c, 60 if not fl else N - 60, dark)
    draw_chevrons(d, N - c, N - 60 if not fr else 60, N - c, 60 if not fr else N - 60, dark)
    draw_chevrons(d, 60 if not fb else N - 60, N - c, N - 60 if not fb else 60, N - c, dark)
    draw_chevrons(d, 60 if not ft else N - 60, c, N - 60 if not ft else 60, c, dark)
    return img


def make_textures():
    return {
        "TorusTexture.png": edge_texture(gradient("#1d3b66", "#7fd1c4"), (BLUE, BLUE), (GREEN, GREEN)),
        "MobiusStripTexture.png": edge_texture(gradient("#2a2f55", "#e3a6c2"), (TEAL, TEAL), (TEAL, TEAL),
                                               flips=(False, True, False, True)),
        "KleinBottleTexture.png": edge_texture(gradient("#2e3f1f", "#c58fd1"), (PINK, PINK), (YELLOW, YELLOW),
                                               flips=(False, False, True, False)),
    }


def main():
    dst = LIB / "assets" / "raster_images"
    dst.mkdir(parents=True, exist_ok=True)
    for name, label, size, bg in PLACEHOLDERS:
        make_image(HERE / name, label, size, bg)
        shutil.copy2(HERE / name, dst / name)
    for name, img in make_textures().items():
        img.save(HERE / name)
        shutil.copy2(HERE / name, dst / name)


if __name__ == "__main__":
    main()
