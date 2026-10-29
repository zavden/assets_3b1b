"""Placeholders for the private assets of the 2024/holograms video (they lived in Grant's Dropbox).

Creates:
  1. Placeholder images in _lib/assets/raster_images/ (the code looks for them by name:
     ImageMobject("HologramFilm.jpg") ...). They are boxes with the name, made with
     _tools/placeholder.py, except the three of LightFieldDraft, which are RGBA layers of the same
     size (scene, "top half cutoff" and lamp) drawn with PIL.
  2. _lib/data/2024/holograms/data/MultiplePOVs.2.mp4: placeholder video for model.py
     (ExtractFramesFromFootage reads the Dropbox mp4 with cv2); a rotating wireframe cube.
     Requires ffmpeg.
  3. _lib/data/2024/holograms/data/PiCreaturePointCloud.csv: 3D point cloud (x,y,z, with
     header) that diffraction.py::SuperpositionOfPoints reads. In the original it was a scan of the
     pi creature; here they are random points inside the silhouette of a PiCreature, with volume
     (z) in the shape of a rounded bulge. Requires manimgl (it uses manim_imports_ext).

The scenes that use them change the path with a `# CHANGE`.

Usage: python make_holograms_assets.py [--skip-video] [--skip-points]"""
import argparse
import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]  # .../_lib
ASSETS = LIB / "assets"
RASTER = ASSETS / "raster_images"
DATA_OUT = LIB / "data" / "2024" / "holograms" / "data"
sys.path.insert(0, str(LIB.parent / "_tools"))
from placeholder import make_image, font  # noqa: E402

# (file in raster_images/, label, size, background color)
IMAGES = [
    # supplements.py
    ("ContrastWithPhotography.png", "ContrastWithPhotography", "1920x1080", "#3a3f4a"),
    ("HologramProcess.jpg", "HologramProcess", "1280x720", "#2b3a4a"),
    ("SimplestHologram.jpg", "SimplestHologram", "1280x720", "#3a2b4a"),
    ("HologramEquation.png", "HologramEquation", "1280x720", "#2b4a3a"),
    ("ZonePlateExposure.png", "ZonePlateExposure", "1280x720", "#333333"),
    ("DotReconstruction.png", "DotReconstruction", "1280x720", "#222a33"),
    ("MultipleDotHologram.png", "MultipleDotHologram", "1280x720", "#33222a"),
    ("DiffractionGrating.png", "DiffractionGrating", "1280x720", "#2a3322"),
    ("CraigSallyPaulGrant.png", "CraigSallyPaulGrant", "1920x1080", "#44363a"),
    ("CraigSallyHologramSetup.png", "CraigSallyHologramSetup", "1920x1080", "#36443a"),
    ("DiffractionGratingGreenLaser.jpg", "DiffractionGratingGreenLaser", "1920x1080", "#1f3a26"),
    ("FilmFromBehind.png", "FilmFromBehind", "1920x1080", "#3a3326"),
    # diffraction.py
    ("HologramFilm.jpg", "HologramFilm", "1280x720", "#3a2b2b"),
    ("SinglePointHologram.png", "SinglePointHologram", "1920x1080", "#2b2b3a"),
]


def make_light_field_draft():
    """LightFieldScene, TopHalfCutoff and Lamp: RGBA layers of the same size (1600x1000)."""
    out = RASTER / "LightFieldDraft"
    out.mkdir(parents=True, exist_ok=True)
    W, H = 1600, 1000
    f = font(44)
    small = font(30)

    # Scene: wall at the back, floor and a table with an object
    scene = Image.new("RGBA", (W, H), "#2a2e36")
    d = ImageDraw.Draw(scene)
    d.rectangle([0, int(H * 0.55), W, H], fill="#3b3f48")  # floor
    d.polygon([(0, int(H * 0.55)), (W, int(H * 0.55)), (W, int(H * 0.5)), (0, int(H * 0.5))], fill="#23262d")
    d.rectangle([int(W * 0.45), int(H * 0.45), int(W * 0.85), int(H * 0.52)], fill="#5b4a3a")  # mesa
    d.rectangle([int(W * 0.48), int(H * 0.52), int(W * 0.50), int(H * 0.75)], fill="#4a3b2e")
    d.rectangle([int(W * 0.80), int(H * 0.52), int(W * 0.82), int(H * 0.75)], fill="#4a3b2e")
    d.ellipse([int(W * 0.58), int(H * 0.30), int(W * 0.68), int(H * 0.46)], fill="#8a6f55")  # object
    d.polygon([(int(W * 0.70), int(H * 0.46)), (int(W * 0.76), int(H * 0.30)), (int(W * 0.80), int(H * 0.46))],
              fill="#6f8a55")
    d.rectangle([4, 4, W - 5, H - 5], outline="#888888", width=4)
    d.multiline_text((W / 2, int(H * 0.88)), "LightFieldScene\n[imagen de relleno]", font=f,
                     fill="#dddddd", anchor="mm", align="center")
    scene.save(out / "LightFieldScene.png")

    # Top half cutoff: only the top part of the scene (bottom half transparent)
    top = scene.copy()
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rectangle([0, 0, W, int(H * 0.5)], fill=255)
    top.putalpha(mask)
    d = ImageDraw.Draw(top)
    d.text((W / 2, 40), "TopHalfCutoff [relleno]", font=small, fill="#dddddd", anchor="mm")
    top.save(out / "TopHalfCutoff.png")

    # Lamp: in the upper left corner, where the scene puts the light source
    lamp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lamp)
    cx, cy = int(W * 0.143), int(H * 0.114)
    d.polygon([(cx - 60, cy - 10), (cx + 60, cy - 10), (cx + 30, cy - 70), (cx - 30, cy - 70)], fill="#c9b27a")
    d.rectangle([cx - 8, cy - 10, cx + 8, cy + 90], fill="#555555")
    d.ellipse([cx - 40, cy + 90, cx + 40, cy + 110], fill="#555555")
    d.text((cx, cy + 135), "Lamp [relleno]", font=small, fill="#dddddd", anchor="mm")
    lamp.save(out / "Lamp.png")


def make_video(out):
    """16 s placeholder video (1080x1080, 24 fps): a rotating wireframe cube."""
    if shutil.which("ffmpeg") is None:
        print("   ! no hay ffmpeg; no se creó el mp4")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    size, fps, seconds = 1080, 24, 16
    verts = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], dtype=float)
    edges = [(i, j) for i in range(8) for j in range(i + 1, 8) if np.sum(verts[i] != verts[j]) == 1]
    f = font(40)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{size}x{size}", "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264",
           "-pix_fmt", "yuv420p", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(fps * seconds):
        t = k / fps
        img = Image.new("RGB", (size, size), "#202428")
        d = ImageDraw.Draw(img)
        yaw, pitch = 0.5 * t, 0.35 + 0.2 * math.sin(0.4 * t)
        cy_, sy_, cp_, sp_ = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch)
        ry = np.array([[cy_, 0, sy_], [0, 1, 0], [-sy_, 0, cy_]])
        rx = np.array([[1, 0, 0], [0, cp_, -sp_], [0, sp_, cp_]])
        pts = verts @ ry.T @ rx.T
        scale = 1 / (1 - 0.15 * pts[:, 2])
        xy = [(size / 2 + 260 * p[0] * s, size / 2 - 260 * p[1] * s) for p, s in zip(pts, scale)]
        for i, j in edges:
            d.line([xy[i], xy[j]], fill="#9fc5ff", width=5)
        d.text((size / 2, 80), "MultiplePOVs.2.mp4 [video de relleno]", font=f, fill="#dddddd", anchor="mm")
        d.text((size / 2, size - 80), f"t = {t:5.2f} s", font=f, fill="#dddddd", anchor="mm")
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()


def make_point_cloud(out, n_points=500_000, seed=0):
    """CSV x,y,z (with header): points inside the silhouette of a PiCreature, with volume."""
    # manimlib reads sys.argv when imported: we hide it from it
    argv, sys.argv = sys.argv, sys.argv[:1]
    from manim_imports_ext import PiCreature, BLUE_E
    sys.argv = argv
    from scipy import ndimage

    pi = PiCreature(color=BLUE_E)
    body = max(pi.family_members_with_points(), key=lambda m: m.get_height())
    # Body outline (several subpaths) to a 1000x1000 mask with PIL
    res = 1000
    x0, y0 = body.get_left()[0], body.get_bottom()[1]
    span = max(body.get_width(), body.get_height())
    mask_img = Image.new("L", (res, res), 0)
    md = ImageDraw.Draw(mask_img)
    for sub in body.get_subpaths():
        pts = np.array([(p[0] - x0, p[1] - y0) for p in sub[::3]])
        px = pts / span * (res - 1)
        md.polygon([(x, res - 1 - y) for x, y in px], fill=255)
    mask = np.array(mask_img) > 0
    dist = ndimage.distance_transform_edt(mask)
    rng = np.random.default_rng(seed)
    ys, xs = np.nonzero(mask)
    idx = rng.integers(0, len(xs), n_points)
    px, py = xs[idx] + rng.random(n_points), ys[idx] + rng.random(n_points)
    # Volume: flattened ellipsoid, z = ±sqrt(distance to the edge) with a little noise
    depth = np.sqrt(dist[ys[idx], xs[idx]]) / math.sqrt(dist.max())
    z = depth * rng.uniform(-1, 1, n_points)
    pts = np.stack([(px - res / 2) / res * 2 * span / 2, (res / 2 - py) / res * 2 * span / 2, z * 0.5 * span / 2], axis=1)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(out, pts, delimiter=",", header="x,y,z", comments="", fmt="%.4f")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-video", action="store_true")
    ap.add_argument("--skip-points", action="store_true")
    args = ap.parse_args()

    RASTER.mkdir(parents=True, exist_ok=True)
    for name, label, size, bg in IMAGES:
        w, h = map(int, size.split("x"))
        make_image(RASTER / name, label, (w, h), bg)
    make_light_field_draft()
    if not args.skip_video:
        make_video(DATA_OUT / "MultiplePOVs.2.mp4")
    if not args.skip_points:
        make_point_cloud(DATA_OUT / "PiCreaturePointCloud.csv")


if __name__ == "__main__":
    main()
