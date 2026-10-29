"""Generates the placeholder SVG of _2023/moser_reboot/main.py (the original lived in Grant's unpublished
repo):

- cautionary_tale.svg (Introduction): the title "A Cautionary Tale" in CMU Serif Italic, as a SINGLE
  shape (one <path> with a subpath per letter outline). The scene takes `tale[0].get_subpaths()` and
  draws them one by one from left to right, so the original was also a single path.

It is written to _lib/assets/svg_images/.

Usage: python make_moser_reboot_assets.py"""
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

LIB = Path(__file__).resolve().parents[3]  # _lib/assets
FONT = "/usr/share/fonts/cm-unicode/cmunti.otf"


def main():
    font = TTFont(FONT)
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    size = 100
    s = size / font["head"].unitsPerEm
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    x = 0.0
    for ch in "A Cautionary Tale":
        g = gs[cmap[ord(ch)]]
        g.draw(TransformPen(pen, (s, 0, 0, -s, x, size * 0.8)))
        x += g.width * s
    w, h = x, size * 1.1
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.1f}" height="{h:.1f}" '
        f'viewBox="0 0 {w:.1f} {h:.1f}">\n<path fill="#000000" stroke="none" d="{pen.getCommands()}"/>\n</svg>\n'
    )
    out = LIB / "svg_images"
    out.mkdir(parents=True, exist_ok=True)
    (out / "cautionary_tale.svg").write_text(svg)
    print("moser_reboot: cautionary_tale.svg")


if __name__ == "__main__":
    main()
