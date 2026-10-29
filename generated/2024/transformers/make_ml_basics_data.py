"""Placeholder data and assets of _2024/transformers/ml_basics.py.

- _lib/data/2024/transformers/data/image_net_1k/images/{i}.jpeg and image_labels.txt:
  helpers.load_image_net_data read ImageNet-1k from ~/Documents/image_net_1k (with the `datasets` library);
  that set cannot be downloaded here, so the scenes (FlashThroughImageData, PremiseOfML and their
  subclasses) read this placeholder set: 48 generated images (gradient + shapes + noise, with
  the label "[placeholder]") and ImageNet-style category names ("tench, Tinca tinca"). They are not
  real photos of those categories. The scene changes data_path to Path(DATA_DIR, "image_net_1k").
- _lib/assets/svg_images/OpenAI.svg: placeholder logo (a six-petal rosette; ShowGPT3Numbers).

Usage: python make_ml_basics_data.py"""
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]  # _lib
DATA = LIB / "data" / "2024" / "transformers" / "data" / "image_net_1k"
SVG = LIB / "assets" / "svg_images"
FONT_PATHS = [
    "/usr/share/fonts/cm-unicode/cmunrm.otf",
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
]

LABELS = [
    "tench, Tinca tinca", "goldfish, Carassius auratus", "great white shark, white shark",
    "hen", "ostrich, Struthio camelus", "bald eagle, American eagle", "tree frog, tree-frog",
    "box turtle, box tortoise", "green lizard, Lacerta viridis", "king snake, kingsnake",
    "tarantula", "peacock", "goose", "koala, koala bear, kangaroo bear", "jellyfish",
    "snail", "lobster", "flamingo", "pelican", "grey whale, gray whale", "golden retriever",
    "tabby, tabby cat", "tiger, Panthera tigris", "lion, king of beasts, Panthera leo",
    "brown bear, bruin, Ursus arctos", "monarch, monarch butterfly", "zebra", "pig, hog, grunter",
    "llama", "giant panda, panda bear", "acoustic guitar", "airliner", "ambulance", "backpack, back pack",
    "balloon", "banjo", "barn", "bicycle-built-for-two, tandem bicycle", "castle", "cello, violoncello",
    "clock tower", "espresso", "fire engine, fire truck", "grand piano, grand", "lighthouse, beacon",
    "pizza, pizza pie", "sailboat", "volcano",
]
N = len(LABELS)


def font(size):
    for p in FONT_PATHS:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def filler_image(index, size=(640, 480)):
    rng = random.Random(1000 + index)
    w, h = size
    top = np.array([rng.randint(40, 230) for _ in range(3)], dtype=float)
    bot = np.array([rng.randint(40, 230) for _ in range(3)], dtype=float)
    t = np.linspace(0, 1, h)[:, None, None]
    arr = (top * (1 - t) + bot * t) * np.ones((h, w, 3))
    arr += np.random.default_rng(index).normal(0, 6, arr.shape)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(rng.randint(5, 9)):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        s = rng.uniform(30, 120)
        col = tuple(rng.randint(20, 245) for _ in range(3)) + (rng.randint(140, 230),)
        kind = rng.choice(["ellipse", "rect", "tri"])
        if kind == "ellipse":
            d.ellipse([x - s, y - s * 0.7, x + s, y + s * 0.7], fill=col)
        elif kind == "rect":
            d.rectangle([x - s, y - s * 0.6, x + s, y + s * 0.6], fill=col)
        else:
            d.polygon([(x, y - s), (x - s, y + s * 0.7), (x + s, y + s * 0.7)], fill=col)
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    d = ImageDraw.Draw(img)
    d.text((10, h - 10), "[relleno]", font=font(22), fill=(240, 240, 240), anchor="ld",
           stroke_width=2, stroke_fill=(30, 30, 30))
    return img


def openai_placeholder_svg(path):
    """Six-petal rosette (generic placeholder, not the real logo)."""
    petals = []
    for k in range(6):
        a = math.degrees(k * math.pi / 3)
        petals.append(
            f'<ellipse cx="0" cy="-34" rx="16" ry="30" transform="rotate({a:.1f})"/>'
        )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="-60 -60 120 120">'
        '<g fill="#FFFFFF">' + "".join(petals) + '</g>'
        '<circle cx="0" cy="0" r="12" fill="#FFFFFF"/>'
        '</svg>'
    )
    Path(path).write_text(svg)


def main():
    (DATA / "images").mkdir(parents=True, exist_ok=True)
    for i in range(N):
        filler_image(i).save(DATA / "images" / f"{i}.jpeg", quality=90)
    (DATA / "image_labels.txt").write_text("\n".join(LABELS))
    SVG.mkdir(parents=True, exist_ok=True)
    openai_placeholder_svg(SVG / "OpenAI.svg")
    print(f"ml_basics: {N} imágenes de relleno en {DATA}; OpenAI.svg en {SVG}")


if __name__ == "__main__":
    main()
