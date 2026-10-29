"""Color cards with the video's title, instead of the YouTube thumbnails that the scenes downloaded
at run time (ImageMobject("https://img.youtube.com/vi/<id>/maxresdefault.jpg")).

Each card is a 1280x720 PNG (16:9, like maxresdefault) with a gradient, soft geometric shapes, the title
in large type and a "play" triangle. It is written as _lib/assets/raster_images/yt_card_<id>.png; the scenes
(PlaylistMention, ShowPreviousVideos, IntroduceEulersFormula, PreviousVideos) ask for ImageMobject("yt_card_<id>").

The titles of the Deep Learning series are those of the videos themselves; those of other channels are not reproduced
(they are generic: "Euler's formula, ..."). No card imitates a real thumbnail.

Usage: python make_video_cards.py"""
import colorsys
import hashlib
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

try:
    from make_visual_rasters import font  # same font lookup (matplotlib's DejaVu)
except ImportError:  # run from another directory
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from make_visual_rasters import font

OUT = Path(__file__).resolve().parents[3] / "raster_images"
W, H = 1280, 720

CARDS = {
    # inscribed_rect/supplements.py::PlaylistMention
    "OkmNXy7er84": ("More neat proofs\nand puzzle solutions", 0.55),
    # transformers/chm.py::ShowPreviousVideos and part2_supplements::PreviousVideos (Deep Learning series)
    "aircAruvnKk": ("But what is a\nneural network?", 0.60),
    "IHZwWFHWa-w": ("Gradient descent,\nhow neural networks learn", 0.07),
    "Ilg3gGewQ5U": ("What is backpropagation\nreally doing?", 0.12),
    "tIeHLnjs5U8": ("Backpropagation\ncalculus", 0.33),
    "wjZofJX0v4M": ("Transformers,\nthe tech behind LLMs", 0.75),
    "eMlx5fFNoYc": ("Attention in transformers,\nstep-by-step", 0.82),
    "9-Jl0dxWQs8": ("How might LLMs\nstore facts", 0.48),
    # laplace/exponentials.py::IntroduceEulersFormula (other channels: generic titles)
    "-dhHrg-KbJ0": ("Euler's formula,\nvisualized", 0.02),
    "f8CXG7dS-D0": ("Why e^(iπ) = -1", 0.15),
    "ZxYOEwM6Wbk": ("Complex exponentials\nin motion", 0.58),
    "LE2uwd9V5vw": ("Euler's identity\nexplained", 0.38),
    "CRj-sbi2i2I": ("e to the i pi,\na short proof", 0.92),
    "v0YEaeIClKY": ("Rotations and\ne^(ix)", 0.68),
    "sKtloBAuP74": ("A taste of\ncomplex numbers", 0.25),
    "IUTGFQpKaPU": ("Euler's formula\nin 5 minutes", 0.45),
}


def card(slug, title, hue):
    rng = np.random.default_rng(int(hashlib.md5(slug.encode()).hexdigest()[:8], 16))
    S = 2
    c0 = np.array(colorsys.hsv_to_rgb(hue, 0.62, 0.62)) * 255
    c1 = np.array(colorsys.hsv_to_rgb((hue + 0.08) % 1, 0.78, 0.30)) * 255
    yy, xx = np.mgrid[0:H * S, 0:W * S].astype(np.float32)
    t = np.clip((xx / (W * S) * 0.55 + yy / (H * S) * 0.75), 0, 1)[..., None]
    arr = c0 * (1 - t) + c1 * t
    im = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")

    # translucent geometric shapes
    deco = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(deco)
    light = tuple(int(v) for v in np.array(colorsys.hsv_to_rgb(hue, 0.25, 1.0)) * 255)
    for _ in range(7):
        cx, cy = rng.uniform(0.45, 1.05) * W * S, rng.uniform(-0.05, 1.05) * H * S
        r = rng.uniform(70, 260) * S
        if rng.random() < 0.5:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=light + (60,), width=int(5 * S))
        else:
            a = rng.uniform(0, math.pi)
            pts = [(cx + r * math.cos(a + k * 2 * math.pi / 3), cy + r * math.sin(a + k * 2 * math.pi / 3)) for k in range(3)]
            d.polygon(pts, fill=light + (28,))
    im = Image.alpha_composite(im, deco)

    # title
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    lines = title.split("\n")
    size = 92
    f = font(size * S)
    while max(f.getlength(x) for x in lines) > (W - 190) * S and size > 40:   # so that it fits with a margin
        size -= 4
        f = font(size * S)
    x0, y0 = 80 * S, int(H * S * 0.5 - len(lines) * size * S * 0.6)
    for i, line in enumerate(lines):
        y = y0 + i * int(size * S * 1.18)
        dl.text((x0 + 4 * S, y + 5 * S), line, font=f, fill=(0, 0, 0, 120))
        dl.text((x0, y), line, font=f, fill=(255, 255, 255, 255))
    im = Image.alpha_composite(im, lay)

    # play button and mark
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    do = ImageDraw.Draw(ov)
    cx, cy, r = (W - 120) * S, (H - 110) * S, 52 * S
    do.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 215))
    do.polygon([(cx - 16 * S, cy - 26 * S), (cx - 16 * S, cy + 26 * S), (cx + 28 * S, cy)], fill=(40, 40, 60, 255))
    do.rounded_rectangle([60 * S, (H - 86) * S, 252 * S, (H - 44) * S], radius=10 * S, fill=(0, 0, 0, 110))
    do.text((156 * S, (H - 65) * S), "video card", font=font(24 * S, bold=False), fill=(255, 255, 255, 220), anchor="mm")
    im = Image.alpha_composite(im, ov)
    return im.resize((W, H), Image.LANCZOS).convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, (title, hue) in CARDS.items():
        card(slug, title, hue).save(OUT / f"yt_card_{slug}.png", optimize=True)
    print(f"escritas {len(CARDS)} tarjetas en {OUT}")


if __name__ == "__main__":
    main()
