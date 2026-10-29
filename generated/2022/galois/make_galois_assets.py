"""Generates the placeholder assets of _2022/galois (the originals were illustrations commissioned by Grant, in his
Dropbox: videos/2022/galois/...). Everything goes in _lib/assets/raster_images/, where _lib/manim_imports_ext.py
looks for them by file name:

- Flower.png (groups.py, FlowerSymmetries): 8-petal flower drawn with PIL, on a transparent background.
  Petals of two alternating tones and a center: 90 degrees is a symmetry, 45 degrees is not (so you can see that the
  scene rotates it 45, 90, 135, 180... degrees).
- transition-to-hospital-2.png, mural.png (art_supplements.py, OutpaintTransition and
  NightSkyOutpaintingTransition): placeholder panoramas (box with a label) over which the scene
  pans.
- Cauchy-Portrait-Cutoff.png, Fourier-Portrait.png, Poisson-Portrait-Outpainted.png (art_supplements.py,
  CauchyFourierPoisson): placeholder portraits.

Usage: python make_galois_assets.py"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]  # _lib/assets
sys.path.insert(0, str(ASSETS.parents[1] / "_tools"))
from placeholder import make_image

IMAGES = [
    ("transition-to-hospital-2.png", "transition to hospital (panorama)", "4320x1080", "#2f3a45"),
    ("mural.png", "night sky mural", "2400x1500", "#1f2a44"),
    ("Cauchy-Portrait-Cutoff.png", "Cauchy portrait", "700x900", "#3d3a30"),
    ("Fourier-Portrait.png", "Fourier portrait", "800x1000", "#30343d"),
    ("Poisson-Portrait-Outpainted.png", "Poisson portrait", "900x1000", "#3d3030"),
]


def make_flower(out, size=1000, n_petals=8):
    ss = 2  # supersampling
    s = size * ss
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    c = s / 2
    colors = [(238, 120, 150, 255), (246, 170, 190, 255)]
    for k in range(n_petals):
        ang = 2 * math.pi * k / n_petals
        petal = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(petal)
        # petal: ellipse that goes from the center upward
        w, h0, h1 = 0.13 * s, 0.05 * s, 0.47 * s
        d.ellipse([c - w, c - h1, c + w, c - h0], fill=colors[k % 2])
        d.ellipse([c - 0.035 * s, c - 0.4 * s, c + 0.035 * s, c - 0.17 * s], fill=(255, 220, 230, 255))
        petal = petal.rotate(-math.degrees(ang), center=(c, c), resample=Image.BICUBIC)
        img = Image.alpha_composite(img, petal)
    d = ImageDraw.Draw(img)
    d.ellipse([c - 0.1 * s, c - 0.1 * s, c + 0.1 * s, c + 0.1 * s], fill=(250, 200, 60, 255))
    img = img.resize((size, size), Image.LANCZOS)
    img.save(out)


if __name__ == "__main__":
    root = ASSETS / "raster_images"
    root.mkdir(parents=True, exist_ok=True)
    make_flower(root / "Flower.png")
    for name, label, size, bg in IMAGES:
        w, h = map(int, size.split("x"))
        make_image(root / name, label, (w, h), bg)
