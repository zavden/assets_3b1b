"""Generates booth.svg and company_building.svg, placeholder SVGs for outside_videos/talent
(the originals are private).

- booth.svg: fair stall with a striped awning, posts, counter and sign (~0.86 width/height ratio).
  The code only does set_height(1.35) and paints it a single color, so it is drawn with shapes
  separated by gaps so that the structure can be told apart even in a single color.
- company_building.svg: office building with windows (holes) and a door; the code does
  set_height(3), set_fill(GREY_B) and moves it to the left edge.

Usage: python make_talent_svgs.py   (writes here and to _lib/assets/svg_images/)"""
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]


def rect(x0, y0, x1, y1, hole=False):
    if hole:  # opposite direction -> hole
        return f"M {x0},{y0} L {x0},{y1} L {x1},{y1} L {x1},{y0} Z"
    return f"M {x0},{y0} L {x1},{y0} L {x1},{y1} L {x0},{y1} Z"


def svg(w, h, paths):
    body = "\n".join(f'<path d="{d}"/>' for d in paths)
    return f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n{body}\n</svg>\n'


def booth():
    paths = []
    paths.append(rect(4, 8, 116, 16))  # top bar
    n = 6
    x0, x1 = 6, 114
    sw = (x1 - x0) / n
    for k in range(n):  # awning with stripes and scalloped edge
        a, b = x0 + k * sw + 1, x0 + (k + 1) * sw - 1
        r = (b - a) / 2
        if k % 2 == 0:
            paths.append(f"M {a:.2f},19 L {b:.2f},19 L {b:.2f},40 A {r:.2f},{r:.2f} 0 0 1 {a:.2f},40 Z")
        else:  # shorter alternating stripes, to tell them apart while being a single color
            paths.append(f"M {a:.2f},19 L {b:.2f},19 L {b:.2f},36 A {r:.2f},{r:.2f} 0 0 1 {a:.2f},36 Z")
    paths.append(rect(12, 52, 18, 92))   # posts
    paths.append(rect(102, 52, 108, 92))
    # sign (frame with a hole)
    paths.append(rect(40, 54, 80, 72) + " " + rect(43, 57, 77, 69, hole=True))
    # counter with a hollow panel
    paths.append(rect(6, 92, 114, 126) + " " + rect(12, 98, 108, 120, hole=True))
    paths.append(rect(2, 130, 118, 136))  # floor
    (HERE / "booth.svg").write_text(svg(120, 140, paths))


def company_building():
    paths = []
    # main tower with windows and door as holes
    main = rect(44, 12, 112, 196)
    for r in range(8):
        for c in range(4):
            x = 50 + c * 15
            y = 24 + r * 19
            main += " " + rect(x, y, x + 9, y + 11, hole=True)
    main += " " + rect(68, 170, 88, 196, hole=True)
    paths.append(main)
    # low wing on the left
    wing = rect(6, 90, 40, 196)
    for r in range(5):
        for c in range(2):
            x = 12 + c * 14
            y = 100 + r * 19
            wing += " " + rect(x, y, x + 8, y + 11, hole=True)
    paths.append(wing)
    # cornice and antenna
    paths.append(rect(40, 6, 116, 12))
    paths.append(rect(76, -14 + 14, 80, 6))
    paths.append(rect(2, 196, 120, 200))  # floor
    (HERE / "company_building.svg").write_text(svg(122, 200, paths))


def main():
    booth()
    company_building()
    for n in ("booth.svg", "company_building.svg"):
        shutil.copy(HERE / n, LIB / "assets" / "svg_images" / n)
    print("ok")


if __name__ == "__main__":
    main()
