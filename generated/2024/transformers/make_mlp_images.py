"""Placeholder thumbnails of _2024/transformers/mlp.py (LastTwoChapters and its subclasses): Chapter5_TN5.png and
Chapter6_TN4.png, which the scene read from /Users/grant/3Blue1Brown Dropbox/.../Thumbnails. They are 16:9 boxes
with the chapter number and the label "[placeholder]", made with _tools/placeholder.make_image.

The scene now looks for them by name (ImageMobject("Chapter5_TN5")), so they are written to
_lib/assets/raster_images/.

Usage: python make_mlp_images.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]  # _lib/assets
sys.path.insert(0, str(ASSETS.parents[1] / "_tools"))
from placeholder import make_image

# (file, label, size, background color)
IMAGES = [
    ("Chapter5_TN5.png", "Chapter 5: Transformers (miniatura)", (1280, 720), "#2b3a55"),
    ("Chapter6_TN4.png", "Chapter 6: Attention (miniatura)", (1280, 720), "#3a2b55"),
]


def main():
    out = ASSETS / "raster_images"
    out.mkdir(parents=True, exist_ok=True)
    for name, label, size, bg in IMAGES:
        make_image(out / name, label, size, bg)
    print("mlp: miniaturas de relleno escritas en", out)


if __name__ == "__main__":
    main()
