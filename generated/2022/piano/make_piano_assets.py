"""Generates the data of _2022/piano that in the original lived in `_2022/piano/data/` (Grant's Dropbox,
not in the public repo):

- data/audio_clips/SignalFromSpeech.wav: a speech fragment by Grant. Here it is a "speech-like"
  stereo signal (syllables with varying pitch, harmonics filtered by formants and
  some noise), of 3 s at 44.1 kHz.
- data/3-16-attempts/Help_Long_as_piano_5ms.mid, Help_Long_STFT.mid, Help_Long_online.mid:
  three "MIDI transcriptions" of the same piece. In the original they are Grant's attempts
  at converting audio to piano notes; here the piece is the Ode to Joy (Beethoven,
  public domain) with accompaniment, and the STFT/online versions add the typical errors
  of those methods (short spurious notes, octave errors, missed notes).

Output: _lib/assets/generated/2022/piano/data/ (the scenes receive it with `data_files`).

Usage: python make_piano_assets.py"""
import random
from pathlib import Path

import mido
import numpy as np
from scipy.io import wavfile

HERE = Path(__file__).resolve().parent
OUT = HERE / "data"

TICKS_PER_BEAT = 480
TEMPO = 250000  # microseconds per quarter note (240 bpm), the initial value the scene assumes


# ---------------------------------------------------------------- MIDI

def ode_to_joy():
    """List of (midi note, start in quarter notes, duration in quarter notes, velocity)."""
    C4 = 60
    scale = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

    def n(name, octave=4):
        return C4 + 12 * (octave - 4) + scale[name]

    phrase_a = [("E", 1), ("E", 1), ("F", 1), ("G", 1), ("G", 1), ("F", 1), ("E", 1), ("D", 1),
                ("C", 1), ("C", 1), ("D", 1), ("E", 1), ("E", 1.5), ("D", 0.5), ("D", 2)]
    phrase_b = [("E", 1), ("E", 1), ("F", 1), ("G", 1), ("G", 1), ("F", 1), ("E", 1), ("D", 1),
                ("C", 1), ("C", 1), ("D", 1), ("E", 1), ("D", 1.5), ("C", 0.5), ("C", 2)]
    phrase_c = [("D", 1), ("D", 1), ("E", 1), ("C", 1), ("D", 1), ("E", 0.5), ("F", 0.5), ("E", 1),
                ("C", 1), ("D", 1), ("E", 0.5), ("F", 0.5), ("E", 1), ("D", 1), ("C", 1), ("D", 1),
                ("G", 2)]
    phrase_d = phrase_a

    notes = []
    t = 0.0
    rng = random.Random(7)
    for phrase in [phrase_a, phrase_b, phrase_c, phrase_d, phrase_b]:
        for item in phrase:
            name, dur = item[0], item[1]
            octave = item[2] if len(item) > 2 else 4
            vel = rng.randint(70, 100)
            notes.append((n(name, octave), t, dur * 0.9, vel))
            t += dur
    total = t
    # Accompaniment: bass in octaves every two beats
    bass_cycle = [("C", 3), ("G", 2), ("C", 3), ("G", 2), ("C", 3), ("F", 2), ("G", 2), ("C", 3)]
    t = 0.0
    i = 0
    while t < total - 1:
        name, octave = bass_cycle[i % len(bass_cycle)]
        notes.append((n(name, octave), t, 1.8, rng.randint(50, 75)))
        notes.append((n(name, octave) + 7, t, 1.8, rng.randint(40, 60)))
        t += 2
        i += 1
    return notes


def corrupt(notes, kind, seed):
    """Imitates the errors of an automatic audio -> MIDI transcription."""
    rng = random.Random(seed)
    out = []
    for note, start, dur, vel in notes:
        r = rng.random()
        if kind == "stft":
            if r < 0.06:      # wrong octave
                note += rng.choice([-12, 12])
            elif r < 0.10:    # missed note
                continue
            out.append((note, start + rng.uniform(-0.04, 0.04), dur * rng.uniform(0.6, 1.1), vel))
            if rng.random() < 0.18:  # short spurious note
                out.append((note + rng.choice([-7, -5, 5, 7, 12]), start + rng.uniform(0, dur), 0.12, 35))
        elif kind == "online":
            if r < 0.08:
                continue
            out.append((note, start + rng.uniform(0.0, 0.12), dur * rng.uniform(0.4, 0.9), vel))
            if rng.random() < 0.10:
                out.append((note + 12, start + 0.1, 0.1, 30))
        else:
            out.append((note, start, dur, vel))
    return out


def write_midi(path, notes):
    events = []
    for note, start, dur, vel in notes:
        note = int(min(max(note, 21), 108))
        t0 = int(round(start * TICKS_PER_BEAT))
        t1 = max(t0 + 1, int(round((start + dur) * TICKS_PER_BEAT)))
        events.append((t0, 1, "note_on", note, int(vel)))
        events.append((t1, 0, "note_off", note, 0))
    events.sort()
    mid = mido.MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage("set_tempo", tempo=TEMPO, time=0))
    last = 0
    for tick, _, kind, note, vel in events:
        track.append(mido.Message(kind, note=note, velocity=vel, time=tick - last))
        last = tick
    path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(path)


# ---------------------------------------------------------------- audio

def speech_like(sample_rate=44100, seconds=3.0, seed=3):
    rng = np.random.default_rng(seed)
    n = int(sample_rate * seconds)
    t = np.arange(n) / sample_rate
    # (start, end, initial f0, final f0, formants F1, F2, F3)
    syllables = [
        (0.15, 0.55, 118, 140, 730, 1090, 2440),
        (0.70, 1.05, 140, 125, 270, 2290, 3010),
        (1.15, 1.70, 125, 165, 570, 840, 2410),
        (1.85, 2.30, 165, 130, 660, 1720, 2410),
        (2.40, 2.85, 130, 105, 300, 870, 2240),
    ]
    signal = np.zeros(n)
    for a, b, f0a, f0b, f1, f2, f3 in syllables:
        i0, i1 = int(a * sample_rate), int(b * sample_rate)
        tt = np.arange(i1 - i0) / sample_rate
        u = tt / (b - a)
        f0 = f0a + (f0b - f0a) * u
        phase = 2 * np.pi * np.cumsum(f0) / sample_rate
        env = np.sin(np.pi * u) ** 0.7
        seg = np.zeros_like(tt)
        for h in range(1, int(4000 / min(f0a, f0b))):
            f = h * f0
            gain = sum(a_ * np.exp(-0.5 * ((f - fm) / bw) ** 2)
                       for a_, fm, bw in [(1.0, f1, 90), (0.6, f2, 140), (0.3, f3, 200)])
            seg += gain * np.sin(h * phase + h)
        seg *= env / max(1e-9, np.abs(seg).max())
        # initial consonant: filtered noise
        noise = rng.normal(size=tt.size)
        noise = np.convolve(noise, np.ones(3) / 3, mode="same") * np.exp(-tt * 60) * 0.35
        signal[i0:i1] += seg + noise
    signal += 0.01 * rng.normal(size=n)
    signal /= np.abs(signal).max()
    left = signal
    right = 0.9 * np.roll(signal, 12)
    stereo = np.stack([left, right], axis=1)
    return sample_rate, (stereo * 0.8 * 32767).astype(np.int16)


def main():
    notes = ode_to_joy()
    write_midi(OUT / "3-16-attempts" / "Help_Long_as_piano_5ms.mid", notes)
    write_midi(OUT / "3-16-attempts" / "Help_Long_STFT.mid", corrupt(notes, "stft", 11))
    write_midi(OUT / "3-16-attempts" / "Help_Long_online.mid", corrupt(notes, "online", 12))

    sr, data = speech_like()
    (OUT / "audio_clips").mkdir(parents=True, exist_ok=True)
    wavfile.write(OUT / "audio_clips" / "SignalFromSpeech.wav", sr, data)
    print(f"escrito en {OUT}")


if __name__ == "__main__":
    main()
