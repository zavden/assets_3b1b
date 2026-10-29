"""Generates the placeholder assets of _2022/some2 (announcement.py and winners.py), which lived in Grant's Dropbox or in his output folder:

In _lib/assets/svg_images/ (the scene asks for them by name):
- BrilliantLogo.svg (announcement.py, Winners): box with an X (_tools/placeholder.py).
- teaching.svg, gem.svg, memory.svg (winners.py, FourCategories): simple placeholder icons
  (blackboard with teacher, gem, memory chip), with flat fills so that set_fill paints them.
- quarter-note.svg (winners.py, MusicSidenote): a quarter note (head and stem).

In _lib/data/2022/some2/winners/ (DOC_DIR of winners.py, which in the original was his output folder):
- thumbnails/<slug>.jpg: a placeholder thumbnail (1280x720) for each video cited in ExampleChannels,
  Winners and featured_entries.csv.
- featured_entries.csv: columns Title, Author, Link (FourCategories reads it with pandas and uses 17 rows):
  the 5 real winners cited in the Winners scene and 12 placeholder mentions.
- sponsor_logos/: Brilliant.png, RiscZero.png, ProtocolLabs.png (placeholders) and GoogleFonts.svg (placeholder).

Usage: python make_some2_assets.py"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]  # _lib/assets
DATA = ASSETS.parent / "data" / "2022" / "some2" / "winners"
sys.path.insert(0, str(ASSETS.parents[1] / "_tools"))
from placeholder import make_image, make_svg


def shrink(points, k=0.9):
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    return [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in points]


def poly(points, **style):
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in style.items())
    return f'<polygon points="{pts}" {attrs}/>'


def svg(body, size=100):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}px" height="{size}px" '
            f'viewBox="0 0 {size} {size}">{body}</svg>')


def gem_svg():
    facets = [
        [(5, 42), (30, 20), (40, 42)],
        [(30, 20), (70, 20), (60, 42), (40, 42)],
        [(70, 20), (95, 42), (60, 42)],
        [(5, 42), (40, 42), (50, 92)],
        [(40, 42), (60, 42), (50, 92)],
        [(60, 42), (95, 42), (50, 92)],
    ]
    return svg("<g>" + "".join(poly(shrink(f, 0.93), fill="#ffffff") for f in facets) + "</g>")


def memory_svg():
    body = '<rect x="26" y="26" width="48" height="48" rx="4" fill="#ffffff"/>'
    pins = ""
    for t in (34, 46, 58):
        pins += f'<rect x="{t}" y="10" width="8" height="14" fill="#ffffff"/>'
        pins += f'<rect x="{t}" y="76" width="8" height="14" fill="#ffffff"/>'
        pins += f'<rect x="10" y="{t}" width="14" height="8" fill="#ffffff"/>'
        pins += f'<rect x="76" y="{t}" width="14" height="8" fill="#ffffff"/>'
    return svg("<g>" + body + pins + "</g>")


def teaching_svg():
    frame = "".join([
        '<rect x="6" y="14" width="88" height="6" fill="#ffffff"/>',
        '<rect x="6" y="56" width="88" height="6" fill="#ffffff"/>',
        '<rect x="6" y="14" width="6" height="48" fill="#ffffff"/>',
        '<rect x="88" y="14" width="6" height="48" fill="#ffffff"/>',
        '<rect x="22" y="30" width="30" height="4" fill="#ffffff"/>',
        '<rect x="22" y="42" width="44" height="4" fill="#ffffff"/>',
    ])
    teacher = ('<circle cx="22" cy="72" r="6" fill="#ffffff"/>'
               '<polygon points="12,96 32,96 28,80 16,80" fill="#ffffff"/>'
               '<polygon points="30,82 62,64 64,68 32,87" fill="#ffffff"/>')
    return svg("<g>" + frame + teacher + "</g>")


def quarter_note_svg():
    return svg('<g><ellipse cx="38" cy="78" rx="18" ry="12" transform="rotate(-20 38 78)" fill="#ffffff"/>'
               '<rect x="52" y="10" width="7" height="68" fill="#ffffff"/></g>')


SVGS = {
    "teaching.svg": teaching_svg(),
    "gem.svg": gem_svg(),
    "memory.svg": memory_svg(),
    "quarter-note.svg": quarter_note_svg(),
}

# Slugs de winners.py
EXAMPLE_CHANNELS = ["3gyHKCDq1YA", "5M2RWtD4EzI", "-64UT8yikng", "_DaTsI42Wvo", "6JxvKfSV9Ns", "dKtsjQtigag",
                    "8x374slJGuo", "_lb1AxwXLaM", "-vxW42R47bc", "UJp4q2D2Nh0", "2dwQUUDt5Is"]
WINNERS = [
    ("a-767WnbaCQ", "Percolation: a Mathematical Phase Transition", "Spectral Collective"),
    ("crystalgroups", "Clear Crystal Conundrums", "Ex Planaria"),
    ("5M2RWtD4EzI", "This Is the Calculus They Won't Teach You", "A Well-Rested Dog"),
    ("gsZiJeaMO48", "How Realistic CGI Works (And How To Do It Way Faster)", "Joshua Maros"),
    ("6hVPNONm7xw", "The Coolest Hat Puzzle You've Probably Never Heard", "Going Null"),
]
HONORABLE = ["v_HeaeUUOnc", "piF6D6CQxUw", "QC3CjBZLHXs", "KufsL2VgELo", "zR_hpai3XkY", "HeBP3MG-WHg",
             "2dwQUUDt5Is", "3gyHKCDq1YA", "nK2jYk37Rlg", "l7bYY2U5ld8", "dwNxVpbEVcc", "CFBa2ezTQJQ",
             "gnUYoQ1pwes", "LUCvSsx6-EU", "-vxW42R47bc", "inverse-turing-test", "bezier-curve-guide",
             "does-every-game-have-a-winner", "Autodiff", "panorama-homography"]
FEATURED_EXTRA = 12  # placeholder mentions, in addition to the 5 winners

SPONSORS = [
    ("Brilliant.png", "Brilliant", "1000x300", "#2b5548"),
    ("RiscZero.png", "RISC Zero", "1000x300", "#3a3a3a"),
    ("ProtocolLabs.png", "Protocol Labs", "1000x300", "#26405a"),
]


def main():
    svg_dir = ASSETS / "svg_images"
    svg_dir.mkdir(parents=True, exist_ok=True)
    make_svg(svg_dir / "BrilliantLogo.svg", (100, 100))
    for name, text in SVGS.items():
        (svg_dir / name).write_text(text)

    thumbs = DATA / "thumbnails"
    thumbs.mkdir(parents=True, exist_ok=True)
    featured = [(t, a, f"https://youtu.be/{s}") for s, t, a in WINNERS]
    for k in range(FEATURED_EXTRA):
        featured.append((f"Featured entry {k + 1}", f"Author {k + 1}", f"https://youtu.be/{HONORABLE[k]}"))
    slugs = dict.fromkeys(EXAMPLE_CHANNELS + [w[0] for w in WINNERS] + HONORABLE)
    for slug in slugs:
        make_image(thumbs / f"{slug}.jpg", slug, (1280, 720), "#2b3a55")
    with open(DATA / "featured_entries.csv", "w", newline="") as fp:
        w = csv.writer(fp)
        w.writerow(["Title", "Author", "Link"])
        w.writerows(featured)

    logos = DATA / "sponsor_logos"
    logos.mkdir(parents=True, exist_ok=True)
    for name, label, size, bg in SPONSORS:
        w, h = map(int, size.split("x"))
        make_image(logos / name, label, (w, h), bg)
    make_svg(logos / "GoogleFonts.svg", (400, 120))


if __name__ == "__main__":
    main()
