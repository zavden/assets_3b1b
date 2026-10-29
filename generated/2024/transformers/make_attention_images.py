"""Placeholder images of _2024/transformers/attention.py (the originals were DALL-E images and captures
saved in Grant's Dropbox). They are simple drawings made with PIL, with the label "[placeholder]":

- Dalle3_fluffy, Dalle3_blue, Dalle3_creature, Dalle3_creature_2, Dalle3_verdant, Dalle3_forest
  (AttentionPatterns, IntroduceValueMatrix: one image per word of "a fluffy blue creature roamed
  the verdant forest")
- BlueFluff, VerdantForest   (AttentionPatterns, IntroduceValueMatrix)
- AttentionPaperStill        (DescribeAttentionEquation: a page of the paper "Attention is all you need"
                              with a gap where the scene puts the equation)
- AttentionPattern0..4       (MultiHeadedAttention: attention patterns with a causal mask of different heads;
                              the original read them from /Users/grant/..., the scene now looks for them by name)
- gpu_large.svg              (Parallelizability: a schematic GPU chip)

The code looks for them by name with ImageMobject("...") / SVGMobject("..."), so they are written to
_lib/assets/raster_images/ and _lib/assets/svg_images/.

Usage: python make_attention_images.py"""
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]  # _lib/assets
RASTER = ASSETS / "raster_images"
SVG = ASSETS / "svg_images"
FONT_PATHS = [
    "/usr/share/fonts/cm-unicode/cmunrm.otf",
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
]
SIZE = (1000, 1000)


def font(size):
    for p in FONT_PATHS:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def vertical_gradient(size, top, bottom):
    w, h = size
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    t = np.linspace(0, 1, h)[:, None]
    for i in range(3):
        arr[:, :, i] = (top[i] * (1 - t) + bottom[i] * t).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def tag(img, text="[relleno]"):
    d = ImageDraw.Draw(img)
    f = font(max(14, img.size[1] // 36))
    d.text((12, img.size[1] - 12), text, font=f, fill=(235, 235, 235), anchor="ld",
           stroke_width=2, stroke_fill=(30, 30, 30))
    return img


# ------------------------------------------------------------ creatures

def fluffy_blob(color, bg=((184, 214, 232), (120, 160, 120)), seed=1, eyes=True, horns=False,
                size=SIZE, fur=1400):
    rng = random.Random(seed)
    w, h = size
    img = vertical_gradient(size, *bg)
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy, r = w * 0.5, h * 0.54, w * 0.29
    d.ellipse([cx - r * 1.05, cy + r * 0.85, cx + r * 1.05, cy + r * 1.15], fill=(40, 60, 40, 90))
    if horns:
        for sx in (-1, 1):
            d.polygon([(cx + sx * r * 0.55, cy - r * 0.8), (cx + sx * r * 0.9, cy - r * 1.35),
                       (cx + sx * r * 0.25, cy - r * 0.95)], fill=(235, 225, 200, 255))
    for _ in range(fur):
        a = rng.uniform(0, 2 * math.pi)
        rad = r * math.sqrt(rng.uniform(0, 1)) * 1.05
        x, y = cx + rad * math.cos(a), cy + rad * math.sin(a) * 1.05
        s = rng.uniform(0.03, 0.07) * w
        sh = rng.randint(-25, 25)
        d.ellipse([x - s, y - s, x + s, y + s],
                  fill=tuple(int(np.clip(c + sh, 0, 255)) for c in color) + (255,))
    if eyes:
        for sx in (-1, 1):
            ex, ey, er = cx + sx * r * 0.38, cy - r * 0.18, r * 0.2
            d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(250, 250, 250, 255))
            d.ellipse([ex - er * 0.45 + sx * 4, ey - er * 0.45, ex + er * 0.45 + sx * 4, ey + er * 0.45],
                      fill=(20, 20, 30, 255))
        d.arc([cx - r * 0.3, cy + r * 0.05, cx + r * 0.3, cy + r * 0.5], 15, 165, fill=(30, 40, 90, 255), width=7)
    return img.filter(ImageFilter.GaussianBlur(0.8))


def fluff_texture(seed=3, size=SIZE):
    rng = random.Random(seed)
    img = vertical_gradient(size, (225, 230, 240), (190, 200, 215))
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(1800):
        x, y = rng.uniform(0, size[0]), rng.uniform(0, size[1])
        s = rng.uniform(15, 55)
        v = rng.randint(225, 255)
        d.ellipse([x - s, y - s, x + s, y + s], fill=(v, v, min(255, v + 5), 150))
    return img.filter(ImageFilter.GaussianBlur(2))


def blue_texture(size=SIZE):
    arr = np.zeros((size[1], size[0], 3), dtype=np.float32)
    yy, xx = np.mgrid[0:size[1], 0:size[0]] / size[0]
    wave = 0.5 + 0.5 * np.sin(8 * xx + 4 * np.sin(5 * yy))
    arr[..., 0] = 20 + 50 * wave
    arr[..., 1] = 80 + 90 * wave
    arr[..., 2] = 170 + 70 * wave
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def leaf_texture(seed=5, size=SIZE):
    rng = random.Random(seed)
    img = vertical_gradient(size, (30, 90, 40), (60, 140, 60))
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(260):
        x, y = rng.uniform(0, size[0]), rng.uniform(0, size[1])
        a = rng.uniform(0, math.pi)
        l, wd = rng.uniform(70, 150), rng.uniform(22, 40)
        dx, dy = math.cos(a) * l / 2, math.sin(a) * l / 2
        g = rng.randint(120, 200)
        d.polygon([(x - dx, y - dy), (x + math.sin(a) * wd, y - math.cos(a) * wd),
                   (x + dx, y + dy), (x - math.sin(a) * wd, y + math.cos(a) * wd)],
                  fill=(rng.randint(20, 70), g, rng.randint(30, 70), 220))
    return img


def forest(seed=7, size=SIZE, lush=True):
    rng = random.Random(seed)
    w, h = size
    img = vertical_gradient(size, (150, 200, 235), (200, 225, 200))
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon([(0, h * 0.55), (w * 0.3, h * 0.4), (w * 0.6, h * 0.52), (w, h * 0.38), (w, h), (0, h)],
              fill=(60, 110, 90, 255))
    d.rectangle([0, h * 0.72, w, h], fill=(40, 100, 45, 255))
    for k in range(34):
        x = rng.uniform(-0.05, 1.05) * w
        base = h * rng.uniform(0.68, 0.98)
        th = h * rng.uniform(0.25, 0.5) * (0.6 + 0.5 * (base / h))
        tw = th * 0.38
        g = rng.randint(80, 170) if lush else rng.randint(60, 110)
        col = (rng.randint(15, 60), g, rng.randint(20, 60), 255)
        d.rectangle([x - tw * 0.06, base - th * 0.1, x + tw * 0.06, base + th * 0.02], fill=(80, 55, 35, 255))
        for j in range(3):
            top = base - th * (1 - j * 0.22)
            d.polygon([(x, top), (x - tw * (0.5 + j * 0.15), top + th * 0.45), (x + tw * (0.5 + j * 0.15), top + th * 0.45)],
                      fill=col)
    return img


# ------------------------------------------------------------ paper

def paper_still(size=(1920, 1080)):
    """A page of the paper with a gap centered at [-0.414, 1.177] (scene coordinates)."""
    w, h = size
    img = Image.new("RGB", size, (252, 252, 250))
    d = ImageDraw.Draw(img)
    rng = random.Random(11)

    def px(x, y):
        return (x + 7.111) / 14.222 * w, (4 - y) / 8 * h

    d.text((w / 2, 70), "Attention Is All You Need", font=font(58), fill=(20, 20, 20), anchor="mm")
    d.text((w / 2, 130), "[página de relleno]", font=font(30), fill=(130, 130, 130), anchor="mm")
    d.text((140, 230), "3.2.1  Scaled Dot-Product Attention", font=font(38), fill=(20, 20, 20), anchor="lm")
    ex, ey = px(-0.414, 1.177)
    hole_h = 1.07 / 8 * h
    for y0, y1 in ((290, ey - hole_h * 0.9), (ey + hole_h * 0.9, h - 120)):
        y = y0
        while y < y1:
            length = rng.uniform(0.85, 1.0) if rng.random() > 0.12 else rng.uniform(0.3, 0.6)
            d.rounded_rectangle([140, y - 7, 140 + length * (w - 280), y + 7], radius=6, fill=(205, 205, 205))
            y += 44
    d.text((ex, ey), "Attention(Q, K, V) = softmax( Q K^T / sqrt(d_k) ) V", font=font(56), fill=(185, 185, 185), anchor="mm")
    d.text((w - 150, ey), "(1)", font=font(46), fill=(185, 185, 185), anchor="mm")
    return img


# ------------------------------------------------------------ attention patterns

TOKENS = ["a", "fluffy", "blue", "creature", "roamed", "the", "verdant", "forest"]


def attention_pattern(kind, size=(1280, 720)):
    """Attention pattern grid (columns = querying tokens, rows = tokens being looked at) with a causal mask."""
    rng = np.random.default_rng(kind)
    n = 14 if kind else 10
    scores = rng.normal(0, 1.0, (n, n))
    if kind == 1:    # looks at the previous token
        scores += 5 * np.eye(n, k=1)
    elif kind == 2:  # looks at the first token
        scores[0, :] += 4
    elif kind == 3:  # local window
        scores -= 1.2 * np.abs(np.subtract.outer(np.arange(n), np.arange(n)))
    elif kind == 4:  # adjectives toward nouns
        for i, j in ((1, 3), (2, 3), (6, 8), (7, 8), (6, 10), (9, 10)):
            if i < n and j < n:
                scores[i, j] += 5
    # scores[i, j]: row i (key) for column j (query); causal: i <= j
    mask = np.triu(np.ones((n, n), dtype=bool))
    scores = np.where(mask, scores, -np.inf)
    e = np.exp(scores - scores.max(axis=0, keepdims=True))
    e = np.where(mask, e, 0)
    probs = e / e.sum(axis=0, keepdims=True)

    w, h = size
    img = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(img)
    cell = int(h * 0.78 / n)
    x0, y0 = (w - cell * n) // 2, int(h * 0.1)
    for i in range(n):
        for j in range(n):
            xa, ya = x0 + j * cell, y0 + i * cell
            if mask[i, j]:
                v = int(255 * min(1.0, probs[i, j] * 1.8) ** 0.8)
                d.rectangle([xa + 2, ya + 2, xa + cell - 2, ya + cell - 2], fill=(v, v, v))
            d.rectangle([xa, ya, xa + cell, ya + cell], outline=(40, 40, 40))
    d.text((w / 2, h - 28), "[relleno]" + ("" if kind else " (antes de dividir en cabezas)"),
           font=font(26), fill=(160, 160, 160), anchor="mm")
    return img


# ------------------------------------------------------------ GPU

def gpu_svg(path):
    """A GPU chip: board, heat sink with fins and pins. A single gray stroke, like an icon."""
    pins = []
    for k in range(8):
        pos = 70 + k * 46
        pins.append(f'<rect x="{pos}" y="10" width="14" height="40" />')
        pins.append(f'<rect x="{pos}" y="450" width="14" height="40" />')
        pins.append(f'<rect x="10" y="{pos}" width="40" height="14" />')
        pins.append(f'<rect x="450" y="{pos}" width="40" height="14" />')
    blades = []
    for k in range(7):
        a = k * 2 * math.pi / 7
        x1, y1 = 250 + 28 * math.cos(a), 250 + 28 * math.sin(a)
        x2, y2 = 250 + 105 * math.cos(a + 0.6), 250 + 105 * math.sin(a + 0.6)
        x3, y3 = 250 + 105 * math.cos(a + 1.1), 250 + 105 * math.sin(a + 1.1)
        blades.append(f'<path d="M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f} L {x3:.1f} {y3:.1f} Z" />')
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">'
        '<g fill="#888888">' + "".join(pins) + '</g>'
        '<rect x="50" y="50" width="400" height="400" rx="26" fill="#888888"/>'
        '<rect x="85" y="85" width="330" height="330" rx="16" fill="#222222"/>'
        '<circle cx="250" cy="250" r="125" fill="#888888"/>'
        '<circle cx="250" cy="250" r="112" fill="#222222"/>'
        '<g fill="#888888">' + "".join(blades) + '</g>'
        '<circle cx="250" cy="250" r="26" fill="#888888"/>'
        '</svg>'
    )
    Path(path).write_text(svg)


def main():
    RASTER.mkdir(parents=True, exist_ok=True)
    SVG.mkdir(parents=True, exist_ok=True)
    blue = (70, 130, 215)
    tag(fluff_texture()).save(RASTER / "Dalle3_fluffy.png")
    tag(blue_texture()).save(RASTER / "Dalle3_blue.png")
    tag(fluffy_blob((225, 140, 50), seed=2, horns=True)).save(RASTER / "Dalle3_creature.png")
    tag(fluffy_blob((150, 125, 100), seed=3)).save(RASTER / "Dalle3_creature_2.png")
    tag(leaf_texture()).save(RASTER / "Dalle3_verdant.png")
    tag(forest(seed=8, lush=False)).save(RASTER / "Dalle3_forest.png")
    tag(fluffy_blob(blue, seed=4)).save(RASTER / "BlueFluff.png")
    tag(forest(seed=9, lush=True)).save(RASTER / "VerdantForest.png")
    paper_still().save(RASTER / "AttentionPaperStill.png")
    for k in range(5):
        attention_pattern(k).save(RASTER / f"AttentionPattern{k}.png")
    gpu_svg(SVG / "gpu_large.svg")
    print("attention: imágenes de relleno escritas en", RASTER, "y", SVG)


if __name__ == "__main__":
    main()
