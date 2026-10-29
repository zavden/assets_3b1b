"""Placeholders for the private assets of _2024/transformers/generation.py (they lived in Grant's Dropbox).

Creates in _lib/assets/raster_images/ (the code looks for them by name):
  AudioSnippet.png         (VoiceToTextExample) placeholder audio waveform, drawn with PIL
  PiCreatureDalle3_5.png   (TextToImage) placeholder "generated" image: box with the name, made
                           with _tools/placeholder.py (the original was made by DALL-E 3)

Usage: python make_generation_assets.py"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]  # .../_lib
RASTER = LIB / "assets" / "raster_images"
sys.path.insert(0, str(LIB.parent / "_tools"))
from placeholder import make_image, font  # noqa: E402


def make_audio_snippet(out, size=(1500, 1200)):
    """Waveform with three syllables (envelopes) on a dark background."""
    w, h = size
    img = Image.new("RGB", size, "#14181f")
    d = ImageDraw.Draw(img)
    mid = h // 2
    d.line([(40, mid), (w - 40, mid)], fill="#2a3340", width=2)
    rng = random.Random(4)
    n = 260
    for i in range(n):
        t = i / (n - 1)
        env = max(
            math.exp(-((t - c) ** 2) / (2 * s ** 2)) * a
            for c, s, a in [(0.16, 0.05, 0.9), (0.38, 0.07, 0.75), (0.63, 0.06, 1.0), (0.84, 0.05, 0.6)]
        )
        amp = (0.04 + env) * rng.uniform(0.55, 1.0) * (h * 0.42)
        x = 60 + t * (w - 120)
        d.line([(x, mid - amp), (x, mid + amp)], fill="#58c4dd", width=4)
    d.text((w / 2, h - 50), "[audio de relleno]", font=font(40), fill="#6a7482", anchor="mm")
    img.save(out)


def main():
    RASTER.mkdir(parents=True, exist_ok=True)
    make_audio_snippet(RASTER / "AudioSnippet.png")
    make_image(RASTER / "PiCreatureDalle3_5.png", "PiCreatureDalle3 5", (1000, 1000), "#2f4552")
    print("assets de generation.py listos")


if __name__ == "__main__":
    main()
