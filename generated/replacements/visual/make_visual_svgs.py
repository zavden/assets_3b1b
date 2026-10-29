"""Own replacements (drawn by code) of 23 third-party SVGs. Each one is written with the same name
and in the same folder where the scene looks for it (_lib/assets/svg_images/), so the scenes do not change.

The originals were icons from Noun Project / onlinewebfonts / Illustrator of uncertain origin (or derived from
them): here they are drawn from scratch with the shapes of geom.py, respecting only what the code expects.

  computer_chip                   chip with pins, ring and core (the scene puts |Q> on top)
  cat_outline                     closed silhouette of a sitting cat (ONE single outline: it is extruded and projected)
  BinaryFunctionCircuit           board: two buses of tracks that go down to an integrated circuit and leave at the bottom
  Car                             car from the side; ONE <path> with 9 subpaths that custom/drawings.Car distributes:
                                  (0,1) right wheel (disk + hole), (2,3) left wheel, (4,6,7) body
                                  with two windows, (5) headlight, (8) taillight. Faces right.
  key                             key (ring with hole, shaft, collar and three teeth); used rotated 135 degrees
  push_pin                        tilted pushpin; the tip ends at the lower right
  hearts                          heart with border
  magnifying_glass2               magnifying glass: element 0 = ring+handle with the glass as subpath 1 (the scene extracts it
                                  with get_subpaths()[1]); element 1 = glass highlight
  light_bulb                      yellow light bulb: body, 5 rays and 3 bands of the base (9 parts)
  lightbulb                       "outline" light bulb made with filled shapes (the scene fills it white)
  earth                           globe: ring + schematic continents, square (the scene fits it to a circle)
  lock                            padlock: body, shackle and keyhole as holes
  person                          standing person: body + head (2 parts)
  virus                           virion of spikes with a bulb; subpath 0 is the outline (the scene isolates it)
  monster-holding-piece-sign-3    element 0: small circle; element 1: ONE closed outline of a furry monster
                                  holding a round sign (the scene draws that outline with
                                  Fourier circles)

  --- added by R9 (the three missing suits, the two crowns and three manimlib/_lib classes) ---
  clubs, diamonds,                 (custom/drawings.py: PlayingCard -> SuitSymbol(suit, height=card_height/7); 2020
  spades                            beta1::AskAboutUnknownProbabilities and beta2::FiniteVsContinuum). ONE <path> each,
                                  in the style of hearts: flat fill + darker border of the same tone (red
                                  for diamonds; exact black for clubs/spades, like the originals).
                                  Width/height proportions measured in the originals:"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geom import (Doc, K, P, Sub, capsule, circle, ellipse, poly, rchain, rpoly, rrect,  # noqa: E402
                  spline, thick_polyline)

OUT = Path(__file__).resolve().parents[3] / "svg_images"
PI = math.pi
D2R = math.radians


def dpt(c, r, deg):
    a = D2R(deg)
    return P(c[0] + r * math.cos(a), c[1] + r * math.sin(a))


# ---------------------------------------------------------------------------- chip

def computer_chip():
    x0, y0, x1, y1 = 18, 18, 82, 82
    n, pw, pl = 7, 5.0, 9.0
    pitch = (x1 - x0) / n
    pts, rad = [], []

    def corner(p):
        pts.append(p)
        rad.append(4.5)

    def edge_pins(a, b, outward):
        """Pins along the edge a->b (not including the corners)."""
        a, b = P(a), P(b)
        d = (b - a) / np.linalg.norm(b - a)
        for i in range(n):
            c = a + d * pitch * (i + 0.5)
            for p in (c - d * pw / 2, c - d * pw / 2 + outward * pl, c + d * pw / 2 + outward * pl, c + d * pw / 2):
                pts.append(p)
                rad.append(0.9 if np.dot(p - c, outward) > 0 else 0)

    corner((x0, y0))
    edge_pins((x0, y0), (x1, y0), P(0, -1))
    corner((x1, y0))
    edge_pins((x1, y0), (x1, y1), P(1, 0))
    corner((x1, y1))
    edge_pins((x1, y1), (x0, y1), P(0, 1))
    corner((x0, y1))
    edge_pins((x0, y1), (x0, y0), P(-1, 0))
    outer = rpoly(pts, rad)
    ring = rrect(x0 + 7, y0 + 7, 50, 50, 3, rev=True)
    die = rrect(x0 + 13, y0 + 13, 38, 38, 2.5)
    dots = [circle(x0 + 3.5 + dx, y0 + 3.5 + dy, 1.5, rev=True) for dx in (0, 57) for dy in (0, 57)]
    d = Doc("computer_chip: chip con pines (reemplazo propio)")
    d.add([outer, ring] + dots + [die])
    return d


# ---------------------------------------------------------------------------- circuit

def circuit():
    d = Doc("BinaryFunctionCircuit: placa con pistas (reemplazo propio)")
    w = 3.0
    pad_r, hole_r = 5.0, 2.4

    def pad(p):
        return [circle(p[0], p[1], pad_r), circle(p[0], p[1], hole_r, rev=True)]

    def track(points, w=w, end_pad=True, start_pad=True):
        pts = [P(p) for p in points]
        # the ends stop at the edge of the ring (the track ends at the center, under the ring)
        subs = [thick_polyline(pts, w)]
        if start_pad:
            subs += pad(pts[0])
        if end_pad:
            subs += pad(pts[-1])
        return subs

    # Integrated circuit
    ic = rrect(32, 50, 52, 22, 3)
    notch = circle(32, 61, 3.2, rev=True)
    d.add([ic, notch])

    for k in range(4):
        sx, xt = 6 + 12 * k, 36 + 6 * k
        dx = xt - sx
        d.add(track([(sx, 6), (sx, 14), (xt, 14 + dx), (xt, 51)], end_pad=False))
        d.add(track([(116 - sx, 6), (116 - sx, 14), (116 - xt, 14 + dx), (116 - xt, 51)], end_pad=False))
    outs = [(38, 18), (48, 38), (58, 58), (68, 78), (78, 98)]
    for x, xe in outs:
        dx = xe - x
        y0 = 76
        if abs(dx) >= 20:
            pts = [(x, 71), (x, y0), (xe, y0 + abs(dx))]
        else:
            pts = [(x, 71), (x, y0), (xe, y0 + abs(dx)), (xe, 94)]
        d.add(track(pts, start_pad=False))
    return d


# ---------------------------------------------------------------------------- car

def car():
    # working coordinates: width 194, height 98, facing right. At the end x is compressed (0.955) so the
    # proportion (~1.93) resembles the original; the wheels move but remain circles.
    R, ri = 18.0, 10.5
    wl, wr = (47, 80), (147, 80)
    arch = 22.0
    body = rchain([(3, 80), (3, 56), (9, 46), (30, 42), (62, 2), (116, 2), (150, 42), (186, 50), (192, 58), (192, 80)],
                  [0, 5, 6, 3, 6, 6, 4, 6, 6, 0])
    body.line((147 + arch, 80))
    body.arc((147, 80), arch, arch, 0, -PI)
    body.line((47 + arch, 80))
    body.arc((47, 80), arch, arch, 0, -PI)
    body.line((3, 80))
    win_rear = rpoly([(40, 39), (60, 11), (70, 11), (70, 39)], [1.5, 2, 2, 1.5], rev=True)
    win_front = rpoly([(77, 11), (111, 11), (134, 39), (77, 39)], [2, 2, 1.5, 1.5], rev=True)
    sx = 0.955
    squash = lambda sub: sub.scale(sx, 1.0)
    subs = [
        circle(wr[0] * sx, wr[1], R), circle(wr[0] * sx, wr[1], ri, rev=True),        # 0, 1 right wheel
        circle(wl[0] * sx, wl[1], R), circle(wl[0] * sx, wl[1], ri, rev=True),        # 2, 3 left wheel
        squash(body),                                                                 # 4 body
        squash(rrect(178, 56, 13, 9, 3)),                                             # 5 headlight
        squash(win_front),                                                            # 6 front window
        squash(win_rear),                                                             # 7 rear window
        squash(rrect(4, 57, 12, 8, 3)),                                               # 8 taillight
    ]
    d = Doc("Car: coche de lado (reemplazo propio). Un solo <path> con 9 subtrazos que usa custom/drawings.Car")
    d.add(subs, fill="#9aa0a6")
    return d


# ---------------------------------------------------------------------------- key

def key():
    c, r = (0.0, 16.0), 15.0
    hw = 3.5
    yj = c[1] + math.sqrt(r * r - hw * hw)
    th = math.asin(hw / r)
    # starts at the left junction of the ring with the rod and goes around the ring over the top
    s = Sub(P(c[0] + r * math.cos(PI - th), c[1] + r * math.sin(PI - th)))
    s.arc(c, r, r, PI - th, 2 * PI + th)
    right = [(hw, yj), (hw, 37), (6.5, 38), (6.5, 43), (hw, 44), (hw, 65),
             (11.5, 66), (11.5, 73), (hw, 74), (hw, 77), (9.5, 78), (9.5, 85), (hw, 86),
             (hw, 88), (12.5, 89), (12.5, 96), (hw, 97), (hw, 100)]
    rr = [0, 0, 1, 1, 0, 0, 1.2, 1.2, 0, 0, 1.2, 1.2, 0, 0, 1.2, 1.2, 0, 0]
    left = [(-hw, 100), (-hw, 44), (-6.5, 43), (-6.5, 38), (-hw, 37), (-hw, yj)]
    lr = [0, 0, 1, 1, 0, 0]
    s.join(rchain(right, rr))
    s.join(rchain(left, lr))
    hole = circle(c[0], c[1], 7.5, rev=True)
    d = Doc("key: llave (reemplazo propio)")
    d.add([s, hole])
    return d


# ---------------------------------------------------------------------------- pushpin

def push_pin():
    prof = [(-22, 0), (22, 0), (22, 12), (14, 15), (18, 38), (31, 41), (31, 50), (3, 50), (0, 100),
            (-3, 50), (-31, 50), (-31, 41), (-18, 38), (-14, 15), (-22, 12)]
    rad = [5, 5, 3, 2, 2, 2.5, 2.5, 0, 0, 0, 2.5, 2.5, 2, 2, 3]
    body = rpoly(prof, rad)
    slot = rpoly([(-8, 19), (-4.5, 19), (-5.5, 34), (-9, 34)], 1.2, rev=True)
    rim = rpoly([(-17, 3.5), (13, 3.5), (13, 6.5), (-17, 6.5)], 1.2, rev=True)
    subs = [body.rotate(-25), slot.rotate(-25), rim.rotate(-25)]
    d = Doc("push_pin: chincheta inclinada (reemplazo propio)")
    d.add(subs)
    return d


# ---------------------------------------------------------------------------- heart

def hearts():
    s = Sub((50, 96))
    s.cubic((22, 74), (2, 56), (2, 31))
    s.cubic((2, 14), (14, 2), (27, 2))
    s.cubic((38, 2), (46, 9), (50, 20))
    s.cubic((54, 9), (62, 2), (73, 2))
    s.cubic((86, 2), (98, 14), (98, 31))
    s.cubic((98, 56), (78, 74), (50, 96))
    d = Doc("hearts: corazon con borde (reemplazo propio)")
    d.add(s, fill="#e0383e", stroke="#9c1c24", sw=2.2)
    return d


# ---------------------------------------------------------------------------- magnifying glass

def magnifying_glass2():
    c = P(38, 38)
    Rr, r_in = 36.0, 28.0
    th = D2R(45)
    hw = 6.5
    phi = math.asin(hw / Rr)
    u = P(math.cos(th), math.sin(th))
    nrm = P(-math.sin(th), math.cos(th))
    a = Rr * math.cos(phi)
    L = 50.0
    s = Sub(c + Rr * P(math.cos(th + phi), math.sin(th + phi)))
    s.arc(c, Rr, Rr, th + phi, th + 2 * PI - phi)
    s.line(c + L * u - hw * nrm)
    s.arc(c + L * u, hw, hw, th - PI / 2, th + PI / 2)
    s.line(c + a * u + hw * nrm)
    lens = circle(c[0], c[1], r_in, rev=True)
    # highlight: curved band on the glass
    rg, hg = 20.0, 2.4
    a0, a1 = D2R(190), D2R(262)
    g = Sub(c + (rg + hg) * P(math.cos(a0), math.sin(a0)))
    g.arc(c, rg + hg, rg + hg, a0, a1)
    g.arc(c + rg * P(math.cos(a1), math.sin(a1)), hg, hg, a1, a1 + PI)
    g.arc(c, rg - hg, rg - hg, a1, a0)
    g.arc(c + rg * P(math.cos(a0), math.sin(a0)), hg, hg, a0 + PI, a0 + 2 * PI)
    d = Doc("magnifying_glass2: lupa (reemplazo propio). Elemento 0: contorno + cristal (subtrazo 1)")
    d.add([s, lens])
    d.add(g)
    return d


# ---------------------------------------------------------------------------- light bulbs

def bulb_outline(cx, cy, r, neck_w, neck_y, bottom_y):
    """Smooth outline of a light bulb (list of points, clockwise) and its corners."""
    pts = []
    for deg in np.linspace(-205, 25, 13):
        pts.append(dpt((cx, cy), r, deg))
    pts += [P(cx + neck_w * 1.15, cy + r * 1.0 + 4), P(cx + neck_w, neck_y), P(cx + neck_w, bottom_y),
            P(cx - neck_w, bottom_y), P(cx - neck_w, neck_y), P(cx - neck_w * 1.15, cy + r * 1.0 + 4)]
    n = len(pts)
    return pts, {n - 4, n - 3}


def light_bulb():
    cx, cy, r = 50, 52, 26
    pts, corners = bulb_outline(cx, cy, r, 11, 78, 80)
    body = spline(pts, corners=corners)
    d = Doc("light_bulb: bombilla amarilla (reemplazo propio)")
    yellow = "#ffd527"
    d.add(body, fill=yellow)
    # rays (angles measured from the vertical upward); the order is the original's: right, right down...
    for ang in (50, 14, 90, 130, 166):     # degrees, and upward
        p0 = P(cx + 36 * math.cos(D2R(ang)), cy - 36 * math.sin(D2R(ang)))
        p1 = P(cx + 47 * math.cos(D2R(ang)), cy - 47 * math.sin(D2R(ang)))
        d.add(capsule(p0, p1, 5.5), fill=yellow)
    for (w, y) in ((24, 85), (21, 91.5), (16, 98)):
        d.add(rrect(cx - w / 2, y, w, 5, 2.5), fill=yellow)
    return d


def lightbulb():
    cx, cy = 50, 46
    d = Doc("lightbulb: bombilla de contorno hecha con formas rellenas (reemplazo propio)")
    g = "#888888"
    ptsO, cO = bulb_outline(cx, cy, 25, 11.5, 76, 78)
    ptsI, cI = bulb_outline(cx, cy, 20.5, 7.2, 76, 74)
    d.add([spline(ptsO, corners=cO), spline(ptsI, corners=cI, rev=True)], fill=g)
    # base: two bands with a ring
    d.add([rrect(cx - 12, 82, 24, 7, 3), rrect(cx - 9.5, 84.4, 19, 2.2, 1, rev=True)], fill=g)
    d.add(rrect(cx - 7, 92, 14, 6, 3), fill=g)
    # filament
    fil = thick_polyline([(cx - 8, 70), (cx - 8, 56), (cx - 3, 46), (cx, 54), (cx + 3, 46), (cx + 8, 56), (cx + 8, 70)], 2.4)
    d.add(fil, fill=g)
    # rays
    for ang in (90, 55, 125, 20, 160, -15, 195):
        p0 = P(cx + 36 * math.cos(D2R(ang)), cy - 36 * math.sin(D2R(ang)))
        p1 = P(cx + 47 * math.cos(D2R(ang)), cy - 47 * math.sin(D2R(ang)))
        d.add(capsule(p0, p1, 4.2), fill=g)
    for ang in (-50, 230):
        p0 = P(cx + 32 * math.cos(D2R(ang)), cy - 32 * math.sin(D2R(ang)))
        p1 = P(cx + 40 * math.cos(D2R(ang)), cy - 40 * math.sin(D2R(ang)))
        d.add(capsule(p0, p1, 4.2), fill=g)
    return d


# ---------------------------------------------------------------------------- earth

def earth():
    c = (50, 50)
    ring = [circle(*c, 50), circle(*c, 45.5, rev=True)]
    cont = [
        # North America
        spline([(19, 30), (27, 22), (37, 20), (45, 24), (45, 32), (39, 39), (35, 46), (30, 44), (27, 37), (21, 36)]),
        # South America
        spline([(35, 52), (43, 55), (47, 64), (43, 75), (38, 83), (33, 76), (32, 64)]),
        # Africa
        spline([(57, 40), (67, 38), (75, 47), (71, 60), (65, 74), (59, 70), (55, 58), (54, 48)]),
        # Europa
        spline([(56, 25), (64, 21), (70, 25), (68, 31), (60, 33)]),
        # Asia (edge)
        spline([(73, 27), (82, 31), (85, 41), (78, 37), (72, 34)]),
        # isla
        spline([(78, 62), (84, 61), (85, 68), (79, 70)]),
        # Greenland
        spline([(48, 11), (56, 10), (55, 17), (49, 17)]),
    ]
    d = Doc("earth: globo con continentes esquematicos (reemplazo propio)")
    d.add(ring + cont)
    return d


# ---------------------------------------------------------------------------- padlock

def lock():
    sh = Sub((12, 22)).arc((34, 22), 22, 22, PI, 2 * PI)
    sh.line((56, 40))
    sh.join(rchain([(56, 40), (68, 40), (68, 100), (0, 100), (0, 40), (12, 40)], [0, 6, 6, 6, 6, 0]))
    opening = Sub((22, 40)).line((22, 22))
    opening.arc((34, 22), 12, 12, PI, 2 * PI)
    opening.line((46, 40))
    opening = opening.reversed()
    cx, cy, rk = 34, 62, 6.5
    th = math.atan2(math.sqrt(rk * rk - 2.7 ** 2), -2.7)
    kh = Sub(P(cx + rk * math.cos(th), cy + rk * math.sin(th)))
    kh.arc((cx, cy), rk, rk, th, 2 * PI + math.atan2(math.sqrt(rk * rk - 2.7 ** 2), 2.7))
    kh.line((cx + 4.4, 84))
    kh.line((cx - 4.4, 84))
    d = Doc("lock: candado (reemplazo propio)")
    d.add([sh, opening, kh.reversed()])
    return d


# ---------------------------------------------------------------------------- persona

def person():
    W = 43.5
    body = [(14, 25), (29.5, 25), (38.5, 27), (43.5, 34), (43.5, 66), (35.5, 66), (35.5, 42), (33.1, 42),
            (33.1, 100), (22.9, 100), (22.9, 70), (20.6, 70), (20.6, 100), (10.4, 100), (10.4, 42), (8, 42),
            (8, 66), (0, 66), (0, 34), (5, 27)]
    rad = [0, 0, 4, 4, 2.5, 2.5, 0, 0, 2.5, 2.5, 0, 0, 2.5, 2.5, 0, 0, 2.5, 2.5, 4, 4]
    d = Doc("person: persona de pie (reemplazo propio)")
    d.add(rpoly(body, rad))
    d.add(circle(W / 2, 11, 11))
    return d


# ---------------------------------------------------------------------------- virus

def virus():
    cx = cy = 50.0
    Rb, D, rb, w = 30.0, 44.0, 6.0, 2.3
    n = 10
    s = None
    eps = math.asin(w / Rb)
    ab = math.sqrt(Rb * Rb - w * w)
    sb = math.sqrt(rb * rb - w * w)
    dl = math.asin(w / rb)
    for i in range(n):
        al = -PI / 2 + 2 * PI * i / n
        u = P(math.cos(al), math.sin(al))
        v = P(-math.sin(al), math.cos(al))
        c = P(cx, cy)
        b1 = c + ab * u - w * v
        t1 = c + (D - sb) * u - w * v
        cb = c + D * u
        if s is None:
            s = Sub(b1)
        s.line(t1)
        s.arc(cb, rb, rb, al - PI + dl, al + PI - dl)
        s.line(c + ab * u + w * v)
        al2 = -PI / 2 + 2 * PI * (i + 1) / n
        s.arc(c, Rb, Rb, al + eps, al2 - eps)
    dots = [circle(43, 46, 3.4, rev=True), circle(57, 42, 2.7, rev=True), circle(54, 57, 2.1, rev=True)]
    d = Doc("virus: virion con espinas (reemplazo propio). El subtrazo 0 es el contorno exterior")
    d.add([s] + dots)
    return d


# ---------------------------------------------------------------------------- cat

def cat_outline():
    # silhouette of a cat sitting in profile, facing right; tail curled to the left. ONE outline.
    pts = [
        (55, 2),    # 0 tip of the left ear (corner)
        (64, 12),   # 1 valley between ears
        (79, 1),    # 2 tip of the right ear (corner)
        (82, 14),   # 3
        (87, 22),   # 4 forehead
        (92, 28),   # 5 snout
        (89, 32),   # 6 mouth
        (84, 36),   # 7 chin / jowl
        (79, 42),   # 8 front of the neck
        (79, 52),   # 9 chest
        (82, 63),   # 10
        (81, 78),   # 11 front leg
        (84, 91),   # 12 paw
        (89, 97),   # 13
        (85, 99),   # 14 lower right corner
        (62, 99),   # 15 base
        (40, 99),   # 16
        (24, 98),   # 17 start of the tail
        (10, 96),   # 18
        (3, 86),    # 19 tail lower-left
        (2, 72),    # 20
        (5, 58),    # 21
        (10, 48),   # 22 tip of the tail
        (16, 51),   # 23 inner face of the tail
        (12, 61),   # 24
        (13, 74),   # 25
        (20, 87),   # 26
        (22, 74),   # 27 hip
        (28, 58),   # 28 back
        (36, 41),   # 29
        (44, 28),   # 30 nape
        (49, 14),   # 31
    ]
    s = spline(pts, corners={0, 2, 14})
    d = Doc("cat_outline: gato sentado (reemplazo propio). Un solo contorno cerrado")
    d.add(s)
    return d


# ---------------------------------------------------------------------------- monster

def monster():
    """Outline of a furry monster holding a round sign, obtained from the union of shapes (rasterized
    and vectorized with OpenCV) and with jagged fur. A single closed outline."""
    import cv2
    from PIL import Image, ImageDraw

    S = 1600
    sc = S / 100.0
    im = Image.new("L", (S, S), 0)
    dr = ImageDraw.Draw(im)

    def E(cx, cy, rx, ry):
        dr.ellipse([(cx - rx) * sc, (cy - ry) * sc, (cx + rx) * sc, (cy + ry) * sc], fill=255)

    def Pg(pts):
        dr.polygon([(x * sc, y * sc) for x, y in pts], fill=255)

    def Cap(p0, p1, w):
        dr.line([(p0[0] * sc, p0[1] * sc), (p1[0] * sc, p1[1] * sc)], fill=255, width=int(w * sc))
        E(p0[0], p0[1], w / 2, w / 2)
        E(p1[0], p1[1], w / 2, w / 2)

    E(46, 64, 25, 26)                       # body
    E(46, 28, 15, 15)                       # head
    Pg([(31, 22), (27, 3), (42, 15)])       # left horn
    Pg([(61, 22), (65, 3), (50, 15)])       # right horn
    Cap((25, 52), (14, 80), 11)             # left arm
    Cap((67, 52), (80, 35), 11)             # raised right arm
    E(82, 31, 6.5, 6.5)                     # hand
    Cap((83, 31), (85, 11), 2.8)            # sign pole
    E(86, 10, 9, 9)                         # round sign
    E(36, 91, 11, 6)                        # left foot
    E(57, 91, 11, 6)                        # right foot
    a = np.array(im)
    a = cv2.GaussianBlur(a, (0, 0), 3)
    a = (a > 127).astype(np.uint8) * 255
    cnts, _ = cv2.findContours(a, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)[:, 0, :].astype(float)
    # resample at a constant step and jag the skin (fur) outward
    seg = np.linalg.norm(np.diff(np.vstack([c, c[:1]]), axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    total = cum[-1]
    step = 34.0
    m = int(total / step)
    t = np.linspace(0, total, m, endpoint=False)
    px = np.interp(t, cum, np.append(c[:, 0], c[0, 0]))
    py = np.interp(t, cum, np.append(c[:, 1], c[0, 1]))
    pts = np.stack([px, py], axis=1)
    # outward normals
    tang = np.roll(pts, -2, axis=0) - np.roll(pts, 2, axis=0)
    nrm = np.stack([tang[:, 1], -tang[:, 0]], axis=1)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
    centre = pts.mean(axis=0)
    if np.mean(np.sum(nrm * (pts - centre), axis=1)) < 0:
        nrm = -nrm
    rng = np.random.default_rng(7)
    amp = np.where(np.arange(m) % 2 == 0, 22.0, -3.0) * (0.7 + 0.6 * rng.random(m))
    xs, ys = pts[:, 0] / sc, pts[:, 1] / sc
    smooth = (xs > 74) & (ys < 27)          # the sign and the upper part of the pole are smooth
    smooth |= (ys < 16)                     # and the tips of the horns
    amp[smooth] = 0.0
    pts = pts + nrm * amp[:, None]
    pts = pts / sc
    d = Doc("monster-holding-piece-sign-3: monstruo peludo con un cartel (reemplazo propio). "
            "Elemento 0: circulo; elemento 1: contorno cerrado")
    d.add(circle(90, 62, 3.2), fill="none", stroke="#000000", sw=0.8)
    d.add(poly([tuple(p) for p in pts]), fill="none", stroke="#000000", sw=0.8)
    return d


# ---------------------------------------------------------------------------- utilities (suits, crowns, cloud)

def sample(sub, n=24):
    """Dense points of a Sub (to measure tight boxes)."""
    pts = [sub.start]
    for sg in sub.segs:
        if sg[0] == "L":
            pts.append(sg[1])
        else:
            p0, c1, c2, p1 = pts[-1], sg[1], sg[2], sg[3]
            for k in range(1, n + 1):
                t = k / n
                u = 1 - t
                pts.append(u ** 3 * p0 + 3 * u * u * t * c1 + 3 * u * t * t * c2 + t ** 3 * p1)
    return np.array(pts)


def fit(subs, x0, y0, x1, y1):
    """Takes the set of subpaths (non-uniform scale + translation) to the box [x0,x1]x[y0,y1]."""
    pts = np.vstack([sample(s) for s in subs])
    ax, ay = pts[:, 0].min(), pts[:, 1].min()
    bx, by = pts[:, 0].max(), pts[:, 1].max()
    sx, sy = (x1 - x0) / (bx - ax), (y1 - y0) / (by - ay)
    return [s.map(lambda p: P(x0 + (p[0] - ax) * sx, y0 + (p[1] - ay) * sy)) for s in subs]


def mirror_outline(start, half, cx):
    """Outline symmetric about the vertical x=cx. `half`: segments ('L', p) / ('C', c1, c2, p) of the left
    half, from `start` (on the axis) to an end point also on the axis. Returns the closed Sub."""
    s = Sub(start)
    pts = [P(start)]
    for sg in half:
        if sg[0] == "L":
            s.line(sg[1])
        else:
            s.cubic(sg[1], sg[2], sg[3])
        pts.append(P(sg[-1]))
    for i in range(len(half) - 1, -1, -1):
        sg, back = half[i], pts[i]
        mx = lambda p: P(2 * cx - p[0], p[1])  # noqa: E731
        if sg[0] == "L":
            s.line(mx(back))
        else:
            s.cubic(mx(sg[2]), mx(sg[1]), mx(back))
    return s


def circle_hits(c0, r0, c1, r1):
    """The two intersection points of two circles."""
    c0, c1 = P(c0), P(c1)
    d = np.linalg.norm(c1 - c0)
    a = (r0 * r0 - r1 * r1 + d * d) / (2 * d)
    h = math.sqrt(max(r0 * r0 - a * a, 0.0))
    m = c0 + (c1 - c0) * a / d
    n = np.array([-(c1 - c0)[1], (c1 - c0)[0]]) / d
    return m + n * h, m - n * h


def ang(c, p):
    return math.atan2(p[1] - c[1], p[0] - c[0])


def on_circle(c, r, a):
    return P(c[0] + r * math.cos(a), c[1] + r * math.sin(a))


# ---------------------------------------------------------------------------- suits of the deck

SUIT_RED = dict(fill="#e0383e", stroke="#9c1c24", sw=2.2)     # the same style as hearts
SUIT_BLACK = dict(fill="#000000", stroke="#000000", sw=2.2)   # exact black (there is no darker tone)


def diamonds():
    # diamond with slightly concave sides; width/height ratio = 0.79 (the original 0.796)
    cx, hw, ym = 40.0, 38.0, 50.0
    half = [("C", (cx - 6, 22), (cx - hw + 5, ym - 12), (cx - hw, ym)),
            ("C", (cx - hw + 5, ym + 12), (cx - 6, 78), (cx, 98))]
    d = Doc("diamonds: rombo con borde (reemplazo propio, mismo estilo que hearts)")
    d.add(mirror_outline((cx, 2), half, cx), **SUIT_RED)
    return d


def spades():
    # tip at the top, two rounded lobes, neck and wide foot; ratio 0.79 (the original 0.791)
    cx = 40.0
    half = [("C", (34, 20), (2.3, 38), (1.8, 60)),            # left flank to the widest point
            ("C", (1.8, 75), (12, 85), (25, 85)),           # base of the lobe
            ("C", (31, 85), (36, 82), (37.5, 78.5)),      # goes up toward the neck (reentrant corner)
            ("C", (37, 90), (33, 96), (22, 98.5)),        # the neck goes down and opens into the foot
            ("L", (cx, 98.5))]
    d = Doc("spades: pica con borde (reemplazo propio, mismo estilo que hearts)")
    d.add(mirror_outline((cx, 2), half, cx), **SUIT_BLACK)
    return d


def clubs():
    # three lobes (circles of equal radius) joined at the center and a foot; width/height = 1.08 (the original 1.085)
    r = 21.5
    T, L, R = P(50, 23.5), P(23.5, 55.5), P(76.5, 55.5)
    mid = (T + L + R) / 3

    def outer(c0, c1):                   # the cut of two circles that falls outside the clover
        a, b = circle_hits(c0, r, c1, r)
        return a if np.linalg.norm(a - mid) > np.linalg.norm(b - mid) else b

    p_tl, p_tr = outer(T, L), outer(T, R)
    a_stem = math.radians(163)           # where the foot leaves the right lobe
    pr = on_circle(R, r, a_stem)
    pl = P(100 - pr[0], pr[1])
    up = lambda a, ref: a + 2 * PI * math.ceil((ref - a) / (2 * PI))  # noqa: E731  (a >= ref)
    s = Sub(p_tl)
    s.arc(T, r, r, ang(T, p_tl), up(ang(T, p_tr), ang(T, p_tl)))          # top lobe, over the top
    a0 = ang(R, p_tr)
    s.arc(R, r, r, a0, up(a_stem, a0))                                    # right: right, bottom, down to the foot
    s.cubic(pr + P(-1.0, 12), P(54.2, 81), P(65, 90.5))                     # foot, right side
    s.cubic(P(57, 87.6), P(43, 87.6), P(34, 90.5))                        # slightly arched base
    s.cubic(P(45.8, 81), pl + P(1.0, 12), pl)                             # foot, left side
    b0 = ang(L, pl)
    s.arc(L, r, r, b0, up(ang(L, p_tl), b0))                              # left: bottom, left, top
    d = Doc("clubs: trebol con borde (reemplazo propio, mismo estilo que hearts)")
    d.add(s, **SUIT_BLACK)
    return d


# ---------------------------------------------------------------------------- crowns (face cards of the deck)

def king_crown():
    # five points with balls joined to the band (ONE piece); the central one taller and with a bigger ball
    bead = [4.2, 4.6, 7.2, 4.6, 4.2]
    tx = [4, 26, 50, 74, 96]
    ty = [24, 17, 6.5, 17, 24]
    neck = 2.0
    pts = []
    for x, y, r in zip(tx, ty, bead):
        k = math.asin(neck / r)
        pts.append((P(x, y), r, PI / 2 + k, PI / 2 - k + 2 * PI))   # from one side of the neck to the other over the top
    c0, r0, a00, a01 = pts[0]
    s = Sub(P(0, 40))
    s.cubic(P(0, 36), P(c0[0] - 1.5, on_circle(c0, r0, a00)[1] + 8), on_circle(c0, r0, a00))
    s.arc(c0, r0, r0, a00, a01)
    e = on_circle(c0, r0, a01)
    valleys = [P(15, 41), P(38, 37), P(62, 37), P(85, 41)]
    for i in range(1, 5):
        c, r, a0, a1 = pts[i]
        st = on_circle(c, r, a0)
        v = valleys[i - 1]
        s.cubic(e + P(0.5, 8), v + P(-5, 0), v)              # hollow valley between one neck and the next
        s.cubic(v + P(5, 0), st + P(-0.5, 8), st)
        s.arc(c, r, r, a0, a1)
        e = on_circle(c, r, a1)
    s.cubic(e + P(1.5, 8), P(100, 36), P(100, 40))
    s.cubic(P(86, 59), P(66, 64), P(50, 64))                 # arched lower band
    s.cubic(P(34, 64), P(14, 59), P(0, 40))
    d = Doc("king_crown: corona de rey, una pieza (reemplazo propio)")
    d.add(s, fill="#000000")
    return d


def queen_crown():
    # five sharp points with hollow curves between them and five LOOSE balls on top: 6 subpaths, [0] = crown
    tips = [(2, 20), (26, 12), (50, 5), (74, 12), (98, 20)]
    vals = [(14, 48), (38, 44), (62, 44), (86, 48)]
    pts = [(10, 62)]                    # lower left corner
    corners = [0]
    for i, t in enumerate(tips):
        pts.append(t)
        corners.append(len(pts) - 1)
        if i < 4:
            pts.append(vals[i])
    pts.append((90, 62))
    corners.append(len(pts) - 1)
    pts.append((50, 70))                # center of the lower (arched) band
    body = spline(pts, corners=corners)
    beads = [circle(x, y - 6.5, 3.6) for x, y in tips]
    d = Doc("queen_crown: corona de reina, cuerpo + 5 bolas sueltas (reemplazo propio)")
    d.add([body] + beads, fill="#000000")
    return d


# ---------------------------------------------------------------------------- thought bubble

def scallop(pts, k=0.42):
    """Cloud: arcs outward between consecutive points (clockwise on screen), with the cusp inward."""
    pts = [P(p) for p in pts]
    n = len(pts)
    s = None
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        c = np.linalg.norm(b - a)
        dvec = (b - a) / c
        out = np.array([dvec[1], -dvec[0]])         # outer normal (clockwise with y down)
        sag = k * c
        R = (c * c / 4 + sag * sag) / (2 * sag)
        cen = (a + b) / 2 - out * (R - sag)
        half = math.asin(min(c / (2 * R), 1.0))
        a0 = ang(cen, a)
        if s is None:
            s = Sub(a)
        s.arc(cen, R, R, a0, a0 + 2 * half)
    return s


def bubbles_thought():
    # [0..2] three circles of the tail (large -> small, down to the left) and [3] the cloud, outline only
    base = [(0, -1.0), (0.45, -0.95), (0.9, -0.62), (0.97, -0.05), (0.62, 0.52), (0.0, 0.78),
            (-0.62, 0.55), (-0.97, -0.08), (-0.82, -0.62), (-0.42, -0.95)]
    base = [P(0.0 + 78 * x, 0.0 + 66 * y) for x, y in base]
    cloud = scallop(base, 0.40)
    # proportions measured in the original: cloud 1.683 x 1.405, center (+0.02, +0.30) with respect to the
    # whole, which is 1.719 x 2.0 (height = 2); tail: three circles of diameter 0.277, 0.162, 0.086 down to the
    # left
    u = 100.0
    cloud = fit([cloud], (0.02 - 0.8415) * u, (-0.30 - 0.7025) * u, (0.02 + 0.8415) * u, (-0.30 + 0.7025) * u)[0]
    tail = [circle(-0.43 * u, 0.55 * u, 0.1385 * u), circle(-0.63 * u, 0.83 * u, 0.081 * u),
            circle(-0.82 * u, 0.96 * u, 0.043 * u)]
    d = Doc("Bubbles_thought: nube de pensamiento (contorno) + 3 circulos de cola (reemplazo propio). "
            "Elementos: [0] circulo medio, [1] pequeno, [2] diminuto, [3] nube")
    for c in tail:
        d.add(c, fill="none", stroke="#000000", sw=1.0)
    d.add(cloud, fill="none", stroke="#000000", sw=1.0)
    return d


# ---------------------------------------------------------------------------- video icon

def video_icon():
    # [0] rounded frame (outer outline + hole), [1] "play" triangle slightly to the right of center
    outer = rrect(0, 0, 384, 273, 44)
    inner = rrect(17, 17, 350, 239, 30, rev=True)
    tri = rpoly([(156, 83), (156, 186), (250, 134.5)], 6)
    d = Doc("video_icon: marco de pantalla con triangulo de play (reemplazo propio). [0] marco, [1] triangulo")
    d.add([outer, inner], fill="#000000")
    d.add(tri, fill="#000000")
    return d


# ---------------------------------------------------------------------------- faro

def lighthouse():
    # 0: outline lighthouse (tower, gallery, lantern, dome and base) and 1-4: windows (the door first), pills
    subs = [
        circle(0, 3, 2.4),                                           # finial
        Sub((-9.5, 16)).arc((0, 16), 9.5, 10, PI, 2 * PI),           # dome
        rrect(-8, 16, 16, 16, 2), rrect(-4.8, 19.6, 9.6, 12.4, 3, rev=True),    # lantern (with window)
        rrect(-19, 32, 38, 4, 1.6),                                  # gallery platform
        rrect(-14, 36, 28, 8, 1.2), rrect(-11, 38.6, 22, 5.4, 0.8, rev=True),   # railing
        poly([(-13, 44), (13, 44), (21, 96), (-21, 96)]),            # tower: outer outline...
        poly([(-9.6, 47.4), (9.6, 47.4), (17.2, 91), (-17.2, 91)], rev=True),   # ...and hole
        rrect(-26.5, 94, 53, 6, 2),                                  # base
    ]
    win = [capsule((0, 81.25), (0, 85.75), 3.0)] + [capsule((0, y - 1.45), (0, y + 1.45), 3.0)
                                                       for y in (73.0, 63.5, 54.0)]
    d = Doc("lighthouse: faro de contorno con 4 ventanas (reemplazo propio). [0] cuerpo, [1] puerta, [2..4] ventanas")
    d.add(subs, fill="#ffffff")           # white, like the original (Lighthouse sets fill_color WHITE)
    for w in win:
        d.add(w, fill="#ffffff")
    return d


ICONS = {
    "computer_chip": computer_chip,
    "cat_outline": cat_outline,
    "BinaryFunctionCircuit": circuit,
    "Car": car,
    "key": key,
    "push_pin": push_pin,
    "hearts": hearts,
    "magnifying_glass2": magnifying_glass2,
    "light_bulb": light_bulb,
    "lightbulb": lightbulb,
    "earth": earth,
    "lock": lock,
    "person": person,
    "virus": virus,
    "monster-holding-piece-sign-3": monster,
    "diamonds": diamonds,
    "spades": spades,
    "clubs": clubs,
    "king_crown": king_crown,
    "queen_crown": queen_crown,
    "Bubbles_thought": bubbles_thought,
    "video_icon": video_icon,
    "lighthouse": lighthouse,
}


def main():
    names = sys.argv[1:] or list(ICONS)
    OUT.mkdir(parents=True, exist_ok=True)
    for name in names:
        ICONS[name]().write(OUT / f"{name}.svg")
        print("escrito", OUT / f"{name}.svg")


if __name__ == "__main__":
    main()
