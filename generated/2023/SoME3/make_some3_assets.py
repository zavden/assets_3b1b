"""Generates the placeholder assets of _2023/SoME3/main.py (the originals lived in Grant's Dropbox,
videos/2023/SoME3/):

- Thumbnails of the contest entries (ThumbnailProgression, MetaThumbnail, OtherGreatOnes): a
  1280x720 image per entry, with the entry's title, written at the root of
  _lib/assets/raster_images/ as <title>.png. The scenes ask for "/Users/grant/.../EntryThumbnails/<title>"
  (without extension) and _lib/manim_imports_ext.py looks for <title> by name in that folder.
- LOGO_stacked_w_registration_white.svg: white placeholder mark of two lines ("Jane" / "Street",
  outlines of CMU Serif Bold, a single shape), at the root of _lib/assets/svg_images/. It is the replacement
  for the Jane Street logo (the real one is not public); Credits asks for it by Grant's Dropbox path.

Usage: python make_some3_assets.py"""
import colorsys
import hashlib
import sys
import textwrap
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[2]  # _lib/assets
sys.path.insert(0, str(LIB.parents[1] / "_tools"))
from placeholder import make_image

NAMES = [
    "Pixel Art Anti Aliasing",
    "The Math of Saving The Enola Gay",
    "Making a Pitch Shifter",
    "Cayley Graphs and Pretty Things",
    "The Longest Increasing Subsequence",
    "The Matrix Arcade: A Visual Explorable of Matrix Transformations",
    "Watching Neural Networks Learn",
    "Functions are Vectors",
    "The Art of Linear Programming",
    "The Mosaic Problem - How and Why to do Math for Fun",
    "Affording a Planet With Geometry",
    "When CAN'T Math Be Generalized?",
    "Rotation + Translation = Rotation. Animated proof",
    "Rethinking the real line",
    "How did the Ancient Egyptians find this volume without Algebra?",
    "A Subtle Aspect of Circular Motion",
    "Minimal Surfaces & the Calculus of Variations",
    "How does a computer-calculator compute logarithms?",
    "What Happens If We Add Fractions Incorrectly?",
    "Can you guess this shape from its shadows?",
    "Chasing Fixed Points: Greedy Gremlin's Trade-Off",
    "How Computers Use Numbers",
    "Mathematical Magic Mirrorball",
    "The Mathematics of String Art",
    "How Infinity Works",
    # OtherGreatOnes / MetaThumbnail
    "Signed Distance Functions",
    "A Study In Greyscale",
    "Conservative matrix fields",
    "Are Elo Systems Overrated?",
    "The essence of multivariable calculus",
    "The Principle of Least Action",
]

FONT = "/usr/share/fonts/cm-unicode/cmunbx.otf"


def entry_color(name):
    h = int(hashlib.md5(name.encode()).hexdigest()[:6], 16)
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360, 0.45, 0.32)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def text_d(lines, size, line_gap=1.05):
    """Outlines of the lines of text (centered) as a single SVG d attribute."""
    font = TTFont(FONT)
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    s = size / font["head"].unitsPerEm
    widths = []
    for line in lines:
        widths.append(sum(gs[cmap[ord(ch)]].width * s for ch in line))
    pen = SVGPathPen(gs)
    for i, line in enumerate(lines):
        x = (max(widths) - widths[i]) / 2
        y = size * (0.8 + i * line_gap)
        for ch in line:
            g = gs[cmap[ord(ch)]]
            g.draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
            x += g.width * s
    return pen.getCommands(), max(widths), size * (0.8 + (len(lines) - 1) * line_gap + 0.25)


def main():
    out = LIB / "raster_images"
    out.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        label = "\n".join(textwrap.wrap(name, 26))
        make_image(out / f"{name}.png", label, (1280, 720), entry_color(name))

    d, w, h = text_d(["Jane", "Street"], 100)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.1f}" height="{h:.1f}" '
        f'viewBox="0 0 {w:.1f} {h:.1f}">\n<path fill="#ffffff" stroke="none" d="{d}"/>\n</svg>\n'
    )
    svg_dir = LIB / "svg_images"
    svg_dir.mkdir(parents=True, exist_ok=True)
    (svg_dir / "LOGO_stacked_w_registration_white.svg").write_text(svg)
    print(f"SoME3: {len(NAMES)} miniaturas + LOGO_stacked_w_registration_white.svg")


if __name__ == "__main__":
    main()
