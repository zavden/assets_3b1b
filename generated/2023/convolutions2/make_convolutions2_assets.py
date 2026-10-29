"""Generates the placeholder assets of _2023/convolutions2 (the originals lived in Grant's Dropbox,
videos/2023/...):

- LastFewVideos (gauss_example_supplements.py): 4 thumbnails of 1280x720 with the video's title, at the
  root of _lib/assets/raster_images/ (EquationThumbnail.png, Thumbnail.png, Thumbnail.jpg, Thumbnail2.png):
  the scene asks for them by Grant's Dropbox path (2022/convolutions/discrete/images/EquationThumbnail.png,
  2023/clt/main/images/Thumbnail.png, 2023/clt/Thumbnail.jpg, 2023/convolutions2/Thumbnail/Thumbnail2.png)
  and _lib/manim_imports_ext.py looks for them by name.
- DiscreteDistributionSum.png (continuous.py, Convolutions scene): "hand-made" diagram of the discrete case,
  with the distributions of two dice X and Y and that of the sum X + Y (triangular), on a black background. In
  _lib/assets/raster_images/.
- SubstackQR2.svg (gauss_example_supplements.py, DrawQRCode): real QR (segno) of https://www.3blue1brown.com.
  The first two submobjects are the background and the frame (the scene removes them with `code.remove(*code[:2])`);
  a square per data module and the pieces of the 3 position eyes follow. In _lib/assets/svg_images/.

Usage: python make_convolutions2_assets.py"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]  # _lib/assets
sys.path.insert(0, str(ASSETS.parents[1] / "_tools"))
from placeholder import make_image

THUMBNAILS = [
    ("EquationThumbnail.png", "Convolutions (discrete)", "#2b3a55"),
    ("Thumbnail.png", "Central limit theorem", "#2b4a55"),
    ("Thumbnail.jpg", "Why pi is in a Gaussian", "#3a2b55"),
    ("Thumbnail2.png", "Convolutions (continuous)", "#2b5548"),
]


def make_thumbnails():
    root = ASSETS / "raster_images"
    for rel, label, bg in THUMBNAILS:
        out = root / rel
        make_image(out, f"Miniatura: {label}", (1280, 720), bg)


def make_discrete_diagram():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.family"] = "DejaVu Serif"
    fig = plt.figure(figsize=(6.5, 5.0), dpi=200, facecolor="black")
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.15], hspace=0.65, wspace=0.3,
                          left=0.08, right=0.96, top=0.9, bottom=0.1)
    faces = np.arange(1, 7)
    p = np.full(6, 1 / 6)

    def style(ax, title, color, xs, ys, xticks):
        ax.set_facecolor("black")
        ax.bar(xs, ys, color=color, width=0.8)
        ax.set_title(title, color="white", fontsize=15)
        ax.set_xticks(xticks)
        ax.set_ylim(0, 0.3)
        ax.set_yticks([])
        ax.tick_params(colors="#bbbbbb", labelsize=9)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color("#bbbbbb")

    style(fig.add_subplot(gs[0, 0]), "X", "#58c4dd", faces, p, faces)
    style(fig.add_subplot(gs[0, 1]), "Y", "#ffff00", faces, p, faces)
    sums = np.arange(2, 13)
    conv = np.convolve(p, p)
    ax = fig.add_subplot(gs[1, :])
    style(ax, "X + Y", "#83c167", sums, conv, sums)
    fig.text(0.52, 0.52, R"$\ast$", color="white", fontsize=22, ha="center", va="center")
    fig.text(0.5, 0.025, "[imagen de relleno]", color="#777777", fontsize=8, ha="center")
    fig.savefig(ASSETS / "raster_images" / "DiscreteDistributionSum.png", facecolor="black")
    plt.close(fig)


def make_qr(out, text="https://www.3blue1brown.com"):
    import segno

    def fmt(v):
        return f"{v:g}"

    def rect_d(x, y, w, h):
        return f"M{fmt(x)} {fmt(y)}h{fmt(w)}v{fmt(h)}h{fmt(-w)}Z"

    qr = segno.make(text, error="L", boost_error=False)
    matrix = [list(row) for row in qr.matrix]
    n = len(matrix)
    in_finder = [[False] * n for _ in range(n)]
    finders_at = [(0, 0), (0, n - 7), (n - 7, 0)]
    for (r0, c0) in finders_at:
        for r in range(r0, r0 + 7):
            for c in range(c0, c0 + 7):
                in_finder[r][c] = True
    m = 2  # silence zone
    parts = [
        # the first two are removed in the scene: background and frame
        f'<path fill="#ffffff" stroke="none" d="{rect_d(-m, -m, n + 2 * m, n + 2 * m)}"/>',
        f'<path fill="none" stroke="#000000" stroke-width="0.15" d="{rect_d(-m, -m, n + 2 * m, n + 2 * m)}"/>',
    ]
    for r in range(n):
        for c in range(n):
            if matrix[r][c] and not in_finder[r][c]:
                parts.append(f'<path fill="#000000" stroke="none" d="{rect_d(c, r, 1, 1)}"/>')
    for (r0, c0) in finders_at:
        ring = rect_d(c0, r0, 7, 7) + f"M{fmt(c0 + 1)} {fmt(r0 + 1)}v5h5v-5Z"
        parts.append(f'<path fill="#000000" stroke="none" d="{ring}"/>')
        parts.append(f'<path fill="#000000" stroke="none" d="{rect_d(c0 + 2, r0 + 2, 3, 3)}"/>')
    size = n + 2 * m
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-m} {-m} {size} {size}" '
           f'width="{size * 10}" height="{size * 10}">\n' + "\n".join(parts) + "\n</svg>\n")
    out.write_text(svg)


def main():
    make_thumbnails()
    make_discrete_diagram()
    svg_dir = ASSETS / "svg_images"
    svg_dir.mkdir(parents=True, exist_ok=True)
    make_qr(svg_dir / "SubstackQR2.svg")
    print("convolutions2: 4 miniaturas, DiscreteDistributionSum.png, SubstackQR2.svg")


if __name__ == "__main__":
    main()
