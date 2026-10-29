"""Generates the placeholder assets of cross_entropy that are not in the public repo
(they lived in Grant's Dropbox) and converts those that are into formats that
manimgl does not read (.ai -> .svg, .tif -> .png).

Usage (from any folder):
    python make_cross_entropy_placeholders.py

Outputs (next to this script):
    arrow.svg, file_icon.svg, scottish_flag.svg   faithful conversions of images/*.ai (pdftocairo)
    Stationary.png                                faithful conversion of images/lunar_rover_assets/Stationary.tif
    Stationary_fade_right.png                     APPROXIMATION: Stationary with a gradient to transparent on the right side
    BigModel.png                                  PLACEHOLDER: large neural network (the original, "Paul Assets/BigModel.png", is private)
    Sprite_Vertical.png, Sprite_Horizontal.png    PLACEHOLDER: top-down view of the robot
    far_away_moon.png                             PLACEHOLDER: lunar surface texture (tileable)
    pi_creature_mission_control.png               PLACEHOLDER: pi creature at a console
    flags/<name>.svg                              PLACEHOLDER: simple hand-drawn flags
    clockwise.svg                                 PLACEHOLDER: "turn clockwise" icon (the robot's fifth instruction)
    Tree.svg                                      PLACEHOLDER: drawing of a tree (background to trace over in TreeEditor)"""
import os
import math
import random
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
# The video's images/ folder in a clone of 3b1b/videos (THREEB1B_VIDEOS or, by default, next to converted/)
SRC = Path(os.environ.get("THREEB1B_VIDEOS", HERE.parents[5] / "videos")) / "_2026" / "cross_entropy" / "images"
PI_SVG = HERE.parent.parent.parent / "PiCreature" / "happy.svg"
FONT = "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf"


def font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except Exception:
        return ImageFont.load_default()


# ------------------------------------------------------------ faithful conversions
def convert_real_assets():
    for name in ["arrow", "file_icon", "scottish_flag"]:
        subprocess.run(["pdftocairo", "-svg", str(SRC / f"{name}.ai"), str(HERE / f"{name}.svg")], check=True)
    # The Scottish flag comes with a bleed rectangle larger than the page: it is cropped to the page
    flag = HERE / "scottish_flag.svg"
    flag.write_text(flag.read_text().replace('<rect x="-40" y="-30" width="480" height="360"', '<rect x="0" y="0" width="400" height="300"'))
    # The same flag serves for "Scottish Gaelic" (the name language_tree.py looks it up by)
    (HERE / "flags").mkdir(exist_ok=True)
    (HERE / "flags" / "Scottish Gaelic.svg").write_text(flag.read_text())
    im = Image.open(SRC / "lunar_rover_assets" / "Stationary.tif").convert("RGB")
    im.save(HERE / "Stationary.png")
    # Stationary_fade_right.png: it is not in the repo; it is approximated by fading the right edge to transparent
    rgba = np.array(im.convert("RGBA")).astype(float)
    W = rgba.shape[1]
    x = np.arange(W) / W
    alpha = np.clip((0.82 - x) / 0.14, 0, 1)
    rgba[..., 3] = rgba[..., 3] * alpha[None, :]
    Image.fromarray(rgba.astype(np.uint8), "RGBA").save(HERE / "Stationary_fade_right.png")


# ------------------------------------------------------------ placeholder: top-down sprite
def draw_rover(vertical=True, size=512):
    S = 4  # supersampling
    W = size * S
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    teal = (47, 160, 170, 255)
    dark = (20, 24, 28, 255)
    metal = (200, 205, 210, 255)

    def rr(box, r, **kw):
        d.rounded_rectangle([c * S for c in box], radius=r * S, **kw)

    # wheels (corners)
    for cx in (70, 442):
        for cy in (95, 417):
            rr((cx - 38, cy - 62, cx + 38, cy + 62), 14, fill=dark, outline=(70, 70, 70, 255), width=3 * S)
            for k in range(-3, 4):
                y = cy + k * 15
                d.line([(cx - 34) * S, y * S, (cx + 34) * S, y * S], fill=(60, 60, 60, 255), width=2 * S)
    # axles
    d.rectangle([108 * S, 90 * S, 404 * S, 100 * S], fill=metal)
    d.rectangle([108 * S, 412 * S, 404 * S, 422 * S], fill=metal)
    # body
    rr((120, 70, 392, 442), 40, fill=teal, outline=(25, 100, 110, 255), width=4 * S)
    rr((150, 105, 362, 260), 24, fill=(235, 238, 240, 255))      # panel solar
    for k in range(1, 4):
        d.line([(150 + 53 * k) * S, 105 * S, (150 + 53 * k) * S, 260 * S], fill=(120, 130, 140, 255), width=2 * S)
    d.line([150 * S, 182 * S, 362 * S, 182 * S], fill=(120, 130, 140, 255), width=2 * S)
    # camera / eyes
    for cx in (215, 297):
        d.ellipse([(cx - 28) * S, 300 * S, (cx + 28) * S, 356 * S], fill=(240, 240, 245, 255), outline=dark, width=3 * S)
        d.ellipse([(cx - 14) * S, 314 * S, (cx + 14) * S, 342 * S], fill=dark)
    # base of the antenna, at the lower right (it coincides with the scene's "blinker")
    d.ellipse([(346 - 22) * S, (413 - 22) * S, (346 + 22) * S, (413 + 22) * S], fill=(220, 150, 60, 255), outline=dark, width=3 * S)
    d.ellipse([(346 - 8) * S, (413 - 8) * S, (346 + 8) * S, (413 + 8) * S], fill=(250, 240, 200, 255))
    im = im.resize((size, size), Image.LANCZOS)
    d2 = ImageDraw.Draw(im)
    d2.text((size // 2, 24), "[robot de relleno]", font=font(22), fill=(230, 230, 230, 255), anchor="mm")
    if not vertical:
        im = im.rotate(90)
    return im


# ------------------------------------------------------------ placeholder: lunar surface
def make_moon(size=512, seed=3):
    rng = np.random.default_rng(seed)
    # tileable noise: sum of periodic noises at several scales (FFT)
    def periodic_noise(n, beta):
        fx = np.fft.fftfreq(n)[:, None]
        fy = np.fft.fftfreq(n)[None, :]
        f = np.sqrt(fx**2 + fy**2)
        f[0, 0] = 1
        spec = (rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))) / f**beta
        spec[0, 0] = 0
        x = np.fft.ifft2(spec).real
        return (x - x.min()) / (x.max() - x.min())

    base = periodic_noise(size, 1.6)
    fine = periodic_noise(size, 0.8)
    h = 0.75 * base + 0.25 * fine
    # periodic craters
    yy, xx = np.mgrid[0:size, 0:size]
    for _ in range(40):
        cx, cy = rng.integers(0, size, 2)
        r = rng.uniform(8, 48)
        dx = (xx - cx + size / 2) % size - size / 2
        dy = (yy - cy + size / 2) % size - size / 2
        dist = np.sqrt(dx**2 + dy**2) / r
        bowl = np.where(dist < 1, -0.18 * (1 - dist**2), 0)
        rim = 0.10 * np.exp(-((dist - 1.05) ** 2) / 0.012)
        h = h + bowl + rim
    gx = np.roll(h, -1, 1) - np.roll(h, 1, 1)
    gy = np.roll(h, -1, 0) - np.roll(h, 1, 0)
    shade = np.clip(0.55 + 6.0 * (gx + gy), 0.15, 1.0)
    gray = np.clip(70 + 120 * shade * (0.6 + 0.4 * h), 0, 255)
    rgb = np.stack([gray, gray * 0.98, gray * 0.95], axis=-1).astype(np.uint8)
    return Image.fromarray(rgb, "RGB")


# ------------------------------------------------------------ placeholder: pi creature at a console
def make_mission_control(size=700):
    out = HERE / "pi_creature_mission_control.png"
    pi_png = HERE / "_pi_tmp.png"
    subprocess.run(["inkscape", str(PI_SVG), "--export-type=png", f"--export-filename={pi_png}", "-h", str(int(size * 0.62))],
                   check=True, capture_output=True)
    pi = Image.open(pi_png).convert("RGBA")
    pi_png.unlink()
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # pi creature behind the console
    im.alpha_composite(pi, ((size - pi.width) // 2, int(size * 0.10)))
    d = ImageDraw.Draw(im)
    # monitor
    mw, mh = int(size * 0.52), int(size * 0.28)
    mx, my = (size - mw) // 2, int(size * 0.44)
    d.rounded_rectangle([mx, my, mx + mw, my + mh], radius=14, fill=(25, 30, 38, 255), outline=(150, 160, 170, 255), width=5)
    d.rounded_rectangle([mx + 14, my + 14, mx + mw - 14, my + mh - 14], radius=8, fill=(12, 70, 60, 255))
    rng = random.Random(1)
    for i in range(6):
        y = my + 28 + i * 20
        d.line([mx + 28, y, mx + 28 + rng.randint(80, mw - 80), y], fill=(120, 255, 190, 255), width=4)
    # mesa
    ty = int(size * 0.74)
    d.rounded_rectangle([int(size * 0.04), ty, int(size * 0.96), ty + int(size * 0.14)], radius=16, fill=(70, 78, 90, 255), outline=(150, 160, 170, 255), width=5)
    for i in range(10):
        x = int(size * 0.12) + i * int(size * 0.075)
        d.ellipse([x, ty + 28, x + 24, ty + 52], fill=[(230, 80, 80, 255), (240, 200, 60, 255), (90, 200, 120, 255)][i % 3])
    d.text((size // 2, int(size * 0.95)), "[control de misión: imagen de relleno]", font=font(22), fill=(230, 230, 230, 255), anchor="mm")
    im.save(out)


# ------------------------------------------------------------ placeholder: simple flags
def _flag(body, w=300, h=200):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}pt" height="{h}pt" viewBox="0 0 {w} {h}">\n'
            f'{body}\n</svg>\n')


def _stripes(colors, vertical=False, w=300, h=200):
    n = len(colors)
    out = []
    for i, c in enumerate(colors):
        if vertical:
            out.append(f'<rect x="{w * i / n}" y="0" width="{w / n + 0.5}" height="{h}" fill="{c}"/>')
        else:
            out.append(f'<rect x="0" y="{h * i / n}" width="{w}" height="{h / n + 0.5}" fill="{c}"/>')
    return "\n".join(out)


def make_flags():
    flags = {
        "Czech": _stripes(["#FFFFFF", "#D7141A"]) + '\n<polygon points="0,0 150,100 0,200" fill="#11457E"/>',
        "English": '<rect width="300" height="200" fill="#FFFFFF"/>\n<rect x="127" y="0" width="46" height="200" fill="#CE1124"/>\n<rect x="0" y="77" width="300" height="46" fill="#CE1124"/>',
        "French": _stripes(["#0055A4", "#FFFFFF", "#EF4135"], vertical=True),
        "German": _stripes(["#000000", "#DD0000", "#FFCE00"]),
        "Italian": _stripes(["#009246", "#FFFFFF", "#CE2B37"], vertical=True),
        "Polish": _stripes(["#FFFFFF", "#DC143C"]),
        "Spanish": '<rect width="300" height="200" fill="#AA151B"/>\n<rect y="50" width="300" height="100" fill="#F1BF00"/>',
        "Swedish": '<rect width="300" height="200" fill="#006AA7"/>\n<rect x="90" y="0" width="40" height="200" fill="#FECC00"/>\n<rect x="0" y="80" width="300" height="40" fill="#FECC00"/>',
        # Very simplified Welsh dragon (circle + tail) over white/green
        "Welsh": _stripes(["#FFFFFF", "#00AB39"]) + '\n<ellipse cx="150" cy="100" rx="55" ry="32" fill="#D30731"/>\n<polygon points="110,100 60,60 100,125" fill="#D30731"/>\n<polygon points="190,100 245,70 205,125" fill="#D30731"/>\n<circle cx="188" cy="85" r="6" fill="#FFFFFF"/>',
    }
    (HERE / "flags").mkdir(exist_ok=True)
    for name, body in flags.items():
        (HERE / "flags" / f"{name}.svg").write_text(_flag(body))


# ------------------------------------------------------------ placeholder: large neural network
def make_big_model(w=1200, h=800):
    rng = random.Random(5)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    layers = [6, 9, 12, 12, 9, 6]
    xs = [int(w * (0.08 + 0.84 * i / (len(layers) - 1))) for i in range(len(layers))]
    pts = []
    for x, n in zip(xs, layers):
        ys = [int(h * (0.1 + 0.8 * (j + 0.5) / n)) for j in range(n)]
        pts.append([(x, y) for y in ys])
    for a, b in zip(pts, pts[1:]):
        for p in a:
            for q in b:
                if rng.random() < 0.55:
                    d.line([p, q], fill=(110, 130, 170, 110), width=2)
    for layer in pts:
        for (x, y) in layer:
            c = rng.choice([(80, 150, 200, 255), (60, 170, 160, 255), (190, 140, 70, 255)])
            d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=c, outline=(230, 230, 235, 255), width=3)
    d.text((w // 2, h - 22), "[modelo grande: imagen de relleno]", font=font(30), fill=(230, 230, 230, 255), anchor="mm")
    im.save(HERE / "BigModel.png")


def make_clockwise_svg():
    """Clockwise circular arrow (filled silhouette, like arrow.svg)."""
    cx = cy = 250
    r_out, r_in = 150, 105
    r_mid = (r_out + r_in) / 2
    a0, a1 = math.radians(-70), math.radians(200)   # in SVG (y down) an increasing angle is clockwise
    n = 60
    outer = [(cx + r_out * math.cos(a0 + (a1 - a0) * i / n), cy + r_out * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    inner = [(cx + r_in * math.cos(a0 + (a1 - a0) * i / n), cy + r_in * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n, -1, -1)]
    tx, ty = -math.sin(a1), math.cos(a1)            # tangent (turning direction) at the end of the arc
    rx, ry = math.cos(a1), math.sin(a1)             # radial
    bx, by = cx + r_mid * rx, cy + r_mid * ry
    head = [(bx + 48 * rx, by + 48 * ry), (bx + 85 * tx, by + 85 * ty), (bx - 48 * rx, by - 48 * ry)]
    pts = outer + [head[0], head[1], head[2]] + inner
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    (HERE / "clockwise.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="500pt" height="500pt" viewBox="0 0 500 500">\n'
        f'<path d="{d}" fill="#F5EB13" fill-opacity="1"/>\n</svg>\n')


def make_tree_svg():
    """Branching binary tree (white strokes, no fill) that serves as the 'drawing of the language family'."""
    w, h = 1000, 700
    segs = []

    def branch(x, y, length, angle, depth):
        if depth == 0:
            return
        x2 = x + length * math.cos(angle)
        y2 = y + length * math.sin(angle)
        segs.append(f"M {x:.1f} {y:.1f} L {x2:.1f} {y2:.1f}")
        branch(x2, y2, length * 0.72, angle - 0.42, depth - 1)
        branch(x2, y2, length * 0.72, angle + 0.42, depth - 1)

    branch(40, h / 2, 190, 0.0, 7)
    d = " ".join(segs)
    (HERE / "Tree.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}pt" height="{h}pt" viewBox="0 0 {w} {h}">\n'
        f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="3"/>\n</svg>\n')


def main():
    convert_real_assets()
    make_tree_svg()
    make_clockwise_svg()
    make_big_model()
    make_flags()
    (HERE / "Sprite_Vertical.png").unlink(missing_ok=True)
    draw_rover(True).save(HERE / "Sprite_Vertical.png")
    draw_rover(False).save(HERE / "Sprite_Horizontal.png")
    make_moon().save(HERE / "far_away_moon.png")
    make_mission_control()


if __name__ == "__main__":
    main()
