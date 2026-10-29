"""Placeholders for the private assets of _2024/transformers/supplements.py (they lived in Grant's Dropbox).

Creates, where the code looks for them by name:
  _lib/assets/raster_images/
    Zoolander.png                     (DifferentUsesOfModel) placeholder box
    nn1_thumbnail.png ... nn4_...     (GamePlan) placeholder thumbnails of chapters 1-4 of the series
    Chapter5/6/7.png                  (GamePlan) placeholder thumbnails of chapters 5-7; in the
                                      original they were Grant's Dropbox paths (Thumbnails/Chapter{n}),
                                      which _lib resolves by name
    EmbeddingStill.jpg                (EmbeddingLabel) placeholder background (the scene leaves it commented out;
                                      Dropbox path resolved by name)
    NetworkEnd.png                    (NetworkEndAnnotation) "fake" capture of the end of the network: the
                                      phrase "Harry Potter ... least favourite Professor" at the top and a
                                      probability bar for "Snape", placed where the scene
                                      draws its rectangles
    AttentionPaper.png                (HighlightAttentionTitle) placeholder first page of a paper,
                                      with the title "Attention is All You Need" at the top
  _lib/assets/svg_images/
    OpenAI.svg                        own GENERIC logo (ring with a four-pointed star);
                                      it is not OpenAI's real logo
    ChatBot.svg                       (ChatBotIcon) speech bubble with a robot face
    warning.svg                       (IntroducingMLPs, ContrastBetween...) warning triangle

Usage: python make_supplements_assets.py"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]  # .../_lib
RASTER = LIB / "assets" / "raster_images"
SVG = LIB / "assets" / "svg_images"
sys.path.insert(0, str(LIB.parent / "_tools"))
sys.path.insert(0, str(HERE))
from placeholder import make_image, font  # noqa: E402
from make_chm_assets import svg_doc, rounded_rect_path, circle_path  # noqa: E402

# (file in raster_images/, label, size, background color)
IMAGES = [
    ("Zoolander.png", "Zoolander", "1000x1250", "#3a3a4a"),
    ("nn1_thumbnail.png", "nn1 thumbnail", "1280x720", "#2b3a4a"),
    ("nn2_thumbnail.png", "nn2 thumbnail", "1280x720", "#2b4a3a"),
    ("nn3_thumbnail.png", "nn3 thumbnail", "1280x720", "#4a3a2b"),
    ("nn4_thumbnail.png", "nn4 thumbnail", "1280x720", "#3a2b4a"),
    ("Chapter5.png", "Chapter 5", "1280x720", "#2b3a4a"),
    ("Chapter6.png", "Chapter 6", "1280x720", "#2b4a3a"),
    ("Chapter7.png", "Chapter 7", "1280x720", "#4a3a2b"),
    ("EmbeddingStill.jpg", "EmbeddingStill", "1920x1080", "#222a33"),
]

# The manim screen measures 14.2222 x 8 units; the image is 1920 x 1080 (135 px per unit)
PX = 135


def to_px(x, y):
    return 960 + x * PX, 540 - y * PX


def make_network_end(out):
    img = Image.new("RGB", (1920, 1080), "#111418")
    d = ImageDraw.Draw(img)
    f = font(50)
    # The three phrases at the top, centered where the scene frames them
    for text, x in [("Harry Potter", -5.58), ("least favourite", 1.39), ("Professor", 4.77)]:
        d.text(to_px(x, 3.35), text, font=f, fill="#e8e8e8", anchor="mm")
    d.text(to_px(-4.25, 3.35), "'s", font=f, fill="#e8e8e8", anchor="mm")
    d.text(to_px(-1.75, 3.35), "most feared and", font=f, fill="#e8e8e8", anchor="mm")
    # Final distribution: bars with "Snape" on top
    cx, cy = to_px(5.0, 1.11)
    d.rectangle([cx - 236, cy - 20, cx + 236, cy + 20], fill="#3f8fa0")
    d.text((cx - 250, cy), "Snape", font=font(38), fill="#e8e8e8", anchor="rm")
    for i, (w, label) in enumerate([(0.2, "Lupin"), (0.12, "McGonagall"), (0.08, "Quirrell")]):
        y = cy + 62 * (i + 1)
        d.rectangle([cx - 236, y - 14, cx - 236 + 472 * w, y + 14], fill="#55606a")
        d.text((cx - 250, y), label, font=font(30), fill="#9aa0aa", anchor="rm")
    d.text((960, 1040), "[imagen de relleno]", font=font(28), fill="#6a6f78", anchor="mm")
    img.save(out)


def make_attention_paper(out):
    img = Image.new("RGB", (1920, 1080), "white")
    d = ImageDraw.Draw(img)
    # Title at (-0.037, 3.28) with height 0.219 units
    d.text(to_px(-0.037, 3.28), "Attention is All You Need", font=font(40), fill="black", anchor="mm")
    for i, name in enumerate(["Author One", "Author Two", "Author Three", "Author Four"]):
        d.text((960 + (i - 1.5) * 330, 205), name, font=font(28), fill="#222222", anchor="mm")
    d.text((960, 260), "Abstract", font=font(30), fill="black", anchor="mm")
    y = 310
    for i in range(9):
        length = 760 if i % 9 != 8 else 380
        d.rounded_rectangle([580, y, 580 + length, y + 12], radius=6, fill="#cccccc")
        y += 32
    for col in range(2):
        for i in range(14):
            length = 410 if i % 7 != 6 else 200
            d.rounded_rectangle([420 + col * 560, 660 + i * 26, 420 + col * 560 + length, 668 + i * 26], radius=4, fill="#dddddd")
    d.text((960, 1050), "[página de relleno]", font=font(26), fill="#999999", anchor="mm")
    img.save(out)


def make_openai_logo():
    ring = circle_path(150, 150, 130, True) + " " + circle_path(150, 150, 108, False)
    pts = []
    for k in range(8):
        r = 78 if k % 2 == 0 else 22
        a = -math.pi / 2 + k * math.pi / 4
        pts.append((150 + r * math.cos(a), 150 + r * math.sin(a)))
    star = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    return svg_doc(300, 300, f'<g fill="#ffffff" stroke="none"><path d="{ring}"/><path d="{star}"/></g>')


def make_chatbot():
    body = " ".join([
        # speech bubble with tail at the bottom left (subpath 0), eyes and mouth as holes
        "M 70 40 L 330 40 A 30 30 0 0 1 360 70 L 360 210 A 30 30 0 0 1 330 240 L 150 240 L 90 290 L 100 240 L 70 240 "
        "A 30 30 0 0 1 40 210 L 40 70 A 30 30 0 0 1 70 40 Z",
        circle_path(140, 130, 20, False),
        circle_path(260, 130, 20, False),
        "M 140 180 L 140 192 L 260 192 L 260 180 Z",
    ])
    extras = (f'<path d="{rounded_rect_path(10, 100, 28, 170, 8)}"/>'
              f'<path d="{rounded_rect_path(372, 100, 390, 170, 8)}"/>'
              '<path d="M 192 40 L 192 8 L 208 8 L 208 40 Z"/>')
    return svg_doc(400, 300, f'<g fill="#ffffff" stroke="none"><path d="{body}"/>{extras}</g>')


def make_warning():
    tri = "M 150 20 Q 160 20 166 30 L 280 235 Q 288 252 270 252 L 30 252 Q 12 252 20 235 L 134 30 Q 140 20 150 20 Z"
    bang = "M 138 100 L 138 180 L 162 180 L 162 100 Z"
    dot = circle_path(150, 214, 13, False)
    return svg_doc(300, 270, f'<g fill="#ffffff" stroke="none"><path d="{tri} {bang} {dot}"/></g>')


def main():
    RASTER.mkdir(parents=True, exist_ok=True)
    SVG.mkdir(parents=True, exist_ok=True)
    for name, label, size, bg in IMAGES:
        w, h = map(int, size.split("x"))
        make_image(RASTER / name, label, (w, h), bg)
    make_network_end(RASTER / "NetworkEnd.png")
    make_attention_paper(RASTER / "AttentionPaper.png")
    (SVG / "OpenAI.svg").write_text(make_openai_logo(), encoding="utf-8")
    (SVG / "ChatBot.svg").write_text(make_chatbot(), encoding="utf-8")
    (SVG / "warning.svg").write_text(make_warning(), encoding="utf-8")
    print("assets de supplements.py listos")


if __name__ == "__main__":
    main()
