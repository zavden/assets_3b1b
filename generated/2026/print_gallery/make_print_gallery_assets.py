"""Generates the placeholder images of the "Print Gallery" video (2026/print_gallery).

The real images (rectified Escher lithograph, the "pi house", Paul's cutouts)
lived in Grant's Dropbox and are not public. Here they are replaced by procedural
images with recognizable structure (picture frames, cities, harbors, arcades,
portraits, houses with the Π character) so that the conformal transformations (exp, log,
Droste zooms) are visible.

Important detail: the "log images" are strips that the code reads as the plane
(x = log|z|, y = arg z), with extent (log(scale), TAU). For the Droste effect to be
continuous, the strip is PERIODIC on both axes (the left/right and top/bottom edges
match) and the cells are square in that space (so that, after exp,
the frames end up as nearly conformal ring sectors):

    PrintGalleryLog.png     scale 256 -> width/height ratio = ln(256)/TAU = 0.8825
                            7 columns x 8 rows of cells
    PiHouseLog.png          scale 16  -> width/height ratio = ln(16)/TAU  = 0.4413
                            3 columns x 7 rows of cells
    UltraHighResPiHouse.png square image on the plane (Droste of PiHouseLog with
                            factor 16) as CreatePiHouseLog reads it

It also generates:
    outlines/*.png          Paul's outlines (person, frame, building, arcade) for ZoomWithColors
    LogImage.png            horizontal version of PrintGalleryLog (supplements)

pi_creature_dizzy.svg and EscherPiCreature.svg are written by pi_creature/install_pi.py (own Π character).

Usage:  python make_print_gallery_assets.py"""
import colorsys
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import map_coordinates

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]  # .../_lib
TAU = 2 * math.pi
SS = 3  # supersampling

FONT_PATHS = [
    "/usr/share/fonts/cm-unicode/cmunrm.otf",
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
]


def font(size):
    for p in FONT_PATHS:
        if Path(p).exists():
            return ImageFont.truetype(p, int(size))
    return ImageFont.load_default()


def hsv(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
    return (int(r * 255), int(g * 255), int(b * 255))


def lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def vgrad(d, box, c_top, c_bot):
    x0, y0, x1, y1 = box
    n = max(1, int(y1 - y0))
    for k in range(n):
        d.line([(x0, y0 + k), (x1, y0 + k)], fill=lerp(c_top, c_bot, k / n))


def circle(d, cx, cy, r, fill):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


# ---------------------------------------------------------------- paintings (gallery cells)

def paint_town(d, box, rng, hue):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    vgrad(d, box, hsv(hue, 0.55, 0.95), hsv(hue + 0.08, 0.25, 1.0))
    circle(d, x0 + w * rng.uniform(.2, .8), y0 + h * rng.uniform(.15, .3), h * 0.08, (255, 240, 160))
    n = rng.randint(4, 6)
    bw = w / n
    for k in range(n):
        bh = h * rng.uniform(.3, .7)
        bx0, bx1 = x0 + k * bw + bw * .06, x0 + (k + 1) * bw - bw * .06
        col = hsv(hue + 0.5 + rng.uniform(-.05, .05), 0.35, rng.uniform(.22, .42))
        d.rectangle([bx0, y1 - bh, bx1, y1], fill=col)
        if rng.random() < .5:
            d.polygon([(bx0, y1 - bh), (bx1, y1 - bh), ((bx0 + bx1) / 2, y1 - bh - bw * .45)], fill=lerp(col, (0, 0, 0), .3))
        wh = h * 0.07
        yy = y1 - bh + wh * .8
        while yy + wh < y1 - h * .04:
            for cx in (bx0 + (bx1 - bx0) * .3, bx0 + (bx1 - bx0) * .7):
                d.rectangle([cx - wh * .45, yy, cx + wh * .45, yy + wh * .8],
                            fill=(255, 220, 120) if rng.random() < .6 else lerp(col, (0, 0, 0), .4))
            yy += wh * 1.7


def paint_harbor(d, box, rng, hue):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    horizon = y0 + h * 0.58
    vgrad(d, (x0, y0, x1, horizon), hsv(hue, 0.4, 0.95), hsv(hue + 0.05, 0.15, 1.0))
    vgrad(d, (x0, horizon, x1, y1), hsv(0.58, 0.7, 0.75), hsv(0.6, 0.8, 0.45))
    circle(d, x0 + w * rng.uniform(.25, .75), y0 + h * .22, h * .09, (255, 235, 150))
    for k in range(5):
        yy = horizon + (k + 1) * (y1 - horizon) / 6
        d.line([(x0 + w * .1, yy), (x1 - w * .1, yy)], fill=(190, 220, 240), width=max(1, int(h * .012)))
    # faro
    lx = x0 + w * rng.uniform(.15, .3)
    d.polygon([(lx - w * .05, horizon), (lx + w * .05, horizon), (lx + w * .03, y0 + h * .3), (lx - w * .03, y0 + h * .3)], fill=(235, 235, 235))
    d.polygon([(lx - w * .045, horizon - h * .1), (lx + w * .045, horizon - h * .1), (lx + w * .04, horizon - h * .17), (lx - w * .04, horizon - h * .17)], fill=(200, 40, 40))
    # boats
    for _ in range(2):
        bx = x0 + w * rng.uniform(.4, .85)
        by = horizon + h * rng.uniform(.08, .25)
        s = h * rng.uniform(.12, .2)
        d.polygon([(bx - s * .6, by), (bx + s * .6, by), (bx + s * .4, by + s * .2), (bx - s * .4, by + s * .2)], fill=(80, 40, 20))
        d.polygon([(bx, by - s), (bx, by - s * .1), (bx + s * .55, by - s * .1)], fill=(250, 250, 240))
        d.polygon([(bx - .06 * s, by - s * .8), (bx - .06 * s, by - s * .1), (bx - s * .45, by - s * .1)], fill=(240, 230, 200))


def paint_arcade(d, box, rng, hue):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    wall = hsv(0.08 + rng.uniform(-.02, .02), 0.35, 0.92)
    d.rectangle(box, fill=wall)
    d.rectangle([x0, y0, x1, y0 + h * .08], fill=lerp(wall, (0, 0, 0), .3))
    n = 3
    aw = w / n
    for row in range(2):
        yb = y1 - row * h * .45
        for k in range(n):
            ax0, ax1 = x0 + k * aw + aw * .18, x0 + (k + 1) * aw - aw * .18
            ytop = yb - h * .36
            d.rectangle([ax0, ytop + (ax1 - ax0) / 2, ax1, yb - h * .03], fill=(50, 35, 45))
            d.ellipse([ax0, ytop, ax1, ytop + (ax1 - ax0)], fill=(50, 35, 45))
            d.line([(ax0 - 2, yb - h * .03), (ax1 + 2, yb - h * .03)], fill=lerp(wall, (0, 0, 0), .4), width=max(1, int(h * .02)))
        d.rectangle([x0, yb - h * .45 - h * .02, x1, yb - h * .45 + h * .02], fill=lerp(wall, (0, 0, 0), .25)) if row == 1 else None


def paint_portrait(d, box, rng, hue):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    vgrad(d, box, hsv(hue, 0.45, 0.55), hsv(hue + .05, 0.5, 0.3))
    cx = x0 + w / 2
    cloth = hsv(hue + .5, 0.6, 0.6)
    d.ellipse([cx - w * .4, y0 + h * .62, cx + w * .4, y1 + h * .5], fill=cloth)
    d.rectangle([cx - w * .07, y0 + h * .5, cx + w * .07, y0 + h * .68], fill=(225, 180, 150))
    circle(d, cx, y0 + h * .38, h * .2, (235, 190, 160))
    d.pieslice([cx - h * .21, y0 + h * .17, cx + h * .21, y0 + h * .55], 180, 360, fill=hsv(0.07, 0.6, 0.25))
    for sx in (-1, 1):
        circle(d, cx + sx * h * .08, y0 + h * .39, h * .022, (30, 30, 40))


def paint_math(d, box, rng, hue):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=hsv(0.5 + rng.uniform(-.05, .05), 0.55, 0.28))
    glyph = rng.choice(["π", "e", "i", "ln", "Σ", "z", "√", "τ", "θ"])
    f = font(h * (0.55 if len(glyph) == 1 else 0.42))
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), glyph, font=f, fill=hsv(rng.choice([.12, .55, .95]), .35, 1.0), anchor="mm")


def paint_abstract(d, box, rng, hue):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    bg = hsv(hue, 0.5, 0.9)
    d.rectangle(box, fill=bg)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for k in range(5, 0, -1):
        circle(d, cx, cy, min(w, h) * .1 * k, hsv(hue + .08 * k, 0.6, 0.95 if k % 2 else 0.35))
    for k in range(4):
        d.line([(x0, y0 + k * h / 4), (x1, y0 + k * h / 4)], fill=(255, 255, 255), width=max(1, int(h * .012)))


PAINTERS = [paint_town, paint_harbor, paint_arcade, paint_portrait, paint_math, paint_abstract]


def draw_gallery_cell(d, box, rng, idx, row, col):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=hsv(0.06 + 0.02 * ((row + col) % 2), 0.35, 0.30))
    m = 0.06 * w
    fx0, fy0, fx1, fy1 = x0 + m, y0 + m, x1 - m, y1 - m
    d.rectangle([fx0, fy0, fx1, fy1], fill=(205, 165, 45))
    b = 0.035 * w
    d.rectangle([fx0 + b, fy0 + b, fx1 - b, fy1 - b], fill=(125, 90, 20))
    b2 = 0.06 * w
    d.rectangle([fx0 + b2, fy0 + b2, fx1 - b2, fy1 - b2], fill=(238, 229, 205))
    b3 = 0.11 * w
    pbox = (fx0 + b3, fy0 + b3, fx1 - b3, fy1 - b3)
    painter = PAINTERS[idx]
    hue = rng.random()
    painter(d, pbox, rng, hue)


def make_print_gallery_strip(out, cols=7, rows=8, cell_h=140, seed=1):
    cell_w = round(cell_h * (math.log(256) / TAU) * rows / cols)
    W, H = cols * cell_w, rows * cell_h
    img = Image.new("RGB", (W * SS, H * SS))
    d = ImageDraw.Draw(img)
    order = list(range(len(PAINTERS)))
    for r in range(rows):
        for c in range(cols):
            rng = random.Random(seed * 10007 + r * 131 + c)
            idx = rng.choices(range(len(PAINTERS)), weights=[3, 2, 2, 2, 2, 1])[0]
            box = (c * cell_w * SS, r * cell_h * SS, (c + 1) * cell_w * SS, (r + 1) * cell_h * SS)
            draw_gallery_cell(d, box, rng, idx, r, c)
    img = img.resize((W, H), Image.LANCZOS)
    img.save(out)
    return img


# ---------------------------------------------------------------- pi house

_PI_GEOM = None


def _pi_geometry():
    """Geometry of the Π character ("plain") in its 200x200 frame, taken from the generator in
    `pi_creature/generar_expresiones.py` (body and mouth as polygons, eyes as circles)."""
    global _PI_GEOM
    if _PI_GEOM is None:
        import re
        import sys
        sys.path.insert(0, str(HERE.parents[1] / "pi_creature"))
        import generar_expresiones as gen

        def poly(path):
            pts, cur = [], None
            for cmd, args in re.findall(r"([MLQZ])\s*([^MLQZ]*)", path):
                nums = [tuple(map(float, a.split(","))) for a in args.split()]
                if cmd in "ML":
                    pts.extend(nums)
                    cur = nums[-1]
                elif cmd == "Q":
                    for k in range(1, 7):
                        t = k / 6
                        (cx_, cy_), (x, y) = nums
                        pts.append(((1 - t) ** 2 * cur[0] + 2 * (1 - t) * t * cx_ + t * t * x,
                                    (1 - t) ** 2 * cur[1] + 2 * (1 - t) * t * cy_ + t * t * y))
                    cur = nums[-1]
            return pts

        fig = gen.Fig({})
        eyes = fig.eyes()
        body = poly(fig.cuerpo())
        mouth = poly(fig.boca())
        _PI_GEOM = (eyes, body, mouth)
    return _PI_GEOM


def draw_pi_creature(d, cx, base_y, s, color):
    """Draws the Π character (capital Pi letter with eyes) standing on `base_y`, centered at `cx`, with the same
    height (`s`) as the previous drawing; `color` is the body's. Order: eyes, body, mouth (like PiCreature)."""
    eyes, body, mouth = _pi_geometry()
    k = s / 182.0  # the character is 182 tall in its frame (eyes at y=8, feet at y=190)

    def T(x, y):
        return (cx + (x - 100) * k, base_y - (190 - y) * k)

    for c, r, pu in eyes:
        ex, ey = T(*c)
        circle(d, ex, ey, r * k, (255, 255, 255))
        px, py = T(*pu)
        circle(d, px, py, r * k * 0.4, (0, 0, 0))
        circle(d, px - r * k * 0.12, py - r * k * 0.12, r * k * 0.12, (255, 255, 255))
    d.polygon([T(x, y) for x, y in body], fill=color)
    d.polygon([T(x, y) for x, y in mouth], fill=(10, 20, 25))


def draw_house_cell(d, box, rng, idx):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    hue = rng.random()
    ground = y0 + h * .78
    vgrad(d, (x0, y0, x1, ground), hsv(0.58 + 0.05 * (idx % 3), 0.5, 0.95), hsv(0.58, 0.15, 1.0))
    d.rectangle([x0, ground, x1, y1], fill=hsv(0.3, 0.55, 0.55))
    circle(d, x0 + w * rng.uniform(.15, .85), y0 + h * .17, h * .07, (255, 235, 140))
    # house
    hx0, hx1 = x0 + w * .22, x1 - w * .22
    hy0 = y0 + h * .42
    body = hsv(hue, 0.45, 0.92)
    d.rectangle([hx0, hy0, hx1, ground], fill=body)
    d.polygon([(hx0 - w * .05, hy0), (hx1 + w * .05, hy0), ((hx0 + hx1) / 2, y0 + h * .2)], fill=hsv(0.02, 0.7, 0.55))
    d.rectangle([hx1 - w * .15, y0 + h * .2, hx1 - w * .07, y0 + h * .33], fill=hsv(0.02, 0.5, 0.4))
    # door + pi
    dw = (hx1 - hx0) * .26
    dx = (hx0 + hx1) / 2
    d.rectangle([dx - dw / 2, ground - h * .2, dx + dw / 2, ground], fill=hsv(hue + .5, 0.5, 0.35))
    d.text((dx, hy0 + h * .09), "π", font=font(h * .16), fill=(255, 255, 255), anchor="mm")
    # windows
    for sx in (-1, 1):
        wx = dx + sx * (hx1 - hx0) * .33
        ww = (hx1 - hx0) * .17
        d.rectangle([wx - ww, ground - h * .27, wx + ww, ground - h * .12], fill=(255, 225, 130))
        d.line([(wx, ground - h * .27), (wx, ground - h * .12)], fill=(90, 60, 30), width=max(1, int(h * .01)))
        d.line([(wx - ww, ground - h * .195), (wx + ww, ground - h * .195)], fill=(90, 60, 30), width=max(1, int(h * .01)))
    # tree
    left = rng.random() < .5
    tx = x0 + w * .08 if left else x1 - w * .08
    d.rectangle([tx - w * .015, ground - h * .12, tx + w * .015, ground], fill=(100, 60, 30))
    circle(d, tx, ground - h * .16, h * .08, (40, 130, 60))
    # pi creature
    if rng.random() < .6:
        cx = x1 - w * .12 if left else x0 + w * .12
        draw_pi_creature(d, cx, y1 - h * .02, h * .2, hsv(rng.choice([0.5, 0.55, 0.58]), 0.9, 0.6))
    d.rectangle([x0, y0, x1, y1], outline=(30, 30, 30), width=max(1, int(h * .012)))


def make_pi_house_strip(out, out_small, cols=3, rows=7, cell_h=140, seed=2):
    cell_w = round(cell_h * (math.log(16) / TAU) * rows / cols)
    W, H = cols * cell_w, rows * cell_h
    img = Image.new("RGB", (W * SS, H * SS))
    d = ImageDraw.Draw(img)
    for r in range(rows):
        for c in range(cols):
            rng = random.Random(seed * 10007 + r * 131 + c)
            box = (c * cell_w * SS, r * cell_h * SS, (c + 1) * cell_w * SS, (r + 1) * cell_h * SS)
            draw_house_cell(d, box, rng, r * cols + c)
    img = img.resize((W, H), Image.LANCZOS)
    img.save(out)
    img.resize((max(1, W // 2), max(1, H // 2)), Image.LANCZOS).save(out_small)
    return img


def make_ultra_high_res_pi_house(strip, out, n=2048, scale_factor=16):
    """Square image on the z plane: Droste of the strip (x=log|z|, y=arg z).
    CreatePiHouseLog reads it with z2 = (z1 + 1 + i) / 2, z1 in the unit disk."""
    arr = np.asarray(strip.convert("RGB")).astype(np.float32)
    Hs, Ws = arr.shape[:2]
    xs = (np.arange(n) + 0.5) / n
    X, Y = np.meshgrid(xs, xs)
    z1 = 2 * (X + 1j * Y) - (1 + 1j)
    rho = np.maximum(np.abs(z1), 1e-9)
    theta = np.angle(z1) % TAU
    a = (1 + np.log(rho) / np.log(scale_factor)) % 1.0
    b = theta / TAU
    coords = np.array([b * Hs - 0.5, a * Ws - 0.5])
    chans = [map_coordinates(arr[..., k], coords, order=1, mode="grid-wrap") for k in range(3)]
    res = np.stack(chans, axis=-1).clip(0, 255).astype(np.uint8)
    Image.fromarray(res).save(out)


# ---------------------------------------------------------------- Paul's outlines

def make_outlines(folder):
    folder.mkdir(parents=True, exist_ok=True)
    S = 4
    H = 800

    def canvas(aspect):
        W = int(H * aspect)
        im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
        return im, ImageDraw.Draw(im), W * S, H * S

    def save(im, name):
        W, Hh = im.size
        im.resize((W // S, Hh // S), Image.LANCZOS).save(folder / name)

    lw = 6 * S
    # Person (silhouette)
    for name, filled in [("PersonOutline.png", False), ("PersonMask.png", True)]:
        im, d, W, Hh = canvas(0.45)
        cx = W / 2
        shapes = lambda f: (
            d.ellipse([cx - W * .16, Hh * .03, cx + W * .16, Hh * .03 + W * .32], **f),
            d.rounded_rectangle([cx - W * .3, Hh * .2, cx + W * .3, Hh * .6], radius=W * .1, **f),
            d.rectangle([cx - W * .25, Hh * .58, cx - W * .03, Hh * .97], **f),
            d.rectangle([cx + W * .03, Hh * .58, cx + W * .25, Hh * .97], **f),
        )
        if filled:
            shapes(dict(fill=(255, 220, 60, 255)))
        else:
            shapes(dict(outline=(255, 220, 60, 255), width=lw))
        save(im, name)
    # Frame
    im, d, W, Hh = canvas(1.25)
    for k in range(3):
        d.rectangle([k * lw * 2, k * lw * 2, W - 1 - k * lw * 2, Hh - 1 - k * lw * 2], outline=(255, 70, 70, 255), width=lw)
    save(im, "Frame.png")
    # Building
    im, d, W, Hh = canvas(1.0)
    col = (60, 220, 200, 255)
    d.rectangle([W * .1, Hh * .25, W * .9, Hh * .97], outline=col, width=lw)
    d.polygon([(W * .05, Hh * .25), (W * .95, Hh * .25), (W * .5, Hh * .03)], outline=col, width=lw)
    for r in range(3):
        for c in range(4):
            x = W * (.18 + c * .19)
            y = Hh * (.33 + r * .16)
            d.rectangle([x, y, x + W * .11, y + Hh * .1], outline=col, width=lw)
    d.rectangle([W * .43, Hh * .8, W * .57, Hh * .97], outline=col, width=lw)
    save(im, "Building.png")
    # Arcade
    im, d, W, Hh = canvas(2.5)
    col = (110, 240, 110, 255)
    n = 5
    for k in range(n):
        ax0, ax1 = W * (k + .15) / n, W * (k + .85) / n
        r_ = (ax1 - ax0) / 2
        d.line([(ax0, Hh * .4), (ax0, Hh * .97), (ax1, Hh * .97), (ax1, Hh * .4)], fill=col, width=lw)
        d.arc([ax0, Hh * .4 - r_, ax1, Hh * .4 + r_], 180, 360, fill=col, width=lw)
    d.line([(0, Hh * .1), (W, Hh * .1)], fill=col, width=lw)
    save(im, "Arcade.png")


# ---------------------------------------------------------------- main

def main():
    tex = HERE / "textures"
    tex.mkdir(exist_ok=True)
    pg = make_print_gallery_strip(tex / "PrintGalleryLog.png")
    ph = make_pi_house_strip(tex / "PiHouseLog.png", tex / "PiHouseLogSmall.png")
    make_ultra_high_res_pi_house(ph, tex / "UltraHighResPiHouse.png")
    make_outlines(HERE / "outlines")
    # LogImage for supplements: the strip rotated 90 degrees (horizontal)
    (HERE / "exponential").mkdir(exist_ok=True)
    pg.transpose(Image.ROTATE_90).save(HERE / "exponential" / "LogImage.png")

    print("ok")


if __name__ == "__main__":
    main()
