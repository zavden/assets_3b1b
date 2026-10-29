"""Replacement images for 2018/pi_day (the originals lived in Grant's deleted videos/assets folder).

Written to _lib/assets/raster_images/ where ImageMobject finds them by name:
  Leonhard_Euler_by_Handmann.jpg  copy of the public-domain Handmann portrait (Euler.jpg, already in raster_images)
  Leonard_Euler_pixelated.png     the same portrait, heavily pixelated (made by code)
  Leonard_Euler_revealed.png      the portrait tinted red with drawn devil horns (made by code; a gag in the scene)
  dalembert_zoom.png              wide strip imitating a zoomed line of an old printed page (placeholder, made by code)
  Analysis_page_showing_pi.png    page imitating an old printed page with a highlighted line (placeholder, made by code)
Run: python make_pi_day_assets.py
"""
import random
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

OUT = Path(__file__).resolve().parents[3] / "raster_images"
FONTS = ["/usr/share/fonts/cm-unicode/cmunrm.otf", "/usr/share/fonts/dejavu-sans-fonts/DejaVuSerif.ttf"]


def font(size):
    for p in FONTS:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def portraits():
    src = OUT / "Euler.jpg"
    shutil.copyfile(src, OUT / "Leonhard_Euler_by_Handmann.jpg")
    im = Image.open(src).convert("RGB")
    w, h = im.size
    small = im.resize((w // 24, h // 24), Image.BILINEAR)
    small.resize((w, h), Image.NEAREST).save(OUT / "Leonard_Euler_pixelated.png")
    red = ImageOps.colorize(ImageOps.grayscale(im), black="#200000", white="#ff9080")
    d = ImageDraw.Draw(red)
    d.polygon([(w * .22, h * .16), (w * .30, h * .02), (w * .40, h * .14)], fill="#a00000", outline="#400000")
    d.polygon([(w * .60, h * .14), (w * .70, h * .02), (w * .78, h * .16)], fill="#a00000", outline="#400000")
    red.save(OUT / "Leonard_Euler_revealed.png")


def text_page(size, seed, lines, highlight=None, label=""):
    w, h = size
    img = Image.new("RGB", size, "#efe6cf")
    d = ImageDraw.Draw(img)
    rng = random.Random(seed)
    margin = w * 0.08
    step = (h - 2 * margin) / lines
    for i in range(lines):
        y = margin + i * step
        length = rng.uniform(0.75, 1.0) if i % 9 != 8 else rng.uniform(0.2, 0.5)
        if highlight is not None and i == highlight:
            d.rectangle([margin * .6, y - step * .1, w - margin * .6, y + step * .75], outline="#a02020", width=max(3, w // 200))
        d.rounded_rectangle([margin, y, margin + length * (w - 2 * margin), y + step * 0.32], radius=4, fill="#4a4030")
    if label:
        d.text((w / 2, h - margin / 2), label, font=font(max(14, h // 40)), fill="#806040", anchor="mm")
    return img


def pages():
    text_page((2400, 520), 1, 5, label="[placeholder: zoom on a printed line]").save(OUT / "dalembert_zoom.png")
    text_page((1100, 1500), 2, 24, highlight=9, label="[placeholder: old printed page]").save(OUT / "Analysis_page_showing_pi.png")


if __name__ == "__main__":
    portraits()
    pages()
