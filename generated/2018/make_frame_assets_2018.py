"""Own replacements for 13 `raster_images/` files that 2018 scenes load and that were screenshots/thumbnails of Grant's work
(`assets2018_fotogramas.csv`). The `assets/` folder of 3b1b/videos is gone, so each file is rebuilt with the SAME name,
width, height and mode as the original, never reading a pixel of Grant's file:

  - 7 come from a frame (ffmpeg) of OUR render of a matching scene (`renders/2018/<project>/<Scene>.mp4`), scaled with
    "cover" (no distortion, LANCZOS) to the final size: 5 thumbnails of `borsuk_addition` and the 2 `SphereSurfaceProof*`.
  - 3 Dandelin pictures (`ConjectureLineEquivalence{Big,Small}Sphere`, `ShowCircleToCircleLine`) were frames of an animation
    Grant made outside manim; they are drawn with numpy/PIL (shaded spheres, a tangent plane, tangency circles).
  - 3 EOLA thumbnails (`eola{5,6,7}_thumbnail`) are title cards drawn with PIL (CMU Serif), no brand logo.

  python make_frame_assets_2018.py [--out DIR] [--install] [--only A.png,B.jpg] [--list]

  --out DIR   where the images go (default: a temp folder, NOT the repo).
  --install   write into _lib/assets/raster_images/ (the original is first saved in _tools/.cache/assets2018/originales/
              if it is not there yet) and the registry into replacements/assets2018/assets2018_frames_sources.json.
  --list      print the table image -> scene -> instant and exit.

Needs ffmpeg/ffprobe, numpy and PIL (venv).
"""
import argparse
import datetime
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parents[2]          # _lib/assets
ROOT = ASSETS.parents[1]                               # converted
RENDERS = ROOT / "renders" / "2018"
RASTER = ASSETS / "raster_images"
FONTS = ASSETS / "fonts"
BACKUP = ROOT / "_tools" / ".cache" / "assets2018" / "originales" / "raster_images"
REGISTRY = ASSETS / "generated" / "replacements" / "assets2018" / "assets2018_frames_sources.json"
LICENSE = "CC BY-NC-SA 4.0 (own work, derived from 3b1b/videos)"

# name -> (width, height, mode) of the original (only the size/mode are consulted, from assets2018_fotogramas.csv)
SPEC = {
    "BorsukUlamThumbnail.png": (1920, 1080, "RGBA"),
    "ContinuousNecklaceThumbnail.png": (1920, 1080, "RGBA"),
    "NecklaceSphereAssociationThumbnail.png": (1920, 1080, "RGBA"),
    "NecklaceThumbnail.png": (1920, 1080, "RGBA"),
    "TopologyProofThumbnail.png": (1920, 1080, "RGBA"),
    "SphereSurfaceProof1.png": (2560, 1440, "RGBA"),
    "SphereSurfaceProof2.png": (2560, 1440, "RGBA"),
    "ConjectureLineEquivalenceBigSphere.png": (2560, 1440, "RGBA"),
    "ConjectureLineEquivalenceSmallSphere.png": (2560, 1440, "RGBA"),
    "ShowCircleToCircleLine.png": (2560, 1440, "RGBA"),
    "eola5_thumbnail.jpg": (4057, 2285, "RGB"),
    "eola6_thumbnail.jpg": (4082, 2285, "RGB"),
    "eola7_thumbnail.jpg": (4072, 2299, "RGB"),
}
# name -> (project, scene, fraction of the video duration, subject)
FRAMES = {
    "NecklaceThumbnail.png": ("borsuk_addition", "MinimizeSharding", 0.5, "thumbnail of the necklace-splitting video"),
    "BorsukUlamThumbnail.png": ("borsuk_addition", "FunctionGInputSpace", 0.5, "thumbnail of the Borsuk-Ulam video"),
    "TopologyProofThumbnail.png": ("borsuk_addition", "RotationOfEquatorGraphInOuputSpace", 0.5, "thumbnail of the topological proof video"),
    "ContinuousNecklaceThumbnail.png": ("borsuk_addition", "DivisionOfUnity", 0.5, "thumbnail of the continuous necklace video"),
    "NecklaceSphereAssociationThumbnail.png": ("borsuk_addition", "NecklaceSphereConnectionTitle", 0.6,
                                               "thumbnail of the necklace-sphere association video"),
    "SphereSurfaceProof1.png": ("sphere_area", "RectangulatedSphere", 0.6, "frame of the first sphere surface-area proof"),
    "SphereSurfaceProof2.png": ("sphere_area", "SecondProof", 0.5, "frame of the sphere-in-cylinder surface-area proof"),
}
EOLA = {  # chapter -> title
    "eola5_thumbnail.jpg": (5, "Three-dimensional linear transformations"),
    "eola6_thumbnail.jpg": (6, "The determinant"),
    "eola7_thumbnail.jpg": (7, "Inverse matrices, column space and null space"),
}
DRAWN = ("ConjectureLineEquivalenceBigSphere.png", "ConjectureLineEquivalenceSmallSphere.png", "ShowCircleToCircleLine.png")


def grab_frame(video: Path, frac: float, out: Path):
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                         str(video)], text=True).strip())
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-ss", f"{dur * frac:.3f}", "-i", str(video),
                           "-frames:v", "1", str(out)])
    return dur * frac


def cover(im, size):
    w, h = size
    k = max(w / im.width, h / im.height)
    nw, nh = max(w, round(im.width * k)), max(h, round(im.height * k))
    im = im.resize((nw, nh), Image.LANCZOS)
    x0, y0 = (nw - w) // 2, (nh - h) // 2
    return im.crop((x0, y0, x0 + w, y0 + h))


def sphere(canvas: np.ndarray, cx, cy, r, color, light=(-0.45, -0.6, 0.66)):
    """Shaded sphere (Lambert + soft edge) over `canvas` (H, W, 3 float 0..1)."""
    h, w, _ = canvas.shape
    x0, x1, y0, y1 = max(0, int(cx - r - 2)), min(w, int(cx + r + 3)), max(0, int(cy - r - 2)), min(h, int(cy + r + 3))
    yy, xx = np.mgrid[y0:y1, x0:x1]
    nx, ny = (xx - cx) / r, (yy - cy) / r
    d2 = nx * nx + ny * ny
    nz = np.sqrt(np.clip(1 - d2, 0, 1))
    l = np.array(light) / np.linalg.norm(light)
    shade = np.clip(nx * l[0] + ny * l[1] + nz * l[2], 0, 1)
    spec = np.clip(nx * l[0] + ny * l[1] + nz * l[2], 0, 1) ** 24 * 0.35
    col = np.array(color)[None, None, :] * (0.22 + 0.78 * shade)[..., None] + spec[..., None]
    alpha = np.clip((r - np.sqrt(d2) * r) / 1.5, 0, 1)[..., None]
    canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1] * (1 - alpha) + np.clip(col, 0, 1) * alpha


def draw_dandelin(name: str, size) -> Image.Image:
    w, h = size
    canvas = np.zeros((h, w, 3), float)
    canvas[:] = (0.04, 0.04, 0.05)
    big, small = (0.20, 0.45, 0.80), (0.95, 0.75, 0.25)
    if name == "ConjectureLineEquivalenceBigSphere.png":
        sphere(canvas, w * 0.5, h * 0.48, h * 0.34, big)
    elif name == "ConjectureLineEquivalenceSmallSphere.png":
        sphere(canvas, w * 0.5, h * 0.58, h * 0.18, small)
    else:  # ShowCircleToCircleLine: both spheres
        sphere(canvas, w * 0.40, h * 0.40, h * 0.27, big)
        sphere(canvas, w * 0.62, h * 0.70, h * 0.14, small)
    im = Image.fromarray((canvas * 255).astype(np.uint8)).convert("RGBA")
    ss = 2
    ov = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    S = lambda x, y: (x * w * ss, y * h * ss)
    # tilted plane (semi-transparent parallelogram) and a tangency ellipse
    d.polygon([S(0.12, 0.84), S(0.62, 0.92), S(0.92, 0.70), S(0.42, 0.62)], fill=(180, 180, 190, 60), outline=(220, 220, 230, 160))
    if name == "ShowCircleToCircleLine":
        d.line([S(0.40, 0.40), S(0.62, 0.70)], fill=(255, 230, 80, 255), width=8 * ss)
        for cx, cy, rr in ((0.40, 0.40, 0.27 * h), (0.62, 0.70, 0.14 * h)):
            d.ellipse([cx * w * ss - rr * ss * 0.9, cy * h * ss + rr * ss * 0.05, cx * w * ss + rr * ss * 0.9, cy * h * ss + rr * ss * 0.45],
                      outline=(255, 120, 90, 230), width=5 * ss)
    else:
        d.ellipse([S(0.5, 0.5)[0] - 0.22 * w * ss, 0.78 * h * ss, S(0.5, 0.5)[0] + 0.22 * w * ss, 0.86 * h * ss],
                  outline=(255, 120, 90, 230), width=5 * ss)
    ov = ov.resize((w, h), Image.LANCZOS)
    return Image.alpha_composite(im, ov)


def draw_eola(name: str, size) -> Image.Image:
    w, h = size
    chapter, title = EOLA[name]
    im = Image.new("RGB", size, (22, 24, 30))
    d = ImageDraw.Draw(im)
    f = lambda px: ImageFont.truetype(str(FONTS / "CMUSerif-Roman.ttf"), px)
    fb = lambda px: ImageFont.truetype(str(FONTS / "CMUSerif-Bold.ttf"), px)
    d.rectangle([w * 0.05, h * 0.06, w * 0.95, h * 0.94], outline=(90, 140, 190), width=max(6, w // 400))
    d.text((w * 0.5, h * 0.20), "Essence of linear algebra", font=f(int(h * 0.075)), fill=(150, 170, 200), anchor="mm")
    d.text((w * 0.5, h * 0.40), f"Chapter {chapter}", font=fb(int(h * 0.15)), fill=(255, 255, 255), anchor="mm")
    words, lines, cur = title.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f(int(h * 0.095))) > w * 0.8 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = t
    lines.append(cur)
    for i, ln in enumerate(lines):
        d.text((w * 0.5, h * (0.62 + 0.12 * i)), ln, font=f(int(h * 0.095)), fill=(240, 200, 90), anchor="mm")
    return im


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    names = [n for n in SPEC if not a.only or n in a.only.split(",")]
    if a.list:
        for n in names:
            print(n, SPEC[n], FRAMES.get(n, "drawn" if n in DRAWN else "title card"))
        return
    out = a.out or Path(tempfile.mkdtemp(prefix="frames2018_"))
    out.mkdir(parents=True, exist_ok=True)
    registry, tmp = {}, Path(tempfile.mkdtemp(prefix="grab2018_"))
    for n in names:
        w, h, mode = SPEC[n]
        note, via, scene_ref = "", "drawing", ""
        if n in FRAMES:
            proj, scene, frac, subject = FRAMES[n]
            video = RENDERS / proj / f"{scene}.mp4"
            png = tmp / (n + ".png")
            if video.exists():
                t = grab_frame(video, frac, png)
                scene_ref = f"renders/2018/{proj}/{scene}.mp4 at {t:.2f}s"
            elif (RENDERS / proj / f"{scene}.png").exists():  # static scene: the render is a PNG
                shutil.copy2(RENDERS / proj / f"{scene}.png", png)
                scene_ref = f"renders/2018/{proj}/{scene}.png"
            else:
                print("MISSING render:", video)
                continue
            im = cover(Image.open(png).convert("RGB"), (w, h))
            via = "frame"
            note = f"cover-scaled frame of {scene_ref}"
        elif n in DRAWN:
            subject, im = "own drawing of the Dandelin spheres picture (spheres, plane, tangency circles)", draw_dandelin(n, (w, h))
        else:
            subject, im = f"own title card for EOLA chapter {EOLA[n][0]}", draw_eola(n, (w, h))
        im = im.convert("RGBA") if mode == "RGBA" else im.convert("RGB")
        dst = out / n
        if n.endswith(".jpg"):
            im.save(dst, quality=90)
        else:
            im.save(dst)
        registry["raster_images/" + n] = {
            "asset": "raster_images/" + n, "name": n, "subject": subject, "author": "own (code" + (" + own render)" if via == "frame" else ")"),
            "license": LICENSE, "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/", "page_url": "",
            "changes": "Frame of an own render of the matching scene, cover-scaled to the original size and mode; no pixel of Grant's file is used."
                       if via == "frame" else "Drawn from scratch with numpy/PIL at the original size and mode; no pixel of Grant's file is used.",
            "status": "generated", "via": via, "note": note, "recipe_version": "2018-frames-v1",
            "verified_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        print("ok", n, dst)
    shutil.rmtree(tmp, ignore_errors=True)
    if a.install:
        BACKUP.mkdir(parents=True, exist_ok=True)
        for n in registry:
            n = Path(n).name
            if (RASTER / n).exists() and not (BACKUP / n).exists():
                shutil.copy2(RASTER / n, BACKUP / n)
            shutil.copy2(out / n, RASTER / n)
        REGISTRY.parent.mkdir(parents=True, exist_ok=True)
        old = json.loads(REGISTRY.read_text()) if REGISTRY.exists() else {}
        old.update(registry)
        REGISTRY.write_text(json.dumps(old, indent=1, ensure_ascii=False))
        print("installed", len(registry), "->", RASTER)


if __name__ == "__main__":
    main()
