"""Own replacement for `raster_images/VerticalTempGradient.png` (2019 diffyq, 51 scenes with
`color_using_background_image("VerticalTempGradient")`): vertical temperature gradient, red at the top and blue
at the bottom, with the same colors as the scenes' `temperature_to_color` (red, yellow, green, turquoise, blue).
It is a gradient made with numpy; it copies nothing from Grant's original.

  python make_vertical_temp_gradient.py [--out FOLDER]   (by default writes _lib/assets/raster_images/VerticalTempGradient.png)"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image

ASSETS = Path(__file__).resolve().parents[3]
# From top (hot) to bottom (cold); positions relative to the height
STOPS = [
    (0.00, (255, 0, 0)),
    (0.12, (255, 66, 0)),
    (0.25, (255, 236, 0)),
    (0.375, (177, 216, 65)),
    (0.50, (119, 198, 127)),
    (0.625, (93, 208, 177)),
    (0.75, (89, 199, 212)),
    (0.875, (88, 196, 221)),
    (1.00, (88, 196, 221)),
]
SIZE = (2560, 1440)


def make(path):
    h = SIZE[1]
    t = np.linspace(0, 1, h)
    pos = [p for p, _ in STOPS]
    channels = [np.interp(t, pos, [c[i] for _, c in STOPS]) for i in range(3)]
    row = np.stack(channels, axis=1).round().astype(np.uint8)
    img = np.repeat(row[:, None, :], SIZE[0], axis=1)
    Image.fromarray(img, "RGB").convert("RGBA").save(path)
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = Path(a.out) if a.out else ASSETS / "raster_images"
    out.mkdir(parents=True, exist_ok=True)
    print(make(out / "VerticalTempGradient.png"))
