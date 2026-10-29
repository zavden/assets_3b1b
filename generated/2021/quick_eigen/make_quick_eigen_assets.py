"""Placeholder image for _2021/quick_eigen (the original is private, from Grant's Dropbox).
It writes to _lib/assets/raster_images/, where the code looks for it by name.

- eigen_thumbnail.png: thumbnail of the video "Eigenvectors and eigenvalues" (PreviousVideoWrapper).

Usage: python make_quick_eigen_assets.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB_ASSETS = HERE.parents[2]
sys.path.insert(0, str(LIB_ASSETS.parents[1] / "_tools"))
from placeholder import make_image

IMAGES = [
    ("eigen_thumbnail.png", "miniatura: Eigenvectors and eigenvalues", (1280, 720), "#1f3a4a"),
]


def main():
    out_dir = LIB_ASSETS / "raster_images"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, label, size, bg in IMAGES:
        make_image(out_dir / name, label, size, bg)
        print("escrito", out_dir / name)


if __name__ == "__main__":
    main()
