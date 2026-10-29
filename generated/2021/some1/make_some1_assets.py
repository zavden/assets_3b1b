"""Generates the placeholder assets of _2021/some1_winners.py (the originals were YouTube thumbnails that
the scene downloads with urllib, and files from Grant's Dropbox):

- raster_images/some1_thumbnails/<slug>.jpg: a placeholder thumbnail (1280x720) for each video of
  WINNERS and HONORABLE_MENTIONS (with its title and author) and for each synthetic entry of the listing.
  `yt_slug_to_image_file(slug)` looks there; if the file exists, `save_thumbnail_locally` downloads nothing.
- raster_images/Leios.png: placeholder of the Leios Labs logo/photo (Introduction).
- _lib/data/some1_video_urls_ordered.txt: list of URLs that AllVideosOrdered reads
  (`get_youtube_slugs`): the 30 named videos plus ENTRIES_EXTRA synthetic entries "SoME1_entry_NNN"
  (the original listing had hundreds of contest entries).

Usage: python make_some1_assets.py"""
import colorsys
import hashlib
import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[2]  # _lib/assets
DATA = LIB.parent / "data"
sys.path.insert(0, str(LIB.parents[1] / "_tools"))
from placeholder import make_image

# (title, author, slug): copied from WINNERS + HONORABLE_MENTIONS of _2021/some1_winners.py
VIDEOS = [
    ("That weird light at the bottom of a mug - ENVELOPES", "Paralogical", "fJWnA4j0_ho"),
    ("Hiding Images in Plain Sight: The Physics Of Magic Windows", "Matt Ferraro", "CatInCausticImage"),
    ("The Beauty of Bezier Curves", "Freya Holmer", "aVwxzDHniEw"),
    ("What Is The Most Complicated Lock Pattern?", "Dr. Zye", "PKjbBQ0PBCQ"),
    ("Pick's theorem: The wrong, amazing proof", "spacematt", "uh-yRNqLpOg"),
    ("Dirac's belt trick, Topology, and Spin 1/2 particles", "Noah Miller", "ACZC_XEyg9U"),
    ("Galois-Free Guarantee! | The Insolubility of the Quintic", "Carl Turner", "BSHv9Elk1MU"),
    ("The Two Envelope Problem - a Mystifying Probability Paradox", "Formant", "_NGPncypY68"),
    ("The Math Behind Font Rasterization | How it Works", "GamesWithGabe", "LaYPoMPRSlk"),
    ("What is a Spinor?", "Mia Hughes", "SpinorArticle"),
    ("Understanding e", "Veli Peltola", "e_comic"),
    ("Ancient Multiplication Trick", "Inigo Quilez", "CsMrHzp850M"),
    (None, "Fanren Yishi", "FiveIntsTheorem"),  # title in Chinese
    ("Lehmer Factor Stencils", "Proof of Concept", "QzohwKT6TNA"),
    ("What is the limit of a sequence of graphs?", "Spectral Collective", "7Gj9BH4IZ-4"),
    ("Steiner's Porism: proving a cool animation", "Joseph Newton", "fKAyaP8IzlE"),
    ("Wait, Probabilities can be Negative?!", "Steven G", "std9EBbtOC0"),
    ("This random graph fact will blow your mind", "Snarky Math", "3QjZ31lj974"),
    ("Why is pi here? Estimating pi by Buffon's noodle!", "Mihai Nica", "e-RUyCs9B08"),
    ("Introduction to Waves", "Rob Schlub", "IntroToWaves"),
    ("ComplexFunctions", "Treena", "Treena"),
    ("I spent an entire summer to find this spiral", "Sort of School", "n-e9C8g5x68"),
    ("HACKENBUSH: a window to a new world of math", "Owen Maitzen", "ZYj4NkeGPdM"),
    ("The Tale of the Lights Puzzle", "Throw Math At It", "9aZsABF-Vj4"),
    ("The BEST Way to Find a Random Point in a Circle", "nubDotDev", "4y_nmpv-9lI"),
    ("Secrets of the Fibonacci Tiles", "Eric Severson", "Ct7oltmdJrM"),
    ("The Tale of Three Triangles", "Robin Truax", "5nuYD2M2AX8"),
    ("How Karatsuba's algorithm gave us new ways to multiply", "Nemean", "cCKOl5li6YM"),
    ("Can you change a sum by rearranging its numbers? --- The Riemann Series Theorem", "Morphocular", "U0w0f0PDdPA"),
    ("Neural manifolds - The Geometry of Behaviour", "Artem Kirsanov", "QHj9uVmwA_0"),
]
ENTRIES_EXTRA = 60


def color_for(key):
    h = int(hashlib.md5(key.encode()).hexdigest()[:6], 16) / 0xFFFFFF
    r, g, b = colorsys.hsv_to_rgb(h, 0.45, 0.32)
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


def main():
    thumbs = LIB / "raster_images" / "some1_thumbnails"
    thumbs.mkdir(parents=True, exist_ok=True)
    slugs = []
    for title, author, slug in VIDEOS:
        label = "\n".join(textwrap.wrap(title, 26)) if title else slug
        make_image(thumbs / f"{slug}.jpg", f"{label}\n- {author}", (1280, 720), color_for(slug))
        slugs.append(slug)
    for i in range(1, ENTRIES_EXTRA + 1):
        slug = f"SoME1_entry_{i:03d}"
        make_image(thumbs / f"{slug}.jpg", f"SoME1 entry {i}", (1280, 720), color_for(slug))
        slugs.append(slug)
    make_image(LIB / "raster_images" / "Leios.png", "Leios Labs", (512, 512), "#2b4a3a")
    DATA.mkdir(parents=True, exist_ok=True)
    # get_youtube_slugs does url[len(prefix):-1]: each line must end in "\n"
    (DATA / "some1_video_urls_ordered.txt").write_text("".join(f"https://youtu.be/{s}\n" for s in slugs))


if __name__ == "__main__":
    main()
