"""Generates the placeholder assets of outside_videos/short_links.py (the originals lived in Grant's Dropbox,
shorts/Custom Audio/lower_link/, and on his desktop):

- iPhone.svg (PiLookingAtPhone): single-shape phone silhouette: rounded body with the screen
  as a hole, a notch at the top and the bottom bar. The scene does set_height(3), stretch(1.2, 0) and
  set_fill(GREY_A). In _lib/assets/svg_images/.
- Comment screenshots (CommentFlurry*): the scene does os.listdir(folder) and loads each .png, so
  folders with images are needed. Dark comment cards are generated (avatar, name, placeholder
  text, "likes") of width 900 px and variable height, in
  _lib/assets/raster_images/short_links/lower_link/<subfolder>/comment_N.png for the subfolders "" 
  (the root), OnLinks, OnBlockCollisions, OnPrisms, OnFourier and OtherQuestions.

Usage: python make_short_links_assets.py"""
import colorsys
import random
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]  # _lib/assets

FONT = "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf"

COMMENTS = {
    "": [
        "Honestly the best explanation I have seen. Subscribed!",
        "Wait, why does this work? I need a part two.",
        "I watched this three times and finally got it.",
        "Who else came here from the full video?",
        "This is why I love math.",
        "Short and sweet. More of these please!",
    ],
    "OnLinks": [
        "Clicking the link in the description right now.",
        "Is the link at the bottom of the screen clickable?",
        "Where do I find the link to the longer version?",
        "The link in the pinned comment is broken for me.",
        "Love that you put the link on screen.",
        "Link in the video? Sneaky, but it works.",
        "Thanks for the link, reading the paper tonight.",
        "I did not know you could tap the title card!",
    ],
    "OnBlockCollisions": [
        "The blocks computing pi still blows my mind.",
        "Why is the number of collisions the digits of pi?",
        "I tried this in Python and got 31415. Wow.",
        "The clack sound in this one is so satisfying.",
        "Can you do the same with three blocks?",
        "Phase space turning into a circle is magic.",
        "My physics teacher showed us this in class.",
        "Elastic collisions never looked so good.",
    ],
    "OnPrisms": [
        "So light really does slow down inside glass?",
        "Why does the rainbow come out in that order?",
        "I never understood prisms until this video.",
        "Is the index of refraction just a ratio of speeds?",
        "Now explain why the sky is blue!",
        "Snell's law finally makes sense to me.",
        "Great visuals on the wave fronts.",
        "What happens with a prism made of water?",
    ],
    "OnFourier": [
        "Epicycles drawing a picture is wild.",
        "The Fourier transform is everywhere, even in my guitar tuner.",
        "Finally I get why the integral picks out a frequency.",
        "Winding it around a circle was the key insight.",
        "Can the heat equation video come back?",
        "I code audio plugins and this helped a lot.",
        "Sines and cosines are secretly rotating vectors.",
        "The center of mass trick is beautiful.",
    ],
    "OtherQuestions": [
        "What software do you use for the animations?",
        "How long does it take to make one of these?",
        "Do you have a video on eigenvectors?",
        "Can you make one about the Basel problem?",
        "Where did you learn to teach like this?",
        "Will there be a follow up on neural networks?",
        "What music is playing in the background?",
        "Do you take requests for topics?",
    ],
}

NAMES = ["mathfan42", "curious_cat", "quantumleaper", "pi_day_enjoyer", "notarobot", "linear_alice",
         "bayes_bob", "euler_stan", "topology_tim", "sine_wave_sam"]
AGES = ["2 days ago", "1 week ago", "3 weeks ago", "2 months ago", "5 months ago", "1 year ago"]


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def make_comment(out, text, rng):
    W = 900
    pad = 36
    f_name, f_text, f_small = font(FONT_B, 30), font(FONT, 34), font(FONT, 24)
    lines = textwrap.wrap(text, 42)
    text_y = pad + 100
    likes_y = text_y + len(lines) * 46 + 14
    h = likes_y + 34 + pad
    img = Image.new("RGB", (W, h), "#0f0f0f")
    d = ImageDraw.Draw(img)
    r, g, b = colorsys.hsv_to_rgb(rng.random(), 0.55, 0.75)
    color = (int(r * 255), int(g * 255), int(b * 255))
    d.ellipse([pad, pad, pad + 84, pad + 84], fill=color)
    name = rng.choice(NAMES)
    d.text((pad + 84 + 28, pad + 2), f"@{name}{rng.randint(1, 99)}", font=f_name, fill="#f1f1f1")
    d.text((pad + 84 + 28, pad + 44), rng.choice(AGES), font=f_small, fill="#909090")
    for i, line in enumerate(lines):
        d.text((pad + 84 + 28, text_y + i * 46), line, font=f_text, fill="#f1f1f1")
    d.text((pad + 84 + 28, likes_y), f"{rng.randint(2, 4800)} likes", font=f_small, fill="#909090")
    d.text((W - pad, likes_y), "[comentario de relleno]", font=f_small, fill="#5a5a5a", anchor="ra")
    d.rectangle([0, 0, W - 1, h - 1], outline="#303030", width=2)
    img.save(out)


def make_iphone(out):
    def rrect(x, y, w, h, r, hole=False):
        k = 0.5523 * r
        if not hole:
            return (f"M {x + r},{y} L {x + w - r},{y} C {x + w - r + k},{y} {x + w},{y + r - k} {x + w},{y + r} "
                    f"L {x + w},{y + h - r} C {x + w},{y + h - r + k} {x + w - r + k},{y + h} {x + w - r},{y + h} "
                    f"L {x + r},{y + h} C {x + r - k},{y + h} {x},{y + h - r + k} {x},{y + h - r} "
                    f"L {x},{y + r} C {x},{y + r - k} {x + r - k},{y} {x + r},{y} Z")
        return (f"M {x + r},{y} C {x + r - k},{y} {x},{y + r - k} {x},{y + r} "
                f"L {x},{y + h - r} C {x},{y + h - r + k} {x + r - k},{y + h} {x + r},{y + h} "
                f"L {x + w - r},{y + h} C {x + w - r + k},{y + h} {x + w},{y + h - r + k} {x + w},{y + h - r} "
                f"L {x + w},{y + r} C {x + w},{y + r - k} {x + w - r + k},{y} {x + w - r},{y} Z")

    paths = [
        rrect(0, 0, 100, 200, 16) + " " + rrect(5, 14, 90, 172, 5, hole=True),  # body with a hollow screen
        rrect(35, 5, 30, 5, 2.5),  # horn
        rrect(38, 191, 24, 3, 1.5),  # bottom bar
    ]
    body = "\n".join(f'<path fill="#ffffff" stroke="none" d="{p}"/>' for p in paths)
    out.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="200" viewBox="0 0 100 200">\n{body}\n</svg>\n')


def main():
    svg_dir = ASSETS / "svg_images"
    svg_dir.mkdir(parents=True, exist_ok=True)
    make_iphone(svg_dir / "iPhone.svg")
    root = ASSETS / "raster_images" / "short_links" / "lower_link"
    n = 0
    for sub, comments in COMMENTS.items():
        folder = root / sub
        folder.mkdir(parents=True, exist_ok=True)
        rng = random.Random(f"short_links:{sub}")
        for i, text in enumerate(comments, start=1):
            make_comment(folder / f"comment_{i}.png", text, rng)
            n += 1
    print(f"short_links: iPhone.svg + {n} comentarios")


if __name__ == "__main__":
    main()
