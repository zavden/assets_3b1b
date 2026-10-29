"""Generates the placeholder assets of _2021/siggraph.py (the original lived in Grant's Dropbox):

- acm_logo.png: texture that InterpolatingOrientations(WithQuaternions) pastes on one face of the cube
  (TexturedSurface(logo[0], "acm_logo")). It is a placeholder box with the text "ACM", not the real logo.
  It is written to _lib/assets/raster_images/.

Usage: python make_siggraph_assets.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[2]  # _lib/assets
sys.path.insert(0, str(LIB.parents[1] / "_tools"))
from placeholder import make_image


def main():
    out = LIB / "raster_images" / "acm_logo.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    make_image(out, "ACM", (1024, 1024), "#2a5a85")


if __name__ == "__main__":
    main()
