"""Generates the assets that _2021/shadows.py looks up by name and that are not in the public repo:

- svg_images/cat_outline.svg: single-stroke cat silhouette (copy of svg_images/sitting_cat.svg, which is
  already a single closed <path>). The scene uses SVGMobject("cat_outline").family_members_with_points()[0].
- svg_images/dog_outline.svg: single closed-stroke dog silhouette, drawn here as a smoothed polygon
  (Chaikin); own placeholder, it is not Grant's original drawing.
- raster_images/Fourier.jpg and Riemann_cropped.jpeg: fallback, copies of Joseph Fourier.jpg and Riemann.jpeg if they exist;
  the definitive ones are downloaded from Commons by replacements/downloads/make_downloaded_assets.py.
- raster_images/Shadows_Integral_Intro.png: placeholder image (ThreeCamps shows it on the classroom screen;
  in the video it was a frame of the surface integral).

Usage: python make_shadows_assets.py   (requires setup_assets.py to have already copied the original assets)"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]  # _lib/assets
sys.path.insert(0, str(ASSETS.parents[1] / "_tools"))
from placeholder import make_image

# Outline of a dog in profile, facing right (x right, y down), traced clockwise from the nose.
DOG_POINTS = [
    (292, 80), (289, 90), (272, 94), (252, 100), (240, 106),             # snout and jaw
    (232, 124), (228, 148), (224, 172), (222, 196), (228, 210),          # neck, chest, front leg
    (226, 217), (200, 217), (200, 206), (203, 178),                      # front leg (foot and back)
    (190, 167), (160, 165), (135, 167), (124, 172),                      # belly
    (122, 190), (127, 204), (133, 215), (132, 218), (104, 218),          # hind leg
    (104, 206), (100, 192), (88, 178), (77, 152), (68, 128),             # thigh and rump
    (52, 114), (32, 92), (21, 70), (27, 65), (46, 85), (68, 102),        # cola
    (92, 93), (130, 89), (170, 87), (200, 85), (213, 72),                # back
    (208, 42), (214, 14), (232, 40), (241, 53), (254, 62),               # ear and forehead
    (272, 69), (288, 73),                                                # snout
]


def chaikin(points, iterations=3):
    pts = list(points)
    for _ in range(iterations):
        new = []
        n = len(pts)
        for i in range(n):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
            new.append((0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1))
            new.append((0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1))
        pts = new
    return pts


def write_dog(path):
    pts = chaikin(DOG_POINTS)
    d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 310 230" width="310" height="230">'
        f'<path fill="#000000" d="{d}"/></svg>\n'
    )


def main():
    svg = ASSETS / "svg_images"
    img = ASSETS / "raster_images"
    shutil.copy(svg / "sitting_cat.svg", svg / "cat_outline.svg")
    write_dog(svg / "dog_outline.svg")
    # Fallback only: the originals come from Grant's assets/ (may not be there) and make_downloaded_assets.py
    # (rows 58 and 59) afterwards writes Fourier.jpg and Riemann_cropped.jpeg downloaded from Commons
    for src, dst in (("Joseph Fourier.jpg", "Fourier.jpg"), ("Riemann.jpeg", "Riemann_cropped.jpeg")):
        if (img / src).exists():
            shutil.copy(img / src, img / dst)
    make_image(img / "Shadows_Integral_Intro.png", "Shadows: integral intro", (1920, 1080), "#26364a")
    print("Assets de shadows generados")


if __name__ == "__main__":
    main()
