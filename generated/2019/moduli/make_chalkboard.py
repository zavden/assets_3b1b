"""Own replacement for `raster_images/chalkboard.png` (chalkboard background of `moduli.TriangleModuliSpace`): very
dark gray with soft Gaussian noise and some eraser streaks, made with numpy. No third-party data.

  python make_chalkboard.py [--out FOLDER]   (by default writes _lib/assets/raster_images/chalkboard.png)"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ASSETS = Path(__file__).resolve().parents[3]
SIZE = (2560, 1440)


def make(path, seed=2019):
    rng = np.random.default_rng(seed)
    w, h = SIZE
    base = np.full((h, w), 34.0)
    # fine-grain noise and large blotches
    fine = rng.normal(0, 4.0, (h, w))
    blobs = Image.fromarray(rng.normal(128, 40, (h // 16, w // 16)).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    blobs = (np.asarray(blobs.filter(ImageFilter.GaussianBlur(8))).astype(float) - 128) * 0.12
    img = base + fine + blobs
    # light eraser streaks: long, very soft strokes
    streaks = Image.new("L", (w, h), 0)
    px = np.asarray(streaks).astype(float)
    for _ in range(40):
        y0 = rng.integers(0, h)
        x0 = rng.integers(0, w // 2)
        length = rng.integers(w // 6, w // 2)
        slope = rng.normal(0, 0.05)
        thick = rng.integers(10, 40)
        xs = np.arange(x0, min(w, x0 + length))
        ys = (y0 + slope * (xs - x0)).astype(int)
        for dy in range(-thick // 2, thick // 2):
            yy = np.clip(ys + dy, 0, h - 1)
            px[yy, xs] += rng.uniform(1.0, 3.0)
    streaks = Image.fromarray(px.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))
    img = img + np.asarray(streaks).astype(float)
    out = np.clip(img, 0, 255).astype(np.uint8)
    Image.fromarray(np.stack([out] * 3, axis=2), "RGB").convert("RGBA").save(path)
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = Path(a.out) if a.out else ASSETS / "raster_images"
    out.mkdir(parents=True, exist_ok=True)
    print(make(out / "chalkboard.png"))
