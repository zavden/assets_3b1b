"""Own replacements (drawn by code) of 23 SVGs and 3 PNGs from the `assets/` folder of 3b1b/videos (deleted from the
repo by Grant, so they cannot be redistributed). Each one is written with the same name and in the same folder
where the scene looks for it (_lib/assets/svg_images/ and _lib/assets/raster_images/), so the scenes do not change.
Everything comes from primitives (rounded rectangles, ellipses, polygons, thick strokes, splines) of geom.py;
the organic shapes (cats, monster, pangolin, snowflake...) are built as union/subtraction of primitives and passed through
`merge()`, which turns them into clean outlines (with their holes). No original was traced or vectorized.

What each scene expects (and how it is met). `n` = number of <path> elements = len(SVGMobject.submobjects):

  alien              (monster::IntroduceMonsterSize) set_height(3), fill GREEN_E, DrawBorderThenFill. n=2: [0] body
                     with spikes, arms/legs and an eye hole; [1] pupil.
  beer               (telestration_contribution::TelestrationContribution) beer[0] GREY_C = mug (body, handle, with
                     an empty interior), beer[1] WHITE = foam, beer[2] #ff9900 = beer. n=3, order = layers.
  clipboard          (med_test, 14 scenes; get_covid_clipboard) set_width(2.5), a single color, the text is centered
                     (shifted 0.1-0.2 down) on the board at 70 % of the width. n=2: [0] double frame of the board,
                     [1] top clip (with a hole). The interior is left empty for the text.
  factory            (beta/beta1::RunCarFactory) factory[0] is ONE path; it is flipped (flip) and placed at the left edge,
                     height 6; a rectangle 1.1 tall x 6.75 wide covers the lower strip (cars). n=1:
                     sawtooth roof on the left, three chimneys on the right, windows as holes.
  fat_cat            (TelestrationContribution) cat.flip(), fill GREY_C. n=1: fat cat sitting in profile (faces
                     left, tail on the right), closed eyes/whiskers/belly as holes.
  sitting_cat        (TelestrationContribution) n=1: silhouette of a cat sitting in profile, long tail on the left.
  female_doctor      (med_test: LearnAboutPositiveResult, ConfusedByFPR, GigerenzerSession) the scene does
  male_doctor        doc.remove(doc[0]), set_height(3), a SINGLE color (GREY_B/C) and gloss: after removing [0] a bust
                     of a female/male doctor must be visible. With a uniform color the details are only visible if they are gaps, so
                     face/hair/coat/stethoscope are separated by slits. female n=5: [0] ring (removed), [1] hair,
                     [2] face+neck, [3] coat (stethoscope as a slit), [4] stethoscope piece.
                     male n=6: [0] ring, [1] hair, [2] face+neck with glasses (slits), [3] ears (2), [4] coat,
                     [5] stethoscope piece.
  lightning_bolt     (hamming, 12 scenes; zap_anim) bolt[0].add_line_to(start): n=1, ONE closed subpath. It is
                     filled RED_B and the outline is drawn (ShowCreation); GrowFromPoint from the UR corner.
  like               (TelestrationContribution) 3 copies, fill BLUE, width = the article's width. n=1: thumbs up
                     (sleeve with a hole + hand) and a heart; 4 subpaths.
  monster            (monster, 9 scenes) n=1, ONE path. The scenes look for the eyes with
                     get_subpath_end_indices_from_points: two small subpaths (width < 10 % of the total width) in the
                     upper half, ordered by x, and squash them in y (blink). Here: outline + 2 eyes (circles,
                     holes) + smile (wide hole: does not count as an eye). No other small subpath at the top.
  muscle             (TelestrationContribution) fill GREY_BROWN, white stroke 2. n=1: the classic "strength" icon:
                     vertical forearm with the fist on top (3 finger slits), elbow at the bottom left, horizontal upper
                     arm with the bulging biceps (curved slit at the top). Outline of hand-made Bezier
                     curves + 4 slits (holes) as subpaths; the slits look like white lines.
  pangolin           (sir::SubtlePangolin) height 0.5, no fill, GREY_BROWN stroke 1, ShowCreationThenFadeOut. Only
                     the outline is visible. n=1: pangolin walking in profile, facing left: long snout that
                     narrows, arched back, thick tail that narrows and rises at the tip, four short legs with
                     claws. Closed outline + eye (hole) + ~250 scales as open arcs (UNclosed subpaths,
                     in a "shingle" tiling that follows the back and tail and shrinks toward the tip).
  punchcard          (hamming::HammingAtBell) punchcard.remove(*punchcard[23:]); [0] gets a FadeIn and [1:] a Write
                     with lag; from [1:] 4 "bits" are sampled that are squashed (stretch 0.2) or shifted 1.2
                     times their width to the left. n=23: [0] card frame (cut corner), [1..22] 22
                     equal rectangles (punches) in 3 rows (7+8+7) in reading order.
  server_stack       (monster::IntroduceMonsterSize, hamming::SenderReceiverDynamic) fill GREY, stroke BLACK 2,
                     set_gloss, set_height(3). n=5: [0] top cover, [1..4] four modules with 3 LEDs (holes).
  woman_icon         (med_test: WomanIcon in 11 scenes) remove(self[0]), fill GREY_B, set_height(0.5), 1000
                     copies in a grid. n=3: [0] white background square (removed), [1] head, [2] body/dress.
  woman              (not used directly in the scenes) n=2: [0] bust, [1] blouse collar.
  PenroseTriangle    (med_test::AskIfItsAParadox) remove(p[0]); then CurvesAsSubmobjects(p_triangle[0]) with
                     set_fill(opacity=0), stroke GREY_B 3, ShowCreation. n=2: [0] white square (removed), [1] the
                     impossible triangle as outlines of the visible faces of three beams (isometric render with
                     occlusion; the final beam covers the start of the first).
  symmetry_ambigram  (monster::IntroduceGroupTheory) fill BLUE, match_width(title), Write, 20 % ghost copy,
                     Rotate(PI): must coincide with itself rotated 180 degrees. n=8. SIMPLIFICATION: a real
                     "symmetry" ambigram (s<->y, y<->r, m<->t, m<->e) is not feasible by code; "symm" is written in
                     stroke letters and the second half is the first rotated 180 degrees: the whole figure is
                     exactly rotationally symmetric (what the scene needs) but the right half does not read
                     "etry".
  robot              (hamming, 9 scenes; bayes/part1::StateGoal) set_color(GREY), gloss, set_height(0.5-1.5),
                     no indices. n=4: [0] antenna, [1] head (ring), [2] eyes and mouth, [3] ears (2).
  snowflake          (monster, 5 scenes and _2017/mug) fill GREY_C, stroke WHITE 1, gloss, shadow; it is rotated 60 degrees and
                     flipped: D6 symmetry (six identical arms). n=2: [0] snowflake (with a central hexagonal gap),
                     [1] central hexagon.
  apple_logo         (ctracing::AppleGoogleCoop) set_color("#b3b3b3"), set_height(2) next to google_logo_black.
                     Own emblem: isometric cube (3 rhombi with slits). n=1, 3 subpaths. It is NOT an apple.
  BellSystemLogo     svg + png (hamming::HammingAtBell): ImageMobject and SVGMobject with match_height/move_to, so they
                     coincide: the outline covers the whole image. Own emblem: octagonal badge with a network
                     (central hexagonal node joined to three nodes). No bell, no text, no circle.

PNG (in raster_images/):
  BellSystemLogo.png    1234x1236 RGB: the same drawing as the SVG (the same document is rasterized); outside, black.
  google_logo_black.png 2224x2268 RGB: three overlapping ellipses (teal, orange, violet) over black, full
                        bleed. Own emblem; it is not a G.
  doctor_pair.png       1022x676 RGBA: composite with the figures of female_doctor (in front, dark coat,
                        light stethoscope) and male_doctor (behind, light tones), on a transparent background.

Usage: python make_visual_svgs_2020.py [name ...]     (without arguments it generates all 26)"""
import math
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geom import Doc, P, Sub, circle, ellipse, poly, rpoly, rrect, spline  # noqa: E402

SVG_OUT = Path(__file__).resolve().parents[3] / "svg_images"
PNG_OUT = Path(__file__).resolve().parents[3] / "raster_images"
# SVGs hand-made by Codex (CC0) that surpass the drawing by code: if one with the same name exists, that one is copied
CODEX_SVG = Path(__file__).resolve().parents[1] / "codex" / "entregas" / "2020"
D2R = math.radians


# ------------------------------------------------------------------ geometric utilities

def flat(sub, n=14):
    pts = [sub.start]
    for s in sub.segs:
        if s[0] == "L":
            pts.append(s[1])
        else:
            p0, c1, c2, p1 = pts[-1], s[1], s[2], s[3]
            for k in range(1, n + 1):
                t = k / n
                u = 1 - t
                pts.append(u ** 3 * p0 + 3 * u * u * t * c1 + 3 * u * t * t * c2 + t ** 3 * p1)
    return np.array(pts)


def area(sub):
    p = flat(sub, 6)
    x, y = p[:, 0], p[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def solid(sub):
    return sub if area(sub) >= 0 else sub.reversed()


def hole(sub):
    return sub if area(sub) <= 0 else sub.reversed()


def cr_path(points, n=16):
    """Dense points of an open Catmull-Rom curve through `points`."""
    pts = [P(p) for p in points]
    ext = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-1])
    return out


def stroke(points, w0, w1=None, n=14, smooth=True):
    """Thick stroke (round ends) along a curve; the width goes from w0 to w1. Returns a list of Sub."""
    w1 = w0 if w1 is None else w1
    pts = dense(cr_path(points, n), min(w0, w1 if w1 else w0) / 6) if smooth else dense([P(p) for p in points], w0 / 6)
    m = len(pts)
    return [circle(p[0], p[1], (w0 + (w1 - w0) * i / max(1, m - 1)) / 2) for i, p in enumerate(pts)]


def dense(pts, maxstep):
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        k = max(1, int(np.linalg.norm(b - a) / maxstep))
        for j in range(1, k + 1):
            out.append(a + (b - a) * j / k)
    return out


def merge(ops, res=16, step=0.45, corner_deg=55, blur=1.4, margin=3):
    """ops: list of (+1|-1, Sub). Unites/subtracts the shapes and returns the resulting outlines (exteriors and
    holes) as smooth Sub: one clean outline per connected piece, without internal seams."""
    allp = np.vstack([flat(s, 10) for _, s in ops])
    x0, y0 = allp[:, 0].min() - margin, allp[:, 1].min() - margin
    W = int((allp[:, 0].max() + margin - x0) * res) + 2
    H = int((allp[:, 1].max() + margin - y0) * res) + 2
    im = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(im)
    for sign, s in ops:
        pts = [((p[0] - x0) * res, (p[1] - y0) * res) for p in flat(s, 10)]
        dr.polygon(pts, fill=255 if sign > 0 else 0)
    a = cv2.GaussianBlur(np.array(im), (0, 0), blur)
    a = (a > 127).astype(np.uint8) * 255
    cnts, hier = cv2.findContours(a, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    outs = []
    for c, h in zip(cnts, hier[0]):
        if len(c) < 12 or cv2.contourArea(c) < 4 * res:
            continue
        c = c[:, 0, :].astype(float)
        k = max(2, int(step * res))
        pts = [P((p[0] + 0.5) / res + x0, (p[1] + 0.5) / res + y0) for p in c[np.arange(0, len(c), k)]]
        n = len(pts)
        corners = []
        for i in range(n):
            v1, v2 = pts[i] - pts[i - 1], pts[(i + 1) % n] - pts[i]
            l1, l2 = np.linalg.norm(v1), np.linalg.norm(v2)
            if l1 > 1e-9 and l2 > 1e-9:
                if math.degrees(math.acos(max(-1, min(1, float(v1 @ v2) / (l1 * l2))))) > corner_deg:
                    corners.append(i)
        outs.append((h[3] != -1, spline(pts, corners=corners)))
    return [hole(s) if is_hole else solid(s) for is_hole, s in sorted(outs, key=lambda t: t[0])]


def ell(cx, cy, rx, ry, rot=0.0):
    return ellipse(cx, cy, rx, ry, rot=rot)


def _flatten(subs):
    out = []
    for s in subs:
        out.extend(s if isinstance(s, list) else [s])
    return out


def add(*subs):
    return [(1, s) for s in _flatten(subs)]


def cut(*subs):
    return [(-1, s) for s in _flatten(subs)]


def tri(a, b, c):
    return poly([a, b, c])


# ------------------------------------------------------------------ rasterizer (for the PNGs)

def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def element_mask(subs, size, view, ss):
    x0, y0, x1, y1 = view
    W, H = size
    sx, sy = W * ss / (x1 - x0), H * ss / (y1 - y0)
    mask = Image.new("L", (W * ss, H * ss), 0)
    md = ImageDraw.Draw(mask)
    for s in sorted(subs, key=lambda s: -abs(area(s))):
        md.polygon([((p[0] - x0) * sx, (p[1] - y0) * sy) for p in flat(s, 20)], fill=255 if area(s) >= 0 else 0)
    return mask


def doc_bbox(doc):
    pts = np.vstack([np.array(s.points()) for _, _, subs in doc.elements for s in subs])
    return pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()


def raster_doc(doc, size, fills, bg=(0, 0, 0, 0), view=None, ss=3, under=None):
    """Rasterizes a Doc to RGBA of `size`. fills[i]: '#rrggbb' or None (omit). `under`: {i: color} paints beforehand
    the filled silhouette (without holes) of element i, so that its holes show that color."""
    view = view or doc_bbox(doc)
    W, H = size
    img = Image.new("RGBA", (W * ss, H * ss), bg)
    for i, (_, _, subs) in enumerate(doc.elements):
        if fills[i] is None:
            continue
        mask = element_mask(subs, size, view, ss)
        if under and i in under:
            a = np.array(mask)
            cnts, _ = cv2.findContours(a, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            sil = np.zeros_like(a)
            cv2.fillPoly(sil, cnts, 255)
            img.alpha_composite(Image.composite(Image.new("RGBA", img.size, hexc(under[i]) + (255,)),
                                                Image.new("RGBA", img.size, (0, 0, 0, 0)), Image.fromarray(sil)))
        img.alpha_composite(Image.composite(Image.new("RGBA", img.size, hexc(fills[i]) + (255,)),
                                            Image.new("RGBA", img.size, (0, 0, 0, 0)), mask))
    return img.resize((W, H), Image.LANCZOS)


# ---------------------------------------------------------------------------- alien

def alien():
    ops = add(circle(38, 36, 21), ell(38, 56, 13, 17),
              tri((24, 20), (20, 0), (33, 16)), tri((32, 16), (38, -4), (44, 16)), tri((43, 16), (56, 0), (52, 20)),
              stroke([(22, 44), (10, 52), (7, 68), (13, 84), (24, 85)], 5.5),
              stroke([(54, 44), (66, 52), (69, 68), (63, 84), (52, 85)], 5.5),
              stroke([(32, 66), (31, 80), (24, 92)], 5.5), stroke([(44, 66), (45, 80), (52, 92)], 5.5),
              ell(22, 93, 7, 3.2), ell(54, 93, 7, 3.2))
    ops += cut(circle(38, 36, 9.5))
    d = Doc("alien: extraterrestre de un ojo (reemplazo propio). [0] cuerpo con hueco de ojo, [1] pupila")
    d.add(merge(ops), fill="#333333")
    d.add(circle(38, 36, 4.5), fill="#333333")
    return d


# ---------------------------------------------------------------------------- beer

def beer():
    x0, x1 = 12, 48
    glass = merge(add(rrect(5, 24, 50, 72, 12), rrect(48, 34, 20, 48, 10)) +
                  cut(rpoly([(x0, 16), (x1, 16), (x1, 90), (x0, 90)], [0, 0, 8, 8]), rrect(54, 43, 8, 30, 4)))
    foam = merge(add(circle(15, 24, 10), circle(27, 17, 12), circle(40, 20, 10), circle(49, 28, 7),
                     rrect(9, 22, 44, 16, 4), stroke([(18, 38), (18, 52)], 7), stroke([(40, 36), (40, 44)], 6)))
    beerp = rpoly([(x0, 42), (x1, 42), (x1, 90), (x0, 90)], [0, 0, 8, 8])
    d = Doc("beer: jarra de cerveza (reemplazo propio). [0] jarra, [1] espuma, [2] cerveza")
    d.add(glass, fill="#000000")
    d.add(foam, fill="#666666")
    d.add(beerp, fill="#ff9900")
    return d


# ---------------------------------------------------------------------------- clipboard

def clipboard():
    board = [rrect(2, 10, 67, 90, 6), rrect(5.5, 13.5, 60, 83, 3.5, rev=True),
             rrect(9, 17, 53, 76, 2.5), rrect(12.5, 20.5, 46, 69, 1.5, rev=True)]
    clip = [rrect(16, 4, 39, 17, 5), rrect(26, 0, 19, 11, 5), circle(35.5, 6, 3.2, rev=True)]
    d = Doc("clipboard: tablero con pinza (reemplazo propio). [0] marco doble, [1] pinza")
    d.add(board, fill="#333333")
    d.add(merge(add(clip[:2]) + cut(clip[2])), fill="#333333")
    return d


# ---------------------------------------------------------------------------- factory

def factory():
    pts = [(0, 100), (0, 30), (22, 48), (22, 30), (44, 48), (44, 30), (66, 48), (66, 40), (72, 40),
           (72, 4), (87, 4), (87, 40), (94, 40), (94, 12), (109, 12), (109, 40), (116, 40), (116, 0), (131, 0),
           (131, 40), (143, 40), (143, 100)]
    subs = [poly(pts)]
    for r in range(2):
        for c in range(3):
            subs.append(rrect(6 + c * 15, 58 + r * 14, 9, 8, 0.5, rev=True))
    for c in range(7):
        subs.append(rrect(72 + c * 10, 56, 7, 8, 0.5, rev=True))
    subs.append(rrect(74, 78, 18, 22, 0.5, rev=True))
    d = Doc("factory: fabrica con tejado de sierra y chimeneas (reemplazo propio). UN path")
    d.add(subs)
    return d


# ---------------------------------------------------------------------------- cats

def fat_cat():
    ops = add(ell(52, 70, 33, 27, -10), ell(34, 33, 17, 15), ell(38, 56, 16, 22, 15),
              tri((20, 24), (20, 6), (32, 18)), tri((36, 18), (47, 8), (49, 26)),
              ell(25, 93, 13, 5), ell(52, 95, 12, 4.5),
              stroke([(76, 82), (90, 90), (98, 82), (92, 70)], 6, 3.5))
    ops += cut(stroke([(24, 29), (26, 31), (29, 29)], 1.6, smooth=False),
               stroke([(37, 28), (40, 30), (43, 28)], 1.6, smooth=False),
               stroke([(8, 38), (18, 40)], 1.1), stroke([(8, 44), (18, 43)], 1.1),
               stroke([(46, 40), (56, 38)], 1.1),
               stroke([(34, 84), (46, 78), (60, 76)], 1.6),
               stroke([(30, 62), (36, 72), (44, 70)], 1.6))
    d = Doc("fat_cat: gato gordo sentado (reemplazo propio)")
    d.add(merge(ops))
    return d


def sitting_cat():
    ops = add(circle(68, 22, 12.5), tri((57, 17), (58, 0), (69, 11)), tri((69, 11), (80, 0), (80, 18)),
              ell(63, 50, 14, 28, 12), ell(48, 74, 26, 24), rrect(26, 86, 66, 14, 5),
              stroke([(74, 52), (76, 98)], 11),
              stroke([(30, 92), (12, 90), (4, 70), (6, 48), (16, 36), (24, 38)], 7, 4.5))
    d = Doc("sitting_cat: gato sentado de perfil, cola a la izquierda (reemplazo propio)")
    d.add(merge(ops))
    return d


# ---------------------------------------------------------------------------- doctors

def _doctor(male):
    disc = [circle(50, 50, 50), circle(50, 50, 47, rev=True)]
    coat = rpoly([(14, 96), (15, 76), (30, 67), (41, 63), (50, 79), (59, 63), (70, 67), (85, 76), (86, 96)],
                 [14, 6, 6, 2, 0, 2, 6, 6, 14])
    tube = stroke([(38, 66), (31, 76), (32, 88)], 2.6) + stroke([(62, 66), (70, 74), (70, 80)], 2.6)
    coat_el = merge(add(coat) + cut(tube, circle(32, 90, 7), circle(70, 83, 5.5)))
    chest = [circle(32, 90, 4.4), circle(70, 83, 3.3)]
    neck = poly([(44.5, 48), (55.5, 48), (55.5, 62), (56.5, 64), (50, 75.5), (43.5, 64), (44.5, 62)])
    if not male:
        hair = merge(add(ell(50, 34, 24, 27), rrect(26, 36, 48, 28, 9)) + cut(ell(50, 38, 15.5, 19.5)))
        face = merge(add(ell(50, 38, 13.5, 17.5), neck))
        d = Doc("female_doctor: busto de medica (reemplazo propio). [0] aro, [1] pelo, [2] rostro, [3] bata, [4] pieza")
        for el in (disc, hair, face, coat_el, chest):
            d.add(el, fill="#333333")
        return d
    hair = merge(add(ell(50, 33, 22.5, 20)) + cut(ell(50, 44, 18.5, 23)))
    face = merge(add(ell(50, 41, 16.5, 20.5), neck) +
                 cut(circle(41.5, 41, 7.6), circle(58.5, 41, 7.6), rrect(46, 40, 8, 2, 0.5)) +
                 add(circle(41.5, 41, 5.6), circle(58.5, 41, 5.6)))
    ears = [ell(32.5, 43, 3.2, 6), ell(67.5, 43, 3.2, 6)]
    d = Doc("male_doctor: busto de medico con gafas (reemplazo propio). [0] aro, [1] pelo, [2] rostro, [3] orejas, "
            "[4] bata, [5] pieza")
    for el in (disc, hair, face, ears, coat_el, chest):
        d.add(el, fill="#333333")
    return d


def female_doctor():
    return _doctor(False)


def male_doctor():
    return _doctor(True)


# ---------------------------------------------------------------------------- helpers de muscle / pangolin

class OpenSub(Sub):
    """OPEN subpath (without the final Z): serves for loose lines (the pangolin's scales)."""

    def d(self):
        return super().d().rstrip("Z").rstrip()


def bez(start, *segs):
    """Hand-made closed outline: each segment is (x, y) = line or (c1x, c1y, c2x, c2y, x, y) = cubic."""
    s = Sub(start)
    for g in segs:
        s.line(g) if len(g) == 2 else s.cubic(g[0:2], g[2:4], g[4:6])
    return s


def lens(pts, w, n=10):
    """Lens-shaped slit (sharp tips, maximum width w) along a curve through `pts`. It is a hole."""
    c = cr_path(pts, n)
    m = len(c)
    left, right = [], []
    for i, p in enumerate(c):
        a, b = c[max(0, i - 1)], c[min(m - 1, i + 1)]
        t = (b - a) / np.linalg.norm(b - a)
        nr = np.array([-t[1], t[0]])
        h = w / 2 * math.sin(math.pi * i / (m - 1)) ** 0.8
        left.append(p + nr * h)
        right.append(p - nr * h)
    return hole(spline(left + right[::-1][1:-1], corners=[0, m - 1]))


def vstroke(points, widths, n=14):
    """Like stroke() but with a width per control point (linearly interpolated): list of circles."""
    out = []
    for i, p in enumerate(cr_path(points, n)):
        k, t = divmod(i, n)
        w = widths[-1] if k >= len(widths) - 1 else widths[k] * (1 - t / n) + widths[k + 1] * t / n
        out.append(circle(p[0], p[1], w / 2))
    return out


def toes(x, y, n, length, spread, ang):
    """Fan of n clawed fingers (tapering strokes) from (x, y) toward the angle `ang` (degrees, y down)."""
    out = []
    for i in range(n):
        a = D2R(ang + (i - (n - 1) / 2) * spread)
        e = P(x, y) + P(math.cos(a), math.sin(a)) * length
        out += vstroke([(x, y), tuple(P(x, y) * 0.5 + e * 0.5), tuple(e)], [3.0, 2.2, 1.2], 6)
    return out


def poly_mask(subs, view, res):
    """uint8 mask (res px per unit) of a list of Sub (those with negative area are holes)."""
    x0, y0, x1, y1 = view
    im = Image.new("L", (int((x1 - x0) * res) + 1, int((y1 - y0) * res) + 1), 0)
    dr = ImageDraw.Draw(im)
    for s in sorted(subs, key=lambda s: -abs(area(s))):
        dr.polygon([((p[0] - x0) * res, (p[1] - y0) * res) for p in flat(s, 12)], fill=255 if area(s) >= 0 else 0)
    return np.array(im)


def pangolin_scales(body, trunk, widths, nh=4, rmin=2.2, margin=0.8, res=12, view=(-5, -5, 170, 80)):
    """Pangolin scales: open semicircles (bulging toward the tail) in a shingle tiling. They follow the
    axis `trunk` (trunk + tail) with half-width w/2: the rows go along the axis and each scale measures ~ half-width/nh
    (minimum radius `rmin`, so they shrink toward the tip of the tail). Only the scale that fits entirely inside
    the outline `body` (and the trunk/tail, without legs or head) is drawn, with a `margin` of slack."""
    sil = poly_mask(body, view, res)
    zone = poly_mask(merge(add(vstroke(trunk, widths)), res=12), view, res)
    dist = np.minimum(cv2.distanceTransform((sil > 0).astype(np.uint8), cv2.DIST_L2, 3),
                      cv2.distanceTransform((zone > 0).astype(np.uint8), cv2.DIST_L2, 3)) / res

    def ok(q):
        x, y = int((q[0] - view[0]) * res), int((q[1] - view[1]) * res)
        return 0 <= y < dist.shape[0] and 0 <= x < dist.shape[1] and dist[y, x] >= margin

    S = np.array(dense(cr_path(trunk, 16), 0.3))
    sarc = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(S, axis=0), axis=1))])
    frac = np.linspace(0, 1, len(widths))
    half = lambda s: float(np.interp(s / sarc[-1], frac, [w / 2 for w in widths]))
    arcs, s, k = [], 4.0, 0
    while s < sarc[-1] - 1:
        h = half(s)
        if h < rmin + 0.8:
            break
        r = max(h / nh, rmin)
        i = min(max(int(np.searchsorted(sarc, s)), 1), len(S) - 2)
        t = (S[i + 1] - S[i - 1]) / np.linalg.norm(S[i + 1] - S[i - 1])
        nrm = np.array([-t[1], t[0]])
        ang = math.atan2(t[1], t[0])
        v = -h + r + (r if k % 2 else 0)
        while v <= h - r + 1e-6 + (r if k % 2 else 0):
            c = S[i] + nrm * v
            a = OpenSub(c + r * np.array([math.cos(ang - math.pi / 2), math.sin(ang - math.pi / 2)]))
            a.arc(c, r, r, ang - math.pi / 2, ang + math.pi / 2)
            if all(ok(q) for q in flat(a, 6)):
                arcs.append(a)
            v += 2 * r
        s += r
        k += 1
    return arcs


# ---------------------------------------------------------------------------- bolt / like / muscle

def lightning_bolt():
    pts = [(44, 0), (86, 0), (62, 38), (88, 38), (14, 100), (36, 52), (8, 52)]
    d = Doc("lightning_bolt: rayo (reemplazo propio). UN subtrazo")
    d.add(rpoly(pts, [1.5, 1.5, 1.5, 1.5, 1, 1.5, 1.5]))
    return d


def like():
    cuff = [rrect(0, 44, 24, 54, 5), circle(12, 86, 3.8, rev=True)]
    hand = merge(add(rrect(34, 50, 58, 46, 9), stroke([(54, 52), (62, 30), (66, 14)], 17),
                     stroke([(60, 58), (96, 58)], 12), stroke([(60, 70), (100, 70)], 12),
                     stroke([(60, 82), (97, 82)], 12), stroke([(60, 93), (90, 93)], 11), rrect(34, 50, 16, 46, 4)))
    heart = merge(add(circle(82, 11, 7.2), circle(95, 11, 7.2), tri((75, 11), (102, 11), (88.5, 28))))
    d = Doc("like: pulgar arriba con corazon (reemplazo propio)")
    d.add(cuff + hand + heart)
    return d


def muscle():
    """"Strength" icon: flexed arm in profile. One Bezier outline (from the top left, clockwise: fist, wrist,
    forearm, elbow crease, biceps, shoulder, lower edge, elbow) and 4 slits."""
    out = bez((14, 37),
              (12, 34, 4, 32, 4, 24), (4, 14),                 # fist: left side
              (4, 6, 10, 1, 19, 1), (30, 1),                   # fist: top
              (39, 1, 45, 6, 45, 14), (45, 22),                # fist: right side
              (45, 28, 41, 32, 37, 35),                        # wrist
              (37, 46), (37, 68),                              # right edge of the forearm to the crease
              (38, 56, 46, 34, 63, 32),                        # biceps: rises from the crease and bulges
              (75, 30, 80, 40, 83, 50),                        # goes down toward the shoulder
              (86, 47, 91, 45, 95, 48),                        # shoulder (deltoid)
              (99, 52, 101, 57, 101, 63), (101, 74),
              (101, 81, 98, 85, 92, 86),                       # end of the upper arm
              (72, 90, 48, 99, 28, 99),                        # lower edge (triceps) to the elbow
              (12, 99, 2, 94, 2, 82),                          # elbow
              (2, 66, 11, 52, 14, 40))                         # left edge of the forearm
    slits = [lens([(27, 8), (34, 7.5), (40, 8.5)], 2.2),       # fingers
             lens([(27, 14), (34, 13.5), (40, 14.5)], 2.2),
             lens([(27, 20), (33, 19.5), (39, 20.5)], 2.2),
             lens([(49, 63), (52, 50), (63, 41)], 3.2)]        # top of the biceps
    d = Doc("muscle: brazo flexionando el biceps (reemplazo propio). UN path: contorno + 4 rendijas")
    d.add([solid(out)] + slits)
    return d


# ---------------------------------------------------------------------------- monster

def monster():
    ops = add(ell(50, 62, 31, 36), ell(50, 30, 25, 22), ell(50, 44, 28, 20),
              stroke([(24, 52), (12, 70), (11, 84)], 17), stroke([(76, 52), (88, 70), (89, 84)], 17),
              circle(10.5, 86, 8), circle(89.5, 86, 8), ell(37, 94, 13, 6), ell(63, 94, 13, 6),
              tri((28, 18), (22, 2), (38, 12)), tri((62, 12), (78, 2), (72, 18)))
    for x, y, a in [(21, 40, 200), (14, 56, 190), (80, 40, -20), (88, 56, -10), (28, 90, 100), (72, 90, 80),
                    (50, 6, 270)]:      # locks of hair
        ca, sa = math.cos(D2R(a)), math.sin(D2R(a))
        base = P(x, y)
        ops += add(tri(base + P(-sa, ca) * 5, base - P(-sa, ca) * 5, base + P(ca, sa) * 9))
    body = merge(ops)
    eyes = [circle(40, 28, 3.6, rev=True), circle(60, 28, 3.6, rev=True)]
    smile = [hole(s) for s in merge(add(stroke([(36, 40), (50, 46), (64, 40)], 2.4)))]
    d = Doc("monster: monstruo peludo (reemplazo propio). UN path: contorno + 2 ojos + sonrisa")
    d.add(body + eyes + smile)
    return d


# ---------------------------------------------------------------------------- pangolin

def pangolin():
    """Pangolin in profile (faces left). Silhouette = union of variable-width strokes (trunk+tail, head,
    legs) passed through merge(); on top, scales as open arcs in a shingle tiling (see `pangolin_scales`)."""
    trunk = [(42, 41), (54, 33), (68, 28), (84, 29), (100, 36), (114, 44), (128, 51), (141, 53), (151, 48)]
    w_trunk = [18, 25, 30, 31, 26, 18, 11, 6.5, 2.8]
    head = [(42, 41), (32, 45), (22, 50), (13, 54)]
    w_head = [17, 10.5, 6, 2.6]
    ops = add(vstroke(trunk, w_trunk), vstroke(head, w_head))
    legs = [([(48, 42), (46, 50), (45, 54)], [10, 8.5, 7.5], 43, 3.8),     # near front
            ([(63, 43), (62, 50), (62, 54)], [9, 8, 7.5], 60, 3.8),        # far front
            ([(82, 43), (82, 50), (81, 54)], [9, 8, 7.5], 79, 3.4),        # far hind
            ([(96, 42), (97, 50), (97, 54)], [10, 8.5, 7.5], 95, 3.4)]     # near hind
    for pts, w, fx, claw in legs:
        ops += add(vstroke(pts, w, 6), ell(fx + 1, 55, 4.4, 2.4), toes(fx - 3.0, 55.3, 3, claw, 30, 172))
    body = [s_ for s_ in merge(ops, res=24, step=0.5, blur=2.2) if area(s_) > 0 or abs(area(s_)) > 6]
    scales = pangolin_scales(body, trunk, w_trunk)
    d = Doc("pangolin: pangolin de perfil con escamas (reemplazo propio). UN path: contorno + ojo + escamas abiertas")
    d.add(body + scales + [circle(26.5, 47.4, 1.25, rev=True)])
    return d


# ---------------------------------------------------------------------------- punchcard

def punchcard():
    outer = rpoly([(0, 12), (12, 0), (164, 0), (164, 100), (0, 100)], [0, 6, 6, 6, 6])
    inner = rpoly([(3.5, 13.5), (13.5, 3.5), (160.5, 3.5), (160.5, 96.5), (3.5, 96.5)], [0, 4, 4, 4, 4], rev=True)
    d = Doc("punchcard: tarjeta perforada (reemplazo propio). [0] marco, [1..22] perforaciones")
    d.add([outer, inner], fill="#333333")
    pitch = (164 - 30) / 8
    for y, n in [(20, 7), (47, 8), (74, 7)]:
        start = 15 + (8 - n) * pitch / 2
        for i in range(n):
            d.add(rrect(start + i * pitch, y, 9, 12, 0.8), fill="#333333")
    return d


# ---------------------------------------------------------------------------- server

def server_stack():
    d = Doc("server_stack: rack de servidores (reemplazo propio). [0] tapa, [1..4] modulos con 3 led")
    d.add(rpoly([(7, 0), (95, 0), (102, 16), (0, 16)], [2, 2, 1, 1]), fill="#000000")
    for k in range(4):
        y = 21 + k * 21
        d.add([rrect(0, y, 102, 17, 2.2)] + [circle(76 + 9 * j, y + 8.5, 2.3, rev=True) for j in range(3)],
              fill="#000000")
    return d


# ---------------------------------------------------------------------------- woman

def woman_icon():
    body = rpoly([(40, 31), (60, 31), (80, 72), (59, 72), (59, 94), (41, 94), (41, 72), (20, 72)],
                 [5, 5, 4, 0, 3, 3, 0, 4])
    d = Doc("woman_icon: figura femenina de pie (reemplazo propio). [0] cuadro blanco, [1] cabeza, [2] cuerpo")
    d.add(poly([(0, 0), (100, 0), (100, 100), (0, 100)]), fill="#FFFFFF")
    d.add(circle(50, 15, 11), fill="#333333")
    d.add(body, fill="#333333")
    return d


def woman():
    bust = merge(add(ell(50, 35, 22, 26), rrect(25, 32, 50, 30, 10), ell(50, 100, 42, 30)) +
                 cut(ell(50, 40, 14.5, 18)) + add(ell(50, 41, 13, 17), rrect(45, 50, 10, 16, 2)))
    collar = poly([(38, 70), (50, 86), (62, 70), (56, 66), (50, 76), (44, 66)])
    d = Doc("woman: busto de mujer (reemplazo propio). [0] busto, [1] cuello de la blusa")
    d.add(bust, fill="#333333")
    d.add(collar, fill="#FFFFFF")
    return d


# ---------------------------------------------------------------------------- Penrose

def penrose():
    """Three beams in an isometric render with occlusion (painter's algorithm): V1 along x, V2 along y and V3 along
    z; the high end of V3 projects over the start of V1 and covers it: the impossible triangle."""
    N, t = 5.0, 1.0
    boxes = [((0, N), (0, t), (0, t)), ((N - t, N), (0, N), (0, t)), ((N - t, N), (N - t, N), (0, N))]

    def proj(x, y, z):
        return np.array([0.8660254 * (x - y), -(z - 0.5 * (x + y))])      # and downward (svg)

    faces = []
    for (xa, xb), (ya, yb), (za, zb) in boxes:
        faces.append(([(xb, ya, za), (xb, yb, za), (xb, yb, zb), (xb, ya, zb)], (xb, (ya + yb) / 2, (za + zb) / 2)))
        faces.append(([(xa, yb, za), (xb, yb, za), (xb, yb, zb), (xa, yb, zb)], ((xa + xb) / 2, yb, (za + zb) / 2)))
        faces.append(([(xa, ya, zb), (xb, ya, zb), (xb, yb, zb), (xa, yb, zb)], ((xa + xb) / 2, (ya + yb) / 2, zb)))
    faces.sort(key=lambda f: sum(f[1]))
    allp = np.array([proj(*p) for f, _ in faces for p in f])
    mn, mx = allp.min(axis=0), allp.max(axis=0)
    res = 110.0
    W, H = int((mx[0] - mn[0]) * res) + 8, int((mx[1] - mn[1]) * res) + 8
    lab = np.zeros((H, W), np.int32)
    for i, (f, _) in enumerate(faces):
        pts = np.array([(proj(*p) - mn) * res + 4 for p in f]).round().astype(np.int32)
        cv2.fillPoly(lab, [pts], i + 1)
    scale = 92.0 / max(mx[0] - mn[0], mx[1] - mn[1]) / res
    ox = 50 - (mx[0] - mn[0]) * res * scale / 2 - 4 * scale
    oy = 50 - (mx[1] - mn[1]) * res * scale / 2 - 4 * scale
    subs = []
    for i in range(len(faces)):
        m = (lab == i + 1).astype(np.uint8) * 255
        cnts, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        if hier is None:
            continue
        for c, h in zip(cnts, hier[0]):
            if cv2.contourArea(c) < 40:
                continue
            ap = cv2.approxPolyDP(c, 2.2, True)[:, 0, :].astype(float)
            s = poly([(p[0] * scale + ox, p[1] * scale + oy) for p in ap])
            subs.append(hole(s) if h[3] != -1 else solid(s))
    d = Doc("PenroseTriangle: triangulo imposible (reemplazo propio). [0] cuadro blanco, [1] caras visibles de 3 vigas")
    d.add(poly([(0, 0), (100, 0), (100, 100), (0, 100)]), fill="#FFFFFF")
    d.add(subs, fill="#333333")
    return d


# ---------------------------------------------------------------------------- ambigram

def symmetry_ambigram():
    """'symm' in stroke letters + that half rotated 180 degrees: rotationally symmetric (see the docstring)."""
    sx, sy = 1.25, 1.25
    glyphs = {
        "s": ([[(10, 5), (6, 2), (2, 5), (5, 12), (10, 16), (9, 24), (5, 27), (1, 24)]], 11),
        "y": ([[(1, 2), (4, 14), (6, 20)], [(11, 2), (7, 20), (2, 36)]], 13),
        "m": ([[(1, 27), (1, 2)], [(1, 10), (5, 2), (9, 10), (9, 27)], [(9, 10), (13, 2), (17, 10), (17, 27)]], 18),
    }
    word, x, els = "symm", 0.0, []
    for ch in word:
        paths, w = glyphs[ch]
        ops = []
        for p in paths:
            pts = [(x + a * sx, b * sy) for a, b in p]
            ops += add(stroke(pts, 3.4))
        els.append(merge(ops, res=14))
        x += w * sx + 4
    cx, cy = x + 0.0, (2 * sy + 36 * sy) / 2
    right = [[s.rotate(180, (cx, cy)) for s in el] for el in els[::-1]]
    d = Doc("symmetry_ambigram: 'symm' + su giro de 180 grados (reemplazo propio, ver docstring)")
    for el in els + right:
        d.add(el, fill="#000000")
    return d


# ---------------------------------------------------------------------------- robot

def robot():
    antenna = merge(add(rrect(50, 10, 6, 24, 1), circle(53, 8, 8)))
    head = [rrect(12, 28, 82, 68, 26), rrect(22, 38, 62, 48, 18, rev=True)]
    face = [circle(40, 60, 8.5), circle(66, 60, 8.5), rrect(44, 75, 18, 5, 1.5)]
    ears = [rrect(2, 50, 13, 26, 5), rrect(91, 50, 13, 26, 5)]
    d = Doc("robot: robot de juguete (reemplazo propio). [0] antena, [1] cabeza, [2] ojos y boca, [3] orejas")
    for el in (antenna, head, face, ears):
        d.add(el, fill="#000000")
    return d


# ---------------------------------------------------------------------------- snowflake

def snowflake():
    c = P(43.3, 50.0)
    arm = add(stroke([(43.3, 46), (43.3, 4)], 5.2, 2.6, smooth=False),
              tri((43.3, 0), (46.6, 8), (43.3, 14)), tri((43.3, 0), (40, 8), (43.3, 14)))
    for u, ln, w in [(18, 14, 3.4), (29, 11, 3.0), (39, 7, 2.6)]:
        y = c[1] - u
        for sgn in (-1, 1):
            tip = P(c[0] + sgn * ln * math.sin(D2R(58)), y - ln * math.cos(D2R(58)))
            arm += add(stroke([(c[0], y), tuple(tip)], w + 0.6, w - 0.8, smooth=False))
    ops = []
    for k in range(6):
        ops += [(1, s.rotate(60 * k, c)) for _, s in arm]
    def hx(r):
        return poly([tuple(c + r * P(math.cos(D2R(30 + 60 * i)), math.sin(D2R(30 + 60 * i)))) for i in range(6)])

    ops += add(hx(11)) + cut(hx(8.4))
    d = Doc("snowflake: copo de nieve D6 (reemplazo propio). [0] copo con hueco hexagonal, [1] hexagono central")
    d.add(merge(ops, res=20, step=0.35), fill="#000000")
    d.add(hx(7), fill="#FFFFFF")
    return d


# ---------------------------------------------------------------------------- emblems

def apple_logo():
    c = P(43.3, 50)
    v = {a: c + 50 * P(math.cos(D2R(a)), math.sin(D2R(a))) for a in (-90, -30, 30, 90, 150, 210)}
    faces = [(210, -90, -30), (-30, 30, 90), (90, 150, 210)]
    subs = []
    for a, b, e in faces:
        cen = (v[a] + v[b] + v[e] + c) / 4
        sh = (cen - c) / np.linalg.norm(cen - c) * 2.2
        quad = [c + sh, v[a] + sh, v[b] + sh, v[e] + sh]
        subs.append(solid(rpoly([tuple(p) for p in quad], 3.5)))
    d = Doc("apple_logo: emblema propio (cubo isometrico), NO es una manzana. 3 rombos con rendijas")
    d.add(subs, fill="#000000")
    return d


def bell_doc():
    W, H = 1234.0, 1236.0

    def octa(ins, cut_):
        return rpoly([(ins + cut_, ins), (W - ins - cut_, ins), (W - ins, ins + cut_), (W - ins, H - ins - cut_),
                      (W - ins - cut_, H - ins), (ins + cut_, H - ins), (ins, H - ins - cut_), (ins, ins + cut_)], 80)

    ctr = P(W / 2, H / 2)

    def hexa(r, rot=0):
        return poly([tuple(ctr + r * P(math.cos(D2R(rot + 60 * i)), math.sin(D2R(rot + 60 * i)))) for i in range(6)])

    d = Doc("BellSystemLogo: insignia octogonal con red de nodos (emblema propio, sin campana ni texto)")
    d.add([octa(0, 360), octa(40, 330).reversed()], fill="#999999")
    d.add(octa(40, 330), fill="#333333")
    d.add([hexa(150, 30), hexa(95, 30).reversed()], fill="#999999")
    d.add(hexa(55, 30), fill="#999999")
    for ang in (-90, 30, 150):
        u = P(math.cos(D2R(ang)), math.sin(D2R(ang)))
        end = ctr + u * 440
        ops = add(stroke([tuple(ctr + u * 130), tuple(end - u * 60)], 50, smooth=False), circle(end[0], end[1], 105)) \
            + cut(circle(end[0], end[1], 62)) + add(circle(end[0], end[1], 36))
        d.add(merge(ops, res=2, step=6, blur=1.0, margin=10), fill="#999999")
    for ang in (-30, 90, 210):
        p = ctr + 300 * P(math.cos(D2R(ang)), math.sin(D2R(ang)))
        d.add(circle(p[0], p[1], 34), fill="#999999")
    return d


def bell_svg():
    return bell_doc()


def bell_png():
    d = bell_doc()
    fills = ["#999999", "#333333", "#999999", "#999999", "#999999", "#999999", "#999999", "#999999", "#999999",
             "#999999"]
    im = raster_doc(d, (1234, 1236), fills, bg=(0, 0, 0, 255), view=(0, 0, 1234, 1236))
    return im.convert("RGB")


def google_png():
    W, H = 2224, 2268
    rx = W / 2.9
    ry = rx * 1.0
    cs = [(W / 2, ry), (rx, H - ry), (W - rx, H - ry)]
    cols = ["#14c8b0", "#ff8a2b", "#8e5cff"]
    base = Image.new("RGB", (W, H), (0, 0, 0))
    ss = 2
    for (cx, cy), col in zip(cs, cols):
        m = Image.new("L", (W * ss, H * ss), 0)
        ImageDraw.Draw(m).ellipse([(cx - rx) * ss, (cy - ry) * ss, (cx + rx) * ss, (cy + ry) * ss], fill=255)
        m = m.resize((W, H), Image.LANCZOS)
        layer = Image.composite(Image.new("RGB", (W, H), hexc(col)), Image.new("RGB", (W, H), (0, 0, 0)), m)
        base = ImageChops.screen(base, layer)
    return base


def doctor_pair_png():
    W, H = 1022, 676
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # man (behind, on the right, light tones)
    md = male_doctor()
    sz = (500, 640)
    mfills = [None, "#c4c4c4", "#d8d8d8", "#d8d8d8", "#d0d0d0", "#8a8a8a"]
    view = (14, 0, 86, 96)
    mi = raster_doc(md, sz, mfills, view=view, under={2: "#8f8f8f"})
    out.alpha_composite(mi, (W - sz[0], 16))
    # woman (in front, on the left, dark coat)
    fd = female_doctor()
    sz2 = (530, 676)
    ffills = [None, "#b5b5b5", "#dcdcdc", "#101010", "#101010"]
    fi = raster_doc(fd, sz2, ffills, view=view, under={3: "#e8e8e8"})
    # light halo around the woman to separate her from the man
    a = np.array(fi.split()[3])
    halo = cv2.dilate(a, np.ones((9, 9), np.uint8))
    hl = Image.composite(Image.new("RGBA", sz2, (60, 60, 60, 255)), Image.new("RGBA", sz2, (0, 0, 0, 0)),
                         Image.fromarray(halo))
    out.alpha_composite(hl, (0, 0))
    out.alpha_composite(fi, (0, 0))
    return out


# ---------------------------------------------------------------------------- log

SVGS = {
    "alien": (alien, 2), "beer": (beer, 2), "clipboard": (clipboard, 2), "factory": (factory, 2),
    "fat_cat": (fat_cat, 2), "female_doctor": (female_doctor, 2), "male_doctor": (male_doctor, 2),
    "lightning_bolt": (lightning_bolt, 2), "like": (like, 2), "monster": (monster, 2), "muscle": (muscle, 2),
    "pangolin": (pangolin, 2), "punchcard": (punchcard, 0), "server_stack": (server_stack, 0),
    "sitting_cat": (sitting_cat, 2), "woman_icon": (woman_icon, 0), "PenroseTriangle": (penrose, 0),
    "symmetry_ambigram": (symmetry_ambigram, 2), "robot": (robot, 2), "snowflake": (snowflake, 2),
    "woman": (woman, 0), "apple_logo": (apple_logo, 2), "BellSystemLogo": (bell_svg, 0),
}
PNGS = {"BellSystemLogo": bell_png, "google_logo_black": google_png, "doctor_pair": doctor_pair_png}
ALL = list(SVGS) + [n for n in PNGS if n not in SVGS]


def main():
    names = sys.argv[1:] or ALL
    SVG_OUT.mkdir(parents=True, exist_ok=True)
    PNG_OUT.mkdir(parents=True, exist_ok=True)
    for name in names:
        if name not in SVGS and name not in PNGS:
            sys.exit(f"nombre desconocido: {name}. Validos: {', '.join(ALL)}")
        if name in SVGS and (CODEX_SVG / f"{name}.svg").exists():
            shutil.copy2(CODEX_SVG / f"{name}.svg", SVG_OUT / f"{name}.svg")
            print("copiado (Codex)", SVG_OUT / f"{name}.svg")
        elif name in SVGS:
            fn, margin = SVGS[name]
            fn().write(SVG_OUT / f"{name}.svg", margin=margin)
            print("escrito", SVG_OUT / f"{name}.svg")
        if name in PNGS:
            im = PNGS[name]()
            im.save(PNG_OUT / f"{name}.png", optimize=True)
            print("escrito", PNG_OUT / f"{name}.png", im.size, im.mode)


if __name__ == "__main__":
    main()
