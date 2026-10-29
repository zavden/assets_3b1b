"""Generates the placeholder assets of _2021/matrix_exp.py (the originals lived in Grant's Dropbox).
Everything is written to _lib/assets/raster_images/, where the code looks for them by name:

- mat_exp_exercise.png: book page with the exercise "Compute the matrix e^{At}" (ZoomInOnProblem
  draws rectangles on top at fixed positions, which is why it is 16:9).
- Introductio_in_Analysin_infinitorum.png: cover of Euler's 1748 book (GraphAndHistoryOfExponential).
- Huygens.png, Goldbach.png: portraits of Leibniz's and Euler's correspondents (Leibniz.jpg and Euler.jpg already
  exist in the repo).
- ExpMatThumbnailBackdrop.png: thumbnail background (Thumbnail); in the original it was a frame of the flow of
  ThumbnailBackdrop, here it is a dark blue background.

Usage: python make_matrix_exp_assets.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[2]  # _lib/assets
sys.path.insert(0, str(LIB.parents[1] / "_tools"))
from placeholder import make_image

IMAGES = [
    ("mat_exp_exercise.png", "Exercise: compute the matrix e^(At)\n(pagina de libro)", (1920, 1080), "#3a3a3a"),
    ("Introductio_in_Analysin_infinitorum.png", "Euler:\nIntroductio in\nanalysin infinitorum", (900, 1200), "#4a3a2b"),
    ("Huygens.png", "Christiaan Huygens", (800, 1000), "#2b3a4a"),
    ("Goldbach.png", "Christian Goldbach", (800, 1000), "#3a2b4a"),
    ("ExpMatThumbnailBackdrop.png", "ExpMatThumbnailBackdrop", (1920, 1080), "#16213a"),
]


def main():
    out_dir = LIB / "raster_images"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, label, size, bg in IMAGES:
        make_image(out_dir / name, label, size, bg)


if __name__ == "__main__":
    main()
