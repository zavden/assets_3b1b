"""Generates the placeholder assets of _2021/newton_fractal.py and _2021/holomorphic_dynamics.py (the originals
lived in Grant's Dropbox or were data he generated):

- raster_images/RealNewtonStill.png, RasterizingBezier_1.png, RasterizingBezier_2.png, Coco_logo.png:
  placeholder images (box with the name). The two RasterizingBezier were captures of the scene
  RasterizingBezier; RealNewtonStill, a capture of the real Newton applet.
- raster_images/MandelbrotSet.png, Mandelbrot_boundary.png, MulticoloredNewtonsMapCircle.png,
  NewtonBoundaryProperty.png: images computed with numpy (the Mandelbrot set with Grant's palette,
  its outline, a disk with the basins of the cubic Newton fractal and the Newton fractal with its boundaries).
- raster_images/j_invariant.png, FFT_Diagram.png (placeholder boxes) and Pierre_Fatou.jpg, Gaston_Julia.jpg
  (placeholder portraits).
- svg_images/bezier_example.svg: the Bézier curve (a single <path>, no fill) that RasterizingBezier
  rasterizes (`SVGMobject("bezier_example")[0]`).
- _lib/data/sphere_pixel_values.npy: what ExamplePixels reads (`get_directories()["data"]`): an
  (N, 5, 5, 3) array with the BGR values (0-255) of a 5x5-pixel patch of the image of a shaded
  sphere, while the sphere grows and its edge crosses the patch. Synthetic data.

Usage: python make_newton_fractal_assets.py"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]          # _lib/assets
LIB = ASSETS.parent               # _lib
sys.path.insert(0, str(LIB.parent / "_tools"))
from placeholder import make_image

IMAGES = [
    ("RealNewtonStill", "RealNewtonStill (captura de Newton real)", (1920, 1080), "#2b3a4a"),
    ("RasterizingBezier_1", "RasterizingBezier 1 (captura)", (1920, 1080), "#33363a"),
    ("RasterizingBezier_2", "RasterizingBezier 2 (captura)", (1920, 1080), "#33363a"),
    ("Coco_logo", "Coco logo", (900, 450), "#4a3a2b"),
    ("j_invariant", "j invariant (grafica de la funcion j)", (1200, 900), "#2b3a4a"),
    ("FFT_Diagram", "FFT diagram", (1600, 900), "#33363a"),
    ("Pierre_Fatou", "Pierre Fatou", (600, 800), "#4a3a2b"),
    ("Gaston_Julia", "Gaston Julia", (600, 800), "#3a2b4a"),
]
JPG = {"Pierre_Fatou", "Gaston_Julia"}  # portraits: .jpg; the rest .png

MANDELBROT_COLORS = [
    "#00065c", "#061e7e", "#0c37a0", "#205abc", "#4287d3",
    "#D9EDE4", "#F0F9E4", "#BA9F6A", "#573706",
]
NEWTON_COLORS = ["#440154", "#21908c", "#29abca"]  # ROOT_COLORS_DEEP[::2]

BEZIER_SVG = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="300" viewBox="0 0 800 300">
  <path d="M 20 230 C 160 20, 300 20, 400 150 S 640 290, 780 70" fill="none" stroke="#000000" stroke-width="4"/>
</svg>
"""


def sphere_pixel_values(n_frames=240, patch=5):
    """BGR of a 5x5 patch over a shaded sphere (light at the top left) whose radius grows"""
    light = np.array([-0.5, 0.6, 0.62])
    light /= np.linalg.norm(light)
    cx, cy = 20.0, 20.0                    # center of the sphere in the patch's system (pixels)
    radii = np.linspace(8.0, 60.0, n_frames)
    base = np.array([210.0, 150.0, 70.0])  # color of the sphere (BGR)
    bg = np.array([20.0, 14.0, 10.0])      # almost black background
    out = np.zeros((n_frames, patch, patch, 3))
    for k, R in enumerate(radii):
        for i in range(patch):
            for j in range(patch):
                x, y = j + 0.5, i + 0.5
                dx, dy = x - cx, -(y - cy)
                r2 = dx * dx + dy * dy
                if r2 >= R * R:
                    out[k, i, j] = bg
                    continue
                n = np.array([dx, dy, np.sqrt(R * R - r2)]) / R
                shade = max(0.0, float(n @ light))
                # edge smoothed by half a pixel
                edge = np.clip((R - np.sqrt(r2)) / 1.0, 0, 1)
                col = bg + (base * (0.15 + 0.85 * shade) - bg) * edge
                out[k, i, j] = col
    return np.clip(out, 0, 255).astype(np.uint8)


def grid(center, height, size):
    """Complex plane of size=(w, h) pixels, `height` units tall, centered at `center`"""
    w, h = size
    ys = np.linspace(height / 2, -height / 2, h)
    xs = np.linspace(-height / 2 * w / h, height / 2 * w / h, w)
    return (xs[None, :] + 1j * ys[:, None]) + center


def hex_rgb(c):
    return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)], dtype=float)


def mandelbrot_escape(c, n_steps=200):
    z = np.zeros_like(c)
    escaped = np.full(c.shape, np.inf)
    alive = np.ones(c.shape, dtype=bool)
    for n in range(n_steps):
        z[alive] = z[alive] ** 2 + c[alive]
        gone = alive & (np.abs(z) > 2)
        escaped[gone] = n + 1 - np.log(np.log(np.abs(z[gone]))) / np.log(2)
        alive &= ~gone
    return escaped


def mandelbrot_image(size=(1600, 900), center=-0.7 + 0j, height=2.307):  # BriefMandelbrot: the image is 2.307 tall in the plane
    from PIL import Image
    esc = mandelbrot_escape(grid(center, height, size))
    pal = np.array([hex_rgb(c) for c in MANDELBROT_COLORS])
    img = np.zeros(esc.shape + (3,))
    ok = np.isfinite(esc)
    # same idea as the shader: the palette is traversed with the sqrt of the escape time
    s = np.clip(np.sqrt(esc[ok]) / 8.0 * (len(pal) - 1), 0, len(pal) - 1.001)
    i = s.astype(int)
    f = (s - i)[:, None]
    img[ok] = pal[i] * (1 - f) + pal[i + 1] * f
    return Image.fromarray(img.astype(np.uint8))


def mandelbrot_outline(size=(1200, 900)):
    from PIL import Image
    esc = mandelbrot_escape(grid(-0.65 + 0j, 2.6, size), 300)
    inside = ~np.isfinite(esc)
    edge = inside & ~(np.roll(inside, 1, 0) & np.roll(inside, -1, 0) & np.roll(inside, 1, 1) & np.roll(inside, -1, 1))
    rgba = np.zeros(inside.shape + (4,), dtype=np.uint8)
    rgba[edge] = [255, 255, 255, 255]
    return Image.fromarray(rgba, "RGBA")


def newton_basins(z, coefs, n_steps=40):
    """(0-based) index of the root to which Newton converges from each z, and steps used"""
    p = np.polynomial.Polynomial(coefs)
    dp = p.deriv()
    roots = p.roots()
    for _ in range(n_steps):
        z = z - p(z) / np.where(dp(z) == 0, 1e-12, dp(z))
    idx = np.argmin(np.abs(z[..., None] - roots), axis=-1)
    return idx, roots


def newton_image(size, center, height, coefs=(-1, 0, 0, 1), boundary=False):
    from PIL import Image
    z = grid(center, height, size)
    idx, roots = newton_basins(z, coefs)
    pal = np.array([hex_rgb(c) for c in NEWTON_COLORS])
    img = pal[idx % len(pal)]
    if boundary:
        edge = (idx != np.roll(idx, 1, 0)) | (idx != np.roll(idx, 1, 1))
        img[edge] = 255
    return Image.fromarray(img.astype(np.uint8)), idx


def newton_disk(size=(800, 800)):
    from PIL import Image
    img, idx = newton_image(size, 0j, 3.0)
    arr = np.array(img.convert("RGBA"))
    h, w = size
    yy, xx = np.mgrid[0:h, 0:w]
    arr[(xx - w / 2) ** 2 + (yy - h / 2) ** 2 > (min(w, h) / 2) ** 2, 3] = 0
    return Image.fromarray(arr)


def main():
    for name, label, size, bg in IMAGES:
        ext = "jpg" if name in JPG else "png"
        out = ASSETS / "raster_images" / f"{name}.{ext}"
        out.parent.mkdir(parents=True, exist_ok=True)
        make_image(out, label, size, bg)
    raster = ASSETS / "raster_images"
    mandelbrot_image().save(raster / "MandelbrotSet.png")
    mandelbrot_outline().save(raster / "Mandelbrot_boundary.png")
    newton_disk().save(raster / "MulticoloredNewtonsMapCircle.png")
    newton_image((1920, 1080), 0j, 3.0, boundary=True)[0].save(raster / "NewtonBoundaryProperty.png")
    svg = ASSETS / "svg_images" / "bezier_example.svg"
    svg.parent.mkdir(parents=True, exist_ok=True)
    svg.write_text(BEZIER_SVG)
    data = LIB / "data" / "sphere_pixel_values.npy"
    data.parent.mkdir(parents=True, exist_ok=True)
    np.save(data, sphere_pixel_values())
    print("ok")


if __name__ == "__main__":
    main()
