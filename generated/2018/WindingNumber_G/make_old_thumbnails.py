"""Replacement for the folder `3b1b_videos/Winding/OldThumbnails` used by 2018/WindingNumber_G::AllOfTheVideos.

The original folder (video thumbnails by Grant, in his Dropbox) is not available. The scene lists the folder and shows the
first 16 images in a 4x4 grid, so any 16 images will do. These are 16 colourful, generic thumbnails made by code
(winding-number style colour field + a plain "Thumbnail N" caption). No third-party material.

Output: _lib/assets/raster_images/WindingOldThumbnails/thumb_01.png ... thumb_16.png
Run: python make_old_thumbnails.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[3] / "raster_images" / "WindingOldThumbnails"
FONTS = ["/usr/share/fonts/cm-unicode/cmunrm.otf", "/usr/share/fonts/dejavu-sans-fonts/DejaVuSerif.ttf"]
W, H = 480, 270


def font(size):
    for p in FONTS:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def field(n):
    ys, xs = np.mgrid[0:H, 0:W]
    z = ((xs - W / 2) + 1j * (ys - H / 2)) / (H / 3)
    zeros = [0.9 * np.exp(2j * np.pi * k / (n % 4 + 2)) for k in range(n % 4 + 2)]
    f = np.prod([z - a for a in zeros], axis=0) / (z ** (n % 3) + 1.5 + 1e-3)
    hue = (np.angle(f) / (2 * np.pi)) % 1.0
    val = 0.35 + 0.65 * (1 - np.exp(-np.abs(f)))
    hsv = np.stack([hue * 255, np.full_like(hue, 200), np.clip(val, 0, 1) * 255], -1).astype("uint8")
    return Image.fromarray(hsv, "HSV").convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for n in range(1, 17):
        im = field(n)
        d = ImageDraw.Draw(im)
        d.rectangle([0, H - 52, W, H], fill=(0, 0, 0))
        d.text((16, H - 46), f"Thumbnail {n}", font=font(34), fill=(255, 255, 255))
        im.save(OUT / f"thumb_{n:02d}.png", optimize=True)


if __name__ == "__main__":
    main()
