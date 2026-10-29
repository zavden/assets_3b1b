"""Generates the missing placeholder assets for the CLT videos (2023/clt):

  plate.wav   plate/ceramic "clink" that GaltonBoard (galton_board.py) uses when a ball hits
              a peg. The original (Grant's Dropbox) is not in the public repo: a short jingle is synthesized
              (inharmonic partials with exponential decay, mono, 44.1 kHz, 16 bits).

Writes to _lib/assets/sounds/. Usage: python make_clt_assets.py"""
import wave
from pathlib import Path

import numpy as np

SOUNDS = Path(__file__).resolve().parents[3] / "sounds"


def make_plate(path, sr=44100, dur=0.45, seed=3):
    rng = np.random.default_rng(seed)
    t = np.arange(int(sr * dur)) / sr
    # (frequency Hz, amplitude, decay 1/s): partials of a small plate
    partials = [(1830, 1.0, 14), (2790, 0.6, 18), (4110, 0.45, 24), (5560, 0.25, 32), (7350, 0.12, 45)]
    y = sum(a * np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi)) * np.exp(-d * t) for f, a, d in partials)
    # Initial hit: a very short burst of noise
    y += 0.35 * rng.standard_normal(len(t)) * np.exp(-400 * t)
    y *= np.minimum(1, t / 0.0015)  # soft 1.5 ms attack to avoid clicks
    y /= np.abs(y).max()
    data = (0.8 * y * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())


make_plate(SOUNDS / "plate.wav")
print("ok")
