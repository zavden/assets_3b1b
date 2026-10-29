"""OWN sounds that replace those from the 3b1b repo (authorship not documented) and the coin effect from
Super Mario (Nintendo, not redistributable). They are synthesized with numpy and written to `_lib/assets/sounds/` with
the same name, format (wav 16/24 bits, mp3), sample rate, channels and duration as the originals:

  bell.wav 2.88 s, bell-old1.wav 2.92 s (24 bits, start with 33 ms of silence), short_bell.wav 0.55 s,
  super_short_bell.wav 0.09 s       high glass bell: fundamental partial ~4.2 kHz with exponential
                                    decay + an inharmonic partial (x2.76) that dies quickly
  thud.wav 0.49 s (24 bits)         dull hit: low sine with pitch drop (~260 -> 52 Hz) and cut at 190 ms
  ping.wav 0.52 s                   metallic ping: partials ~2.4 kHz (x2, x2.7, x4.1 fast, x5.7), decays ~50 dB/s
  plink.mp3 0.42 s                  metal-bar "plink": inharmonic modes around 1.2-3.5 kHz, decays fast
  dart_low.wav, dart_med.wav, dart_high.wav
                                    dart impacts: wood hit (100-350 Hz body + click)
  mario_coin.wav 0.29 s             own two-tone "ping" (C6 -> G6, a fifth), NOT Mario's
  clack.wav 0.084 s, slow_clack.wav 0.412 s
                                    clash of two wooden blocks (colliding_blocks_v2). clack: wood timbre
                                    1.7-2.4 kHz with a very fast fall (tau ~0.7 ms) + sharp click + ~14 ms tail; slow_clack:
                                    low "tonk" (modes 340-510 Hz) with a ~60 ms tail. Stereo (L/R highly correlated,
                                    0.96-0.99; the originals 0.945). `colliding_blocks_v2/make_clack_sounds.py` derives from
                                    these reverse_clack, super_slow_clack and super_super_slow_clack (it runs AFTER).
                                    Levels adjusted against the original's measurements with `_tools/handoff/R7_files/fit_clacks.py`

The characteristics (duration, envelope, spectral peaks) were measured on the originals; see
`_tools/handoff/R2_files/analyze_sound.py` (and `_tools/handoff/R7_files/measure_clacks.py` for the clashes) to compare them. Nothing here uses audio from the originals.

The mp3 needs `ffmpeg` (libmp3lame); if it is not there, plink is written as `plink.wav` with a warning.
Usage: python make_replacement_sounds.py"""
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

SOUNDS = Path(__file__).resolve().parents[3] / "sounds"
TAU = 2 * np.pi


# ---------------------------------------------------------------------------- utilities

def taxis(dur, sr):
    return np.arange(int(round(dur * sr))) / sr


def fade_out(x, sr, length):
    """Brings the signal down to zero over the last `length` seconds (cosine)."""
    n = min(len(x), int(length * sr))
    if n > 0:
        x[-n:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, n)))
    return x


def partial(t, f, amp, tau, attack=0.0008, phase=0.0):
    """Damped sine with a soft attack (no click)."""
    env = amp * np.exp(-t / tau)
    if attack:
        env = env * (1 - np.exp(-t / attack))
    return env * np.sin(TAU * f * t + phase)


def band_noise(n, sr, lo, hi, seed):
    """White noise filtered in [lo, hi] Hz (frequency mask with soft edges), RMS 1."""
    rng = np.random.default_rng(seed)
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / sr)
    edge = 0.25
    mask = np.clip((f - lo * (1 - edge)) / (lo * edge + 1e-9), 0, 1) * np.clip((hi * (1 + edge) - f) / (hi * edge), 0, 1)
    y = np.fft.irfft(spec * mask, n)
    return y / (np.sqrt((y ** 2).mean()) + 1e-12)


def normalize(x, peak):
    return x * (peak / np.abs(x).max())


def normalize_rms(x, rms_db, max_peak=0.98):
    """Scale to match the volume (RMS in dBFS) of the original, without exceeding `max_peak`."""
    g = 10 ** (rms_db / 20) / np.sqrt((x ** 2).mean())
    return x * min(g, max_peak / np.abs(x).max())


def stereo(mono, sr, identical, delay_samples=3, gain=0.99):
    """Two channels. The originals are almost always dual-mono with a minimal difference (-55 to -65 dB):
    here, the right one is the left one with a delay of a few samples."""
    if identical:
        return np.stack([mono, mono], axis=1)
    right = np.concatenate([np.zeros(delay_samples), mono[:-delay_samples]]) * gain
    return np.stack([mono, right], axis=1)


def write_wav(path, x, sr, bits, quiet=False):
    """x: (n, channels) in [-1, 1]."""
    x = np.clip(x, -1.0, 1.0)
    path = Path(path)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(x.shape[1])
        w.setsampwidth(bits // 8)
        w.setframerate(sr)
        if bits == 16:
            data = np.round(x * 32767).astype("<i2").tobytes()
        elif bits == 24:
            ints = np.round(x * 8388607).astype("<i4")
            data = ints.view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
        else:
            raise ValueError(bits)
        w.writeframes(data)
    if not quiet:
        print(f"  {path.name}: {len(x) / sr:.3f} s, {sr} Hz, {x.shape[1]} canales, {bits} bits, pico {np.abs(x).max():.3f}")


def write_mp3(path, x, sr, bitrate="128k"):
    path = Path(path)
    if shutil.which("ffmpeg") is None:
        wav_path = path.with_suffix(".wav")
        print("  AVISO: no hay ffmpeg; se escribe", wav_path.name, "en vez de", path.name)
        write_wav(wav_path, x, sr, 16)
        return
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d) / "tmp.wav"
        write_wav(tmp, x, sr, 16, quiet=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-c:a", "libmp3lame", "-b:a", bitrate,
                        "-ar", str(sr), str(path)], check=True)
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    print(f"  {path.name}: mp3 {bitrate}, {float(out):.3f} s, {sr} Hz, {x.shape[1]} canales")


# ---------------------------------------------------------------------------- bells

BELL_F = 4186.0  # do8: fundamental partial of the high bell


def bell_signal(dur, sr, tau=0.19, tail_fade=0.0, start_delay=0.0, high_amp=0.5, high_tau=0.05):
    """Glass bell: fundamental + weak octave + inharmonic partial (x2.76) that dies quickly."""
    t = taxis(dur, sr)
    ts = np.maximum(t - start_delay, 0.0)
    live = (t >= start_delay).astype(float)
    x = partial(ts, BELL_F, 1.0, tau)
    x += partial(ts, BELL_F * 2.0, 0.012, tau, phase=0.7)
    x += partial(ts, BELL_F * 2.76, high_amp, high_tau, phase=1.9)
    x += partial(ts, BELL_F * 1.003, 0.10, tau * 0.8, phase=0.3)  # slow beating, like real glass
    x *= live
    if tail_fade:
        fade_out(x, sr, tail_fade)
    return x


def make_bells():
    sr = 48000
    # bell.wav: 2.884 s, 16 bits stereo
    x = normalize(bell_signal(2.884, sr, tau=0.20), 0.98)
    write_wav(SOUNDS / "bell.wav", stereo(x, sr, identical=False), sr, 16)

    # bell-old1.wav: 2.917 s, 24 bits, dual-mono, 33 ms of digital silence at the start, slightly slower decay
    x = normalize(bell_signal(2.917, sr, tau=0.215, start_delay=0.033), 0.80)
    write_wav(SOUNDS / "bell-old1.wav", stereo(x, sr, identical=True), sr, 24)

    # short_bell.wav: 0.549 s, the bell cut with a fade at the end
    x = normalize(bell_signal(0.549, sr, tau=0.30, tail_fade=0.20, high_amp=0.5, high_tau=0.05), 0.98)
    write_wav(SOUNDS / "short_bell.wav", stereo(x, sr, identical=False), sr, 16)

    # super_short_bell.wav: 0.0915 s, a bell "tick"; the high partial weighs more (the window is very short)
    x = normalize(bell_signal(0.0915, sr, tau=0.06, tail_fade=0.04, high_amp=0.55, high_tau=0.05), 0.98)
    write_wav(SOUNDS / "super_short_bell.wav", stereo(x, sr, identical=False), sr, 16)


# ---------------------------------------------------------------------------- thud

def make_thud():
    sr = 44100
    n = int(0.488 * sr)
    t = np.arange(n) / sr
    # Kick-drum-like pitch drop: ~260 Hz -> 52 Hz with a 20 ms constant; the phase is the integral of the frequency
    f = 52.0 + 208.0 * np.exp(-t / 0.020)
    phase = TAU * np.cumsum(f) / sr
    body = np.sin(phase + 0.35)
    # Envelope measured in the original (normalized): initial click, rises to ~28 ms, falls unhurriedly and dies out at 190 ms
    pts = [(0, 0.0), (0.002, 0.55), (0.008, 0.5), (0.013, 0.62), (0.0196, 0.82), (0.0276, 1.0), (0.0372, 0.91),
           (0.05, 0.87), (0.065, 0.88), (0.081, 0.83), (0.0994, 0.70), (0.118, 0.46), (0.137, 0.28), (0.157, 0.12),
           (0.19, 0.0), (1.0, 0.0)]
    env = np.interp(t, [p[0] for p in pts], [p[1] for p in pts])
    x = body * env
    # A second mode (73 Hz) and a bit of body at 154 Hz, as in a hit on hollow wood
    x += 0.07 * np.sin(TAU * 73 * t) * env + 0.03 * np.sin(TAU * 154 * t) * env * np.exp(-t / 0.03)
    # A dry hit at the start
    x += 0.15 * band_noise(n, sr, 80, 700, 3) * np.exp(-t / 0.004)
    x = normalize(x, 0.723)
    write_wav(SOUNDS / "thud.wav", stereo(x, sr, identical=True), sr, 24)


# ---------------------------------------------------------------------------- ping y plink

def make_ping():
    sr = 48000
    t = taxis(0.520, sr)
    f0 = 2400.0
    # Measured in the original: soft ping (RMS -30 dBFS) with a high partial (~9.8 kHz, as strong as the
    # fundamental at the start) and a ~2 ms click that dominates the peak (0.63).
    x = partial(t, f0, 1.0, 0.175, attack=0.0004)
    x += partial(t, f0 * 2.0, 0.05, 0.12, phase=0.4)
    x += partial(t, f0 * 2.70, 0.045, 0.15, phase=1.1)
    x += partial(t, f0 * 4.09, 1.1, 0.06, attack=0.0004, phase=2.0)
    x += partial(t, f0 * 5.75, 0.03, 0.06, phase=2.5)
    x += 2.2 * band_noise(len(t), sr, 3000, 12000, 5) * np.exp(-t / 0.0008) * (1 - np.exp(-t / 0.0002))
    fade_out(x, sr, 0.010)
    x = normalize(x, 0.629)
    write_wav(SOUNDS / "ping.wav", stereo(x, sr, identical=False), sr, 16)


def make_plink():
    sr = 44100
    t = taxis(0.405, sr)
    f0 = 1180.0
    modes = [  # (ratio, level dB, tau s)
        (0.50, -10, 0.070), (1.00, 0, 0.062), (1.50, -9, 0.050), (1.77, -2, 0.065), (2.00, -12, 0.045),
        (2.82, -7, 0.040), (3.00, -10, 0.040), (3.55, -9, 0.035), (4.00, -10, 0.030), (4.40, -12, 0.028),
    ]
    x = np.zeros_like(t)
    for i, (ratio, db, tau) in enumerate(modes):
        x += partial(t, f0 * ratio, 10 ** (db / 20), tau, attack=0.0015, phase=0.9 * i)
    x += 0.30 * band_noise(len(t), sr, 2000, 7000, 11) * np.exp(-t / 0.006)  # the quill's "toc"
    fade_out(x, sr, 0.015)
    x = normalize(x, 0.788)
    write_mp3(SOUNDS / "plink.mp3", stereo(x, sr, identical=False), sr)


# ---------------------------------------------------------------------------- darts

def dart_signal(dur, sr, modes, noise_amp, noise_band, noise_tau, hiss_amp, hiss_tau, tail_amp, tail_f, seed,
                sweep=None, attack=0.005):
    """Dart hit on a board: body of damped low modes + burst of mid noise + short sharp hiss
    (the "click") + a very soft low tail."""
    t = taxis(dur, sr)
    x = np.zeros_like(t)
    for i, (f, amp, tau) in enumerate(modes):
        if sweep and i == 0:
            f_t = f + sweep[0] * np.exp(-t / sweep[1])
            ph = TAU * np.cumsum(f_t) / sr
            x += amp * np.exp(-t / tau) * (1 - np.exp(-t / attack)) * np.sin(ph)
        else:
            x += partial(t, f, amp, tau, attack=attack, phase=1.3 * i)
    atk = 1 - np.exp(-t / 0.002)
    x += noise_amp * band_noise(len(t), sr, *noise_band, seed) * np.exp(-t / noise_tau) * atk
    x += hiss_amp * band_noise(len(t), sr, 3000, 20000, seed + 1) * np.exp(-t / hiss_tau) * atk
    x += partial(t, tail_f, tail_amp, 0.25, attack=0.01)  # very soft low tail
    return x


def make_darts():
    sr = 48000
    # dart_low: 75-340 Hz body that falls in ~20 ms, sharp click; duration 0.522 s, same volume (RMS) as the original
    modes = [(243, 1.0, 0.020), (220, 0.95, 0.028), (166, 0.45, 0.030), (331, 0.30, 0.014), (129, 0.30, 0.040),
             (98, 0.30, 0.045), (75, 0.22, 0.05)]
    x = dart_signal(0.522, sr, modes, noise_amp=0.25, noise_band=(400, 1500), noise_tau=0.008, hiss_amp=0.10,
                    hiss_tau=0.008, tail_amp=0.0012, tail_f=140.0, seed=21, attack=0.006)
    write_wav(SOUNDS / "dart_low.wav", stereo(normalize_rms(x, -21.6), sr, identical=False), sr, 16)

    # dart_med: similar but with more bass and longer decay; lower centroid
    modes = [(244, 1.0, 0.030), (221, 1.0, 0.035), (185, 0.6, 0.040), (164, 0.6, 0.040), (148, 0.5, 0.040),
             (129, 0.5, 0.040), (90, 0.5, 0.045), (59, 0.4, 0.05), (333, 0.5, 0.020)]
    x = dart_signal(0.521, sr, modes, noise_amp=0.18, noise_band=(300, 1200), noise_tau=0.008, hiss_amp=0.05,
                    hiss_tau=0.008, tail_amp=0.0015, tail_f=110.0, seed=33, attack=0.006)
    write_wav(SOUNDS / "dart_med.wav", stereo(normalize_rms(x, -18.8), sr, identical=False), sr, 16)

    # dart_high (44.1 kHz): low ~103 Hz hit with pitch drop and sub-bass, peak 0.988 and 0.357 s
    sr = 44100
    modes = [(103, 1.0, 0.055), (65, 0.12, 0.06), (46, 0.17, 0.07), (20, 0.10, 0.08), (416, 0.025, 0.02),
             (517, 0.022, 0.02)]
    x = dart_signal(0.357, sr, modes, noise_amp=0.08, noise_band=(150, 900), noise_tau=0.008, hiss_amp=0.03,
                    hiss_tau=0.010, tail_amp=0.0, tail_f=100.0, seed=45, sweep=(40.0, 0.03), attack=0.012)
    fade_out(x, sr, 0.03)
    write_wav(SOUNDS / "dart_high.wav", stereo(normalize_rms(x, -17.3), sr, identical=False), sr, 16)


# ---------------------------------------------------------------------------- block clashes

def two_channel(common, noise_l, noise_r, lag=2, noise_gain=1.0):
    """Stereo of a clash: the tonal part is common (the right one with `lag` samples of delay) and the noise is
    independent in each channel; thus L/R are highly correlated (~0.94) but not dual-mono, as in the originals."""
    right = np.concatenate([np.zeros(lag), common[:len(common) - lag]]) if lag else common
    return np.stack([common + noise_gain * noise_l, right + noise_gain * noise_r], axis=1)


def clack_parts(sr, n, seed, k):
    """Dry clash of two wooden blocks. Returns (common part, each channel's own part), unnormalized;
    `k` are the levels adjusted against the original's measurements (fit_clacks.py).
    Measured in the original: ~2 ms of silence and then a wood timbre of 1.7-2.4 kHz that starts at ~0.7 ms and falls
    very fast (tau ~0.8 ms: most of the energy is in the first 3 ms), followed by a weaker resonance
    lasting ~20 ms (tau ~5 ms), a tail of -40 to -60 dB and a little high/low energy (click and thump)."""
    t = np.arange(n) / sr
    t0 = 0.0021
    ts = np.maximum(t - t0, 0.0)
    live = (t >= t0).astype(float)
    snap = live * (1 - np.exp(-ts / 0.0001))
    fast = np.zeros(n)
    slow = np.zeros(n)
    for i, (f, amp) in enumerate([(1520, 0.35), (1720, 0.75), (1950, 0.90), (2010, 1.00), (2180, 0.85), (2390, 0.60),
                                  (2790, 0.30)]):
        fast += partial(ts, f, amp, k["fast_tau"], attack=k["attack"], phase=1.1 * i)
    for i, (f, amp) in enumerate([(1810, 0.5), (2060, 1.0), (2210, 0.7), (2360, 0.4)]):
        slow += partial(ts, f, amp, k["slow_tau"], attack=0.0008, phase=0.7 * i + 0.3)
    tail = partial(ts, 2060.0, 1.0, k["tail_tau"], attack=0.002) + partial(ts, 2210.0, 0.6, k["tail_tau"], attack=0.002, phase=2.0)
    sub = partial(ts, 70.0, 1.0, 0.006, attack=0.0008, phase=0.5) + 0.3 * partial(ts, 140.0, 1.0, 0.004, attack=0.0004)
    common = fast + k["slow"] * slow + k["tail"] * tail + k["sub"] * sub
    # the sharp click (almost the same in both channels) and a hiss of its own in each channel
    pop = band_noise(n, sr, 3000, 14000, 7) * snap * np.exp(-ts / k["pop_tau"])
    own = band_noise(n, sr, 2500, 20000, seed) * snap * np.exp(-ts / k["pop_tau"])
    hiss = band_noise(n, sr, 3000, 20000, seed + 1) * snap * np.exp(-ts / 0.012)
    common = common + k["mid"] * band_noise(n, sr, 3200, 8000, 11) * snap * np.exp(-ts / 0.002)  # roughness of the wood
    return common + k["pop"] * pop, k["own"] * k["pop"] * own + k["hiss"] * hiss


CLACK_K = dict(fast_tau=0.0007, attack=0.0003, slow=0.004, slow_tau=0.004, tail=0.00343, tail_tau=0.0138,
               sub=0.012, pop=0.04, pop_tau=0.001, own=0.9, hiss=0.00002, mid=0.025)


def make_clack():
    sr = 44100
    n = 3720  # 0.0844 s
    common, _ = clack_parts(sr, n, 0, CLACK_K)
    nl = clack_parts(sr, n, 101, CLACK_K)[1]
    nr = clack_parts(sr, n, 202, CLACK_K)[1]
    x = two_channel(common, nl, nr, lag=0, noise_gain=0.9)
    for c in range(2):
        fade_out(x[:, c], sr, 0.012)
    x = x * (0.99 / np.abs(x).max())
    write_wav(SOUNDS / "clack.wav", x, sr, 16)


def slow_clack_parts(sr, n, seed, k):
    """"Slow motion" version: a low hit (modes 340-510 Hz, plus a dry ~150 Hz thump) that drops about
    30 dB in ~12 ms (tau ~3.5 ms) and leaves a modal tail of ~75 ms (-30 dB, with beating between modes) and faint noise."""
    t = np.arange(n) / sr
    t0 = 0.0012
    ts = np.maximum(t - t0, 0.0)
    live = (t >= t0).astype(float)
    # modes measured in the original: 343, 367, 397, 416, 444, 461, 479, 505 Hz
    modes = [(343, 1.00), (367, 0.35), (397, 0.33), (416, 0.85), (444, 0.95), (461, 0.33), (479, 0.42), (505, 0.45)]
    body = np.zeros(n)
    tail = np.zeros(n)
    for i, (f, amp) in enumerate(modes):
        ph = 0.9 * i + 0.4
        body += partial(ts, f, amp, k["body_tau"], attack=0.0008, phase=ph)
        tail += partial(ts, f, k["tail"] * amp, k["tail_tau"], attack=0.004, phase=ph + 1.7)
    thump = k["thump"] * (partial(ts, 150.0, 0.6, 0.004, attack=0.0008) + partial(ts, 110.0, 0.3, 0.006, attack=0.001, phase=1.0))
    atk = live * (1 - np.exp(-ts / 0.0005))
    knock = band_noise(n, sr, 150, 900, seed) * atk * np.exp(-ts / 0.002)
    mid = band_noise(n, sr, 800, 3200, seed + 1) * atk * np.exp(-ts / k["mid_tau"])
    hiss = band_noise(n, sr, 200, 2500, seed + 2) * atk * np.exp(-ts / 0.05)
    floor = band_noise(n, sr, 13000, 21500, seed + 3) * atk * np.exp(-ts / k["floor_tau"])
    return body + tail + thump, k["knock"] * knock + k["mid"] * mid + k["hiss"] * hiss + k["floor"] * floor


SLOW_K = dict(body_tau=0.0045, tail=0.02, tail_tau=0.06, thump=1.78, knock=0.0107, mid=0.2, mid_tau=0.003,
              hiss=0.01, floor=0.00008, floor_tau=0.3)


def make_slow_clack():
    sr = 44100
    n = 18182  # 0.4123 s
    common, _ = slow_clack_parts(sr, n, 0, SLOW_K)
    nl = slow_clack_parts(sr, n, 303, SLOW_K)[1]
    nr = slow_clack_parts(sr, n, 404, SLOW_K)[1]
    x = two_channel(common, nl, nr, lag=2, noise_gain=0.9)
    for c in range(2):
        fade_out(x[:, c], sr, 0.10)
    x = x * (0.99 / np.abs(x).max())
    write_wav(SOUNDS / "slow_clack.wav", x, sr, 16)


# ---------------------------------------------------------------------------- two-tone coin

def make_coin():
    """Replacement for mario_coin.wav (Nintendo's effect): an own two-tone "ping", 0.287 s, 44.1 kHz."""
    sr = 44100
    dur = 0.287
    t = taxis(dur, sr)
    t1 = 0.080  # the first tone lasts 80 ms, the second the rest
    f1, f2 = 1046.5, 1568.0  # C6 -> G6 (a fifth; the original is a fourth over B5/E6)

    def voice(f, ts):
        # fundamental + 1/n harmonics with shifted phases (bright bell timbre, not the original's square wave),
        # limited below Nyquist
        return sum(np.sin(TAU * n * f * ts + 0.6 * n) / n for n in range(1, 9) if n * f < sr / 2.2)

    a1 = (t < t1) * (1 - np.exp(-t / 0.0015)) * np.exp(-t / 0.25)
    ts = np.maximum(t - t1, 0.0)
    a2 = (t >= t1) * (1 - np.exp(-ts / 0.0015)) * np.exp(-ts / 0.16) * 1.0
    # soft cut of the first tone so it does not click
    a1 = a1 * np.clip((t1 - t) / 0.004, 0, 1)
    x = voice(f1, t) * a1 + voice(f2, t) * a2
    fade_out(x, sr, 0.020)
    x = normalize(x, 0.95)
    write_wav(SOUNDS / "mario_coin.wav", stereo(x, sr, identical=True), sr, 16)


def main():
    SOUNDS.mkdir(parents=True, exist_ok=True)
    print("escribiendo en", SOUNDS)
    make_bells()
    make_thud()
    make_ping()
    make_plink()
    make_darts()
    make_coin()
    make_clack()
    make_slow_clack()


if __name__ == "__main__":
    main()
