"""Generates the placeholder assets of _2022/infinity/roar_to_picture.py (the originals lived in Grant's Dropbox,
videos/2022/infinity/):

- Roar.wav (DecomposeRoar_SlowFPS): a synthetic 5 s "roar", stereo, 44.1 kHz, 16 bits, in
  _lib/assets/generated/2022/infinity/Roar.wav (the scene reads it with wavfile.read, so it goes next to the
  scene with `data_files`). Harmonics of a low tone that drops from 150 to 70 Hz, with amplitude modulation
  ("growl") and noise, under an attack-and-decay envelope.
- monster-holding-piece-sign-3.svg (CombineWavesToImage_SlowFPS): the scene uses `svg[1]` as the stroke
  that the Fourier circles draw. Placeholder: the outer outline of the monster of monster.svg
  (_2020/monster.py) as the second element, preceded by a small circle. In _lib/assets/svg_images/.

Usage: python make_infinity_assets.py"""
import re
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]  # _lib/assets


def make_roar(out, seconds=5.0, rate=44100, seed=3):
    rng = np.random.default_rng(seed)
    n = int(seconds * rate)
    t = np.arange(n) / rate
    f0 = 70 + 80 * np.exp(-t / 1.4)          # falling pitch
    phase = 2 * np.pi * np.cumsum(f0) / rate
    sig = np.zeros(n)
    for k in range(1, 18):
        amp = 1 / k ** 1.1 * (1 + 0.6 * np.sin(3.1 * k))
        sig += amp * np.sin(k * phase + 0.7 * k * k)
    sig *= 0.6 + 0.4 * np.sin(2 * np.pi * 27 * t)        # growl
    noise = np.convolve(rng.normal(size=n), np.ones(6) / 6, mode="same")
    sig += 0.35 * noise
    env = np.minimum(1, t / 0.25) * np.exp(-np.maximum(0, t - 2.5) / 1.1)
    sig *= env
    sig = sig / np.abs(sig).max() * 0.9
    data = (sig * 32767).astype("<i2")
    stereo = np.stack([data, data], axis=1)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(stereo.tobytes())


def make_monster_svg(out):
    src = (ASSETS / "svg_images" / "monster.svg").read_text()
    d = re.search(r' d="([^"]+)"', src).group(1)
    outline = d[:re.search("[zZ]", d).end()]       # only the outer outline
    out.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="100px" height="100px" viewBox="0 0 100 100">'
        '<!-- relleno: el original (monstruo con un letrero de paz) no es público -->'
        '<circle cx="85" cy="12" r="5" fill="none" stroke="#000000" stroke-width="1"/>'
        f'<path d="{outline}" fill="none" stroke="#000000" stroke-width="1"/></svg>'
    )


if __name__ == "__main__":
    make_roar(HERE / "Roar.wav")
    make_monster_svg(ASSETS / "svg_images" / "monster-holding-piece-sign-3.svg")
