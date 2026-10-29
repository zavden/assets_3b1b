"""Generates the missing collision sounds for colliding_blocks_v2/blocks.py (they are not in the public repo):

  reverse_clack.wav          clack.wav reversed (used when the collisions are "undone")
  super_slow_clack.wav       slow_clack.wav stretched x2.5 (resampling: slower and lower)
  super_super_slow_clack.wav slow_clack.wav stretched x5

Writes to _lib/assets/sounds/. Usage: python make_clack_sounds.py"""
import wave
from pathlib import Path

import numpy as np

SOUNDS = Path(__file__).resolve().parents[3] / "sounds"


def read(name):
    with wave.open(str(SOUNDS / name)) as w:
        params = w.getparams()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, params.nchannels)
    return params, data


def write(name, params, data):
    with wave.open(str(SOUNDS / name), "wb") as w:
        w.setnchannels(params.nchannels)
        w.setsampwidth(params.sampwidth)
        w.setframerate(params.framerate)
        w.writeframes(np.clip(data, -32768, 32767).astype(np.int16).tobytes())


def stretch(data, factor):
    n = len(data)
    new_n = int(n * factor)
    x = np.linspace(0, n - 1, new_n)
    return np.stack([np.interp(x, np.arange(n), data[:, c].astype(float)) for c in range(data.shape[1])], axis=1)


params, clack = read("clack.wav")
write("reverse_clack.wav", params, clack[::-1])
params, slow = read("slow_clack.wav")
write("super_slow_clack.wav", params, stretch(slow, 2.5))
write("super_super_slow_clack.wav", params, stretch(slow, 5.0))
print("ok")
