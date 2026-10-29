"""Own replacements for 5 SVG icons of `svg_images/` that 2018 scenes load dynamically (`Guitar`, `Sunglasses`, `Headphones` in
`_lib/custom/drawings.py`, the sponsor mark and the AoPS mark (31 tiles: `AoPSLogo` colors sub-shapes by index)) and that were Grant's files (the static checker could not see them: the
file name comes from a class attribute; the clean-assets render found them). Flat one-color silhouettes drawn from scratch, with the
SAME name and viewBox as the originals, no text and no brand design; no byte of Grant's file is read (only the viewBox, written below).

  python make_icons_2018.py [--install] [--only guitar.svg,...]

  --install   writes into _lib/assets/svg_images/ (the original is first saved in _tools/.cache/assets2018/originales/svg_images/ if it is not
              there yet) and the registry into replacements/assets2018/assets2018_frames_sources.json.
Without --install the files go to a temp folder.
"""
import argparse
import datetime
import json
import math
import shutil
import tempfile
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[2]
ROOT = ASSETS.parents[1]
SVG = ASSETS / "svg_images"
BACKUP = ROOT / "_tools" / ".cache" / "assets2018" / "originales" / "svg_images"
REGISTRY = ASSETS / "generated" / "replacements" / "assets2018" / "assets2018_frames_sources.json"


def doc(viewbox, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}"><!-- Own flat icon drawn from scratch, CC0. -->'
            f'{body}</svg>')


def circle(cx, cy, r):
    return f'<circle stroke="none" cx="{cx}" cy="{cy}" r="{r}"/>'


def poly(points):
    return '<polygon stroke="none" points="' + " ".join(f"{x:.2f},{y:.2f}" for x, y in points) + '"/>'


def bar(p0, p1, width):
    """Rectangle (as polygon) of the given width along the segment p0 -> p1."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    n = math.hypot(dx, dy)
    nx, ny = -dy / n * width / 2, dx / n * width / 2
    return poly([(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)])


def guitar():
    # body: two overlapping circles (lower and upper bout), neck and headstock along the diagonal toward the top right
    body = circle(40, 85, 34) + circle(66, 60, 25) + circle(54, 73, 33)
    neck = bar((70, 55), (128, 14), 8) + bar((126, 16), (140, 6), 14)
    bridge = ""
    return doc("0 0 146 125", body + neck + bridge)


def sunglasses():
    lens = ('<path stroke="none" d="M 6 14 L 44 14 Q 46 36 36 42 Q 22 50 12 40 Q 4 32 6 14 Z"/>'
            '<path stroke="none" d="M 56 14 L 94 14 Q 96 32 88 40 Q 78 50 64 42 Q 54 36 56 14 Z"/>')
    bridge = '<path stroke="none" d="M 44 16 Q 50 8 56 16 L 56 21 Q 50 14 44 21 Z"/>'
    arms = bar((6, 15), (0.5, 8), 3.2) + bar((94, 15), (99.5, 8), 3.2)
    return doc("0 0 100 53.1", lens + bridge + arms)


def headphones():
    cx, cy, ro, ri = 205.17, 215, 172, 150
    # headband: half annulus (upper half), as a path with two arcs
    band = (f'<path stroke="none" d="M {cx - ro} {cy} A {ro} {ro} 0 0 1 {cx + ro} {cy} L {cx + ri} {cy} '
            f'A {ri} {ri} 0 0 0 {cx - ri} {cy} Z"/>')
    cups = ('<rect stroke="none" x="22" y="200" width="82" height="170" rx="30" ry="30"/>'
            '<rect stroke="none" x="306.3" y="200" width="82" height="170" rx="30" ry="30"/>')
    return doc("0 0 410.335 410.335", band + cups)


def udacity():
    # generic "online course" mark: a graduation cap (diamond top, base and tassel), centered in the square
    cap = poly([(1250, 560), (2150, 1010), (1250, 1460), (350, 1010)])
    base = '<path stroke="none" d="M 780 1330 L 1250 1560 L 1720 1330 L 1720 1760 Q 1250 2060 780 1760 Z"/>'
    tassel = bar((2100, 1040), (2100, 1700), 70) + circle(2100, 1760, 90)
    return doc("0 0 2500 2500", cap + base + tassel)


def aops_logo():
    # generic mark: a mosaic of 31 rounded tiles (8 columns x 4 rows, the last cell empty). `AoPSLogo` (_lib/custom/drawings.py) colors the
    # sub-shapes by index (it expects 31 of them), so the mark must have 31 separate shapes; no letters and no brand design.
    tiles = []
    w, h, gx, gy = 80, 56, 12.857, 18.667
    for k in range(31):
        c, r = k % 8, k // 8
        x, y = c * (w + gx), r * (h + gy)
        tiles.append(f'<rect stroke="none" x="{x:.2f}" y="{y:.2f}" width="{w}" height="{h}" rx="14" ry="14"/>')
    return doc("0 0 730 280", "".join(tiles))


ICONS = {"guitar.svg": (guitar, "flat guitar silhouette (own drawing)"),
         "sunglasses.svg": (sunglasses, "flat sunglasses silhouette (own drawing)"),
         "headphones.svg": (headphones, "flat headphones silhouette (own drawing)"),
         "udacity.svg": (udacity, "generic online-course mark: graduation cap (own drawing, not the sponsor logo)"),
         "aops_logo.svg": (aops_logo, "generic 31-tile mosaic mark (own drawing, not the AoPS logo)")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    names = [n for n in ICONS if not a.only or n in a.only.split(",")]
    out = SVG if a.install else Path(tempfile.mkdtemp(prefix="icons2018_"))
    registry = {}
    for n in names:
        fn, subject = ICONS[n]
        if a.install:
            BACKUP.mkdir(parents=True, exist_ok=True)
            if (SVG / n).exists() and not (BACKUP / n).exists():
                shutil.copy2(SVG / n, BACKUP / n)
        (out / n).write_text(fn(), encoding="utf-8")
        registry["svg_images/" + n] = {
            "asset": "svg_images/" + n, "name": n, "subject": subject, "author": "own (code)",
            "license": "CC0", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/", "page_url": "",
            "changes": "Drawn from scratch with the same name and viewBox as the original; no byte of Grant's file is used.",
            "status": "generated", "via": "drawing", "note": "", "recipe_version": "2018-icons-v1",
            "verified_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        print("ok", n)
    if a.install:
        old = json.loads(REGISTRY.read_text()) if REGISTRY.exists() else {}
        old.update(registry)
        REGISTRY.write_text(json.dumps(old, indent=1, ensure_ascii=False))
    else:
        print("temp folder:", out)


if __name__ == "__main__":
    main()
