"""Own replacements (made with code, PIL + numpy) of third-party raster images. Each one is written with the
same name in _lib/assets/raster_images/, where the scene looks for it:

  imo_logo.png         generic "math olympiad" badge: laurel, shield with a pi and a ribbon with
                       the text MATH OLYMPIAD. 800x549 (same ratio as the original). It does not imitate the IMO logo.
  facebook_logo.png    generic social network icon: blue rounded square with two silhouettes of people. 512x512.
  instagram_logo.png   generic photo social network icon: rounded square with a gradient and a frame with
                       mountains and sun. 512x512. It does not imitate the Instagram logo.
  sars_icon.png        four stylized virions (light disk with a crown of spikes) over a gray background of a
                       synthetic "micrograph". 1400x1000.
  TerryTaoIMO.png      illustration of a young man receiving a medal from a presenter, on a stage with
                       the sign MATH OLYMPIAD. 630x720 (7:8 ratio like the original). Generic figures.

Usage: python make_visual_rasters.py [name ...]      (without arguments it generates all)"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).resolve().parents[3] / "raster_images"


# ------------------------------------------------------------------ utilities

def font(size, bold=True, serif=False):
    names = (["DejaVuSerif-Bold.ttf", "DejaVuSerif.ttf"] if serif else ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf"])
    if not bold:
        names = names[::-1]
    dirs = []
    try:
        import matplotlib
        dirs.append(Path(matplotlib.__file__).parent / "mpl-data" / "fonts" / "ttf")
    except Exception:
        pass
    dirs += [Path("/usr/share/fonts/dejavu-sans-fonts"), Path("/usr/share/fonts/dejavu"), Path("/usr/share/fonts/truetype/dejavu")]
    for dd in dirs:
        for n in names:
            if (dd / n).exists():
                return ImageFont.truetype(str(dd / n), size)
    return ImageFont.load_default()


def hexc(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


class Canvas:
    """RGBA canvas that is drawn at double/triple resolution and downscaled at the end (edge smoothing)."""

    def __init__(self, w, h, scale=3, bg=(0, 0, 0, 0)):
        self.w, self.h, self.s = w, h, scale
        self.im = Image.new("RGBA", (w * scale, h * scale), bg)

    def S(self, v):
        if isinstance(v, (list, tuple)):
            return [self.S(x) for x in v]
        return v * self.s

    def layer(self):
        return Image.new("RGBA", self.im.size, (0, 0, 0, 0))

    def composite(self, layer):
        self.im = Image.alpha_composite(self.im, layer)

    def draw(self, fn):
        """fn(draw, S): draws on a new layer and composites it."""
        ly = self.layer()
        fn(ImageDraw.Draw(ly), self.S)
        self.composite(ly)

    def paste_gradient(self, mask_fn, c0, c1, p0, p1):
        """Fills with a linear gradient (from c0 at p0 to c1 at p1) the shape that mask_fn(draw, S) draws."""
        mask = Image.new("L", self.im.size, 0)
        mask_fn(ImageDraw.Draw(mask), self.S)
        W, H = self.im.size
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        p0, p1 = np.array(self.S(list(p0)), float), np.array(self.S(list(p1)), float)
        d = p1 - p0
        t = np.clip(((xx - p0[0]) * d[0] + (yy - p0[1]) * d[1]) / (d @ d), 0, 1)[..., None]
        col = np.array(c0, float) * (1 - t) + np.array(c1, float) * t
        grad = Image.fromarray(col.astype(np.uint8), "RGBA")
        ly = self.layer()
        ly.paste(grad, (0, 0), mask)
        self.composite(ly)

    def paste_radial(self, mask_fn, c_in, c_out, center, radius):
        mask = Image.new("L", self.im.size, 0)
        mask_fn(ImageDraw.Draw(mask), self.S)
        W, H = self.im.size
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        cx, cy = self.S(list(center))
        t = np.clip(np.hypot(xx - cx, yy - cy) / (radius * self.s), 0, 1)[..., None]
        col = np.array(c_in, float) * (1 - t) + np.array(c_out, float) * t
        grad = Image.fromarray(col.astype(np.uint8), "RGBA")
        ly = self.layer()
        ly.paste(grad, (0, 0), mask)
        self.composite(ly)

    def result(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


def star_points(cx, cy, r, n=5, inner=0.4, rot=-90):
    pts = []
    for i in range(2 * n):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def rrect(d, S, box, r, **kw):
    d.rounded_rectangle([S(box[0]), S(box[1]), S(box[2]), S(box[3])], radius=S(r), **kw)


def ellipse(d, S, cx, cy, rx, ry=None, **kw):
    ry = rx if ry is None else ry
    d.ellipse([S(cx - rx), S(cy - ry), S(cx + rx), S(cy + ry)], **kw)


def rot_ellipse_poly(cx, cy, rx, ry, ang_deg, n=36):
    a = math.radians(ang_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return pts


def leaf_poly(cx, cy, length, width, ang_deg, n=24):
    """Leaf (two arcs) centered at (cx, cy), with the long axis at ang_deg."""
    a = math.radians(ang_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for k in range(n + 1):
        t = k / n
        x = (t - 0.5) * length
        y = width * 0.5 * math.sin(math.pi * t) ** 0.8
        pts.append((x, y))
    for k in range(n, -1, -1):
        t = k / n
        x = (t - 0.5) * length
        y = -width * 0.5 * math.sin(math.pi * t) ** 0.8
        pts.append((x, y))
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


# ------------------------------------------------------------------ olympiad badge

def imo_logo():
    W, H = 800, 549
    cv = Canvas(W, H, scale=3)
    cx, cy = 400, 255
    gold, gold_d, gold_l = hexc("#e9b93f"), hexc("#a97b16"), hexc("#f8dc7a")

    # laurel
    def wreath(d, S):
        for side in (-1, 1):
            for k in range(14):
                # position on a circle of radius 228 centered on the shield (from bottom to top)
                ang = math.radians(90 + side * (30 + k * 9.8))
                x, y = cx + 228 * math.cos(ang), cy + 228 * math.sin(ang)
                tang = math.degrees(ang) + 90
                for off, rot in ((-9, -28), (9, 28)):
                    lx, ly_ = x + off * math.cos(ang), y + off * math.sin(ang)
                    pts = leaf_poly(lx, ly_, 52 - k * 0.8, 21, tang + side * rot)
                    d.polygon(S(pts), fill=gold, outline=gold_d)
    cv.draw(wreath)

    # shield: golden ring + blue disk
    cv.paste_gradient(lambda d, S: ellipse(d, S, cx, cy, 176, fill=255), gold_l, gold_d, (cx - 120, cy - 150), (cx + 120, cy + 150))
    cv.paste_radial(lambda d, S: ellipse(d, S, cx, cy, 156, fill=255), hexc("#2c55a0"), hexc("#122a58"), (cx - 30, cy - 50), 190)

    def inner(d, S):
        ellipse(d, S, cx, cy, 132, outline=gold, width=S(4))
        for k in range(24):
            a = math.radians(k * 15)
            ellipse(d, S, cx + 144 * math.cos(a), cy + 144 * math.sin(a), 3.2, fill=hexc("#f4f4f4"))
        for sx in (-1, 1):
            d.polygon(S(star_points(cx + sx * 78, cy + 62, 17, inner=0.45)), fill=gold)
        d.polygon(S(star_points(cx, cy - 98, 19, inner=0.45)), fill=gold)
    cv.draw(inner)

    def pi_sym(d, S):
        f = font(S(190), serif=False)
        d.text((S(cx), S(cy - 4)), "π", font=f, fill=hexc("#fbe7a0"), anchor="mm")
    cv.draw(pi_sym)

    # ribbon
    def ribbon(d, S):
        d.polygon(S([(88, 448), (170, 448), (170, 518), (88, 518), (118, 483)]), fill=hexc("#7d1a24"))
        d.polygon(S([(712, 448), (630, 448), (630, 518), (712, 518), (682, 483)]), fill=hexc("#7d1a24"))
        d.polygon(S([(170, 466), (170, 518), (200, 498)]), fill=hexc("#4e0f16"))
        d.polygon(S([(630, 466), (630, 518), (600, 498)]), fill=hexc("#4e0f16"))
    cv.draw(ribbon)
    cv.paste_gradient(lambda d, S: d.polygon(S([(150, 432), (650, 432), (650, 496), (150, 496)]), fill=255),
                      hexc("#c42a38"), hexc("#8f1b27"), (0, 432), (0, 496))

    def label(d, S):
        f = font(S(44))
        d.text((S(400), S(465)), "MATH OLYMPIAD", font=f, fill=hexc("#ffffff"), anchor="mm")
        d.line(S([(168, 441), (632, 441)]), fill=gold, width=S(2))
        d.line(S([(168, 488), (632, 488)]), fill=gold, width=S(2))
    cv.draw(label)
    return cv.result()


# ------------------------------------------------------------------ social network icons

def social_people():
    W = H = 512
    cv = Canvas(W, H, scale=3)
    cv.paste_gradient(lambda d, S: rrect(d, S, (14, 14, 498, 498), 112, fill=255),
                      hexc("#3a86f5"), hexc("#1a4fbd"), (0, 14), (0, 498))

    def people(d, S):
        # person at the back (smaller, semi-transparent)
        col_b = (255, 255, 255, 150)
        ellipse(d, S, 338, 196, 44, fill=col_b)
        d.pieslice([S(264), S(256), S(412), S(408)], 180, 360, fill=col_b)
        # person in front
        col_f = (255, 255, 255, 255)
        ellipse(d, S, 206, 178, 58, fill=col_f)
        d.pieslice([S(104), S(256), S(308), S(460)], 180, 360, fill=col_f)
        rrect(d, S, (104, 358, 308, 400), 0, fill=col_f)
    cv.draw(people)
    # fixes the bottom edge of the front figure so that it is flat
    return cv.result()


def social_photo():
    W = H = 512
    cv = Canvas(W, H, scale=3)
    # three-color diagonal gradient
    S3 = cv.s
    mask = Image.new("L", cv.im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([14 * S3, 14 * S3, 498 * S3, 498 * S3], radius=112 * S3, fill=255)
    Wp, Hp = cv.im.size
    yy, xx = np.mgrid[0:Hp, 0:Wp].astype(np.float32)
    t = np.clip((xx + yy) / (Wp + Hp), 0, 1)[..., None]
    stops = [(0.0, np.array(hexc("#19b5b0"), float)), (0.5, np.array(hexc("#5a49e6"), float)), (1.0, np.array(hexc("#d23fa8"), float))]
    col = np.zeros((Hp, Wp, 4), float)
    for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:]):
        m = ((t >= t0) & (t <= t1)).astype(float)
        u = np.clip((t - t0) / (t1 - t0), 0, 1)
        col += m * (c0 * (1 - u) + c1 * u)
    ly = cv.layer()
    ly.paste(Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGBA"), (0, 0), mask)
    cv.composite(ly)

    def glyph(d, S):
        w = (255, 255, 255, 255)
        rrect(d, S, (110, 130, 402, 382), 38, outline=w, width=S(22))
        ellipse(d, S, 196, 214, 24, fill=w)                                   # sol
        d.polygon(S([(132, 344), (214, 252), (262, 306), (312, 232), (382, 344)]), fill=w)   # mountains
    cv.draw(glyph)
    return cv.result()


# ------------------------------------------------------------------ virions

def smooth_noise(shape, scale, rng):
    h, w = shape
    small = rng.random((max(2, h // scale + 2), max(2, w // scale + 2))).astype(np.float32)
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(im).astype(np.float32) / 255


def sars_icon():
    W, H = 1400, 1000
    rng = np.random.default_rng(11)
    bg = 96 + 38 * (smooth_noise((H, W), 160, rng) - 0.5) + 22 * (smooth_noise((H, W), 40, rng) - 0.5)
    S = 2
    big = Image.new("L", (W * S, H * S), 0)         # particle mask (glow)
    halo = Image.new("L", (W * S, H * S), 0)
    spikes = Image.new("L", (W * S, H * S), 0)
    parts = [(470, 270, 108), (250, 560, 116), (560, 600, 122), (1090, 640, 118)]
    dg, dh, ds = ImageDraw.Draw(big), ImageDraw.Draw(halo), ImageDraw.Draw(spikes)
    for (cx, cy, r) in parts:
        dh.ellipse([(cx - r - 34) * S, (cy - r - 34) * S, (cx + r + 34) * S, (cy + r + 34) * S], fill=255)
        dg.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=255)
        n = 46
        for k in range(n):
            a = 2 * math.pi * (k + rng.random() * 0.4) / n
            l0, l1 = r - 2, r + 20 + rng.random() * 8
            x0, y0 = cx + l0 * math.cos(a), cy + l0 * math.sin(a)
            x1, y1 = cx + l1 * math.cos(a), cy + l1 * math.sin(a)
            ds.line([x0 * S, y0 * S, x1 * S, y1 * S], fill=255, width=int(3.2 * S))
            ds.ellipse([(x1 - 5.5) * S, (y1 - 5.5) * S, (x1 + 5.5) * S, (y1 + 5.5) * S], fill=255)
    halo = np.asarray(halo.filter(ImageFilter.GaussianBlur(26 * S)).resize((W, H), Image.LANCZOS), float) / 255
    body_m = np.asarray(big.filter(ImageFilter.GaussianBlur(1.2 * S)).resize((W, H), Image.LANCZOS), float) / 255
    spike_m = np.asarray(spikes.filter(ImageFilter.GaussianBlur(1.0 * S)).resize((W, H), Image.LANCZOS), float) / 255
    # inner glow: lighter toward the center, with texture
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    inner = np.zeros((H, W), np.float32)
    for (cx, cy, r) in parts:
        d = np.hypot(xx - cx, yy - cy) / r
        inner = np.maximum(inner, np.clip(1 - d ** 2.2, 0, 1) * (d < 1.05))
    tex = smooth_noise((H, W), 9, rng)
    img = bg * (1 - 0.30 * halo)                                  # dark halo around
    img = img * (1 - body_m) + (172 + 62 * inner + 26 * (tex - 0.5)) * body_m
    img = img * (1 - 0.8 * spike_m) + 168 * 0.8 * spike_m
    img += rng.normal(0, 4.5, img.shape)
    img = np.clip(img, 0, 255).astype(np.uint8)
    rgba = np.stack([img, img, img, np.full_like(img, 255)], axis=-1)
    return Image.fromarray(rgba, "RGBA")


# ------------------------------------------------------------------ stage illustration

def tao_imo():
    W, H = 630, 720
    cv = Canvas(W, H, scale=2)
    S2 = cv.s

    # background: blue curtain with folds, sign, stage floor
    def stage(d, S):
        d.rectangle([0, 0, S(W), S(H)], fill=hexc("#1b2a50"))
    cv.draw(stage)
    Wp, Hp = cv.im.size
    yy, xx = np.mgrid[0:Hp, 0:Wp].astype(np.float32)
    folds = 0.5 + 0.5 * np.sin(xx / S2 / 14.0)
    spot = np.clip(1 - np.hypot(xx / S2 - 330, yy / S2 - 330) / 430, 0, 1)
    base = np.array(hexc("#1b2a50")[:3], float)
    arr = base[None, None, :] * (0.78 + 0.18 * folds[..., None]) + 90 * spot[..., None] * np.array([0.5, 0.55, 0.8])[None, None, :]
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    cv.im = Image.fromarray(np.dstack([arr, np.full(arr.shape[:2], 255, np.uint8)]), "RGBA")

    def banner(d, S):
        rrect(d, S, (60, 38, 570, 112), 14, fill=hexc("#f3efe4"), outline=hexc("#c9a44a"), width=S(4))
        d.text((S(315), S(75)), "MATH OLYMPIAD", font=font(S(40)), fill=hexc("#1b2a50"), anchor="mm")
        for sx in (84, 546):
            d.polygon(S(star_points(sx, 75, 11, inner=0.45)), fill=hexc("#c9a44a"))
    cv.draw(banner)

    def floor(d, S):
        d.rectangle([0, S(520), S(W), S(H)], fill=hexc("#7a5636"))
        for k in range(8):
            y = 520 + k * 28 + (k * k) * 1.2
            d.line([0, S(y), S(W), S(y)], fill=hexc("#654529"), width=S(2))
        d.rectangle([0, S(514), S(W), S(524)], fill=hexc("#4e351e"))
    cv.draw(floor)

    skin1, skin2 = hexc("#e8b48f"), hexc("#d9a07a")

    def person(d, S, x, y_base, scale, suit, shirt, hair, skin, tie=None, bow=0.0):
        """Flat standing figure: feet at y_base, shoulder width ~ 120*scale."""
        sc = scale
        # shadow
        d.ellipse(S([x - 70 * sc, y_base - 8, x + 70 * sc, y_base + 12]), fill=(0, 0, 0, 90))
        # legs
        for dx in (-22, 22):
            d.rounded_rectangle(S([x + dx * sc - 17 * sc, y_base - 190 * sc, x + dx * sc + 17 * sc, y_base - 8]), radius=S(8 * sc), fill=suit)
            d.rounded_rectangle(S([x + dx * sc - 22 * sc, y_base - 16, x + dx * sc + 24 * sc, y_base + 2]), radius=S(8), fill=hexc("#16181d"))
        # torso
        top = y_base - 400 * sc
        d.rounded_rectangle(S([x - 62 * sc, top + 60 * sc, x + 62 * sc, y_base - 170 * sc]), radius=S(26 * sc), fill=suit)
        # shirt + tie
        d.polygon(S([(x - 18 * sc, top + 64 * sc), (x + 18 * sc, top + 64 * sc), (x, top + 150 * sc)]), fill=shirt)
        if tie:
            d.polygon(S([(x - 7 * sc, top + 72 * sc), (x + 7 * sc, top + 72 * sc), (x + 9 * sc, top + 140 * sc), (x, top + 156 * sc), (x - 9 * sc, top + 140 * sc)]), fill=tie)
        # neck and head
        d.rectangle(S([x - 13 * sc, top + 40 * sc, x + 13 * sc, top + 68 * sc]), fill=skin)
        hx, hy = x + bow * 14 * sc, top + 8 * sc + bow * 10 * sc
        ellipse(d, S, hx, hy, 40 * sc, 44 * sc, fill=skin)
        d.pieslice(S([hx - 42 * sc, hy - 50 * sc, hx + 42 * sc, hy + 34 * sc]), 180, 360, fill=hair)
        d.rectangle(S([hx - 41 * sc, hy - 14 * sc, hx + 41 * sc, hy - 6 * sc]), fill=hair)
        ellipse(d, S, hx + 14 * sc, hy + 4 * sc, 3.2 * sc, fill=hexc("#2a2020"))
        ellipse(d, S, hx - 14 * sc, hy + 4 * sc, 3.2 * sc, fill=hexc("#2a2020"))
        d.arc(S([hx - 10 * sc, hy + 12 * sc, hx + 10 * sc, hy + 26 * sc]), 20, 160, fill=hexc("#8a4a3a"), width=S(2))
        return top

    # presenter (right)
    cv.draw(lambda d, S: person(d, S, 448, 604, 1.0, hexc("#454b57"), hexc("#f4f4f4"), hexc("#b9b9b9"), skin2, tie=hexc("#2a3f8f")))
    # young man (left, shorter)
    cv.draw(lambda d, S: person(d, S, 196, 604, 0.78, hexc("#16224a"), hexc("#f7f7f7"), hexc("#1e1a18"), skin1, tie=hexc("#b3262f"), bow=1.0))

    def arms(d, S):
        # the presenter's arm toward the young man, handing over the medal
        d.line([S(404), S(270), S(276), S(372)], fill=hexc("#454b57"), width=S(30))
        ellipse(d, S, 266, 380, 13, fill=skin2)
        # the young man's arms at the sides
        d.line([S(160), S(360), S(150), S(442)], fill=hexc("#16224a"), width=S(22))
        d.line([S(236), S(360), S(244), S(442)], fill=hexc("#16224a"), width=S(22))
        ellipse(d, S, 149, 450, 9, fill=skin1)
        ellipse(d, S, 245, 450, 9, fill=skin1)
    cv.draw(arms)

    def medal(d, S):
        # V-shaped ribbon (red-white-blue) over the chest and golden disk
        d.polygon(S([(176, 346), (196, 346), (206, 412), (192, 416)]), fill=hexc("#c8283a"))
        d.polygon(S([(206, 346), (226, 346), (204, 416), (192, 412)]), fill=hexc("#2a4fa8"))
        d.polygon(S([(196, 346), (206, 346), (200, 396)]), fill=hexc("#f4f4f4"))
        ellipse(d, S, 198, 432, 22, fill=hexc("#d9a520"), outline=hexc("#8c6410"), width=S(3))
        ellipse(d, S, 198, 432, 15, outline=hexc("#f7da6a"), width=S(3))
        d.polygon(S(star_points(198, 432, 9, inner=0.45)), fill=hexc("#f7da6a"))
        d.arc(S([181, 415, 203, 437]), 200, 280, fill=hexc("#fff3b0"), width=S(3))
    cv.draw(medal)

    # flashes
    def sparkles(d, S):
        for (x, y, r) in ((120, 250, 12), (300, 220, 9), (340, 410, 8)):
            d.polygon(S(star_points(x, y, r, n=4, inner=0.28)), fill=hexc("#ffe58a"))
    cv.draw(sparkles)
    return cv.result().convert("RGB")


MAKERS = {
    "imo_logo": imo_logo,
    "facebook_logo": social_people,
    "instagram_logo": social_photo,
    "sars_icon": sars_icon,
    "TerryTaoIMO": tao_imo,
}


def main():
    names = sys.argv[1:] or list(MAKERS)
    OUT.mkdir(parents=True, exist_ok=True)
    for name in names:
        im = MAKERS[name]()
        im.save(OUT / f"{name}.png", optimize=True)
        print("escrito", OUT / f"{name}.png", im.size)


if __name__ == "__main__":
    main()
