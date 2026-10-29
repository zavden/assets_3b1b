"""Generates the placeholder assets of _2023/optics_puzzles (the originals live in Grant's Dropbox,
folder videos/2023/barber_pole/):

- Photos and captures (annotations.py, ior_annotations.py): boxes with the name, made with
  _tools/placeholder.py. The scenes looked for them by absolute path (/Users/grant/...); in the
  working copy it was changed to the name, which is looked up in _lib/assets/raster_images/.
- tank.svg (bending_waves.SnellsLaw): tank silhouette pointing to the right, a single
  white shape (the scene does set_fill(WHITE) and rotates it).

Usage: python make_optics_puzzles_assets.py   (writes here and to _lib/assets/raster_images/
and _lib/assets/svg_images/)"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]  # _lib
sys.path.insert(0, str(LIB.parent / "_tools"))
from placeholder import make_image

# (file, label, size, background color)
IMAGES = [
    ("DemoStill.jpg", "DemoStill (foto del tubo con jarabe)", (1920, 1080), "#2a2f3a"),
    ("RedFilter.jpg", "RedFilter (foto con filtro rojo)", (1920, 1080), "#4a2020"),
    ("GreenFilter.jpg", "GreenFilter (foto con filtro verde)", (1920, 1080), "#204a28"),
    ("RainbowTubes.jpg", "RainbowTubes (foto de tubos)", (1920, 1080), "#33284a"),
    ("RedStill.jpg", "RedStill", (1920, 1080), "#4a2020"),
    ("OrangeStill.jpg", "OrangeStill", (1920, 1080), "#4a3520"),
    ("GreenStill.jpg", "GreenStill", (1920, 1080), "#204a28"),
    ("BlueStill.jpg", "BlueStill", (1920, 1080), "#20304a"),
    ("RainbowStill.jpg", "RainbowStill", (1920, 1080), "#33284a"),
    ("MouldThumbnail.jpg", "Miniatura de Steve Mould", (1280, 720), "#3a3320"),
    ("Part2Thumbnail4.png", "Miniatura Part 2 (v4)", (1280, 720), "#2b3a55"),
    ("Part2Thumbnail6.png", "Miniatura Part 2 (v6)", (1280, 720), "#2b4a55"),
    ("PrismThumbnail2.png", "Miniatura Prism (v2)", (1280, 720), "#3a2b55"),
    ("CleanThumbnail.png", "Miniatura Clean", (1280, 720), "#2b5548"),
    ("Dark-side-of-the-moon.png", "Dark side of the moon", (1000, 1000), "#111111"),
    ("True-prism.png", "True prism", (1200, 1000), "#1a1a2a"),
    ("WaveSumPhaseShift.png", "WaveSumPhaseShift (captura)", (1920, 1080), "#202a35"),
]

TANK_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="240" height="120" viewBox="0 0 240 120">
<g fill="#ffffff" stroke="none">
<rect x="20" y="78" width="170" height="30" rx="15"/>
<polygon points="34,72 42,52 172,52 186,72"/>
<rect x="72" y="30" width="76" height="26" rx="11"/>
<rect x="140" y="38" width="86" height="8"/>
</g>
</svg>
"""


def main():
    raster = LIB / "assets" / "raster_images"
    svgs = LIB / "assets" / "svg_images"
    raster.mkdir(parents=True, exist_ok=True)
    svgs.mkdir(parents=True, exist_ok=True)
    for name, label, size, bg in IMAGES:
        make_image(HERE / name, label, size, bg)
        shutil.copy2(HERE / name, raster / name)
    (HERE / "tank.svg").write_text(TANK_SVG)
    shutil.copy2(HERE / "tank.svg", svgs / "tank.svg")


if __name__ == "__main__":
    main()
