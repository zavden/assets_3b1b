#!/usr/bin/env python3
"""Parametric generator of the expressions of the "capital Pi" character.

Usage:  python generar_expresiones.py [mode ...]     (without arguments: all)
Writes in this same folder, for each mode:
    <mode>_6partes.svg   easy-to-edit format (left eye, right eye, left pupil, right pupil, body, mouth)
    <mode>.svg           12-part format that PiCreature reads (fills at 0, 1, 3, 4, 5 and 7)

HOW TO ADD AN EXPRESSION: add an entry to EXPRESIONES (below) with only what changes
with respect to BASE. Everything in the "plain frame": viewBox 200x200, bar x 20..180, y 30..100, legs down to y=190.

Parameters (all optional):
  tilt      pixels the left end of the bar goes down (and the right one up). Negative: the other way.
  lean      shifts the bar horizontally relative to the feet (px; + = to the right).
  scale     shrinks (<1) the character toward the feet (it "cowers").
  spread    separation of the legs (px, + = wider apart, - = closer together).
  eye_r     radius of the iris;  eye_cy  height of the eye's center (larger = more sunken = half-closed eyelid);
  eye_sep   half of the separation between the eyes (24 in plain).
  look      (dx, dy) of the pupil relative to the center of the iris, both eyes (default (3,2): looks to the right).
  eye_l / eye_r_  dict with dx, dy, r, look to adjust a single eye (left / right on screen).
  mouth     dict with "kind" and its parameters; see function boca().
              kind "crescent": smile/sad/sideways. w, cx, cy, sag (+ smile, - sad), e0/e1 (height of
                               the left/right ends; e1<e0 = sideways smile), t (thickness), skew
              kind "wavy":     straight or wavy/zigzag line. w, cx, cy, amp, freq, phase, e0/e1, t
              kind "open":     D-shaped open mouth. w, cx, cy, depth, lip
              kind "oval":     oval open mouth. cx, cy, rx, ry, rot
  body      "pi" (default), "tau" (capital Tau letter: bar and a single central leg) or "three"
            (Pi with a third leg in the middle). `escribir_variantes()` also generates each expression
            as TauCreatures_<mode>.svg and ThreeLeggedPiCreatures_<mode>.svg (see its docstring).
  arm_r / arm_l   arm at the right / left end of the bar: name from ARMS or a dict with
                  ya (shoulder height, 51..79), pts [(dx,dy) c1, c2, end] in the right arm's coordinates
                  (the left one is mirrored), w0 (thickness at the shoulder), w1 (thickness of the hand)."""
import math
import sys
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent
COLOR_CUERPO = "#E07A3F"
BAR_L, BAR_R, BAR_T, BAR_B = 20, 180, 30, 100

# ----------------------------------------------------------------------------- arms
ARMS = {
    # straight up (raising the hand)
    "up": dict(ya=62, pts=[(10, 0), (14, -18), (14, -46)], w0=15, w1=18),
    # upward and curving over the head (thinking / scratching)
    "scratch": dict(ya=60, pts=[(16, 0), (24, -22), (6, -39)], w0=15, w1=18),
    # hand on the waist (hands on hips); the hand does not touch the leg: no hole is left
    "hip": dict(ya=72, pts=[(18, 2), (22, 28), (-4, 46)], w0=14, w1=16),
    # arm stretched outward, upward / downward
    "out_up": dict(ya=64, pts=[(14, 0), (26, -4), (28, -26)], w0=15, w1=18),
    "out_down": dict(ya=60, pts=[(14, 0), (26, 4), (28, 30)], w0=15, w1=18),
    # explaining gesture: halfway up, open hand facing outward
    "gesture": dict(ya=64, pts=[(12, 0), (24, -4), (24, -26)], w0=15, w1=18),
    # arm hanging next to the body (outside the leg)
    "down": dict(ya=62, pts=[(12, 0), (22, 14), (20, 50)], w0=15, w1=17),
    # raised fist with the elbow outward
    "fist": dict(ya=68, pts=[(20, 0), (28, -12), (12, -30)], w0=15, w1=19),
    # arm stretched horizontally (offering, holding)
    "out": dict(ya=66, pts=[(12, 0), (22, 0), (28, -4)], w0=15, w1=18),
    # greeting: hand tilted outward / inward
    "wave_out": dict(ya=62, pts=[(10, 0), (20, -16), (30, -40)], w0=15, w1=18),
    "wave_in": dict(ya=62, pts=[(12, 0), (18, -20), (0, -44)], w0=15, w1=18),
    # shrug: elbow out, open hand facing up
    "shrug": dict(ya=66, pts=[(16, 0), (26, -2), (24, -22)], w0=15, w1=18),
}

# ----------------------------------------------------------------------------- base
BASE = dict(
    tilt=0, lean=0, scale=1.0, spread=0,
    eye_r=16, eye_cy=24, eye_sep=24, look=(3, 2),
    eye_l={}, eye_r_={},
    mouth=dict(kind="crescent", w=30, cx=100, cy=58, sag=6.75, t=4.5),
    arm_r=None, arm_l=None, kick_r=0, kick_l=0, body="pi",
)

EXPRESIONES = {
    "plain": {},
    # hand on the head, looking up, small straight mouth
    "pondering": dict(tilt=4, eye_cy=25, look=(5, -6),
                      arm_r=dict(ya=62, pts=[(16, 0), (26, -22), (-4, -44)], w0=15, w1=16),
                      mouth=dict(kind="wavy", w=24, cx=104, cy=67, e0=2, e1=-2, t=6)),
    # mischievous: one eye squinting (wink), sideways smile, tilted body
    "tease": dict(tilt=-3, lean=5, look=(6, 1),
                  eye_l=dict(dy=7, r=15, look=(5, 0)), eye_r_=dict(dy=-1, r=17),
                  mouth=dict(kind="crescent", w=34, cx=104, cy=60, sag=7, e0=3, e1=-6, t=6.5)),
    "raise_right_hand": dict(tilt=-2, look=(5, -2), arm_r="up",
                             mouth=dict(kind="crescent", w=28, cx=100, cy=58, sag=6, t=6)),
    # high gaze, small mouth to one side
    "thinking": dict(tilt=4, lean=3, eye_cy=22, look=(4, -8), arm_r="hip",
                     mouth=dict(kind="crescent", w=22, cx=110, cy=66, sag=3.5, e0=1, e1=-4, t=5.5)),
    # uneven eyes and mismatched pupils, wavy mouth, very twisted body
    "confused": dict(tilt=8, lean=-4,
                     eye_l=dict(dy=2, r=14, look=(-3, -3)), eye_r_=dict(dy=-3, r=17, look=(5, 4)),
                     mouth=dict(kind="wavy", w=36, cx=100, cy=66, amp=3.5, freq=1.5, e0=3, e1=-4, t=6)),
    # shrinking: legs together, sunken eyes looking away, trembling mouth
    "hesitant": dict(scale=0.88, spread=-7, tilt=2, lean=-3, eye_r=15, eye_cy=27, look=(-6, 5),
                     arm_r="down", arm_l="down",
                     mouth=dict(kind="crescent", w=22, cx=96, cy=69, sag=-3.5, e0=0, e1=1, t=5.5)),
    # uncomfortable: half-drooping eyes looking sideways, zigzag mouth
    "erm": dict(tilt=-2, lean=3, eye_r=15, eye_cy=28, look=(-7, 1),
                mouth=dict(kind="wavy", w=42, cx=100, cy=67, amp=4, freq=3.5, phase=0.0, t=5.5)),
    # open smile, large high eyes
    "happy": dict(tilt=-2, eye_r=17, eye_cy=25, look=(4, -2),
                  mouth=dict(kind="open", w=46, cx=100, cy=52, depth=28, lip=-3)),
    "raise_left_hand": dict(tilt=2, look=(3, -2), arm_l="up",
                            mouth=dict(kind="crescent", w=28, cx=100, cy=58, sag=6, t=6)),
    # hands on hips, half-closed eyelids, sideways smile
    "sassy": dict(tilt=-4, lean=-4, eye_cy=29, look=(7, -1), arm_r="hip", arm_l="hip",
                  mouth=dict(kind="crescent", w=26, cx=104, cy=62, sag=5, e0=1, e1=-6, t=6)),
    # "maybe": one arm up and one down (scale), uneven eyes, lopsided mouth
    "maybe": dict(tilt=5, look=(-5, -5), arm_r="out_up", arm_l="out_down",
                  eye_l=dict(r=15), eye_r_=dict(r=17, dy=-1),
                  mouth=dict(kind="wavy", w=30, cx=100, cy=65, amp=2.5, freq=1, e0=3, e1=-3, t=6)),
    # celebrates: arms up, legs apart, mouth wide open
    "hooray": dict(spread=6, eye_r=17, eye_cy=25, look=(3, -4), arm_r="up", arm_l="up",
                   mouth=dict(kind="open", w=54, cx=100, cy=50, depth=34, lip=-4)),
    # open oval mouth, pupils forward, arm gesture
    "speaking": dict(tilt=-2, look=(7, 1), arm_r="gesture",
                     mouth=dict(kind="open", w=26, cx=106, cy=56, depth=24, lip=0)),

    # ------------------------------------------------------------------ second batch
    "angry": dict(tilt=3, spread=4, eye_r=14, eye_cy=29, look=(2, 2), arm_r="fist", arm_l="fist",
                  mouth=dict(kind="open", w=40, cx=100, cy=80, depth=24, lip=0, inv=True)),
    "well": dict(tilt=5, lean=3, eye_cy=26, look=(-4, -6), arm_l="hip", arm_r="gesture",
                 mouth=dict(kind="crescent", w=22, cx=96, cy=68, sag=-3.5, e0=-1, e1=2, t=6)),
    "surprised": dict(spread=3, eye_r=18, eye_cy=26, look=(0, 0), arm_r="gesture", arm_l="gesture",
                      mouth=dict(kind="oval", cx=100, cy=66, rx=8, ry=11)),
    "horrified": dict(spread=8, eye_r=18, eye_cy=26, look=(0, 1), arm_r="up", arm_l="up",
                      mouth=dict(kind="open", w=46, cx=100, cy=88, depth=36, lip=0, inv=True)),
    "guilty": dict(scale=0.95, tilt=3, lean=-2, eye_r=15, eye_cy=27, look=(-6, 4), arm_l="scratch",
                   mouth=dict(kind="crescent", w=22, cx=98, cy=66, sag=3, e0=3, e1=-1, t=5.5)),
    "shruggie": dict(tilt=3, eye_cy=26, look=(5, -3), arm_r="shrug", arm_l="shrug",
                     mouth=dict(kind="wavy", w=28, cx=100, cy=65, e0=5, e1=-5, amp=0, t=6)),
    "pleading": dict(tilt=-3, eye_r=18, eye_cy=26, look=(2, -6), arm_r="gesture", arm_l="gesture",
                     mouth=dict(kind="crescent", w=18, cx=100, cy=70, sag=-3, t=5.5)),
    "coin_flip_1": dict(tilt=-2, lean=2, look=(6, -8), arm_r="wave_out",
                        mouth=dict(kind="crescent", w=24, cx=102, cy=58, sag=5, t=6)),
    "coin_flip_2": dict(tilt=2, look=(-3, -8), arm_r="gesture", arm_l="out",
                        mouth=dict(kind="oval", cx=100, cy=67, rx=5, ry=6)),
    "sad": dict(scale=0.95, tilt=4, eye_r=15, eye_cy=28, look=(0, 6), arm_r="down", arm_l="down",
                mouth=dict(kind="crescent", w=24, cx=100, cy=69, sag=-7, t=6)),
    "tired": dict(scale=0.95, tilt=-5, lean=-3, eye_r=15, eye_cy=31, look=(0, 4), arm_l="down", arm_r="scratch",
                  mouth=dict(kind="oval", cx=100, cy=68, rx=8, ry=12)),
    "gracious": dict(tilt=-5, lean=5, eye_r=15, eye_cy=28, look=(3, 2), arm_r="out", arm_l="down",
                     mouth=dict(kind="crescent", w=36, cx=100, cy=56, sag=10, t=6.5)),
    "awe": dict(eye_r=19, eye_cy=27, look=(2, -8), lean=-2, arm_r="down", arm_l="down",
                mouth=dict(kind="open", w=22, cx=100, cy=58, depth=15, lip=-2)),
    "dance_3": dict(spread=10, lean=-6, tilt=-4, look=(4, -3), arm_r="up", arm_l="out_down", kick_r=18,
                    mouth=dict(kind="open", w=40, cx=100, cy=54, depth=22, lip=-3)),

    # ------------------------------------------------------------------ only in discarded scenes
    "dejected": dict(scale=0.9, tilt=8, lean=-5, eye_r=14, eye_cy=29, look=(0, 7), arm_r="down", arm_l="down",
                     mouth=dict(kind="crescent", w=18, cx=100, cy=70, sag=-4, t=6)),
    "frustrated": dict(tilt=-5, eye_r=14, eye_cy=29, look=(0, 2), arm_r="scratch", arm_l="scratch",
                       mouth=dict(kind="wavy", w=38, cx=100, cy=68, amp=3, freq=2.5, t=6)),
    "concerned_musician": dict(tilt=3, eye_cy=24, look=(0, -6), arm_r="fist", arm_l="fist",
                               mouth=dict(kind="crescent", w=20, cx=100, cy=68, sag=-3, t=6)),
    "bump": dict(tilt=-7, lean=4, eye_r=13, eye_cy=31, look=(0, 2), arm_r="scratch",
                 mouth=dict(kind="open", w=34, cx=100, cy=78, depth=20, lip=0, inv=True)),
    "dance_1": dict(lean=6, tilt=-4, spread=4, look=(4, -2), arm_r="up", arm_l="out_down", kick_l=22,
                    mouth=dict(kind="open", w=40, cx=100, cy=54, depth=22, lip=-3)),
    "heistant": "hesitant",
    "sick": dict(scale=0.92, tilt=7, lean=-4, eye_r=13, eye_cy=28, look=(-3, 4), eye_l=dict(r=15, dy=2),
                 arm_r="down",
                 mouth=dict(kind="wavy", w=26, cx=100, cy=70, amp=3, freq=1.5, e0=2, e1=-2, t=6)),

    # ------------------------------------------------------------------ existed in the original, unused in converted scenes
    "conniving": dict(tilt=-3, eye_r=15, eye_cy=29, look=(7, 0), arm_r="fist", arm_l="fist",
                      mouth=dict(kind="crescent", w=40, cx=100, cy=58, sag=9, e0=2, e1=-4, t=6.5)),
    "dance_2": dict(lean=-6, tilt=4, spread=4, look=(-3, -2), arm_l="up", arm_r="out_down", kick_r=22,
                    mouth=dict(kind="open", w=40, cx=100, cy=54, depth=22, lip=-3)),
    "dance_kick": dict(lean=-8, tilt=3, look=(4, -4), arm_l="out_up", arm_r="out_down", kick_r=45,
                       mouth=dict(kind="open", w=36, cx=100, cy=54, depth=20, lip=-3)),
    "lower_right_hand": dict(tilt=-1, look=(5, 0), arm_r="down",
                             mouth=dict(kind="crescent", w=28, cx=100, cy=58, sag=6, t=6)),
    "soulful_musician": dict(tilt=8, lean=-3, eye_r=15, eye_cy=31, look=(0, 3), arm_r="gesture", arm_l="gesture",
                             mouth=dict(kind="oval", cx=100, cy=68, rx=6, ry=8)),
    "telepath": dict(eye_r=14, eye_cy=30, look=(0, -2), arm_r="scratch", arm_l="scratch",
                     mouth=dict(kind="wavy", w=14, cx=100, cy=68, t=6)),
    "wave_1": dict(tilt=-2, look=(5, -1), arm_r="wave_out",
                   mouth=dict(kind="crescent", w=28, cx=100, cy=58, sag=6, t=6)),
    "wave_2": dict(tilt=-1, look=(5, -1), arm_r="up",
                   mouth=dict(kind="crescent", w=28, cx=100, cy=58, sag=6, t=6)),
    "wave_3": dict(tilt=0, look=(5, -1), arm_r="wave_in",
                   mouth=dict(kind="crescent", w=28, cx=100, cy=58, sag=6, t=6)),

    # ------------------------------------------------------------------ no original design (optional)
    "same": dict(tilt=-3, lean=3, look=(6, 0), arm_r="out",
                 mouth=dict(kind="open", w=30, cx=100, cy=56, depth=16, lip=-2)),
    "concentrating": dict(lean=5, eye_r=14, eye_cy=29, look=(4, 3),
                          mouth=dict(kind="oval", cx=108, cy=68, rx=5, ry=3.5)),
    "skeptical": dict(tilt=3, arm_r="hip",
                      eye_l=dict(dy=7, r=14, look=(5, 0)), eye_r_=dict(dy=-2, r=17, look=(5, -3)),
                      mouth=dict(kind="wavy", w=24, cx=104, cy=67, e0=2, e1=-3, t=6)),
    "jamming": dict(lean=7, tilt=-5, spread=5, eye_r=15, eye_cy=30, look=(0, 3), arm_r="fist", arm_l="fist",
                    kick_l=15, mouth=dict(kind="open", w=36, cx=100, cy=56, depth=18, lip=-3)),
    "droopy": dict(scale=0.9, tilt=10, lean=-6, eye_r=15, eye_cy=30, look=(0, 6), arm_l="down", arm_r="down",
                   mouth=dict(kind="crescent", w=20, cx=100, cy=70, sag=-4, t=6)),
    "worried": dict(tilt=3, spread=-3, eye_r=17, eye_cy=25, look=(0, -5), arm_r="fist", arm_l="fist",
                    mouth=dict(kind="wavy", w=28, cx=100, cy=68, amp=2, freq=2.5, t=6)),
    "can": dict(tilt=-2, look=(5, 0), arm_r="out",
                mouth=dict(kind="crescent", w=28, cx=100, cy=58, sag=6, t=6)),
}


# ----------------------------------------------------------------------------- auxiliary geometry
def ribbon_sides(pts, widths):
    """Given an axis (N,2) and widths (N,), returns (side -n, side +n, directions)."""
    pts = np.asarray(pts, float)
    d = np.gradient(pts, axis=0)
    d /= np.linalg.norm(d, axis=1)[:, None]
    n = np.stack([-d[:, 1], d[:, 0]], axis=1)
    w = np.asarray(widths, float)[:, None] / 2
    return pts - n * w, pts + n * w, d, n


def cap(center, r, d, n, a0=0.0, a1=math.pi, k=8):
    """Semicircle from -n (a0=0) passing through d (pi/2) to +n (pi)."""
    out = []
    for th in np.linspace(a0, a1, k + 2)[1:-1]:
        out.append(center + r * (-n * math.cos(th) + d * math.sin(th)))
    return out


def bezier(P, N=24):
    P = np.asarray(P, float)
    t = np.linspace(0, 1, N)[:, None]
    if len(P) == 3:
        return (1 - t) ** 2 * P[0] + 2 * (1 - t) * t * P[1] + t ** 2 * P[2]
    return ((1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1]
            + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3])


def poly_d(points):
    return "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in points) + " Z"


# ----------------------------------------------------------------------------- generator
class Fig:
    def __init__(self, p):
        self.p = {**BASE, **p}
        self.bbox = [1e9, 1e9, -1e9, -1e9]

    # transformations ---------------------------------------------------------
    def bar_dy(self, x):
        return self.p["tilt"] * (100 - x) / 80

    def G(self, x, y):
        """Scales toward the feet and then tilts (lean) the body without moving the feet."""
        k = self.p["scale"]
        x = 100 + (x - 100) * k
        y = 190 + (y - 190) * k
        x += self.p["lean"] * (190 - y) / 90
        return x, y

    def T(self, x, y):
        """Point of the bar: applies the bar's tilt and then G."""
        return self.G(x, y + self.bar_dy(x))

    def note(self, x, y):
        b = self.bbox
        b[0], b[1], b[2], b[3] = min(b[0], x), min(b[1], y), max(b[2], x), max(b[3], y)

    # eyes ----------------------------------------------------------------------
    def eyes(self):
        p = self.p
        res = []
        for side, sx in (("l", -1), ("r", 1)):
            o = p["eye_l"] if side == "l" else p["eye_r_"]
            r = o.get("r", p["eye_r"])
            cx = 100 + sx * p["eye_sep"] + o.get("dx", 0)
            cy = p["eye_cy"] + o.get("dy", 0)
            lk = o.get("look", p["look"])
            c = self.T(cx, cy)
            rr = r * p["scale"]
            pu = (c[0] + lk[0] * p["scale"], c[1] + lk[1] * p["scale"])
            if c[1] - rr < 8:  # do not go past the top edge of plain (keeps the scale)
                dy = 8 - (c[1] - rr)
                c = (c[0], c[1] + dy)
                pu = (pu[0], pu[1] + dy)
            self.note(c[0] - rr, c[1] - rr)
            self.note(c[0] + rr, c[1] + rr)
            res.append((c, rr, pu))
        return res

    # mouth ----------------------------------------------------------------------
    def boca(self):
        m = dict(self.p["mouth"])
        kind = m.pop("kind")
        M = lambda x, y: self.T(x, y)
        if kind in ("crescent", "wavy"):
            w, cx, cy = m.get("w", 30), m.get("cx", 100), m.get("cy", 60)
            e0, e1, t = m.get("e0", 0), m.get("e1", 0), m.get("t", 4.5)
            x0, x1 = cx - w / 2, cx + w / 2
            if kind == "crescent":
                sag = m.get("sag", 6)
                ctrl = (cx + m.get("skew", 0), (e0 + e1) / 2 + cy + 2 * sag)
                axis = bezier([(x0, cy + e0), ctrl, (x1, cy + e1)], 28)
                s = np.linspace(0, 1, 28)
                widths = 1.2 + (t - 1.2) * np.sin(math.pi * s) ** 0.8
            else:
                s = np.linspace(0, 1, 40)
                xs = x0 + (x1 - x0) * s
                ys = cy + e0 + (e1 - e0) * s + m.get("amp", 0) * np.sin(
                    2 * math.pi * m.get("freq", 1) * s + m.get("phase", 0))
                axis = np.stack([xs, ys], axis=1)
                widths = np.full(40, t)
            axis = np.array([M(x, y) for x, y in axis])
            a, b, d, n = ribbon_sides(axis, widths * self.p["scale"])
            r_end = widths[-1] * self.p["scale"] / 2
            r_ini = widths[0] * self.p["scale"] / 2
            pts = list(a) + cap(axis[-1], r_end, d[-1], n[-1]) + list(b[::-1]) \
                + cap(axis[0], r_ini, -d[0], -n[0], 0, math.pi)
            for q in pts:
                self.note(*q)
            return poly_d(pts)
        if kind == "open":
            w, cx, cy = m.get("w", 40), m.get("cx", 100), m.get("cy", 56)
            depth, lip = m.get("depth", 20), m.get("lip", -3)
            sg = -1 if m.get("inv") else 1  # inv: arc facing up (open mouth, sad/screaming)
            x0, x1 = cx - w / 2, cx + w / 2
            n = 24
            pts = []
            # lower edge: curve that drops `depth`
            for tt in np.linspace(0, 1, n):
                x = x0 + (x1 - x0) * tt
                y = cy + sg * depth * (1 - (2 * tt - 1) ** 2) ** 0.75
                pts.append(M(x, y))
            # top edge: slight arc (lip<0 rises in the center)
            for tt in np.linspace(1, 0, n)[1:-1]:
                x = x0 + (x1 - x0) * tt
                y = cy + sg * lip * (1 - (2 * tt - 1) ** 2)
                pts.append(M(x, y))
            for q in pts:
                self.note(*q)
            return poly_d(pts)
        if kind == "oval":
            cx, cy, rx, ry, rot = m["cx"], m["cy"], m["rx"], m["ry"], m.get("rot", 0)
            pts = []
            for th in np.linspace(0, 2 * math.pi, 40, endpoint=False):
                x, y = rx * math.cos(th), ry * math.sin(th)
                xr = x * math.cos(rot) - y * math.sin(rot)
                yr = x * math.sin(rot) + y * math.cos(rot)
                pts.append(M(cx + xr, cy + yr))
            for q in pts:
                self.note(*q)
            return poly_d(pts)
        raise ValueError(kind)

    # arms --------------------------------------------------------------------
    def arm(self, spec, side):
        """Returns the points (on screen) that are inserted into the outline, from edge to edge."""
        if isinstance(spec, str):
            spec = ARMS[spec]
        sx = 1 if side == "r" else -1
        x_edge = BAR_R if side == "r" else BAR_L
        sh = np.array([x_edge, spec["ya"] + self.bar_dy(x_edge)], float)
        rel = [np.array([sx * dx, dy], float) for dx, dy in spec["pts"]]
        P = [sh] + [sh + r for r in rel]
        axis = bezier(P, 26)
        s = np.linspace(0, 1, len(axis))
        widths = spec["w0"] + (spec["w1"] - spec["w0"]) * s
        a, b, d, n = ribbon_sides(axis, widths)
        k = self.p["scale"]
        pts = list(a) + cap(axis[-1], widths[-1] / 2, d[-1], n[-1]) + list(b[::-1])
        pts = [self.G(x, y) for x, y in pts]
        for q in pts:
            self.note(*q)
        return pts

    # body --------------------------------------------------------------------
    def cuerpo(self):
        p = self.p
        s = p["spread"]
        T, G = self.T, self.G
        cmds = []  # list of ("M"|"L"|"Q", [points])

        def L(*pt):
            cmds.append(("L", [pt]))

        def Q(c, pt):
            cmds.append(("Q", [c, pt]))

        def arm_pts(spec, side):
            if spec is None:
                return
            for q in self.arm(spec, side):
                cmds.append(("L", [(float(q[0]), float(q[1]))]))

        start = T(20, 44)
        cmds.append(("M", [start]))
        Q(T(20, 30), T(34, 30))
        L(*T(166, 30))
        Q(T(180, 30), T(180, 44))
        arm_pts(p["arm_r"], "r")
        L(*T(180, 86))
        Q(T(180, 100), T(166, 100))
        kr, kl = math.radians(p["kick_r"]), math.radians(p["kick_l"])

        def legR(x, y):  # right leg, rotated kr (degrees) around the hip
            px, py = 145 + s, 100 + self.bar_dy(145 + s)
            dx, dy = x - px, y - py
            return G(px + dx * math.cos(kr) + dy * math.sin(kr), py - dx * math.sin(kr) + dy * math.cos(kr))

        def legL(x, y):  # left leg, turned kl outward (left)
            px, py = 55 - s, 100 + self.bar_dy(55 - s)
            dx, dy = x - px, y - py
            return G(px + dx * math.cos(kl) - dy * math.sin(kl), py + dx * math.sin(kl) + dy * math.cos(kl))

        yb = lambda x: 100 + self.bar_dy(x)
        body = p["body"]

        def legM(x, y):  # central leg (does not open or kick)
            return G(x, y)

        def middle_leg(half, toe):
            """Central leg from right to left, symmetric; `toe` = how far the foot sticks out."""
            xr, xl = 100 + half, 100 - half
            L(*legM(xr, yb(xr)))
            L(*legM(xr, 172))
            Q(legM(xr, 178), legM(xr + toe * 0.6, 180))
            L(*legM(xr + toe * 0.8, 181))
            Q(legM(xr + toe, 183), legM(xr + toe * 0.9, 190))
            L(*legM(xl - toe * 0.9, 190))
            Q(legM(xl - toe, 183), legM(xl - toe * 0.8, 181))
            L(*legM(xl - toe * 0.6, 180))
            Q(legM(xl, 178), legM(xl, 172))
            L(*legM(xl, yb(xl)))

        if body == "tau":
            middle_leg(15, 10)
        else:
            L(*legR(160 + s, yb(160 + s)))
            L(*legR(160 + s, 170))
            Q(legR(160 + s, 178), legR(168 + s, 180))
            L(*legR(174 + s, 182))
            Q(legR(180 + s, 184), legR(178 + s, 190))
            L(*legR(130 + s, 190))
            L(*legR(130 + s, yb(130 + s)))
            if body == "three":
                middle_leg(12, 6)
            L(*legL(70 - s, yb(70 - s)))
            L(*legL(70 - s, 190))
            L(*legL(22 - s, 190))
            Q(legL(20 - s, 184), legL(26 - s, 182))
            L(*legL(32 - s, 180))
            Q(legL(40 - s, 178), legL(40 - s, 170))
            L(*legL(40 - s, yb(40 - s)))
        L(*T(34, 100))
        Q(T(20, 100), T(20, 86))
        arm_pts(p["arm_l"], "l")
        # the left one goes along the edge upward: bottom side first (the listing already gives that)
        d = []
        for c, pts in cmds:
            for q in pts:
                self.note(*q)
            d.append(c + " " + (" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)))
        return "\n    ".join(d) + " Z"

    # assembled ------------------------------------------------------------------
    def svg6(self, nombre):
        ojos = self.eyes()
        (cl, rl, pl), (cr, rr, pr) = ojos
        cuerpo = self.cuerpo()
        boca = self.boca()
        c = lambda i, x, y, r, col: f'<circle id="{i}" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}"/>'
        partes = [
            c("ojo_izq", *cl, rl, "#ffffff"),
            c("ojo_der", *cr, rr, "#ffffff"),
            c("pupila_izq", *pl, rl * 0.375, "#000000"),
            c("pupila_der", *pr, rr * 0.375, "#000000"),
            f'<path id="cuerpo" fill="{COLOR_CUERPO}" d="\n    {cuerpo}"/>',
            f'<path id="boca" fill="#000000" d="{boca}"/>',
        ]
        return partes

    def escribir(self, nombre, prefijo="", dest=None):
        """Writes `<prefix><name>.svg` (12 parts) and, only without a prefix, `<name>_6partes.svg`."""
        dest = dest or OUT
        partes = self.svg6(nombre)
        cab = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               "<!-- Personaje original basado en la letra Pi mayuscula (no deriva del pi creature de 3Blue1Brown).\n"
               "     Generado por generar_expresiones.py (modo: %s). Formato de %s partes. -->\n"
               '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">\n')
        if not prefijo:
            (dest / f"{nombre}_6partes.svg").write_text(
                cab % (nombre, "6") + "\n".join("  " + x for x in partes) + "\n</svg>\n")
        # 12 parts: fills at 0, 1, 3, 4, 5 and 7. The first two are anchors that fix the frame (x
        # -40..240, y 8..190) so that scale and center do not change with the arms.
        fill = lambda x, y: f'<rect x="{x}" y="{y}" width="0.01" height="0.01" fill="none"/>'
        r = fill(100, 100)
        orden = [fill(-40, 8), fill(240, 190), partes[0], r, r, r, partes[1], r,
                 partes[2], partes[3], partes[4], partes[5]]
        (dest / f"{prefijo}{nombre}.svg").write_text(
            cab % (nombre, "12") + "\n".join("  " + x for x in orden) + "\n</svg>\n")
        b = self.bbox
        if b[0] < -40 or b[2] > 240 or b[1] < 6.5 or b[3] > 190.5:
            print(f"  AVISO {prefijo}{nombre}: se sale del cuadro pinzado: bbox={[round(v) for v in b]}")

    def escribir_tau(self, nombre, dest=None):
        """TauCreatures_<mode>.svg: format that `TauCreature` reads (it does not reorder the parts: init_structure is `pass`).
        Order: 0-1 eyes (white), 2-3 pupils (black, with the highlight as a hole), 4 body, 5 mouth, 6-7 invisible
        anchors (they fix the frame as in the Pi). With own colors, because SVGMobject keeps them;
        the scene uses tau[:4] (eyes, to blink) and tau[4] (body)."""
        dest = dest or OUT
        (cl, rl, pl), (cr, rr, pr) = self.eyes()
        cuerpo, boca = self.cuerpo(), self.boca()
        ojo = lambda c, r: f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{r:.1f}" fill="#ffffff"/>'

        def pupila(pu, r):
            rp = r * 0.4 * 1.15  # the hollow highlight needs somewhat more pupil than the PiCreature class (0.4)
            rd = rp * 0.3
            k = (rp - rd) * 0.72 * math.sqrt(0.5)  # highlight at the top left, inside the border
            hx, hy = pu[0] - k, pu[1] - k
            circ = lambda x, y, rad, sw: (f"M {x - rad:.2f},{y:.2f} A {rad:.2f} {rad:.2f} 0 1 {sw} {x + rad:.2f},{y:.2f} "
                                          f"A {rad:.2f} {rad:.2f} 0 1 {sw} {x - rad:.2f},{y:.2f} Z")
            return f'<path fill="#000000" d="{circ(pu[0], pu[1], rp, 0)} {circ(hx, hy, rd, 1)}"/>'

        fill = lambda x, y: f'<rect x="{x}" y="{y}" width="0.01" height="0.01" fill="none"/>'
        partes = [ojo(cl, rl), ojo(cr, rr), pupila(pl, rl), pupila(pr, rr),
                  f'<path fill="{AZUL}" d="\n    {cuerpo}"/>', f'<path fill="#000000" d="{boca}"/>',
                  fill(-40, 8), fill(240, 190)]
        cab = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               "<!-- Personaje original basado en la letra Tau mayuscula (no deriva del TauCreature de 3Blue1Brown).\n"
               "     Generado por generar_expresiones.py (modo: %s). Para TauCreature: ojos, pupilas, cuerpo, boca, 2 anclas. -->\n"
               '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">\n')
        (dest / f"TauCreatures_{nombre}.svg").write_text(
            cab % nombre + "\n".join("  " + x for x in partes) + "\n</svg>\n")


def escribir_variantes(dest=None):
    """Also writes all the expressions with the Tau body and with three legs, in `dest/tau` and `dest/tres_piernas`
    (TauCreatures_<mode>.svg for TauCreature and ThreeLeggedPiCreatures_<mode>.svg for ThreeLeggedPiCreature)."""
    dest = Path(dest or OUT)
    dt, d3 = dest / "tau", dest / "tres_piernas"
    dt.mkdir(exist_ok=True)
    d3.mkdir(exist_ok=True)
    for n, e in EXPRESIONES.items():
        e = EXPRESIONES[e] if isinstance(e, str) else e
        Fig({**e, "body": "tau"}).escribir_tau(n, dt)
        Fig({**e, "body": "three"}).escribir(n, "ThreeLeggedPiCreatures_", d3)


# ----------------------------------------------------------------------------- loose SVGs (SVGMobject, 6 parts, with their own color)
AZUL = "#1C758A"  # BLUE_E: the scene loads them with SVGMobject, so the color goes in the file


def espiral(cx, cy, r, vueltas=2.5, w=2.6, sentido=1):
    th = np.linspace(0, 2 * math.pi * vueltas, 70)
    rad = r * th / th[-1]
    axis = np.stack([cx + rad * np.cos(sentido * th), cy + rad * np.sin(sentido * th)], axis=1)
    a, b, d, n = ribbon_sides(axis, np.full(70, w))
    pts = list(a) + cap(axis[-1], w / 2, d[-1], n[-1]) + list(b[::-1]) + cap(axis[0], w / 2, -d[0], -n[0])
    return poly_d(pts)


def escribir_sueltos():
    d = OUT / "sueltos"
    d.mkdir(exist_ok=True)
    cab = ('<?xml version="1.0" encoding="UTF-8"?>\n<!-- Personaje original basado en la letra Pi mayuscula. Generado por '
           'generar_expresiones.py. SVG suelto de 6 partes (ojo izq, ojo der, pupila izq, pupila der, cuerpo, boca), '
           'con colores propios porque lo carga SVGMobject. -->\n'
           '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">\n')
    # EscherPiCreature: the "plain" character with colors
    f = Fig({})
    (cl, rl, pl), (cr, rr, pr) = f.eyes()
    c = lambda x, y, r, col: f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}"/>'
    partes = [c(*cl, rl, "#ffffff"), c(*cr, rr, "#ffffff"), c(*pl, rl * 0.375, "#000000"), c(*pr, rr * 0.375, "#000000"),
              f'<path fill="{AZUL}" d="\n    {f.cuerpo()}"/>', f'<path fill="#000000" d="{f.boca()}"/>']
    (d / "EscherPiCreature.svg").write_text(cab + "\n".join("  " + x for x in partes) + "\n</svg>\n")
    # pi_creature_dizzy: spiral pupils and wavy mouth, tilted body
    f = Fig(dict(tilt=5, lean=-3, spread=3, eye_cy=25, eye_r=16,
                 mouth=dict(kind="wavy", w=36, cx=100, cy=67, amp=3.2, freq=2.2, e0=1, e1=-1, t=5.5)))
    (cl, rl, pl), (cr, rr, pr) = f.eyes()
    partes = [c(*cl, rl, "#ffffff"), c(*cr, rr, "#ffffff"),
              f'<path fill="#000000" d="{espiral(cl[0], cl[1], rl * 0.72, sentido=1)}"/>',
              f'<path fill="#000000" d="{espiral(cr[0], cr[1], rr * 0.72, sentido=-1)}"/>',
              f'<path fill="{AZUL}" d="\n    {f.cuerpo()}"/>', f'<path fill="#000000" d="{f.boca()}"/>']
    (d / "pi_creature_dizzy.svg").write_text(cab + "\n".join("  " + x for x in partes) + "\n</svg>\n")


def main():
    nombres = sys.argv[1:] or list(EXPRESIONES)
    for n in nombres:
        e = EXPRESIONES[n]
        Fig(EXPRESIONES[e] if isinstance(e, str) else e).escribir(n)
    if not sys.argv[1:]:
        escribir_sueltos()
        escribir_variantes()
    print(f"{len(nombres)} expresiones escritas en {OUT}")


if __name__ == "__main__":
    main()
