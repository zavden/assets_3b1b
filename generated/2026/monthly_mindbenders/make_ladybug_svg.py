"""Generates ladybug.svg, a placeholder SVG for monthly_mindbenders/ladybug (the original is private).

The code uses SVGMobject("ladybug"), paints it ALL GREY_A and puts a red Dot below it of
radius 0.36 * height, aligned with the bottom edge (`circle.move_to(ladybug, DOWN)`). That is why the
drawing is a ladybug seen from above made only of filled shapes (head, shell ring, wing line, spots,
legs and antennae), with a circular body of diameter ~0.72 of the height and stuck to the bottom edge: that way
the gray shapes sit on top of the red circle.

Usage: python make_ladybug_svg.py   (writes here and to _lib/assets/svg_images/ladybug.svg)"""
import math
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]
W, H = 140, 140
CX, CY, R = 70, 90, 50  # body: circle of radius 50 with the bottom edge at y=140


def circle_path(cx, cy, r, ccw=False):
    sweep = 0 if ccw else 1
    return (f"M {cx - r:.2f},{cy:.2f} A {r:.2f},{r:.2f} 0 1 {sweep} {cx + r:.2f},{cy:.2f} "
            f"A {r:.2f},{r:.2f} 0 1 {sweep} {cx - r:.2f},{cy:.2f} Z")


def thick_line(x1, y1, x2, y2, w):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    pts = [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)]
    return "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"


def polyline_ribbon(points, w):
    return " ".join(thick_line(*points[i], *points[i + 1], w) for i in range(len(points) - 1))


def main():
    parts = []
    # antennae
    parts.append(polyline_ribbon([(64, 16), (58, 8), (50, 3)], 2.4))
    parts.append(polyline_ribbon([(76, 16), (82, 8), (90, 3)], 2.4))
    # head
    parts.append(circle_path(CX, 28, 14))
    # shell ring (outer clockwise, inner counterclockwise = hole)
    parts.append(circle_path(CX, CY, R) + " " + circle_path(CX, CY, R - 5.5, ccw=True))
    # center line between the wings
    parts.append(thick_line(CX, 42, CX, 138, 3))
    # spots
    for (x, y, r) in [(-26, -14, 8), (26, -14, 8), (-30, 12, 9), (30, 12, 9), (-14, 33, 6.5), (14, 33, 6.5)]:
        parts.append(circle_path(CX + x, CY + y, r))
    # legs (3 per side)
    for sx in (-1, 1):
        for (y0, dx, dy) in [(-18, 16, -14), (6, 20, 0), (30, 16, 16)]:
            x_edge = CX + sx * math.sqrt(max(R ** 2 - y0 ** 2, 0))
            pts = [(x_edge - sx * 3, CY + y0), (x_edge + sx * dx * .55, CY + y0 + dy * .4), (x_edge + sx * dx, CY + y0 + dy)]
            parts.append(polyline_ribbon(pts, 4.2))
    body = "\n".join(f'<path d="{d}"/>' for d in parts)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
           f'{body}\n</svg>\n')
    (HERE / "ladybug.svg").write_text(svg)
    shutil.copy(HERE / "ladybug.svg", LIB / "assets" / "svg_images" / "ladybug.svg")
    print("ok")


if __name__ == "__main__":
    main()
