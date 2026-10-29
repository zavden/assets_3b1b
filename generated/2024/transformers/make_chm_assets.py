"""Placeholders for the private assets of _2024/transformers/chm.py (they lived in Grant's Dropbox).

Creates, where the code looks for them by name:
  _lib/assets/raster_images/
    JohnRFirth.png, RiverBank.png, FederalReserve.png, CHMTopText.png, CHM_Exterior.jpeg,
    Chapter5_TN3.png          boxes with the name, made with _tools/placeholder.py
    HumanAIScript.png,        the "script sheet" that rolls up / tears in PartialScript: a cream
    HumanAIScriptTorn.png     page with the prompt text, drawn with PIL (the second ends in
                              a torn edge and is transparent below)
  _lib/assets/svg_images/
    Bot.svg                   robot head: outline, screen (hole) and two eyes in a single stroke,
                              as BadChatBot.get_bot expects (subpaths 0 and 1 = outline and screen,
                              2 onward = eyes; manimgl delivers them in the reverse order of the file)
    comp_worker.svg           silhouette of a person in front of a computer (RLHFWorker/RLHFWorkers)
    JaggedCurl1.svg, JaggedCurl2.svg   open "curled" curves that PartialScript extrudes into surfaces
    TearOff.svg               strip with a jagged top edge
    GenericComputer.svg, History.svg, Museum.svg   icons of ThreeWordsToOne

Usage: python make_chm_assets.py"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]  # .../_lib
RASTER = LIB / "assets" / "raster_images"
SVG = LIB / "assets" / "svg_images"
sys.path.insert(0, str(LIB.parent / "_tools"))
from placeholder import make_image, font  # noqa: E402

# (file in raster_images/, label, size, background color)
IMAGES = [
    ("JohnRFirth.png", "John R. Firth", "800x1000", "#3a3a3a"),
    ("RiverBank.png", "River bank", "1200x800", "#2f4535"),
    ("FederalReserve.png", "Federal Reserve", "1200x800", "#36384a"),
    ("CHMTopText.png", "CHM top text", "1920x1080", "#2b3a4a"),
    ("CHM_Exterior.jpeg", "CHM exterior", "1600x900", "#3a2b4a"),
    ("Chapter5_TN3.png", "Chapter5 TN3", "1280x720", "#2b3a4a"),
]

PAGE_BG = "#FCF5E5"
PROMPT_LINES = [
    ("Human:", "#1C6FB0"),
    ("Can you explain the history of", "#1a1a1a"),
    ("transistors and how they're relevant", "#1a1a1a"),
    ("to computers? What is a transistor,", "#1a1a1a"),
    ("and how exactly is it used to", "#1a1a1a"),
    ("perform computations?", "#1a1a1a"),
    ("", None),
    ("AI assistant:", "#2E9C8F"),
]


def tear_edge(width, y0, seed, amplitude=22, step=14):
    rng = random.Random(seed)
    pts, x = [], 0
    while x < width:
        pts.append((x, y0 + rng.uniform(-amplitude, amplitude)))
        x += step + rng.uniform(-4, 4)
    pts.append((width, y0 + rng.uniform(-amplitude, amplitude)))
    return pts


def make_script_page(out, torn, size=(1200, 1180)):
    """Cream page with the prompt. torn=True: ends in a torn edge and is transparent below."""
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    tear_y = 880
    edge = tear_edge(w, tear_y, seed=3)
    if torn:
        d.polygon([(0, 0), (w, 0), *edge[::-1]], fill=PAGE_BG)
    else:
        d.rectangle([0, 0, w, h], fill=PAGE_BG)
    f = font(66)
    y = 70
    for text, color in PROMPT_LINES:
        if text:
            d.text((70, y), text, font=f, fill=color)
        y += 96
    if not torn:
        # What comes next: gray placeholder lines and the torn edge
        rng = random.Random(5)
        for i in range(4):
            length = rng.uniform(0.55, 0.9) * (w - 140)
            d.rounded_rectangle([70, tear_y + 80 + i * 56, 70 + length, tear_y + 96 + i * 56], radius=8, fill="#cfc7b6")
        d.line(edge, fill="#8a8272", width=3)
        d.text((w - 70, h - 40), "[página de relleno]", font=font(30), fill="#8a8272", anchor="rm")
    else:
        d.line(edge, fill="#8a8272", width=3)
        d.text((w - 70, 40), "[página de relleno]", font=font(30), fill="#8a8272", anchor="rm")
    img.save(out)


# ---------------------------------------------------------------- SVG

def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{body}</svg>\n')


def rounded_rect_path(x0, y0, x1, y1, r, clockwise=True):
    """Rounded rectangle as a closed stroke; clockwise (on screen) or counterclockwise."""
    if clockwise:
        return (f"M {x0 + r} {y0} L {x1 - r} {y0} A {r} {r} 0 0 1 {x1} {y0 + r} L {x1} {y1 - r} "
                f"A {r} {r} 0 0 1 {x1 - r} {y1} L {x0 + r} {y1} A {r} {r} 0 0 1 {x0} {y1 - r} "
                f"L {x0} {y0 + r} A {r} {r} 0 0 1 {x0 + r} {y0} Z")
    return (f"M {x0 + r} {y0} A {r} {r} 0 0 0 {x0} {y0 + r} L {x0} {y1 - r} A {r} {r} 0 0 0 {x0 + r} {y1} "
            f"L {x1 - r} {y1} A {r} {r} 0 0 0 {x1} {y1 - r} L {x1} {y0 + r} A {r} {r} 0 0 0 {x1 - r} {y0} Z")


def circle_path(cx, cy, r, clockwise=True):
    sweep = 1 if clockwise else 0
    return (f"M {cx - r} {cy} A {r} {r} 0 1 {sweep} {cx + r} {cy} A {r} {r} 0 1 {sweep} {cx - r} {cy} Z")


def make_bot():
    # NOTE: manimgl delivers the subpaths of a <path> in the reverse order of the file; BadChatBot.get_bot
    # expects [outline, screen (hole), eye, eye], so they are written backwards: eyes, screen, outline.
    head = " ".join([
        circle_path(240, 215, 24, clockwise=True),
        circle_path(160, 215, 24, clockwise=True),
        rounded_rect_path(95, 145, 305, 295, 35, clockwise=False),
        rounded_rect_path(60, 110, 340, 330, 55, clockwise=True),
    ])
    extras = (
        f'<path d="{rounded_rect_path(30, 190, 52, 250, 8)}"/>'      # ears
        f'<path d="{rounded_rect_path(348, 190, 370, 250, 8)}"/>'
        '<path d="M 192 110 L 192 62 L 208 62 L 208 110 Z"/>'        # antenna
        f'<path d="{circle_path(200, 48, 17)}"/>'
    )
    return svg_doc(400, 400, f'<g fill="#ffffff" stroke="none"><path d="{head}"/>{extras}</g>')


def make_comp_worker():
    parts = [
        circle_path(110, 78, 32),                                                       # head
        "M 66 128 Q 110 108 154 128 L 170 214 L 62 214 Z",                              # torso
        "M 148 140 L 222 186 L 210 204 L 134 160 Z",                                    # arm toward the keyboard
        rounded_rect_path(52, 222, 180, 240, 8),                                        # seat
        "M 108 242 L 120 242 L 120 282 L 108 282 Z",                                    # foot of the chair
        rounded_rect_path(80, 282, 150, 292, 4),                                        # base of the chair
        rounded_rect_path(196, 196, 392, 210, 4),                                       # desk
        "M 212 210 L 226 210 L 226 286 L 212 286 Z",                                    # legs
        "M 366 210 L 380 210 L 380 286 L 366 286 Z",
        rounded_rect_path(232, 96, 356, 184, 8) + " " + rounded_rect_path(242, 106, 346, 174, 4, clockwise=False),  # monitor
        "M 288 184 L 300 184 L 300 196 L 288 196 Z",                                    # support
        rounded_rect_path(214, 186, 270, 194, 3),                                       # keyboard
    ]
    body = "".join(f'<path d="{p}"/>' for p in parts)
    return svg_doc(420, 300, f'<g fill="#ffffff" stroke="none">{body}</g>')


def curl_points(kind, seed):
    rng = random.Random(seed)
    pts = []
    if kind == 1:
        # Flat section that curls upward into a closing spiral
        flat = [(x, 0.0) for x in np_linspace(0, 6, 40)]
        pts += flat
        r0, x0 = 1.6, 6.0
        n = 160
        for i in range(1, n + 1):
            t = i / n
            theta = -math.pi / 2 + 3.2 * math.pi * t
            r = r0 * (1 - 0.62 * t)
            pts.append((x0 + r * math.cos(theta), r0 + r * math.sin(theta)))
    else:
        # Flat section that undulates and ends in a more open curl
        for x in np_linspace(0, 4, 30):
            pts.append((x, 0.0))
        for i in range(1, 140):
            t = i / 140
            x = 4 + 4.5 * t
            y = 1.1 * math.sin(2.2 * math.pi * t) * (0.4 + t)
            pts.append((x, y))
        r0, (x0, y0) = 1.0, pts[-1]
        for i in range(1, 100):
            t = i / 100
            theta = -math.pi / 2 + 1.6 * math.pi * t
            r = r0 * (1 - 0.35 * t)
            pts.append((x0 + r * math.cos(theta), y0 + r0 + r * math.sin(theta)))
    jag = 0.035
    return [(x + rng.uniform(-jag, jag), y + rng.uniform(-jag, jag)) for x, y in pts]


def np_linspace(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def make_curl(kind):
    pts = curl_points(kind, seed=kind)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    s = 60
    x_min, y_min, y_max = min(xs), min(ys), max(ys)
    d = "M " + " L ".join(f"{(x - x_min) * s + 20:.2f} {(y_max - y) * s + 20:.2f}" for x, y in pts)
    w = (max(xs) - x_min) * s + 40
    h = (y_max - y_min) * s + 40
    return svg_doc(round(w), round(h), f'<path d="{d}" fill="none" stroke="#ffffff" stroke-width="4"/>')


def make_tear_off():
    rng = random.Random(7)
    top, x = [], 0
    while x < 400:
        top.append((x, 20 + (14 if (len(top) % 2) else 0) + rng.uniform(-3, 3)))
        x += 11
    d = "M 0 120 L " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in top) + " L 400 120 Z"
    return svg_doc(400, 120, f'<path d="{d}" fill="#ffffff" stroke="none"/>')


def make_generic_computer():
    parts = [
        rounded_rect_path(30, 40, 270, 190, 14) + " " + rounded_rect_path(46, 56, 254, 174, 6, clockwise=False),
        "M 130 190 L 170 190 L 178 230 L 122 230 Z",
        rounded_rect_path(90, 230, 210, 244, 6),
        rounded_rect_path(60, 262, 240, 290, 8) + " " + rounded_rect_path(72, 270, 228, 282, 3, clockwise=False),
    ]
    return svg_doc(300, 320, '<g fill="#ffffff" stroke="none">' + "".join(f'<path d="{p}"/>' for p in parts) + "</g>")


def make_history():
    cx, cy = 150, 150
    ring = circle_path(cx, cy, 120, True) + " " + circle_path(cx, cy, 100, False)
    ticks = "".join(
        f'<path d="M {cx - 4} {cy - 96} L {cx + 4} {cy - 96} L {cx + 4} {cy - 80} L {cx - 4} {cy - 80} Z" '
        f'transform="rotate({a} {cx} {cy})"/>'
        for a in range(0, 360, 90)
    )
    hands = (f'<path d="M {cx - 5} {cy + 14} L {cx - 5} {cy - 70} L {cx + 5} {cy - 70} L {cx + 5} {cy + 14} Z"/>'
             f'<path d="M {cx - 5} {cy - 5} L {cx + 60} {cy - 5} L {cx + 60} {cy + 5} L {cx - 5} {cy + 5} Z" '
             f'transform="rotate(35 {cx} {cy})"/>')
    return svg_doc(300, 300, f'<g fill="#ffffff" stroke="none"><path d="{ring}"/>{ticks}{hands}</g>')


def make_museum():
    parts = ["M 150 30 L 275 100 L 25 100 Z"]                                          # pediment
    parts.append("M 35 108 L 265 108 L 265 124 L 35 124 Z")                           # architrave
    for i in range(5):
        x = 50 + i * 47
        parts.append(f"M {x} 132 L {x + 24} 132 L {x + 24} 222 L {x} 222 Z")          # columns
    parts += ["M 35 230 L 265 230 L 265 246 L 35 246 Z", "M 20 252 L 280 252 L 280 270 L 20 270 Z"]
    return svg_doc(300, 300, '<g fill="#ffffff" stroke="none">' + "".join(f'<path d="{p}"/>' for p in parts) + "</g>")


def main():
    RASTER.mkdir(parents=True, exist_ok=True)
    SVG.mkdir(parents=True, exist_ok=True)
    for name, label, size, bg in IMAGES:
        w, h = map(int, size.split("x"))
        make_image(RASTER / name, label, (w, h), bg)
    make_script_page(RASTER / "HumanAIScript.png", torn=False)
    make_script_page(RASTER / "HumanAIScriptTorn.png", torn=True)
    for name, text in [
        ("Bot.svg", make_bot()),
        ("comp_worker.svg", make_comp_worker()),
        ("JaggedCurl1.svg", make_curl(1)),
        ("JaggedCurl2.svg", make_curl(2)),
        ("TearOff.svg", make_tear_off()),
        ("GenericComputer.svg", make_generic_computer()),
        ("History.svg", make_history()),
        ("Museum.svg", make_museum()),
    ]:
        (SVG / name).write_text(text, encoding="utf-8")
    print("assets de chm.py listos")


if __name__ == "__main__":
    main()
