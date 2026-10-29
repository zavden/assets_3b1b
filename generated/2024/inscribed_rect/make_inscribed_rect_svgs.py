"""Generates the placeholder SVGs of _2024/inscribed_rect (the originals are private):

- example_loop1..4.svg: smooth closed loops, a single <path> without fill, because
  helpers.get_example_loop takes family_members_with_points()[0].
- xmas_tree.svg: Christmas tree outline (three tiers and trunk), a single closed path.
- gingerbread_outline.svg: gingerbread man outline, a single closed path.
- KleinReference.svg: open curve that serves as the axis of the Klein bottle. The code closes it
  with add_line_to, rotates it 180° and gives it a tube of radius 1 -> 0.3 -> 1; that is why it is drawn with
  the body at the lower right of the SVG and the neck curving to the other side.
- scissors.svg, puzzle_piece.svg, gear.svg: simple filled icons.

Usage: python make_inscribed_rect_svgs.py   (writes here and to _lib/assets/svg_images/)"""
import shutil
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]
NAMES = [
    "example_loop1.svg", "example_loop2.svg", "example_loop3.svg", "example_loop4.svg",
    "xmas_tree.svg", "gingerbread_outline.svg", "KleinReference.svg",
    "scissors.svg", "puzzle_piece.svg", "gear.svg",
]


def to_svg_coords(points, size=200, pad=10):
    """Points with y up -> SVG coordinates (y down) inside a frame."""
    pts = np.array(points, dtype=float)
    pts[:, 1] *= -1
    lo = pts.min(0)
    span = (pts.max(0) - lo).max()
    pts = (pts - lo) * (size - 2 * pad) / span + pad
    return pts


def catmull_rom_path(points, closed=True):
    """Path of cubic Béziers that passes smoothly through all the points."""
    p = np.asarray(points)
    n = len(p)
    segs = range(n) if closed else range(n - 1)
    d = [f"M {p[0][0]:.2f},{p[0][1]:.2f}"]
    for i in segs:
        p0 = p[(i - 1) % n] if closed or i > 0 else p[i]
        p1, p2 = p[i], p[(i + 1) % n]
        p3 = p[(i + 2) % n] if closed or i + 2 < n else p2
        c1 = p1 + (p2 - p0) / 6
        c2 = p2 - (p3 - p1) / 6
        d.append(f"C {c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}")
    if closed:
        d.append("Z")
    return " ".join(d)


def polygon_path(points):
    p = np.asarray(points)
    return "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in p) + " Z"


def stroke_svg(d, size=200):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}">\n'
        f'<path d="{d}" fill="none" stroke="#ffffff" stroke-width="2"/>\n</svg>\n'
    )


def fill_svg(paths, w, h):
    body = "\n".join(f'<path d="{d}" fill="#ffffff"/>' for d in paths)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n{body}\n</svg>\n'
    )


def polar_loop(coefs, n=36, stretch=(1.0, 1.0)):
    """r(t) = 1 + sum a cos(k t + phi); coefs = [(k, a, phi), ...]."""
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    r = 1 + sum(a * np.cos(k * t + phi) for k, a, phi in coefs)
    return np.stack([stretch[0] * r * np.cos(t), stretch[1] * r * np.sin(t)], 1)


def example_loops():
    loops = {
        1: polar_loop([(2, 0.18, 0.4), (3, 0.12, 1.3), (5, 0.05, 2.0)], stretch=(1.25, 0.9)),
        2: polar_loop([(2, 0.15, 1.0), (3, 0.22, 0.2), (4, 0.08, 2.5), (6, 0.04, 0.7)]),
        3: polar_loop([(1, 0.10, 0.0), (2, 0.25, 2.2), (5, 0.08, 1.1)], stretch=(1.1, 1.0)),
        4: polar_loop([(2, 0.20, 2.8), (3, 0.16, 1.9), (4, 0.10, 0.3), (7, 0.03, 1.4)], stretch=(1.2, 1.0)),
    }
    for k, pts in loops.items():
        (HERE / f"example_loop{k}.svg").write_text(stroke_svg(catmull_rom_path(to_svg_coords(pts))))


def xmas_tree():
    half = [  # right side, from the tip downward (and upward)
        (0, 5.0), (1.0, 3.6), (0.5, 3.6), (1.6, 2.2), (0.9, 2.2), (2.2, 0.6),
        (0.45, 0.6), (0.45, 0.0),
    ]
    left = [(-x, y) for x, y in reversed(half[1:])]
    pts = half + left
    (HERE / "xmas_tree.svg").write_text(stroke_svg(polygon_path(to_svg_coords(pts))))


def gingerbread():
    half = [  # from the crown downward along the right side
        (0, 3.0), (0.6, 2.85), (0.9, 2.4), (0.75, 1.95), (0.5, 1.72),
        (1.2, 1.62), (2.0, 1.5), (2.3, 1.2), (2.0, 0.9), (1.0, 0.8),
        (0.95, 0.0), (1.3, -1.2), (1.55, -1.9), (1.25, -2.25), (0.8, -2.05),
        (0.3, -0.95),
    ]
    left = [(-x, y) for x, y in reversed(half[1:])]
    pts = half + [(0, -0.75)] + left
    (HERE / "gingerbread_outline.svg").write_text(
        stroke_svg(catmull_rom_path(to_svg_coords(pts)))
    )


def klein_reference():
    # Desired final shape in manim (y up): body at x=0 from bottom to top, neck that goes up, curves
    # to the right, goes down and re-enters the body. The code rotates the SVG 180°, so it is
    # written with x and y inverted.
    final = [
        (0, -2.5), (0, -1.5), (0, -0.5), (0, 0.5), (0.1, 1.5), (0.5, 2.5), (1.4, 3.2),
        (2.4, 3.1), (3.0, 2.3), (3.1, 1.0), (2.8, -0.2), (2.0, -0.8), (1.0, -0.9),
        (0.4, -1.3), (0.15, -2.0),
    ]
    pts = [(-x, -y) for x, y in final]
    (HERE / "KleinReference.svg").write_text(
        stroke_svg(catmull_rom_path(to_svg_coords(pts), closed=False))
    )


def circle_path(cx, cy, r, ccw=False):
    sweep = 0 if ccw else 1
    return (
        f"M {cx - r:.2f},{cy:.2f} A {r},{r} 0 1 {sweep} {cx + r:.2f},{cy:.2f} "
        f"A {r},{r} 0 1 {sweep} {cx - r:.2f},{cy:.2f} Z"
    )


def scissors():
    # Two rings (with a hole) and two crossed leaves, vertical, tips up
    rings = [circle_path(cx, 150, 22) + " " + circle_path(cx, 150, 13, ccw=True) for cx in (35, 95)]
    blades = [
        "M 40,128 L 58,90 L 74,8 L 80,10 L 70,92 L 52,132 Z",
        "M 90,128 L 72,90 L 56,8 L 50,10 L 60,92 L 78,132 Z",
    ]
    pivot = circle_path(65, 88, 5)
    (HERE / "scissors.svg").write_text(fill_svg(rings + blades + [pivot], 130, 180))


def puzzle_piece():
    d = (
        "M 20,40 L 70,40 C 62,20 72,8 85,8 C 98,8 108,20 100,40 L 150,40 L 150,90 "
        "C 170,82 182,92 182,105 C 182,118 170,128 150,120 L 150,170 L 100,170 "
        "C 108,150 98,138 85,138 C 72,138 62,150 70,170 L 20,170 L 20,120 "
        "C 40,128 52,118 52,105 C 52,92 40,82 20,90 Z"
    )
    (HERE / "puzzle_piece.svg").write_text(fill_svg([d], 200, 180))


def gear():
    n_teeth, r_out, r_in, r_hole = 10, 90, 72, 28
    pts = []
    for k in range(n_teeth):
        a = 2 * np.pi * k / n_teeth
        for da, r in ((-0.30, r_in), (-0.17, r_out), (0.17, r_out), (0.30, r_in)):
            t = a + da * 2 * np.pi / n_teeth
            pts.append((100 + r * np.cos(t), 100 + r * np.sin(t)))
    d = polygon_path(pts) + " " + circle_path(100, 100, r_hole, ccw=True)
    (HERE / "gear.svg").write_text(fill_svg([d], 200, 200))


def main():
    example_loops()
    xmas_tree()
    gingerbread()
    klein_reference()
    scissors()
    puzzle_piece()
    gear()
    for n in NAMES:
        shutil.copy(HERE / n, LIB / "assets" / "svg_images" / n)
    print("ok")


if __name__ == "__main__":
    main()
