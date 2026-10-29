"""Mini vector-geometry library for the SVG generators in this directory.

A `Sub` is a closed subpath (start + linear/cubic segments). It is built with constructors
(circle, ellipse, rounded rectangle, rounded polygon, Catmull-Rom spline...), transformed
(rotate, scale, move, reverse direction) and serialized to the `d` of a <path>.

Conventions:
  - Coordinates in the SVG system (y down).
  - A hole is drawn with the opposite direction to the outline that contains it (`rev=True` / `.reversed()`),
    so it looks the same with the nonzero rule and with evenodd.
  - manimgl reverses the order of the subpaths of a <path> (get_subpaths() gives them from last to first):
    `path_el(subs, ..., code_order=True)` writes the subpaths in reverse order so that the index
    the code sees matches the order of the list."""
import math
from pathlib import Path

import numpy as np

K = 0.5522847498307936  # cubic control for a quarter circle


def fmt(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def P(x, y=None):
    if y is None:
        return np.array(x, float)
    return np.array([x, y], float)


class Sub:
    """Closed subpath: `start` and a list of segments ('L', p) or ('C', c1, c2, p)."""

    def __init__(self, start):
        self.start = P(start)
        self.segs = []

    # --- construction
    @property
    def cur(self):
        return self.segs[-1][-1] if self.segs else self.start

    def line(self, p):
        self.segs.append(("L", P(p)))
        return self

    def cubic(self, c1, c2, p):
        self.segs.append(("C", P(c1), P(c2), P(p)))
        return self

    def arc(self, c, rx, ry, a0, a1, rot=0.0):
        """Ellipse arc with center c from angle a0 to a1 (radians, the parameter grows toward y down).
        The current point is assumed to already be that of a0; cubics of <= 90 degrees are added."""
        c = P(c)
        n = max(1, int(math.ceil(abs(a1 - a0) / (math.pi / 2) - 1e-9)))
        da = (a1 - a0) / n
        k = 4 / 3 * math.tan(da / 4)
        cr, sr = math.cos(rot), math.sin(rot)

        def pt(a):
            x, y = rx * math.cos(a), ry * math.sin(a)
            return c + np.array([x * cr - y * sr, x * sr + y * cr])

        def dv(a):
            x, y = -rx * math.sin(a), ry * math.cos(a)
            return np.array([x * cr - y * sr, x * sr + y * cr])

        for i in range(n):
            t0, t1 = a0 + i * da, a0 + (i + 1) * da
            self.cubic(pt(t0) + k * dv(t0), pt(t1) - k * dv(t1), pt(t1))
        return self

    def join(self, other):
        """Appends the segments of another Sub afterwards (with a straight line if they do not connect)."""
        if np.linalg.norm(other.start - self.cur) > 1e-6:
            self.line(other.start)
        self.segs.extend(other.segs)
        return self

    # --- queries / transformations
    def points(self):
        out = [self.start]
        for s in self.segs:
            out.extend(s[1:])
        return out

    def map(self, fn):
        r = Sub(fn(self.start))
        for s in self.segs:
            r.segs.append((s[0],) + tuple(fn(p) for p in s[1:]))
        return r

    def translate(self, dx, dy):
        v = P(dx, dy)
        return self.map(lambda p: p + v)

    def scale(self, sx, sy=None, about=(0, 0)):
        sy = sx if sy is None else sy
        a = P(about)
        return self.map(lambda p: a + (p - a) * np.array([sx, sy]))

    def rotate(self, deg, about=(0, 0)):
        a = P(about)
        t = math.radians(deg)
        c, s = math.cos(t), math.sin(t)
        return self.map(lambda p: a + np.array([c * (p[0] - a[0]) - s * (p[1] - a[1]),
                                                s * (p[0] - a[0]) + c * (p[1] - a[1])]))

    def reversed(self):
        pts = [self.start]
        for s in self.segs:
            pts.append(s[-1])
        # close if the last point does not return to the start: the 'Z' closure does it, it is treated as a straight segment
        r = Sub(pts[-1])
        for i in range(len(self.segs) - 1, -1, -1):
            s = self.segs[i]
            prev = pts[i]
            if s[0] == "L":
                r.line(prev)
            else:
                r.cubic(s[2], s[1], prev)
        return r

    def d(self):
        parts = [f"M {fmt(self.start[0])} {fmt(self.start[1])}"]
        for s in self.segs:
            if s[0] == "L":
                parts.append(f"L {fmt(s[1][0])} {fmt(s[1][1])}")
            else:
                parts.append("C " + " ".join(f"{fmt(p[0])} {fmt(p[1])}" for p in s[1:]))
        parts.append("Z")
        return " ".join(parts)


# ------------------------------------------------------------------ constructors

def circle(cx, cy, r, rev=False):
    return ellipse(cx, cy, r, r, rev=rev)


def ellipse(cx, cy, rx, ry, rot=0.0, rev=False):
    r = math.radians(rot)
    cr, sr = math.cos(r), math.sin(r)
    s = Sub((cx + rx * cr, cy + rx * sr)).arc((cx, cy), rx, ry, 0, 2 * math.pi, rot=r)
    return s.reversed() if rev else s


def poly(pts, rev=False):
    pts = [P(p) for p in pts]
    s = Sub(pts[0])
    for p in pts[1:]:
        s.line(p)
    return s.reversed() if rev else s


def rpoly(pts, radius, rev=False):
    """Polygon with rounded corners. `radius`: number or list (one per vertex, 0 = sharp corner)."""
    pts = [P(p) for p in pts]
    n = len(pts)
    rad = [radius] * n if np.isscalar(radius) else list(radius)
    ins, outs = [], []
    for i in range(n):
        v, a, b = pts[i], pts[i - 1], pts[(i + 1) % n]
        r = rad[i]
        la, lb = np.linalg.norm(a - v), np.linalg.norm(b - v)
        t = min(r, la / 2, lb / 2) if r > 0 else 0.0
        ins.append(v + (a - v) / la * t if t > 0 else v)
        outs.append(v + (b - v) / lb * t if t > 0 else v)
    s = Sub(outs[0])
    for i in range(1, n + 1):
        j = i % n
        s.line(ins[j])
        if np.linalg.norm(ins[j] - outs[j]) > 1e-9:
            v = pts[j]
            s.cubic(ins[j] + (v - ins[j]) * K, outs[j] + (v - outs[j]) * K, outs[j])
    return s.reversed() if rev else s


def rchain(pts, radius):
    """Like rpoly but open: it goes from pts[0] to pts[-1] and only rounds the interior vertices."""
    pts = [P(p) for p in pts]
    n = len(pts)
    rad = [radius] * n if np.isscalar(radius) else list(radius)
    s = Sub(pts[0])
    for i in range(1, n - 1):
        v, a, b = pts[i], pts[i - 1], pts[i + 1]
        r = rad[i]
        la, lb = np.linalg.norm(a - v), np.linalg.norm(b - v)
        t = min(r, la / 2, lb / 2) if r > 0 else 0.0
        if t <= 0:
            s.line(v)
            continue
        pin, pout = v + (a - v) / la * t, v + (b - v) / lb * t
        s.line(pin)
        s.cubic(pin + (v - pin) * K, pout + (v - pout) * K, pout)
    s.line(pts[-1])
    return s


def rrect(x, y, w, h, r, rev=False):
    return rpoly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], r, rev=rev)


def capsule(p0, p1, width, rev=False):
    """Bar with round ends between p0 and p1."""
    p0, p1 = P(p0), P(p1)
    d = p1 - p0
    ang = math.atan2(d[1], d[0])
    n = np.array([-math.sin(ang), math.cos(ang)])
    hw = width / 2
    s = Sub(p0 + n * hw).line(p1 + n * hw)
    s.arc(p1, hw, hw, ang + math.pi / 2, ang - math.pi / 2)
    s.line(p0 - n * hw)
    s.arc(p0, hw, hw, ang - math.pi / 2, ang - 3 * math.pi / 2)
    return s.reversed() if rev else s


def spline(pts, corners=(), closed=True, rev=False):
    """Smooth curve through the points (Catmull-Rom with unit tangents scaled by the chord).
    `corners`: indices of vertices with a corner (different tangent on each side)."""
    pts = [P(p) for p in pts]
    n = len(pts)

    def unit(v):
        m = np.linalg.norm(v)
        return v / m if m > 1e-12 else v

    tin, tout = [], []
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        if i in corners:
            tin.append(unit(b - a))
            tout.append(unit(c - b))
        else:
            t = unit(c - a)
            tin.append(t)
            tout.append(t)
    s = Sub(pts[0])
    for i in range(n):
        j = (i + 1) % n
        if not closed and j == 0:
            break
        L = np.linalg.norm(pts[j] - pts[i])
        s.cubic(pts[i] + tout[i] * L / 3, pts[j] - tin[j] * L / 3, pts[j])
    return s.reversed() if rev else s


def thick_polyline(pts, width, miter_limit=3.0):
    """Outline (polygon) of a thick polyline, with straight ends and mitered vertices."""
    pts = [P(p) for p in pts]
    pts = [p for i, p in enumerate(pts) if i == 0 or np.linalg.norm(p - pts[i - 1]) > 1e-9]
    hw = width / 2
    left, right = [], []
    for i, p in enumerate(pts):
        if i == 0:
            d = pts[1] - p
            nrm = np.array([-d[1], d[0]]) / np.linalg.norm(d)
            off = nrm * hw
        elif i == len(pts) - 1:
            d = p - pts[i - 1]
            nrm = np.array([-d[1], d[0]]) / np.linalg.norm(d)
            off = nrm * hw
        else:
            d1 = p - pts[i - 1]
            d2 = pts[i + 1] - p
            n1 = np.array([-d1[1], d1[0]]) / np.linalg.norm(d1)
            n2 = np.array([-d2[1], d2[0]]) / np.linalg.norm(d2)
            m = n1 + n2
            mm = np.linalg.norm(m)
            m = m / mm
            k = hw / max(np.dot(m, n1), 1 / miter_limit)
            off = m * k
        left.append(p + off)
        right.append(p - off)
    return poly(left + right[::-1])


def arc_pts(c, r, a0, a1, n):
    """Points of an arc (degrees) to use in polygons."""
    c = P(c)
    return [c + r * np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
            for a in np.linspace(a0, a1, n)]


# ------------------------------------------------------------------ SVG output

def bbox(subs):
    pts = np.array([p for s in subs for p in s.points()])
    return pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()


def path_el(subs, fill="#000000", stroke=None, sw=1.0, code_order=True, opacity=None):
    """<path> with several subpaths. With code_order=True they are written in reverse (see the module docstring)."""
    subs = list(subs)
    if code_order:
        subs = subs[::-1]
    d = " ".join(s.d() for s in subs)
    attrs = f'fill="{fill}"'
    if stroke:
        attrs += f' stroke="{stroke}" stroke-width="{fmt(sw)}" stroke-linejoin="round"'
    else:
        attrs += ' stroke="none"'
    if opacity is not None:
        attrs += f' opacity="{fmt(opacity)}"'
    return d, attrs, subs


class Doc:
    """An SVG: a list of <path> elements, each with its list of subpaths."""

    def __init__(self, comment=""):
        self.elements = []   # (d, attrs, subs)
        self.comment = comment

    def add(self, subs, fill="#000000", stroke=None, sw=1.0, code_order=True, opacity=None):
        if isinstance(subs, Sub):
            subs = [subs]
        self.elements.append(path_el(subs, fill, stroke, sw, code_order, opacity))
        return self

    def svg(self, margin=2.0):
        allsubs = [s for _, _, subs in self.elements for s in subs]
        x0, y0, x1, y1 = bbox(allsubs)
        x0, y0, x1, y1 = x0 - margin, y0 - margin, x1 + margin, y1 + margin
        w, h = x1 - x0, y1 - y0
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{fmt(x0)} {fmt(y0)} {fmt(w)} {fmt(h)}" '
                f'width="{fmt(w * 5)}" height="{fmt(h * 5)}">')
        lines = [head]
        if self.comment:
            lines.append(f"<!-- {self.comment} -->")
        for d, attrs, _ in self.elements:
            lines.append(f'<path {attrs} d="{d}"/>')
        lines.append("</svg>")
        return "\n".join(lines) + "\n"

    def write(self, path, margin=2.0):
        Path(path).write_text(self.svg(margin))
