"""Placeholders for the private images (Grant's Dropbox) of 2023/gauss_int and of 2023/clt/wordy_scenes.

Writes to _lib/assets/raster_images/:
  gauss_int/wigner-speech-transition-3.jpg, gauss_int/wigner-speech-transition-4.jpg  (WignerZoom, WignerReverseZoom)
  gauss_int/VCubingxThumbnail.png, BrimathThumbnail.png, DrAlters.png, KeithConrad.png  (OtherVideos)
  gauss_int/EquationThumbnail.png, Thumbnail.png, ProofSummary.jpg                      (NextVideo)
  ConvolutionThumbnail.png                                                              (clt/wordy_scenes)
  Mimas.png, Enceladus.png, Tethys.png, Dione.png, Rhea.png, Titan.png, Iapetus.png    (moons of Saturn, gauss_int/supplements)

The scenes that used absolute Dropbox paths now ask for "gauss_int/<file>" (with # CHANGE).
The rectangles are boxes with the name (_tools/placeholder.py); the moons are shaded gray spheres
with a couple of craters, transparent outside the disk.

Usage: python make_gauss_int_placeholders.py"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]
RASTER = LIB / "assets" / "raster_images"
sys.path.insert(0, str(LIB.parent / "_tools"))
from placeholder import make_image  # noqa: E402

# (path inside raster_images, label, size, background)
IMAGES = [
    ("gauss_int/wigner-speech-transition-3.jpg", "wigner-speech-transition-3", "1920x1080", "#2f3b4a"),
    ("gauss_int/wigner-speech-transition-4.jpg", "wigner-speech-transition-4", "1920x1080", "#4a3b2f"),
    ("gauss_int/VCubingxThumbnail.png", "VCubingxThumbnail", "1280x720", "#2b3a55"),
    ("gauss_int/BrimathThumbnail.png", "BrimathThumbnail", "1280x720", "#552b3a"),
    ("gauss_int/DrAlters.png", "DrAlters", "1280x720", "#2b5548"),
    ("gauss_int/KeithConrad.png", "KeithConrad", "1280x720", "#55482b"),
    ("gauss_int/EquationThumbnail.png", "EquationThumbnail", "1280x720", "#33404d"),
    ("gauss_int/Thumbnail.png", "clt Thumbnail", "1280x720", "#4d3340"),
    ("gauss_int/ProofSummary.jpg", "ProofSummary", "1280x720", "#40504d"),
    ("ConvolutionThumbnail.png", "ConvolutionThumbnail", "1280x720", "#33404d"),
]

# name, base color (RGB), crater seed
MOONS = [
    ("Mimas", (170, 170, 172), 1),
    ("Enceladus", (235, 238, 240), 2),
    ("Tethys", (200, 198, 192), 3),
    ("Dione", (190, 188, 184), 4),
    ("Rhea", (178, 176, 172), 5),
    ("Titan", (214, 160, 70), 6),
    ("Iapetus", (150, 140, 128), 7),
]


def make_moon(path, color, seed, size=400):
    rng = np.random.default_rng(seed)
    ys, xs = np.mgrid[0:size, 0:size]
    x = (xs - size / 2) / (size / 2)
    y = (ys - size / 2) / (size / 2)
    r2 = x**2 + y**2
    inside = r2 <= 1
    z = np.sqrt(np.clip(1 - r2, 0, 1))
    light = np.clip(0.25 + 0.75 * (-0.45 * x - 0.45 * y + 0.77 * z), 0, 1)
    shade = light.copy()
    for _ in range(14):  # craters: darker patches with a light edge
        cx, cy = rng.uniform(-0.7, 0.7, 2)
        if cx**2 + cy**2 > 0.7:
            continue
        rad = rng.uniform(0.05, 0.18)
        d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        shade = np.where(d < rad, shade * 0.75, shade)
        shade = np.where((d >= rad) & (d < rad * 1.15), np.minimum(shade * 1.15, 1), shade)
    rgb = np.stack([shade * c for c in color], axis=-1)
    alpha = np.where(inside, 255, 0).astype(np.uint8)
    img = np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), alpha])
    Image.fromarray(img, "RGBA").save(path)


def main():
    for rel, label, size, bg in IMAGES:
        out = RASTER / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        w, h = map(int, size.split("x"))
        make_image(out, label, (w, h), bg)
    for name, color, seed in MOONS:
        make_moon(RASTER / f"{name}.png", color, seed)


if __name__ == "__main__":
    main()
