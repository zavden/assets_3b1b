"""Placeholder images for outside_videos/for_site (the originals are private, from Grant's Dropbox).
Writes to _lib/assets/raster_images/, where the code looks for them by name.

- physics_icon_base.png  (PhysicsIcon)
- geometry_icon_base.jpg (GeometryIcon)

Usage: python make_for_site_assets.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB_ASSETS = HERE.parents[2]
sys.path.insert(0, str(LIB_ASSETS.parents[1] / "_tools"))
from placeholder import make_image

IMAGES = [
    ("physics_icon_base.png", "physics icon base", (1920, 1080), "#243447"),
    ("geometry_icon_base.jpg", "geometry icon base", (1920, 1080), "#3d3a2a"),
]


def main():
    out_dir = LIB_ASSETS / "raster_images"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, label, size, bg in IMAGES:
        make_image(out_dir / name, label, size, bg)
        print("escrito", out_dir / name)


if __name__ == "__main__":
    main()
