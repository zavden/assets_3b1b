"""Own replacement for 22 images of `raster_images/` that the 2019 scenes use and that were screenshots of
Grant's scenes (thumbnails of his videos, frames of scenes of his own). The `assets/` folder of 3b1b/videos no
longer exists and copies of it cannot be published, so each file is rebuilt with the SAME name, width, height
and mode (RGB/RGBA) as the original, from OUR renders of the equivalent scene
(`renders/2019/<folder>/<Scene>.mp4`, or `.png` if the scene is static):

  - 14 come from a frame (ffmpeg) with "cover" crop and rescale: it is scaled without distortion until it covers
    the final size (LANCZOS) and cropped centered; optionally a previous crop in fractions and rectangles
    filled with black to cover a label that the original thumbnail does not have.
  - HeatSurfaceExample.jpg, MobiusStrip.png, DoublePendulumStart.png, PictoralODE.png,
    eoc_chapter5_thumbnail.jpg and fourier_series_thumbnail.png have no frame of our own that would do (the
    2019 heat surface was an external screenshot, the double pendulum is an external animation, etc.):
    they are drawn by code (numpy/matplotlib/PIL) in the style of the scenes.
  - HeatSurfaceExampleFlipped.jpg is the previous one mirrored left to right (Grant's original was also a
    horizontal mirror, not a vertical one).

No pixel of Grant's originals is read: only their size/mode is consulted (those in the CSV table).
`make_inscribed_rect_images.py` (2024) does NOT produce `MobiusStrip.png` (only `MobiusStripTexture.png`, a
flat texture), which is why the Mobius strip is drawn here.

  python make_frame_assets_2019.py [--out DIR] [--install] [--hires-dir DIR] [--solo A.png,B.jpg]
                                   [--registro FILE.json] [--fresca-desde "YYYY-MM-DD HH:MM"] [--renders DIR] [--listar]

  --out DIR         where the 22 images are written (by default the system temp folder, in frames2019/; NOT the repo).
  --install         writes into _lib/assets/raster_images/ (first saves the original in
                    _tools/.cache/assets2019/previos/raster_images/ if it is not already there) and the record in
                    _lib/assets/generated/replacements/assets2019/assets2019_frames_sources.json.
  --hires-dir DIR   if DIR/<Scene>_<image>.png or DIR/<Scene>.png exists, that frame is used (same
                    instant, higher resolution, e.g. 2560x1440) instead of the video. Crops are given in
                    fractions, so they work for any resolution.
  --solo ...        only those images (with .png/.jpg; HeatSurfaceExampleFlipped drags in HeatSurfaceExample).
  --registro FILE   JSON record (by default OUT/assets2019_frames_sources.json; with --install, the repo's).
  --fresca-desde T  flags in the summary the source videos older than T (renders not refreshed).
  --renders DIR     extra folder (renders/2019 type) where to look for missing renders (for tests only, e.g. the
                    backup renders_respaldo_assets2019_*/2019; do not use it in the final phase: it would be an old render).
  --listar          only prints the table image -> scene -> instant.

Dependencies: system ffmpeg/ffprobe, numpy, PIL and matplotlib from the venv; CMU Serif fonts.
For PictoralODE it uses the own icons rabbit.svg/fox.svg from _lib/assets/svg_images/ (rsvg-convert)."""
import argparse
import datetime
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parents[2]          # _lib/assets
LIB = ASSETS.parent                                    # _lib
ROOT = LIB.parent                                      # converted
RENDERS = ROOT / "renders" / "2019"
RASTER = ASSETS / "raster_images"
SVGS = ASSETS / "svg_images"
PREVIOS = ROOT / "_tools" / ".cache" / "assets2019" / "previos" / "raster_images"
WORK = ROOT / "_work" / "_2019"
REGISTRO_REPO = ASSETS / "generated" / "replacements" / "assets2019" / "assets2019_frames_sources.json"
OUT_PRUEBA = Path(tempfile.gettempdir()) / "frames2019"

LICENCIA = "CC BY-NC-SA 4.0 (own work, derived from 3b1b/videos)"
LICENCIA_URL = "https://creativecommons.org/licenses/by-nc-sa/4.0/"
RECETA = "2019-frames-v1"

FONT_RM = "/usr/share/fonts/cm-unicode/cmunrm.otf"
FONT_IT = "/usr/share/fonts/cm-unicode/cmunti.otf"
FONT_MATH = "/usr/share/fonts/lm-math/latinmodern-math.otf"   # Latin Modern Math (mathematical italics U+1D4xx)
YELLOW, BLUE, GREEN, RED, PINK = (255, 255, 0), (88, 196, 221), (131, 193, 103), (252, 98, 85), (209, 71, 189)

# Size and mode of each image (those of the original; see assets2019_fotogramas.csv). t: None = static scene
# (.png); "ultimo" = last frame of the video; number = seconds from the start. crop: (x0, y0, x1, y1) as
# fractions of the source frame; paint: [((x0, y0, x1, y1), (r, g, b)), ...] gen: name of the function that
# draws the image by code (no source scene).
IMAGENES = {
    # --- frames from our own renders ---
    "ClacksQuestionThumbnail.png": dict(
        size=(2560, 1440), mode="RGBA", scene="clacks/question/Thumbnail", t=None,
        what="miniatura del video 'Clacks question' (pregunta: cuantas colisiones)"),
    "ClacksSolution1Thumbnail.png": dict(
        size=(2560, 1440), mode="RGBA", scene="clacks/solution1/SolutionThumbnail", t=None,
        what="miniatura de 'Clacks solution 1'"),
    "ClacksThumbnail.png": dict(
        size=(2560, 1440), mode="RGB", scene="clacks/question/Thumbnail", t=None,
        what="miniatura de los clacks (pregunta del primer video)"),
    "bayes_thumbnail.png": dict(
        size=(2560, 1440), mode="RGBA", scene="bayes/part1/Thumbnail", t=None,
        what="miniatura del video de Bayes (diagrama de area P(E|H), P(H))"),
    "diffyq_part2_thumbnail.png": dict(
        size=(2560, 1440), mode="RGBA", scene="diffyq/part2/staging/Thumbnail", t=None,
        requiere=["HeatSurfaceExampleFlipped.jpg"],
        what="miniatura de diffyq parte 2 ('What is this?' + ecuacion del calor + superficie)"),
    "diffyq_part3_thumbnail.png": dict(
        size=(2560, 1440), mode="RGBA", scene="diffyq/part3/temperature_graphs/Thumbnail", t=None,
        what="miniatura de diffyq parte 3 (superficie de ondas senoidales que se amortiguan)"),
    "diffyq_part4_thumbnail.png": dict(
        size=(2560, 1440), mode="RGBA", scene="diffyq/part4/fourier_series_scenes/DE4Thumbnail", t=None,
        requiere=["svg_images/FourierOneLine.svg"],
        what="miniatura de diffyq parte 4 (dibujos con epiciclos n=10, 50, 250)"),
    "PrimeSpiral.png": dict(
        size=(2560, 1440), mode="RGBA", scene="spirals/PrimeSpiralsAtScale1000", t=None,
        what="espiral de primos (puntos (p, p) en polares)"),
    "LovePhaseSpace.png": dict(
        size=(2560, 1440), mode="RGBA", scene="diffyq/part1/phase_space/LovePhaseSpace", t=28.0,
        what="espacio de fases del amor (campo de vectores + ecuaciones con corazones)"),
    "AnalyzeCircleGeometry.png": dict(
        size=(3358, 1886), mode="RGBA", scene="clacks/solution1/AnalyzeCircleGeometry", t=6.0,
        what="circulo de colisiones con razon de masas 16:1 y zona final"),
    "BlocksAndWallExampleMass16.png": dict(
        size=(2560, 1440), mode="RGB", scene="clacks/solution1/BlocksAndWallExampleMass16", t=0.0,
        what="bloques y pared con masa 16, contador de colisiones en 0"),
    "boundary_condition_thumbnail.png": dict(
        size=(2560, 1440), mode="RGBA", scene="diffyq/part3/temperature_graphs/BoundaryConditionReference", t="ultimo",
        paint=[((0.0, 0.0, 1.0, 0.32), (0, 0, 0))],      # covers the label "Different rules at the boundary"
        what="varilla con colores de temperatura y flechas en los extremos (sin rotulo)"),
    "linearity_thumbnail.png": dict(
        size=(2555, 1258), mode="RGBA", scene="diffyq/part3/temperature_graphs/BreakDownAFunction", t="ultimo",
        crop=(0.0, 0.0, 1.0, 0.875),                       # leaves out the label "Sine curves" at the bottom
        what="funcion arbitraria = suma de superficies senoidales (cada una con su marca de visto bueno)"),
    "sine_curve_temp_graph.png": dict(
        size=(2598, 1880), mode="RGBA", scene="diffyq/part3/temperature_graphs/SineWaveScaledByExp", t=5.0,
        crop=(0.22, 0.0, 1.0, 1.0),                        # the scene leaves the left 22 % empty
        what="superficie de temperatura: onda seno amortiguada en el tiempo"),
    "temp_initial_condition_example.png": dict(
        size=(3252, 1752), mode="RGBA", scene="diffyq/part3/temperature_graphs/CloserLookAtStraightLine", t=0.0,
        what="condicion inicial de temperatura lineal sobre la varilla (reloj en 0.00)"),
    # --- drawn by code ---
    "HeatSurfaceExample.jpg": dict(
        size=(2560, 1440), mode="RGB", gen="gen_heat_surface",
        what="superficie 3D de temperatura (serie de cosenos truncada de un reparto de bloques calientes/frios)"),
    "HeatSurfaceExampleFlipped.jpg": dict(
        size=(2560, 1440), mode="RGB", derive=("HeatSurfaceExample.jpg", "hflip"),
        what="la superficie anterior reflejada de izquierda a derecha"),
    "MobiusStrip.png": dict(
        size=(1463, 875), mode="RGBA", gen="gen_mobius",
        what="banda de Mobius de superficie azul grisaseo con bordes rojos"),
    "DoublePendulumStart.png": dict(
        size=(2560, 1440), mode="RGBA", gen="gen_double_pendulum",
        what="pendulo doble en su posicion inicial (dos varillas y dos masas)"),
    "PictoralODE.png": dict(
        size=(1212, 812), mode="RGBA", gen="gen_pictorial_ode", usa_svg=["rabbit.svg", "fox.svg"],
        what="EDO presa-depredador con los iconos propios de conejo y zorro"),
    "eoc_chapter5_thumbnail.jpg": dict(
        size=(1280, 720), mode="RGB", gen="gen_eoc5",
        what="tarjeta 'Essence of Calculus, capitulo 5' (2017, sin render; sin logos)"),
    "fourier_series_thumbnail.png": dict(
        size=(1418, 876), mode="RGBA", gen="gen_fourier_series",
        what="sumas parciales de la serie de cosenos de la funcion escalon sobre [0, 1]"),
}


# ----------------------------------------------------------------------------------------------------------
# Image utilities
# ----------------------------------------------------------------------------------------------------------
def fuente(path, size):
    return ImageFont.truetype(path, size)


def sha256_de(path_o_bytes):
    h = hashlib.sha256()
    if isinstance(path_o_bytes, (bytes, bytearray)):
        h.update(path_o_bytes)
    else:
        h.update(Path(path_o_bytes).read_bytes())
    return h.hexdigest()


def a_rgb(im):
    """RGB on black (Manim frames are opaque, but a PNG with alpha is composited over black)."""
    if im.mode == "RGB":
        return im
    im = im.convert("RGBA")
    fondo = Image.new("RGBA", im.size, (0, 0, 0, 255))
    return Image.alpha_composite(fondo, im).convert("RGB")


def cover(im, size):
    """Scales without distortion until covering `size` (LANCZOS) and crops centered."""
    w, h = size
    k = max(w / im.width, h / im.height)
    nw, nh = max(w, round(im.width * k)), max(h, round(im.height * k))
    im = im.resize((nw, nh), Image.LANCZOS)
    x0, y0 = (nw - w) // 2, (nh - h) // 2
    return im.crop((x0, y0, x0 + w, y0 + h))


def ajustar_modo(im, mode):
    """Leaves the image in the original's mode: RGB, or fully opaque RGBA."""
    im = a_rgb(im)
    if mode == "RGBA":
        im = im.convert("RGBA")
    return im


def fracc_a_caja(box, size):
    x0, y0, x1, y1 = box
    w, h = size
    return (round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h))


# ----------------------------------------------------------------------------------------------------------
# Frames from the renders
# ----------------------------------------------------------------------------------------------------------
RAICES = [RENDERS]          # folders where to look for the renders (extended with --renders)


def ruta_origen(scene):
    """(.mp4 or .png) of the scene's render in the first folder that has it; None if it does not exist."""
    for raiz in RAICES:
        for ext in (".mp4", ".png"):
            p = raiz / (scene + ext)
            if p.exists():
                return p
    return None


def duracion(video):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)])
    return float(out.decode().strip())


def extraer_fotograma(video, t, tmp):
    """Frame of the video at instant t (seconds), or the last one if t == 'ultimo'; returns a PIL image."""
    salida = Path(tmp) / "f.png"
    salida.unlink(missing_ok=True)
    if t == "ultimo":
        cmd = ["ffmpeg", "-v", "error", "-y", "-sseof", "-0.5", "-i", str(video), "-update", "1", str(salida)]
    else:
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{float(t):.3f}", "-i", str(video),
               "-frames:v", "1", str(salida)]
    subprocess.run(cmd, check=True)
    im = Image.open(salida)
    im.load()
    return a_rgb(im)


def buscar_hires(hires_dir, scene, nombre):
    if not hires_dir:
        return None
    base = Path(scene).name
    for cand in (f"{base}_{Path(nombre).stem}.png", f"{base}.png"):
        p = Path(hires_dir) / cand
        if p.exists():
            return p
    return None


def hacer_fotograma(nombre, cfg, hires_dir, tmp):
    """Final image (PIL) + provenance data, from the scene's render (or from the hires frame)."""
    scene = cfg["scene"]
    hires = buscar_hires(hires_dir, scene, nombre)
    origen = ruta_origen(scene)
    if hires is not None:
        src = a_rgb(Image.open(hires))
        ruta = hires
        instante = "fotograma hires (mismo instante)"
    elif origen is None:
        raise FileNotFoundError(f"no hay render de {scene} en {[str(r) for r in RAICES]}")
    else:
        ruta = origen
        if origen.suffix == ".png":
            src, instante = a_rgb(Image.open(origen)), "escena estatica (.png)"
        else:
            t = cfg["t"]
            src = extraer_fotograma(origen, t, tmp)
            instante = "ultimo fotograma" if t == "ultimo" else f"{float(t):.2f} s"
    src_size = src.size
    for caja, color in cfg.get("paint", []):
        ImageDraw.Draw(src).rectangle(fracc_a_caja(caja, src.size), fill=color)
    if "crop" in cfg:
        src = src.crop(fracc_a_caja(cfg["crop"], src.size))
    w, h = cfg["size"]
    k = max(w / src.width, h / src.height)
    im = ajustar_modo(cover(src, cfg["size"]), cfg["mode"])
    info = dict(
        source_scene=scene,
        source_video=str(ruta.relative_to(ROOT)) if ROOT in ruta.parents else str(ruta),
        source_from_backup=ruta.is_relative_to(RENDERS) is False,
        source_instant=instante,
        source_resolution=list(src_size),
        crop=cfg.get("crop"),
        upscale_factor=round(k, 2),
        hires=hires is not None,
        source_mtime=datetime.datetime.fromtimestamp(ruta.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
    )
    return im, info


# ----------------------------------------------------------------------------------------------------------
# Images drawn by code
# ----------------------------------------------------------------------------------------------------------
def _matplotlib():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def _fig_a_imagen(fig, size):
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    im = Image.fromarray(buf[..., :3].copy(), "RGB")
    return im if im.size == size else im.resize(size, Image.LANCZOS)


def gen_heat_surface(size):
    """3D temperature surface: distribution of hot/cold blocks over a square, truncated to a few cosine
    modes (hence the Gibbs ripples) and allowed to diffuse a little; colored with a rainbow by
    height (red = hot, blue = cold) and shaded, on a black background."""
    from matplotlib import cm
    from matplotlib.colors import LightSource
    plt = _matplotlib()
    n, modos = 160, 11
    x = (np.arange(n) + 0.5) / n
    X, Y = np.meshgrid(x, x)
    rng = np.random.default_rng(2019)                       # fixed seed
    bloques = rng.uniform(-1.0, 1.0, (4, 4))
    T0 = bloques[(Y * 4).astype(int), (X * 4).astype(int)]
    m = np.arange(modos)
    C = np.cos(np.pi * np.outer(m, x))                      # (modes, n)
    A = (C @ T0 @ C.T) * 4 / n ** 2
    A[0, :] /= 2
    A[:, 0] /= 2
    decae = np.exp(-0.0006 * np.pi ** 2 * (m[:, None] ** 2 + m[None, :] ** 2))
    Z = C.T @ (A * decae) @ C
    Z = (Z - Z.min()) / (Z.max() - Z.min())
    luz = LightSource(azdeg=300, altdeg=50)
    rgb = luz.shade(Z, cmap=cm.jet, vert_exag=0.9, blend_mode="soft", vmin=0, vmax=1)
    fig = plt.figure(figsize=(size[0] / 100, size[1] / 100), dpi=100, facecolor="black")
    ax = fig.add_axes([0, 0, 1, 1], projection="3d", facecolor="black")
    sup = ax.plot_surface(X, Y, Z, facecolors=rgb, rstride=1, cstride=1, linewidth=0, antialiased=False, shade=False)
    sup.set_clip_on(False)                                  # the 3D axis is square and would crop the sides
    ax.set_box_aspect((1, 1, 0.75), zoom=1.3)
    ax.view_init(elev=32, azim=-58)
    ax.set_axis_off()
    im = _fig_a_imagen(fig, size)
    plt.close(fig)
    return im


def gen_mobius(size):
    """Mobius strip (classic parametrization) in grayish blue with a red edge, on a black background. The
    shading comes from the surface's analytic normal (fixed light, on both faces)."""
    plt = _matplotlib()
    u = np.linspace(0, 2 * np.pi, 360)
    v = np.linspace(-1, 1, 36)
    U, V = np.meshgrid(u, v)
    c, sn = np.cos(U / 2), np.sin(U / 2)
    r = 1 + 0.5 * V * c
    X, Y, Z = r * np.cos(U), r * np.sin(U), 0.5 * V * sn
    # partial derivatives with respect to u and v -> normal
    Pu = np.dstack([-0.25 * V * sn * np.cos(U) - r * np.sin(U), -0.25 * V * sn * np.sin(U) + r * np.cos(U),
                    0.25 * V * c])
    Pv = np.dstack([0.5 * c * np.cos(U), 0.5 * c * np.sin(U), 0.5 * sn])
    N = np.cross(Pu, Pv)
    N /= np.linalg.norm(N, axis=2, keepdims=True)
    luz = np.array([-0.45, -0.55, 0.70])
    luz /= np.linalg.norm(luz)
    brillo = 0.38 + 0.62 * np.abs(N @ luz)
    base = np.array([0.40, 0.58, 0.64])
    caras = np.clip(base * brillo[..., None], 0, 1)
    fig = plt.figure(figsize=(size[0] / 100, size[1] / 100), dpi=100, facecolor="black")
    ax = fig.add_axes([0, 0, 1, 1], projection="3d", facecolor="black")
    sup = ax.plot_surface(X, Y, Z, facecolors=caras, rstride=1, cstride=1, linewidth=0, antialiased=False, shade=False)
    sup.set_clip_on(False)
    for s_ in (-1, 1):                                      # the edge is a single closed curve of two turns
        rr = 1 + 0.5 * s_ * np.cos(u / 2)
        ax.plot(rr * np.cos(u), rr * np.sin(u), 0.5 * s_ * np.sin(u / 2), color="#ff5a50", lw=3.6)
    ax.set_box_aspect((1, 1, 0.34), zoom=1.55)
    ax.view_init(elev=33, azim=-68)
    ax.set_axis_off()
    im = _fig_a_imagen(fig, size)
    plt.close(fig)
    return im


def gen_double_pendulum(size):
    """Double pendulum (two white rods, magenta joint, green end mass) on black."""
    k = 2                                                   # supersampling
    w, h = size[0] * k, size[1] * k
    im = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(im)
    px, py = 0.50 * w, 0.58 * h                             # pivote
    l1, l2 = 0.34 * h, 0.30 * h
    a1, a2 = math.radians(125), math.radians(-35)           # angles from the downward vertical
    p1 = (px + l1 * math.sin(a1), py + l1 * math.cos(a1))
    p2 = (p1[0] + l2 * math.sin(a2), p1[1] + l2 * math.cos(a2))
    ancho = 9 * k
    d.line([(px, py), p1], fill=(255, 255, 255), width=ancho)
    d.line([p1, p2], fill=(255, 255, 255), width=ancho)
    for (cx, cy), r, c in [((px, py), 13 * k, (255, 255, 255)), (p1, 22 * k, (209, 71, 189)),
                           (p2, 22 * k, (131, 193, 103))]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    return im.resize(size, Image.LANCZOS)


GRIEGAS = {"α": "\U0001d6fc", "β": "\U0001d6fd", "γ": "\U0001d6fe", "δ": "\U0001d6ff"}   # mathematical italics


def _rasterizar_svg(nombre, alto, color):
    """Rasterizes one of our own svg_images icons (rsvg-convert) and recolors it: the dark areas of the silhouette
    take `color` and the light details (eye, snout) a darkened version, as in the scene (fill_color)."""
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "i.png"
        subprocess.run(["rsvg-convert", "-h", str(alto), str(SVGS / nombre), "-o", str(png)], check=True)
        ic = Image.open(png).convert("RGBA")
    a = np.asarray(ic).astype(float)
    claro = (a[..., :3].mean(axis=2) > 128)[..., None]
    c = np.array(color, float)
    rgb = np.where(claro, c * 0.2, c)
    out = np.dstack([rgb, a[..., 3]]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def gen_pictorial_ode(size):
    """Card with the predator-prey system d(rabbit)/dt = rabbit (alpha - beta fox), d(fox)/dt = fox
    (delta rabbit - gamma), with our own rabbit.svg and fox.svg icons recolored (pale blue and orange)."""
    k = 2
    w, h = size[0] * k, size[1] * k
    im = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    f_it = f_rm = fuente(FONT_MATH, 128 * k)
    ic = 118 * k
    conejo = _rasterizar_svg("rabbit.svg", ic, (198, 214, 239))
    zorro = _rasterizar_svg("fox.svg", ic, (223, 127, 32))

    def texto(x, y, s, f, anclaje="lm"):
        d.text((x, y), s, font=f, fill=(255, 255, 255, 255), anchor=anclaje)
        return x + d.textlength(s, font=f)

    def icono(x, y, img):
        im.alpha_composite(img, (round(x), round(y - img.height / 2)))
        return x + img.width

    def ecuacion(y0, lhs, rhs):
        """y0: axis of the fraction. lhs: 'd' + icon over 'dt'; rhs: list of pieces."""
        x = 70 * k
        # numerator: d + icon; denominator: dt
        xn = texto(x, y0 - 78 * k, "\U0001d451", f_it)
        xn = icono(xn + 4 * k, y0 - 78 * k, lhs)
        xd = texto(x + 50 * k, y0 + 78 * k, "\U0001d451\U0001d461", f_it)
        ancho = max(xn, xd) - x
        d.line([(x - 6 * k, y0), (x + ancho + 6 * k, y0)], fill=(255, 255, 255, 255), width=5 * k)
        x = x + ancho + 40 * k
        x = texto(x, y0, "=", f_rm) + 36 * k
        for pieza in rhs:
            if isinstance(pieza, str):
                x = texto(x, y0, GRIEGAS.get(pieza, pieza), f_it) + 8 * k
            else:
                x = icono(x, y0, pieza) + 8 * k

    ecuacion(h * 0.27, conejo, [conejo, "·", "(", "α", "−", "β", zorro, ")"])
    ecuacion(h * 0.73, zorro, [zorro, "·", "(", "δ", conejo, "−", "γ", ")"])
    return im.resize(size, Image.LANCZOS).convert("RGB")


def gen_eoc5(size):
    """Card for chapter 5 of 'Essence of Calculus' (2017): title and chapter on black, with a yellow
    exponential curve under the axes; no logos or anything from third parties."""
    k = 2
    w, h = size[0] * k, size[1] * k
    im = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(im)
    f1, f2 = fuente(FONT_RM, 118 * k), fuente(FONT_IT, 86 * k)
    d.text((w / 2, 0.20 * h), "Essence of Calculus", font=f1, fill=(255, 255, 255), anchor="mm")
    d.text((w / 2, 0.36 * h), "capítulo 5", font=f2, fill=YELLOW, anchor="mm")
    # axes and curve y = e^(x): grows to the right
    x0, x1, y0, y1 = 0.18 * w, 0.82 * w, 0.93 * h, 0.52 * h
    d.line([(x0, y0), (x1, y0)], fill=(200, 200, 200), width=3 * k)
    d.line([(x0, y0), (x0, y1 - 0.02 * h)], fill=(200, 200, 200), width=3 * k)
    xs = np.linspace(0, 1, 400)
    ys = (np.exp(3.4 * xs) - 1) / (np.exp(3.4) - 1)
    pts = [(x0 + (x1 - x0) * a, y0 - (y0 - y1) * b) for a, b in zip(xs, ys)]
    d.line(pts, fill=YELLOW, width=6 * k, joint="curve")
    return im.resize(size, Image.LANCZOS)


def gen_fourier_series(size):
    """Two axes (ticks at 0.5 and 1.0) with the partial sums of 4/pi (cos(pi x) - cos(3 pi x)/3 + ...), which
    tends to 1 if x < 0.5 and to -1 if x > 0.5: a few thin ones and the last one thick, in yellow (colors of the
    scene FourierSeriesIllustraiton)."""
    k = 2
    w, h = size[0] * k, size[1] * k
    im = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(im)
    xa, xb = 0.10 * w, 0.90 * w
    cy, amp = 0.50 * h, 0.34 * h
    gris = (190, 190, 190)
    d.line([(xa, cy), (xb + 0.03 * w, cy)], fill=gris, width=4 * k)
    d.line([(xa, cy - 1.12 * amp), (xa, cy + 1.12 * amp)], fill=gris, width=4 * k)
    f = fuente(FONT_RM, 50 * k)
    for val in (0.25, 0.5, 0.75, 1.0):
        x = xa + (xb - xa) * val
        d.line([(x, cy - 12 * k), (x, cy + 12 * k)], fill=gris, width=4 * k)
        if val in (0.5, 1.0):
            d.text((x, cy + 62 * k), f"{val:.1f}", font=f, fill=(255, 255, 255), anchor="mm",
                   stroke_width=5 * k, stroke_fill=(0, 0, 0))
    xs = np.linspace(0, 1, 1200)

    def suma(n):
        return sum(4 / np.pi * (-1) ** j * np.cos((2 * j + 1) * np.pi * xs) / (2 * j + 1) for j in range(n))

    def trazar(y, color, ancho, fondo=None):
        pts = [(xa + (xb - xa) * a, cy - amp * b) for a, b in zip(xs, y)]
        if fondo:
            d.line(pts, fill=(0, 0, 0), width=fondo * k, joint="curve")
        d.line(pts, fill=color, width=ancho * k, joint="curve")

    for n, color in [(1, BLUE), (2, GREEN), (3, RED), (4, PINK), (6, (170, 170, 120))]:
        trazar(suma(n), tuple(int(c * 0.55) for c in color), 3)
    trazar(suma(12), YELLOW, 8, fondo=14)
    return im.resize(size, Image.LANCZOS)


GENERADORES = {f.__name__: f for f in
               (gen_heat_surface, gen_mobius, gen_double_pendulum, gen_pictorial_ode, gen_eoc5, gen_fourier_series)}


# ----------------------------------------------------------------------------------------------------------
# Output and record
# ----------------------------------------------------------------------------------------------------------
def hoja_contacto(carpeta, nombres, destino, ancho=480, alto=270, columnas=4):
    """Contact sheet (JPG) with the images already written, to review them at a glance."""
    filas = (len(nombres) + columnas - 1) // columnas
    hoja = Image.new("RGB", (columnas * ancho, filas * (alto + 20)), (48, 48, 48))
    d = ImageDraw.Draw(hoja)
    for i, n in enumerate(nombres):
        im = Image.open(Path(carpeta) / n)
        tam = im.size
        mini = a_rgb(im).copy()
        mini.thumbnail((ancho - 4, alto - 2))
        x, y = (i % columnas) * ancho, (i // columnas) * (alto + 20)
        hoja.paste(mini, (x + 2, y + 20))
        d.text((x + 4, y + 4), f"{n}  {tam[0]}x{tam[1]} {im.mode}", fill=(255, 255, 0))
    hoja.save(destino, quality=88)


def guardar(im, path, nombre):
    if nombre.lower().endswith((".jpg", ".jpeg")):
        im.convert("RGB").save(path, quality=95, subsampling=0)
    else:
        im.save(path, optimize=True)


_INDICE_ESCENAS = {}


def usos_en_escenas(nombre):
    """Up to 3 lines of _work/_2019 (without the .orig.py files) that read the image: it serves as `scene_review`."""
    if not _INDICE_ESCENAS:                                   # they are read only once
        for p in sorted(WORK.rglob("*.py")):
            if p.name.endswith(".orig.py") or "__pycache__" in p.parts:
                continue
            try:
                _INDICE_ESCENAS[p] = p.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
    stem = Path(nombre).stem
    hallazgos = []
    for p, lineas in _INDICE_ESCENAS.items():
        for i, linea in enumerate(lineas, 1):
            if f'"{stem}"' in linea and not linea.lstrip().startswith("#"):
                hallazgos.append({"scene": str(p.relative_to(ROOT)), "line": i, "context": linea.strip()})
    return hallazgos


def entrada_registro(nombre, cfg, im, datos, info, estado, antiguo):
    mismo = antiguo == datos["sha256"]
    ejemplo = usos_en_escenas(nombre)
    if "scene" in cfg:
        autor = f"own (frame of {cfg['scene']})"
        via = "frame"
        cambios = ("Fotograma de un render propio de la escena; recorte/reescala 'cover' (LANCZOS) al tamaño y modo "
                   "exactos del original; no se copia ningún píxel del original de Grant.")
    elif "derive" in cfg:
        autor, via = "own (mirror of HeatSurfaceExample)", "código"
        cambios = "Reflejo horizontal de la imagen propia HeatSurfaceExample (el original también era un espejo)."
    else:
        autor, via = f"own (code: {cfg['gen']})", "código"
        cambios = "Dibujada por código (numpy/matplotlib/PIL); no deriva del original de Grant."
    e = {
        "asset": f"raster_images/{nombre}",
        "name": nombre,
        "subject": cfg["what"],
        "author": autor,
        "license": LICENCIA,
        "license_url": LICENCIA_URL,
        "page_url": "",
        "changes": cambios,
        "status": "generated",
        "via": via,
        "recipe_version": RECETA,
        "verified_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scene_review": {"scene": ejemplo[0]["scene"] if ejemplo else "", "matches": [
            {"line": u["line"], "context": u["context"]} for u in ejemplo[:3]]},
        "note": f"Tamaño y modo conservados ({im.width}x{im.height} {im.mode}).",
        "old_sha256": antiguo if not mismo else None,
        "delivery_state": estado,
        "sha256": datos["sha256"],
        "final_size_bytes": datos["bytes"],
    }
    e.update(info)
    if cfg.get("requiere"):
        e["requires_before_render"] = cfg["requiere"]
    return e


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT_PRUEBA))
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--hires-dir")
    ap.add_argument("--solo")
    ap.add_argument("--registro")
    ap.add_argument("--renders", action="append", default=[],
                    help="carpeta extra (tipo renders/2019) donde buscar renders que falten; solo para pruebas")
    ap.add_argument("--fresca-desde")
    ap.add_argument("--listar", action="store_true")
    args = ap.parse_args()

    RAICES.extend(Path(r) for r in args.renders)
    nombres = list(IMAGENES)
    if args.solo:
        pedidos = {s.strip() for s in args.solo.split(",") if s.strip()}
        desconocidos = pedidos - set(IMAGENES)
        if desconocidos:
            sys.exit(f"imagenes desconocidas: {sorted(desconocidos)}")
        for n in list(pedidos):
            if "derive" in IMAGENES[n]:
                pedidos.add(IMAGENES[n]["derive"][0])
        nombres = [n for n in IMAGENES if n in pedidos]

    if args.listar:
        for n in nombres:
            c = IMAGENES[n]
            t = ("png estatico" if c["t"] is None else c["t"]) if "scene" in c else c.get("gen", c.get("derive"))
            print(f"{n:38s} {c.get('scene', '(codigo)'):70s} {t}")
        return

    out = RASTER if args.install else Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    corte = datetime.datetime.strptime(args.fresca_desde, "%Y-%m-%d %H:%M") if args.fresca_desde else None
    hechas, fallos, resumen = {}, [], []

    with tempfile.TemporaryDirectory() as tmp:
        for n in nombres:
            cfg = IMAGENES[n]
            try:
                if "scene" in cfg:
                    im, info = hacer_fotograma(n, cfg, args.hires_dir, tmp)
                elif "derive" in cfg:
                    base, op = cfg["derive"]
                    im = hechas[base][0].transpose(Image.FLIP_LEFT_RIGHT)
                    info = dict(source_scene=f"(derivada de {base})", source_instant=op)
                else:
                    im = ajustar_modo(GENERADORES[cfg["gen"]](cfg["size"]), cfg["mode"])
                    info = dict(source_scene="(dibujada por codigo)", source_instant="-")
                assert im.size == cfg["size"] and im.mode == cfg["mode"], (n, im.size, im.mode)
                hechas[n] = (im, info)
            except Exception as ex:                                   # noqa: BLE001 - it is reported and execution continues
                fallos.append((n, f"{type(ex).__name__}: {ex}"))

    if args.install and fallos:
        sys.exit(f"--install cancelado, faltan fuentes: {fallos}")

    registro = {}
    for n, (im, info) in hechas.items():
        cfg = IMAGENES[n]
        destino = out / n
        # Grant's original: the backup if it already exists; otherwise the current file (only for its hash)
        previo = PREVIOS / n
        actual = RASTER / n
        if args.install and actual.exists() and not previo.exists():
            PREVIOS.mkdir(parents=True, exist_ok=True)
            shutil.copy2(actual, previo)
        fuente_antigua = previo if previo.exists() else actual
        antiguo = sha256_de(fuente_antigua) if fuente_antigua.exists() else None
        guardar(im, destino, n)
        datos = {"sha256": sha256_de(destino), "bytes": destino.stat().st_size}
        registro[f"raster_images/{n}"] = entrada_registro(
            n, cfg, im, datos, info, "hecha" if args.install else "prueba", antiguo)
        viejo = ""
        if corte and "source_mtime" in info and datetime.datetime.strptime(
                info["source_mtime"], "%Y-%m-%d %H:%M:%S") < corte:
            viejo = "  [render anterior a --fresca-desde]"
        if info.get("source_from_backup"):
            viejo += "  [render tomado de --renders (respaldo)]"
        if cfg.get("requiere"):
            viejo += f"  [requiere antes: {', '.join(cfg['requiere'])}]"
        resumen.append(f"{n:38s} {info['source_scene']:68s} {info['source_instant']:>24s}  "
                       f"{str(info.get('source_resolution', '-')):>12s} x{info.get('upscale_factor', '-')}{viejo}")

    reg_path = Path(args.registro) if args.registro else (REGISTRO_REPO if args.install else out / REGISTRO_REPO.name)
    reg_path.parent.mkdir(parents=True, exist_ok=True)
    if args.solo and reg_path.exists():                       # with --solo only those entries are updated
        previo_reg = json.loads(reg_path.read_text(encoding="utf-8"))
        previo_reg.update(registro)
        registro = previo_reg
    reg_path.write_text(json.dumps(registro, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if not args.install:
        hoja_contacto(out, list(hechas), out / "contacto.jpg")
    print("\n".join(resumen))
    print(f"\n{len(hechas)} imagenes en {out}\nregistro: {reg_path}")
    for n, ex in fallos:
        print(f"FALLO {n}: {ex}")
    if fallos:
        sys.exit(1)


if __name__ == "__main__":
    main()
