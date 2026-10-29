"""Own replacement for `svg_images/BatmanLogo.svg` (2019 diffyq/part2, scene FourierBatman, which draws the
contour with a Fourier series): generic silhouette of a bat with its wings spread, made with a list of
points (right half mirrored). It is not the DC logo and copies nothing from Grant's original: a single closed
stroke, white fill, viewBox 1920x1080 like the original (the scene scales it to height 4).

  python make_bat_silhouette.py [--out FILE.svg]   (by default writes _lib/assets/svg_images/BatmanLogo.svg)"""
import argparse
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[3]
CENTER = (960, 560)
# Right half, from the top to the bottom center: (horizontal offset, y relative to the center)
RIGHT_HALF = [
    (0, -95),                                   # head
    (26, -165), (50, -98),                      # ear
    (110, -100), (205, -150), (330, -205), (470, -228), (610, -208), (720, -150), (805, -55),   # top edge of the wing
    (715, -72), (650, 8), (595, -30), (530, 58), (468, 14), (400, 104), (335, 60), (262, 135),  # scalloped edges
    (195, 90), (130, 125), (70, 80), (36, 175),  # cola
    (0, 215),
]


def svg_text():
    cx, cy = CENTER
    right = [(cx + dx, cy + dy) for dx, dy in RIGHT_HALF]
    left = [(cx - dx, cy + dy) for dx, dy in reversed(RIGHT_HALF[1:-1])]
    points = right + left
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in points) + " Z"
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<!-- Silueta propia de un murcielago (generada por make_bat_silhouette.py); no es el logo de ninguna marca. -->\n"
        '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080">\n'
        f'  <path fill="#FFFFFF" d="{d}"/>\n'
        "</svg>\n"
    )


def make(path):
    Path(path).write_text(svg_text(), encoding="utf-8")
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(ASSETS / "svg_images" / "BatmanLogo.svg"))
    args = parser.parse_args()
    print(make(args.out))
