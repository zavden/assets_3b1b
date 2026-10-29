"""Generates the placeholder assets of _2023/standup_maths (the originals are not in the public repo):

- pool_table.png (pool.py, PoolTableReflections): 2:1 pool table (1600x800) seen from above:
  wooden rail, cushion, green cloth, 6 pockets and the rail's "diamonds" at the positions the
  scene uses (the scene puts `buff=0.475` between the image edge and the cloth, with the image 4 tall,
  that is 95 px of 800; the bottom diamonds go at 0.315 below the cloth and the side ones at 0.309).
  It is written to _lib/assets/raster_images/.
- basketball-court.png (basketball.py, ShotHistory): full horizontal 94x50 ft court
  (1880x1000), hoop at the left end (the scene rotates it 90 degrees and leaves the hoop at the bottom). Dark background
  with light lines so that the yellow dots and the bars are visible. In _lib/assets/raster_images/.
- Shot data (basketball.py, load_data): the original reads /Users/grant/Downloads/allShots/
  nbaShots{aa}_{bb}.csv (NBA shots, columns LOC_X, LOC_Y in tenths of a foot with the hoop at (0, 0), and
  SHOT_MADE_FLAG). Here it is SYNTHETIC data with the same shape (not real shots): 100 000 shots per
  season, from 1997-98 to 2021-22, with the mix of zones changing like in the real league (less
  mid-range and more threes every year). They are written to _lib/data/2023/standup_maths/allShots/.

Usage: python make_standup_maths_assets.py"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]  # _lib/assets
LIB = ASSETS.parent  # _lib
RASTER = ASSETS / "raster_images"
DATA = LIB / "data" / "2023" / "standup_maths" / "allShots"

N_SHOTS = 100_000


# ---------------------------------------------------------------- pool table

def make_pool_table(out):
    W, H = 1600, 800
    px = 200  # px per manim unit (the image is 4 tall)
    buff = 0.475 * px  # edge of the image to the cloth
    img = Image.new("RGB", (W, H), "#4b2e17")
    d = ImageDraw.Draw(img)
    # subtle grain of the rail
    for y in range(0, H, 9):
        d.line([0, y, W, y], fill="#52331b", width=1)
    # cushion and cloth
    d.rectangle([buff - 40, buff - 40, W - buff + 40, H - buff + 40], fill="#0b3d22")
    d.rectangle([buff, buff, W - buff, H - buff], fill="#1b7d49")
    d.rectangle([buff, buff, W - buff, H - buff], outline="#14602f", width=3)
    # pockets
    for (cx, cy, r) in [
        (buff, buff, 46), (W - buff, buff, 46), (buff, H - buff, 46), (W - buff, H - buff, 46),
        (W / 2, buff - 12, 40), (W / 2, H - buff + 12, 40),
    ]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#050505")

    def diamond(cx, cy, r=9):
        d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill="#efe6c9")

    # diamonds: same places the scene uses (9 at the bottom, 5 at the sides), repeated by symmetry
    inner_l, inner_r, inner_t, inner_b = buff, W - buff, buff, H - buff
    for x in np.linspace(inner_l - 0.1 * px, inner_r + 0.1 * px, 9):
        diamond(x, inner_b + 0.315 * px)
        diamond(x, inner_t - 0.315 * px)
    for y in np.linspace(inner_b + 0.1 * px, inner_t - 0.1 * px, 5):
        diamond(inner_r + 0.309 * px, y)
        diamond(inner_l - 0.309 * px, y)
    # break points
    d.ellipse([W * 0.25 - 5, H / 2 - 5, W * 0.25 + 5, H / 2 + 5], fill="#e8e8e8")
    d.line([W * 0.25, buff, W * 0.25, H - buff], fill="#1f8a52", width=2)
    img.save(out)


# ---------------------------------------------------------------- court

def make_court(out):
    S = 20  # px per foot
    W, H = 94 * S, 50 * S
    bg, line, paint = "#2a2118", "#d8d2c2", "#4a2e22"
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    def P(x, y):
        return (x * S, y * S)

    def arc(cx, cy, r, a0, a1, lw=3):
        d.arc([P(cx - r, cy - r), P(cx + r, cy + r)], a0, a1, fill=line, width=lw)

    def end(mirror):
        def X(x):
            return 94 - x if mirror else x
        # paint
        x0, x1 = sorted([X(0), X(19)])
        d.rectangle([P(x0, 17), P(x1, 33)], fill=paint, outline=line, width=3)
        # free-throw circle
        fx = X(19)
        if mirror:  # continuous stroke toward the center of the court, thin toward the hoop
            arc(fx, 25, 6, 90, 270)
            arc(fx, 25, 6, -90, 90, 1)
        else:
            arc(fx, 25, 6, -90, 90)
            arc(fx, 25, 6, 90, 270, 1)
        # three-pointer: corners and arc
        hx = X(5.25)
        r3 = 23.75
        cx = math.sqrt(r3 ** 2 - 22 ** 2)
        d.line([P(X(0), 3), P(X(5.25 + cx), 3)], fill=line, width=3)
        d.line([P(X(0), 47), P(X(5.25 + cx), 47)], fill=line, width=3)
        ang = math.degrees(math.atan2(22, cx))
        if mirror:
            arc(hx, 25, r3, 180 - ang, 180 + ang)
        else:
            arc(hx, 25, r3, -ang, ang)
        # restricted area, hoop and backboard
        if mirror:
            arc(hx, 25, 4, 90, 270)
        else:
            arc(hx, 25, 4, -90, 90)
        d.ellipse([P(hx - 0.75, 25 - 0.75), P(hx + 0.75, 25 + 0.75)], outline="#ff8a3d", width=3)
        d.line([P(X(4), 22), P(X(4), 28)], fill=line, width=5)

    end(False)
    end(True)
    # outline, half court and center circle
    d.rectangle([P(0, 0), P(94 - 0.05, 50 - 0.05)], outline=line, width=4)
    d.line([P(47, 0), P(47, 50)], fill=line, width=3)
    arc(47, 25, 6, 0, 360)
    img.save(out)


# ---------------------------------------------------------------- shot data

def season_shots(year, rng, n=N_SHOTS):
    """Synthetic shots of the season that starts in `year`: (LOC_X, LOC_Y) in tenths of a foot."""
    t = (year - 1997) / (2021 - 1997)
    w = {
        "rim": 0.31 - 0.01 * t,
        "paint": 0.17 - 0.07 * t,
        "mid": 0.30 - 0.18 * t,
        "three": 0.215 + 0.19 * t,
        "heave": 0.005,
    }
    total = sum(w.values())
    counts = rng.multinomial(n, [v / total for v in w.values()])
    xs, ys = [], []

    k = counts[0]  # near the hoop
    r = np.abs(rng.normal(0, 18, k)) + rng.exponential(8, k) * (rng.random(k) < 0.4)
    a = rng.uniform(0, math.pi, k)
    xs.append(r * np.cos(a)); ys.append(r * np.sin(a))

    k = counts[1]  # paint
    xs.append(rng.normal(0, 38, k).clip(-80, 80)); ys.append(rng.uniform(40, 190, k))

    k = counts[2]  # mid-range
    r = rng.uniform(90, 235, k)
    a = rng.beta(2.0, 2.0, k) * math.pi
    a = np.where(rng.random(k) < 0.35, a, np.clip(a + rng.normal(0, 0.3, k), 0.05, math.pi - 0.05))
    xs.append(r * np.cos(a)); ys.append(r * np.sin(a))

    k = counts[3]  # triples
    corner = rng.random(k) < 0.27
    side = rng.choice([-1.0, 1.0], k)
    cx = side * rng.uniform(222, 247, k)
    cy = rng.uniform(-5, 85, k)
    r = 237.5 + rng.exponential(10, k) + (rng.random(k) < 0.08) * rng.uniform(10, 40, k)
    a = rng.beta(2.4, 2.4, k) * (math.pi - 0.62) + 0.31
    ax, ay = r * np.cos(a), r * np.sin(a)
    xs.append(np.where(corner, cx, ax)); ys.append(np.where(corner, cy, ay))

    k = counts[4]  # long-distance shots
    xs.append(rng.uniform(-240, 240, k)); ys.append(rng.uniform(420, 900, k))

    x = np.concatenate(xs)
    y = np.concatenate(ys)
    x = np.clip(np.round(x), -250, 250).astype(int)
    y = np.clip(np.round(y), -50, 900).astype(int)
    dist = np.hypot(x, y)
    p_make = np.clip(0.62 - 0.0011 * np.maximum(dist - 20, 0), 0.2, 0.62)
    made = (rng.random(len(x)) < p_make).astype(int)
    order = rng.permutation(len(x))
    return x[order], y[order], made[order]


def make_shot_data():
    DATA.mkdir(parents=True, exist_ok=True)
    for year in range(1997, 2022):
        rng = np.random.default_rng(year)
        x, y, made = season_shots(year, rng)
        keep = ~((x == 0) & (y == 0))
        name = f"nbaShots{str(year)[-2:]}_{str(year + 1)[-2:]}.csv"
        with open(DATA / name, "w") as f:
            f.write("LOC_X,LOC_Y,SHOT_MADE_FLAG\n")
            np.savetxt(f, np.column_stack([x[keep], y[keep], made[keep]]), fmt="%d", delimiter=",")


def main():
    RASTER.mkdir(parents=True, exist_ok=True)
    make_pool_table(RASTER / "pool_table.png")
    make_court(RASTER / "basketball-court.png")
    make_shot_data()
    print("standup_maths: pool_table.png, basketball-court.png, 25 CSV en", DATA)


if __name__ == "__main__":
    main()
