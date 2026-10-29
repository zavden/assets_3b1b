"""Placeholder images of _2024/transformers/embedding.py and network_flow.py (the originals lived in
Grant's Dropbox). They are simple drawings made with PIL, with the label "[placeholder]" in a corner:

- SmallFluffCreature.png          embedding.ImageTokens (pixelated into patches: fluffy blue creature)
- LipMole.png                     embedding.MultipleMoleEmbeddings and network_flow.MoleExample1 (mole on a lip)
- Tower1..4.png                   embedding.RefineTowerMeaning (generic towers)
- EiffelTower2.png, EiffelTower3.png   ditto (the Eiffel Tower; EiffelTower1.png and ShrewMole.png are already
                                  created by misc_placeholders.py)
- MiniEiffelTower1.png            ditto (a souvenir Eiffel Tower on a table)

The code looks for them by name with ImageMobject("..."), so they are written to _lib/assets/raster_images/.

Usage: python make_embedding_images.py"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]  # _lib/assets
OUT = ASSETS / "raster_images"
FONT_PATHS = [
    "/usr/share/fonts/cm-unicode/cmunrm.otf",
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
]


def font(size):
    for p in FONT_PATHS:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def vertical_gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", size)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=color)
    return img


def tag(img, text="[relleno]"):
    d = ImageDraw.Draw(img)
    f = font(max(14, img.size[1] // 36))
    d.text((12, img.size[1] - 12), text, font=f, fill=(235, 235, 235), anchor="ld",
           stroke_width=2, stroke_fill=(30, 30, 30))
    return img


# ------------------------------------------------------------ fluffy creature

def fluffy_creature(size=(900, 900), seed=1):
    rng = random.Random(seed)
    w, h = size
    img = vertical_gradient(size, (184, 214, 232), (120, 160, 120))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy, r = w * 0.5, h * 0.52, w * 0.30
    # shadow
    d.ellipse([cx - r * 1.05, cy + r * 0.85, cx + r * 1.05, cy + r * 1.15], fill=(40, 60, 40, 90))
    # fur: many untidy blue circles
    for _ in range(1400):
        a = rng.uniform(0, 2 * math.pi)
        rad = r * math.sqrt(rng.uniform(0, 1)) * 1.05
        x, y = cx + rad * math.cos(a), cy + rad * math.sin(a) * 1.05
        s = rng.uniform(0.03, 0.07) * w
        shade = rng.randint(-25, 25)
        d.ellipse([x - s, y - s, x + s, y + s], fill=(70 + shade, 130 + shade, 215 + shade // 2, 255))
    # eyes
    for sx in (-1, 1):
        ex, ey, er = cx + sx * r * 0.38, cy - r * 0.18, r * 0.2
        d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(250, 250, 250, 255))
        d.ellipse([ex - er * 0.45 + sx * 4, ey - er * 0.45, ex + er * 0.45 + sx * 4, ey + er * 0.45],
                  fill=(20, 20, 30, 255))
    # mouth and legs
    d.arc([cx - r * 0.3, cy + r * 0.05, cx + r * 0.3, cy + r * 0.5], 15, 165, fill=(30, 40, 90, 255), width=7)
    for sx in (-1, 1):
        px = cx + sx * r * 0.55
        d.ellipse([px - r * 0.2, cy + r * 0.95, px + r * 0.2, cy + r * 1.15], fill=(60, 115, 200, 255))
    return img.filter(ImageFilter.GaussianBlur(0.8))


# ------------------------------------------------------------ mole on a lip

def lip_mole(size=(1000, 750)):
    w, h = size
    img = vertical_gradient(size, (232, 190, 170), (214, 160, 145))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = w * 0.5, h * 0.5
    # lips
    d.ellipse([cx - w * 0.38, cy - h * 0.30, cx + w * 0.38, cy + h * 0.02], fill=(190, 80, 90, 255))
    d.ellipse([cx - w * 0.36, cy - h * 0.02, cx + w * 0.36, cy + h * 0.34], fill=(205, 95, 105, 255))
    d.line([cx - w * 0.38, cy - h * 0.01, cx + w * 0.38, cy - h * 0.01], fill=(110, 40, 50, 255), width=8)
    # lunar
    mx, my, mr = cx + w * 0.17, cy + h * 0.1, h * 0.035
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(70, 40, 30, 255))
    return img.filter(ImageFilter.GaussianBlur(1.0))


# ------------------------------------------------------------ towers

def sky(size, night=False):
    return vertical_gradient(size, (20, 24, 60), (90, 70, 110)) if night else \
        vertical_gradient(size, (130, 180, 235), (225, 232, 240))


def eiffel(d, cx, base_y, height, color):
    """Silhouette of the Eiffel Tower: wide leg that narrows, two platforms and a spire."""
    half = height * 0.28
    top_y = base_y - height
    pts = [(cx - half, base_y), (cx - half * 0.12, top_y + height * 0.22),
           (cx - half * 0.03, top_y), (cx + half * 0.03, top_y),
           (cx + half * 0.12, top_y + height * 0.22), (cx + half, base_y)]
    d.polygon(pts, fill=color)
    # arch between the legs
    d.pieslice([cx - half * 0.55, base_y - height * 0.32, cx + half * 0.55, base_y + height * 0.08],
               180, 360, fill=None, outline=(40, 40, 50), width=3)
    # platforms
    for frac, wid in ((0.30, 0.34), (0.62, 0.17)):
        y = base_y - height * frac
        d.rectangle([cx - half * wid * 1.7, y - height * 0.012, cx + half * wid * 1.7, y + height * 0.012],
                    fill=(40, 40, 50))
    # lattice
    lattice = (40, 40, 50)
    for k in range(1, 12):
        y = base_y - height * k / 12 * 0.85
        t = (base_y - y) / height
        hw = half * (1 - t / 0.85 * 0.9)
        d.line([(cx - hw, y), (cx + hw, y - height * 0.04)], fill=lattice, width=2)
        d.line([(cx + hw, y), (cx - hw, y - height * 0.04)], fill=lattice, width=2)


def eiffel_image(variant):
    size = (900, 1200)
    night = variant == 3
    img = sky(size, night)
    d = ImageDraw.Draw(img, "RGBA")
    ground = (30, 60, 40) if not night else (15, 25, 20)
    d.rectangle([0, 1020, 900, 1200], fill=ground)
    eiffel(d, 450 + (variant - 2) * 40, 1030, 880, (70, 60, 55) if not night else (200, 170, 90))
    return tag(img)


def tower_image(n):
    size = (900, 1200)
    img = sky(size, night=(n == 4))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 1040, 900, 1200], fill=(70, 100, 70))
    if n == 1:      # faro
        d.polygon([(380, 1040), (520, 1040), (490, 300), (410, 300)], fill=(235, 235, 235))
        for y in (400, 600, 800):
            d.rectangle([405 + (y - 300) * 0.04, y, 495 - (y - 300) * 0.04, y + 70], fill=(200, 50, 50))
        d.rectangle([395, 250, 505, 300], fill=(60, 60, 70))
        d.polygon([(385, 250), (515, 250), (450, 170)], fill=(190, 60, 60))
    elif n == 2:    # clock tower
        d.rectangle([340, 360, 560, 1040], fill=(170, 130, 95))
        d.polygon([(320, 360), (580, 360), (450, 160)], fill=(90, 70, 60))
        d.ellipse([385, 440, 515, 570], fill=(245, 245, 235), outline=(40, 40, 40), width=6)
        d.line([450, 505, 450, 455], fill=(30, 30, 30), width=6)
        d.line([450, 505, 485, 520], fill=(30, 30, 30), width=6)
    elif n == 3:    # castle tower
        d.rectangle([350, 420, 550, 1040], fill=(140, 140, 150))
        for k in range(5):
            d.rectangle([350 + k * 42, 370, 372 + k * 42, 420], fill=(140, 140, 150))
        d.rectangle([425, 720, 475, 800], fill=(40, 40, 60))
        d.polygon([(420, 1040), (480, 1040), (480, 960), (450, 930), (420, 960)], fill=(80, 55, 40))
    else:           # telecommunications tower (at night)
        d.polygon([(425, 1040), (475, 1040), (455, 520), (445, 520)], fill=(180, 180, 190))
        d.ellipse([405, 560, 495, 610], fill=(210, 210, 220))
        d.rectangle([447, 200, 453, 520], fill=(180, 180, 190))
        for y in range(220, 500, 60):
            d.ellipse([444, y, 456, y + 12], fill=(255, 60, 60))
    return tag(img)


def mini_eiffel_image():
    size = (900, 1200)
    img = vertical_gradient(size, (200, 180, 150), (140, 105, 80))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 900, 900, 1200], fill=(105, 75, 55))
    d.ellipse([260, 1040, 640, 1110], fill=(60, 40, 30, 120))
    eiffel(d, 450, 1060, 460, (110, 100, 100))
    # a hand for scale
    d.rounded_rectangle([650, 700, 880, 780], radius=35, fill=(230, 190, 165))
    return tag(img)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tag(fluffy_creature()).save(OUT / "SmallFluffCreature.png")
    tag(lip_mole()).save(OUT / "LipMole.png")
    for n in range(1, 5):
        tower_image(n).save(OUT / f"Tower{n}.png")
    for n in (2, 3):
        eiffel_image(n).save(OUT / f"EiffelTower{n}.png")
    mini_eiffel_image().save(OUT / "MiniEiffelTower1.png")
    print("embedding: imágenes de relleno escritas en", OUT)


if __name__ == "__main__":
    main()
