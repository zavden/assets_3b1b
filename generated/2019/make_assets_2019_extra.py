"""Own or freely licensed replacements for the six files of `_lib/assets/` that, after the 2019 replacements, were still
identical to Grant's (I delete the `assets/` of 3b1b/videos and we cannot publish copies of it). Each file is written
with the SAME name and the same size in pixels (or `viewBox`) and mode as the original, so that the scenes read it
without changes:

  svg_images/imo_logo.svg        own generic emblem (laurel, shield with a pi and MATH OLYMPIAD ribbon). Code, CC0.
                                 viewBox 0 0 300 206. It does not resemble the IMO logo.
  svg_images/sun.svg             own generic sun (disk and 16 rays). Code, CC0. viewBox 0 0 302.4 302.4.
  raster_images/windmill.svg     own generic windmill (black silhouette). Code, CC0. 100x100.
  raster_images/google_logo.png  the own "G" of svg_images/google_logo.svg rasterized. 2223x2268 RGBA.
  raster_images/flags/us.png     flag of the USA from flag-icons (MIT, the same commit as the other flags). 550x289 RGB.
  raster_images/Riemann.jpg      portrait of Riemann (1863, public domain, Wikimedia Commons). 900x750 RGB, "cover" crop
                                 without distortion. Without network (or with --riemann-tarjeta): own card without a face.
  raster_images/IP_Sample_Page1.png  GENERIC sample pages of a mathematics book (header, title, lines of
  raster_images/IP_Sample_Page2.png  text simulated with bars, a curve with its tangent and a circle with its tangent).
  raster_images/IP_Sample_Page3.png  Code, CC0. 1582x1868, 1586x1372 and 1590x1426 RGBA (opaque alpha). No text from any book.

Each step leaves an entry in `assets2019_extra_sources.json` (same format as `assets2019_sources.json`: author,
license, URL, sha256, changes, scenes...). The license of the free sources (flag-icons, Commons) is checked on
every run; the own icons are CC0.

Usage (by default it writes into a temporary folder of the system, NOT into the repository):

  python make_assets_2019_extra.py [--out DIR] [--install] [--only imo_logo sun windmill google_logo us riemann ip_page1 ip_page2 ip_page3]
                                   [--riemann-tarjeta]

  --out DIR           output folder (the files with their path relative to assets/ and the JSON record)
  --install           also copies the files to `_lib/assets/...` (first saving Grant's original in
                      `_tools/.cache/assets2019/previos/<subfolder>/` if it is not already there) and writes the record in
                      `_lib/assets/generated/replacements/assets2019/assets2019_extra_sources.json`
  --only NAME ...     only those files
  --riemann-tarjeta   do not download the portrait: own card with the name and the dates (no face)

Requires Pillow, numpy, matplotlib (text outlines) and rsvg-convert. Downloading flag-icons and the portrait needs network."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import math
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[1]                    # _lib/assets
ROOT = HERE.parents[3]                      # converted
REGISTRO = ASSETS / "generated/replacements/assets2019/assets2019_extra_sources.json"
CACHE = ROOT / "_tools/.cache/assets2019"   # same caches as make_assets_2019.py
PREVIOS = CACHE / "previos"
FUENTES = ASSETS / "fonts"
CC0 = "https://creativecommons.org/publicdomain/zero/1.0/"
VERSION = "2019-extra-v1"
FLAG_COMMIT = "ac7e0eb3259eb62aa6100c435607e2fe03896a97"   # the same flag-icons commit as make_assets_2019.py
COMMONS_RIEMANN = "File:Georg Friedrich Bernhard Riemann.jpeg"
UA = {"User-Agent": "ManimLearningAssets2019Extra/1.0 (independent educational open-source asset audit)"}

# Grant's originals: size, mode and hash (for `old_sha256` and to know whether they must be saved before installing).
ORIGINALES = {
    "svg_images/imo_logo.svg": dict(viewbox="0 0 300 206", bytes=4427,
        sha256="c2b8871c368766b593ca55dd2b8ed5de4cba6af41eccdd713b36f5ab9f97600e"),
    "svg_images/sun.svg": dict(viewbox="0 0 302.4 302.4", bytes=2225,
        sha256="00050e3e3c7ab01fd7396eca01d7614c606a0805b0e2a95c78e19c4acc27bdec"),
    "raster_images/windmill.svg": dict(viewbox="0 0 100 100", bytes=4137,
        sha256="7f66953eb3b406157ffc121d8f20b3cd471339e0f5dafe55aa5c91be107d85cf"),
    "raster_images/google_logo.png": dict(size=(2223, 2268), mode="RGBA", bytes=73339,
        sha256="ac6050da7f571b4f64df148ee022758b0ee93ca3a3d6f31a8e3309477b2a6bbc"),
    "raster_images/flags/us.png": dict(size=(550, 289), mode="RGB", bytes=11584,
        sha256="b5b0da5ae266460e1cb6084e6f48f18a0fbc3c7cd286ecd3f6386503326e698a"),
    "raster_images/Riemann.jpg": dict(size=(900, 750), mode="RGB", bytes=90979,
        sha256="209927f6b7119f511c4a8ac019de81149a15a22d70bbd2dace9872384268a324"),
    "raster_images/IP_Sample_Page1.png": dict(size=(1582, 1868), mode="RGBA", bytes=371475,
        sha256="11ddfa5833ebac38fc67c5047aff4d5d770f58179da8f1cc744c7135f8e1471a"),
    "raster_images/IP_Sample_Page2.png": dict(size=(1586, 1372), mode="RGBA", bytes=292890,
        sha256="7a6ccdd7b7c4a7ded4985aac206c2999c987d9b2ed29b3884780223ee87b22b2"),
    "raster_images/IP_Sample_Page3.png": dict(size=(1590, 1426), mode="RGBA", bytes=529270,
        sha256="a21ad63c34c706c3f405f2e07b95fd0c118b85b446e76e44fbc32fa78356fc00"),
}

# 2019 scenes (`source::Scene`) whose code names the file, and what the actual read is (ManimGL's find_file:
# ImageMobject looks in raster_images/ with .jpg, .jpeg, .png...; SVGMobject only in svg_images/ with .svg).
W = "_2019/windmill.py::"
ESCENAS = {
    "svg_images/imo_logo.svg": [W + n for n in ("IntroduceIMO", "Describe2011IMO", "PerfectScoreData", "SixOnSix",
                                                "ShowTinyTao", "USProcessAlt", "Thumbnail2")],
    "svg_images/sun.svg": ["_2019/clacks/solution2/simple_scenes.py::ClacksSolution2Thumbnail"],
    "raster_images/windmill.svg": [W + "QuixoteReference"],
    "raster_images/google_logo.png": ["_2019/diffyq/part2/fourier_series.py::FourierGoogleG"],
    "raster_images/flags/us.png": [W + n for n in ("IntroduceIMO", "Describe2011IMO", "ShowTinyTao", "USProcessAlt",
                                                   "PerfectScoreData", "SixOnSix")],
    "raster_images/Riemann.jpg": ["_2019/diffyq/part4/staging.py::FourierGainsImmortality",
                                  "_2019/diffyq/part4/staging.py::CommentOnFouriersImmortality"],
    **{f"raster_images/IP_Sample_Page{n}.png": ["_2019/diffyq/part2/staging.py::StrogatzMention"] for n in (1, 2, 3)},
}
# (pattern to look for, file of _work/_2019 for the scene_review field)
REVISION = {
    "svg_images/imo_logo.svg": (r'imo_logo', "windmill/IntroduceIMO.py"),
    "svg_images/sun.svg": (r'ImageMobject\("sun"', "clacks/solution2/simple_scenes/ClacksSolution2Thumbnail.py"),
    "raster_images/windmill.svg": (r'SVGMobject\("windmill"\)', "windmill/QuixoteReference.py"),
    "raster_images/google_logo.png": (r'google_logo', "diffyq/part2/fourier_series/FourierGoogleG.py"),
    "raster_images/flags/us.png": (r'flags|"us"', "windmill/USProcessAlt.py"),
    "raster_images/Riemann.jpg": (r'Riemann', "diffyq/part4/staging/FourierGainsImmortality.py"),
    **{f"raster_images/IP_Sample_Page{n}.png": (r'IP_Sample_Page', "diffyq/part2/staging/StrogatzMention.py") for n in (1, 2, 3)},
}


# ------------------------------------------------------------------ general utilities

def sha(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


def ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


def escribir(ruta: Path, datos: bytes):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_name(ruta.name + ".part")
    tmp.write_bytes(datos)
    tmp.replace(ruta)


def escribir_json(ruta: Path, obj):
    escribir(ruta, (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode())


def rsvg(svg: bytes, *args: str) -> Image.Image:
    """Rasterizes an SVG (via stdin) with rsvg-convert to an RGBA PNG with a transparent background."""
    if not shutil.which("rsvg-convert"):
        raise RuntimeError("Falta rsvg-convert (librsvg)")
    salida = subprocess.run(["rsvg-convert", "-f", "png", *args, "-"], input=svg, check=True,
                            capture_output=True).stdout
    return Image.open(io.BytesIO(salida)).convert("RGBA")


def cargar_descargas():
    """Reuses the download helpers (http with waits, per-URL cache, Commons verification) of the downloads
    generator, pointed at the same cache as make_assets_2019.py."""
    sp = importlib.util.spec_from_file_location("download_helper",
                                                HERE.parent / "replacements/downloads/make_downloaded_assets.py")
    d = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(d)
    d.CACHE = CACHE
    d.UA = UA
    return d


# ------------------------------------------------------------------ SVG geometry

def num(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def pt(p) -> str:
    return f"{num(p[0])},{num(p[1])}"


def d_poligono(pts) -> str:
    return "M" + " L".join(pt(p) for p in pts) + " Z"


def d_circulo(cx, cy, r) -> str:
    """Circle with four cubics (error < 0.03 %)."""
    k = 0.5522847498 * r
    return (f"M{pt((cx + r, cy))} C{pt((cx + r, cy + k))} {pt((cx + k, cy + r))} {pt((cx, cy + r))} "
            f"C{pt((cx - k, cy + r))} {pt((cx - r, cy + k))} {pt((cx - r, cy))} "
            f"C{pt((cx - r, cy - k))} {pt((cx - k, cy - r))} {pt((cx, cy - r))} "
            f"C{pt((cx + k, cy - r))} {pt((cx + r, cy - k))} {pt((cx + r, cy))} Z")


def area(pts) -> float:
    return 0.5 * sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))


def orientado(pts, hueco=False):
    """Outer contour with positive area and holes with negative area (non-zero and even-odd fill rules coincide)."""
    pts = list(pts)
    return pts if (area(pts) < 0) == hueco else pts[::-1]


def estrella(cx, cy, R, fase=-90.0, razon=0.42):
    pts = []
    for k in range(10):
        r = R if k % 2 == 0 else R * razon
        a = math.radians(fase + 36 * k)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def elemento(d, fill=None, stroke=None, sw=None) -> str:
    atributos = ""
    if fill is not None:
        atributos += f' fill="{fill}"'
    if stroke is not None:
        atributos += f' stroke="{stroke}"'
    if sw is not None:
        atributos += f' stroke-width="{num(sw)}"'
    return f'<path{atributos} d="{d}"/>'


def d_texto(texto, centro, alto, fuente, ancho_max=None) -> str:
    """Outlines of a text (matplotlib TextPath) as SVG strokes, centered at `centro` and `alto` units high."""
    from matplotlib.font_manager import FontProperties
    from matplotlib.path import Path as MPath
    from matplotlib.textpath import TextPath
    tp = TextPath((0, 0), texto, size=100, prop=FontProperties(fname=str(FUENTES / fuente)))
    x0, y0, w, h = tp.get_extents().bounds
    k = alto / h
    if ancho_max and w * k > ancho_max:
        k = ancho_max / w

    def T(x, y):
        return pt((centro[0] + (x - x0 - w / 2) * k, centro[1] - (y - y0 - h / 2) * k))

    partes = []
    for v, codigo in tp.iter_segments():
        if codigo == MPath.MOVETO:
            partes.append("M" + T(*v))
        elif codigo == MPath.LINETO:
            partes.append("L" + T(*v))
        elif codigo == MPath.CURVE3:
            partes.append("Q" + T(*v[:2]) + " " + T(*v[2:]))
        elif codigo == MPath.CURVE4:
            partes.append("C" + T(*v[:2]) + " " + T(*v[2:4]) + " " + T(*v[4:]))
        elif codigo == MPath.CLOSEPOLY:
            partes.append("Z")
    return " ".join(partes)


def cabecera(viewbox, extra="") -> str:
    return (f'<?xml version="1.0" encoding="utf-8"?>\n<!-- Dibujo propio (codigo), CC0: make_assets_2019_extra.py -->\n'
            f'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}"{extra}>\n')


# ------------------------------------------------------------------ 1. svg_images/imo_logo.svg

def hacer_imo_logo():
    """Generic emblem: laurel of 56 leaves, golden and blue shield with a pi and three stars, and a red ribbon with the
    text MATH OLYMPIAD. Vector sibling of raster_images/imo_logo.png (same 300:206 = 800:549 proportion). The
    letter outlines come from JetBrains Mono Bold (SIL OFL 1.1, in assets/fonts)."""
    cx, cy, R = 150.0, 97.0, 80.0
    oro, oro_osc, oro_cl = "#E9B93F", "#A97B16", "#F5D77A"
    azul, azul_osc = "#2C55A0", "#122A58"
    rojo, rojo_osc, rojo_mas, crema = "#B3202F", "#7D1A24", "#4E0F16", "#FBE7A0"
    el = []

    # laurel: left branch and its mirror image; two leaves per node (inner and outer), from the ribbon upwards
    for k in range(14):
        ang = math.radians(120 + 9.8 * k)
        px, py = cx + R * math.cos(ang), cy + R * math.sin(ang)
        marcha = math.degrees(ang) + 90
        largo = 21 - 0.45 * k
        for lado, giro in ((-1, 28), (1, -28)):
            bx, by = px + lado * 3.3 * math.cos(ang), py + lado * 3.3 * math.sin(ang)
            a = math.radians(marcha + giro)
            ux, uy = math.cos(a), math.sin(a)
            punta = (bx + ux * largo, by + uy * largo)
            medio = (bx + ux * largo / 2, by + uy * largo / 2)
            c1 = (medio[0] - uy * 4.4, medio[1] + ux * 4.4)
            c2 = (medio[0] + uy * 4.4, medio[1] - ux * 4.4)
            for espejo in (False, True):
                P = [(2 * cx - x, y) if espejo else (x, y) for x, y in ((bx, by), c1, punta, c2)]
                el.append(elemento(f"M{pt(P[0])} Q{pt(P[1])} {pt(P[2])} Q{pt(P[3])} {pt(P[0])} Z", oro, oro_osc, 0.5))

    # ribbon (tails behind, folds, band and text)
    yb0, yb1 = 163.0, 189.0
    for lado in (-1, 1):
        x_in, x_out = cx + lado * 98, cx + lado * 139
        cola = [(x_in, yb0 + 6), (x_out, yb0 + 6), (x_out - lado * 12, yb0 + 19), (x_out, yb1 + 6), (x_in, yb1 + 6)]
        el.append(elemento(d_poligono(cola), rojo_osc))
        el.append(elemento(d_poligono([(x_in, yb1), (x_in, yb1 + 6), (x_in - lado * 12, yb1)]), rojo_mas))
    el.append(elemento(d_poligono([(cx - 100, yb0), (cx + 100, yb0), (cx + 100, yb1), (cx - 100, yb1)]), rojo))
    el.append(elemento(d_poligono([(cx - 100, yb0 + 2), (cx + 100, yb0 + 2), (cx + 100, yb0 + 3.2), (cx - 100, yb0 + 3.2)]), oro_cl))
    el.append(elemento(d_poligono([(cx - 100, yb1 - 3.2), (cx + 100, yb1 - 3.2), (cx + 100, yb1 - 2), (cx - 100, yb1 - 2)]), oro_cl))
    el.append(elemento(d_texto("MATH OLYMPIAD", (cx, (yb0 + yb1) / 2), 12.5, "JetBrainsMono-Bold.ttf", ancho_max=170), "#FBF3DC"))

    # shield: golden ring, dark border, blue disk with a thin ring, 24 dots, stars and pi
    el.append(elemento(d_circulo(cx, cy, 66), oro_cl))
    el.append(elemento(d_circulo(cx, cy, 63), oro_osc))
    el.append(elemento(d_circulo(cx, cy, 61), azul_osc))
    el.append(elemento(d_circulo(cx, cy, 55), azul))
    el.append(elemento(d_circulo(cx, cy, 47), None, oro, 1.4).replace('<path', '<path fill="none"', 1))
    for k in range(24):
        a = math.radians(k * 15)
        el.append(elemento(d_circulo(cx + 58 * math.cos(a), cy + 58 * math.sin(a), 1.3), "#F4F4F4"))
    el.append(elemento(d_poligono(estrella(cx, cy - 36, 8)), oro))
    for lado in (-1, 1):
        el.append(elemento(d_poligono(estrella(cx + lado * 29, cy + 25, 6.5)), oro))
    el.append(elemento(d_texto("π", (cx, cy - 2), 38, "JetBrainsMono-Bold.ttf"), crema))

    svg = cabecera("0 0 300 206") + "\n".join("  " + e for e in el) + "\n</svg>\n"
    return svg.encode(), dict(
        subject="Emblema genérico propio de una «olimpiada de matemáticas» dibujado por código: laurel, escudo con una π "
                "y una cinta con el texto MATH OLYMPIAD (hermano vectorial de raster_images/imo_logo.png); no imita el logo de la IMO",
        note="viewBox 0 0 300 206 como el original. Los contornos de las letras salen de JetBrains Mono Bold (SIL OFL 1.1, "
             "assets/fonts). Ninguna escena lee este SVG por nombre: ImageMobject(\"imo_logo\") resuelve a "
             "raster_images/imo_logo.png (ya sustituida).")


# ------------------------------------------------------------------ 2. svg_images/sun.svg

def hacer_sun():
    """Generic sun: disk and 16 triangular rays (8 long ones that touch the edge of the viewBox and 8 short ones). No color of its own
    (black by default, like the original: the scene paints it)."""
    c = 151.2
    el = [elemento(d_circulo(c, c, 66))]
    for k in range(16):
        ang = math.radians(22.5 * k)
        largo = k % 2 == 0
        r_punta, r_base, medio = (c, 84.0, 15.5) if largo else (126.0, 84.0, 11.0)
        da = medio / r_base
        pts = [(c + r_base * math.cos(ang - da), c + r_base * math.sin(ang - da)),
               (c + r_punta * math.cos(ang), c + r_punta * math.sin(ang)),
               (c + r_base * math.cos(ang + da), c + r_base * math.sin(ang + da))]
        el.append(elemento(d_poligono(pts)))
    svg = cabecera("0 0 302.4 302.4") + "\n".join("  " + e for e in el) + "\n</svg>\n"
    return svg.encode(), dict(
        subject="Sol genérico propio dibujado por código: disco con 16 rayos triangulares (8 largos y 8 cortos), monocromo",
        note="viewBox 0 0 302.4 302.4 como el original; sin color propio (negro por defecto, la escena lo pinta). "
             "ImageMobject(\"sun\") resuelve a raster_images/sun.png (NASA/SDO, ya sustituida); ninguna escena de 2019 "
             "lee este SVG.")


# ------------------------------------------------------------------ 3. raster_images/windmill.svg

def hacer_windmill():
    """Generic windmill: truncated-cone tower with a door and two windows, dome, base and four blades in an X (spar
    and lattice frame of slats with gaps). Black silhouette (fill on the root, like the original); 100x100."""
    hub = (50.0, 39.0)
    el = []

    def en_uv(a, r, v):
        ux, uy = math.cos(a), math.sin(a)
        return (hub[0] + r * ux - v * uy, hub[1] + r * uy + v * ux)

    for k in range(4):
        a = math.radians(45 + 90 * k)
        # larguero
        el.append(elemento(d_poligono(orientado([en_uv(a, -3, -1.2), en_uv(a, 42, -1.2), en_uv(a, 42, 1.2), en_uv(a, -3, 1.2)]))))
        # frame: outer rectangle with three gaps (slats 1.2 thick)
        r0, r1, v0, v1, t, b = 12.0, 40.0, 1.2, 9.6, 1.3, 1.2
        partes = [orientado([en_uv(a, r0, v0), en_uv(a, r1, v0), en_uv(a, r1, v1), en_uv(a, r0, v1)])]
        largo = (r1 - r0 - 2 * t - 2 * b) / 3
        for j in range(3):
            ra = r0 + t + j * (largo + b)
            partes.append(orientado([en_uv(a, ra, v0 + t), en_uv(a, ra + largo, v0 + t),
                                     en_uv(a, ra + largo, v1 - t), en_uv(a, ra, v1 - t)], hueco=True))
        el.append(elemento(" ".join(d_poligono(p) for p in partes)))

    def ventana(x0, x1, y_base, y_arco, n=10):
        """Gap with a semicircular arch: (x0,y_base)->(x0,y_arch)->arc->(x1,y_arch)->(x1,y_base)."""
        r, xc = (x1 - x0) / 2, (x0 + x1) / 2
        arco = [(xc - r * math.cos(math.pi * i / n), y_arco - r * math.sin(math.pi * i / n)) for i in range(n + 1)]
        return orientado([(x0, y_base)] + arco + [(x1, y_base)], hueco=True)

    torre = [orientado([(40, 48), (60, 48), (67.5, 91), (32.5, 91)]),
             ventana(46.5, 53.5, 88, 81), ventana(47.5, 52.5, 64, 59), ventana(47.5, 52.5, 74, 69)]
    el.append(elemento(" ".join(d_poligono(p) for p in torre)))
    cupula = [(50 + 11 * math.cos(math.pi + math.pi * i / 24), 48.5 + 11 * math.sin(math.pi + math.pi * i / 24)) for i in range(25)]
    el.append(elemento(d_poligono(orientado(cupula))))
    el.append(elemento(d_circulo(hub[0], hub[1], 3.4)))
    el.append(elemento(d_poligono(orientado([(24, 91), (76, 91), (76, 95.5), (24, 95.5)]))))
    svg = (cabecera("0 0 100 100", ' width="100px" height="100px" fill="#000000"')
           + "\n".join("  " + e for e in el) + "\n</svg>\n")
    return svg.encode(), dict(
        subject="Molino de viento genérico propio dibujado por código: torre con puerta y ventanas, cúpula y cuatro aspas "
                "de listones, silueta negra",
        note="100x100 como el original. SVGMobject(\"windmill\") (QuixoteReference) lee svg_images/windmill.svg, no este "
             "duplicado que vivía en raster_images/.")


# ------------------------------------------------------------------ 4. raster_images/google_logo.png

def hacer_google_logo():
    """Rasterizes piece index 5 (the own "G") of svg_images/google_logo.svg to 2223x2268 RGBA with a transparent background,
    touching top and bottom (the G is slightly narrower than the canvas). The five auxiliary dots of the SVG are not drawn.
    The scene (FourierGoogleG) reads SVGMobject("google_logo")[5], that is, the SVG; this PNG stays consistent with it."""
    fuente = ASSETS / "svg_images/google_logo.svg"
    svg = fuente.read_text(encoding="utf-8")
    trazos = re.findall(r"<path [^>]*/>", svg)
    assert len(trazos) == 6, "se esperaban 6 trazos en svg_images/google_logo.svg"
    for t in trazos[:-1]:
        svg = svg.replace(t, "", 1)
    color = re.search(r'fill="(#[0-9A-Fa-f]{6})"', trazos[-1]).group(1)
    rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
    gran = rsvg(svg.encode(), "-z", "26")
    alfa = gran.getchannel("A")
    alfa = alfa.crop(alfa.getbbox())
    W, H = ORIGINALES["raster_images/google_logo.png"]["size"]
    k = min(W / alfa.width, H / alfa.height)
    tam = (round(alfa.width * k), round(alfa.height * k))
    alfa = alfa.resize(tam, Image.Resampling.LANCZOS)
    lienzo = Image.new("L", (W, H), 0)
    lienzo.paste(alfa, ((W - tam[0]) // 2, (H - tam[1]) // 2))
    im = Image.new("RGBA", (W, H), rgb + (0,))      # constant color: no dark halos when rescaling
    im.putalpha(lienzo)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue(), dict(
        subject="«G» propia monocroma (pieza de índice 5 de svg_images/google_logo.svg) rasterizada con fondo transparente",
        page_url="",
        note="Rasterizada con rsvg-convert desde svg_images/google_logo.svg (CC0, ya sustituido). FourierGoogleG lee "
             "SVGMobject(\"google_logo\")[5]: ninguna escena de 2019 lee este PNG.")


# ------------------------------------------------------------------ 5. raster_images/flags/us.png

def hacer_us(d):
    """Flag of the USA from flag-icons (MIT). flag-icons' 4x3 is a 640x480 crop of the official flag (1.9:1):
    the viewBox is widened to 912x480 by extending the red background and the white stripes (the canton stays intact) and it is
    rasterized to 550x289 RGB on white, like the rest of the flags of raster_images/flags/."""
    url_lic = f"https://raw.githubusercontent.com/lipis/flag-icons/{FLAG_COMMIT}/LICENSE"
    lic = d.http(url_lic).decode()
    assert "MIT License" in lic and "Permission is hereby granted" in lic, "licencia de flag-icons no verificada"
    tar = d.cached(f"https://codeload.github.com/lipis/flag-icons/tar.gz/{FLAG_COMMIT}", ".tar.gz")
    with tarfile.open(tar, "r:gz") as tf:
        miembro = next(m for m in tf.getmembers() if m.name.endswith("/flags/4x3/us.svg"))
        crudo = tf.extractfile(miembro).read()
    escribir(CACHE / "flag-icons/us.svg", crudo)
    svg = crudo.decode()
    assert svg.count('viewBox="0 0 640 480"') == 1 and svg.count("h640") == 7 and "M0 0h640v480H0" in svg, \
        "el us.svg de flag-icons ya no tiene la forma esperada"
    ancho = svg.replace("640", "912")
    assert ancho.count("912") == 8
    W, H = ORIGINALES["raster_images/flags/us.png"]["size"]
    im = rsvg(ancho.encode(), "-w", str(W), "-h", str(H))
    assert im.size == (W, H)
    fondo = Image.new("RGBA", (W, H), "white")
    fondo.alpha_composite(im)
    buf = io.BytesIO()
    fondo.convert("RGB").save(buf, "PNG", optimize=True)
    return buf.getvalue(), dict(
        subject="Bandera de EE. UU. de flag-icons (MIT), con las proporciones oficiales 1,9:1",
        author="Panayiotis Lipiridis and flag-icons contributors", license="MIT", license_url=url_lic,
        page_url=f"https://github.com/lipis/flag-icons/blob/{FLAG_COMMIT}/flags/4x3/us.svg",
        source_sha256=sha(crudo), status="replaced", via="descargar",
        changes="SVG libre ampliado a viewBox 912x480 (fondo y franjas prolongados; canton sin tocar) y rasterizado a "
                "550x289 RGB sobre blanco con rsvg-convert.",
        note="Mismo commit de flag-icons que el resto de banderas (flags_sources.json). Sustituye la entrada «ya_existe» "
             "de us.png en assets2019_sources.json (era el archivo de Grant, no un reemplazo propio).")


# ------------------------------------------------------------------ 6. raster_images/Riemann.jpg

def tarjeta_riemann(size):
    """Own card (no face) with the name and the dates: the resource for people without a free photo."""
    def fuente(n):
        return ImageFont.truetype(str(FUENTES / "CMUSerif-Roman.ttf"), int(n))
    w, h = size
    im = Image.new("RGB", size, "#E7E8DF")
    dr = ImageDraw.Draw(im)
    dr.rectangle((w * .06, h * .06, w * .94, h * .94), outline="#879C9C", width=max(1, w // 180))
    dr.text((w / 2, h * .46), "Bernhard Riemann", font=fuente(h * .11), fill="#263B46", anchor="mm")
    dr.text((w / 2, h * .62), "1826 – 1866", font=fuente(h * .08), fill="#263B46", anchor="mm")
    return im


def hacer_riemann(d, tarjeta=False):
    """Portrait of Riemann from 1863 (Commons, public domain) with a "cover" crop to 900x750 without distortion. The source is
    vertical (903x986): the crop is anchored at the top so as not to cut off the head. Without network or with --riemann-tarjeta, own card."""
    W, H = ORIGINALES["raster_images/Riemann.jpg"]["size"]
    info = None
    if not tarjeta:
        try:
            info = d.verify_commons([COMMONS_RIEMANN]).get(COMMONS_RIEMANN)
            if not info:
                print("  AVISO: Commons no devolvio una licencia libre admitida para el retrato; tarjeta propia", flush=True)
        except Exception as e:                       # sin red, cooldown, etc.
            print(f"  AVISO: no se pudo verificar/descargar el retrato ({e}); tarjeta propia", flush=True)
    if info:
        origen = d.cached(info["file_url"])
        fuente_img = Image.open(origen)
        im = ImageOps.fit(fuente_img.convert("RGB"), (W, H), Image.Resampling.LANCZOS, centering=(0.5, 0.0))
        extra = dict(info)
        extra.pop("commons_title", None)
        extra.update(commons_title=info["commons_title"], source_sha256=sha(origen.read_bytes()),
                     subject="Retrato de Riemann (1863) de dominio público (Commons)", status="replaced", via="descargar",
                     changes="Fuente libre descargada independientemente; recorte «cover» 900x750 anclado arriba (para no "
                             "cortar la cabeza), reescala sin deformar y conversión a RGB; sin IA.",
                     note="Licencia consultada en esta ejecución. Grabado/retrato de 1863 (Commons: PD Old, CC-PD-Mark), "
                          "distinto de la fotografía sentada del original de Grant.")
    else:
        im = tarjeta_riemann((W, H))
        extra = dict(subject="Tarjeta propia (sin cara) con el nombre y las fechas de Bernhard Riemann",
                     author="propio (código)", license="CC0", license_url=CC0, page_url="", status="generated", via="código",
                     changes="Recreación independiente desde cero, no deriva del original.",
                     note="Sin fuente verificable de dominio público en esta ejecución: tarjeta propia sin cara.")
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "JPEG", quality=92, optimize=True, progressive=True, dpi=(96, 96))
    return buf.getvalue(), extra


# ------------------------------------------------------------------ 7-9. raster_images/IP_Sample_Page{1,2,3}.png

# Same palette as the cover card raster_images/InfinitePowers.jpg (background #E7E8DF, frame #879C9C, ink #263B46); the
# paper is slightly lighter so that the page stands out from the cover.
PAPEL, MARCO, TINTA, BARRA, ACENTO = "#EDEEE6", "#879C9C", "#263B46", "#6C7E85", "#B4533F"
MARGEN = 150


class Pagina:
    """Canvas with x2 supersampling: it is drawn at double size and reduced with LANCZOS to get smooth edges. All the
    coordinates are those of the final size."""
    K = 2

    def __init__(self, size, semilla):
        self.W, self.H = size
        self.im = Image.new("RGB", (self.W * self.K, self.H * self.K), PAPEL)
        self.dr = ImageDraw.Draw(self.im)
        self.rng = np.random.default_rng(semilla)

    def _p(self, *v):
        return [x * self.K for x in v]

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1, radio=0):
        self.dr.rounded_rectangle(self._p(x0, y0, x1, y1), radius=radio * self.K, fill=fill, outline=outline,
                                  width=round(width * self.K))

    def punto(self, x, y, r, fill):
        self.dr.ellipse(self._p(x - r, y - r, x + r, y + r), fill=fill)

    def linea(self, pts, color, ancho, discontinua=False):
        """Polyline with rounded ends and joins; `discontinua` splits it into dashes of 3 widths."""
        if len(pts) > 2 and not discontinua:         # sampled curve: a single polyline with smooth joins
            self.dr.line(self._p(*[c for p in pts for c in p]), fill=color, width=round(ancho * self.K), joint="curve")
            for p in (pts[0], pts[-1]):
                self.punto(*p, ancho / 2, color)
            return
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            largo = math.hypot(xb - xa, yb - ya)
            n = max(1, round(largo / (6 * ancho))) if discontinua else 1
            for i in range(n):
                t0, t1 = i / n, (i + 0.5) / n if discontinua else 1.0
                a = (xa + (xb - xa) * t0, ya + (yb - ya) * t0)
                b = (xa + (xb - xa) * t1, ya + (yb - ya) * t1)
                self.dr.line(self._p(*a, *b), fill=color, width=round(ancho * self.K))
                self.punto(*a, ancho / 2, color)
                self.punto(*b, ancho / 2, color)

    def texto(self, xy, s, fuente, tam, color, ancla="lm"):
        f = ImageFont.truetype(str(FUENTES / fuente), int(tam * self.K))
        self.dr.text(self._p(*xy), s, font=f, fill=color, anchor=ancla)

    def palabras(self, x0, x1, y, alto, justificada, fraccion=1.0, color=BARRA):
        """One line of simulated text: rounded bars (words) of random length separated by gaps."""
        hueco = alto * 0.95
        ancho = (x1 - x0) * (1.0 if justificada else fraccion)
        largos = []
        while True:
            w = float(self.rng.uniform(2.4, 9.0)) * alto
            if sum(largos) + w + hueco * len(largos) > ancho:
                break
            largos.append(w)
        if justificada:                       # distributes the leftover among the gaps: straight right edge
            hueco = (ancho - sum(largos)) / max(1, len(largos) - 1)
        x = x0
        for w in largos:
            self.rect(x, y, x + w, y + alto, fill=color, radio=alto * 0.35)
            x += w + hueco

    def parrafo(self, x0, x1, y, lineas, paso=62, alto=26, sangria=70):
        for i in range(lineas):
            ultima = i == lineas - 1
            self.palabras(x0 + (sangria if i == 0 else 0), x1, y + i * paso, alto, not ultima,
                          float(self.rng.uniform(0.3, 0.75)))
        return y + lineas * paso

    def cabecera(self, n):
        """Thin frame (like the cover), header with the title and the sample number, rule and page number."""
        self.rect(40, 40, self.W - 40, self.H - 40, outline=MARCO, width=4)
        self.texto((MARGEN, 112), "Infinite Powers", "JetBrainsMono-Regular.ttf", 44, BARRA)
        self.texto((self.W - MARGEN, 112), f"Sample page {n}", "JetBrainsMono-Regular.ttf", 44, BARRA, "rm")
        self.rect(MARGEN, 148, self.W - MARGEN, 151, fill=MARCO)
        self.texto((self.W / 2, self.H - 100), str(n), "JetBrainsMono-Regular.ttf", 40, BARRA, "mm")
        self.texto((MARGEN, 235), f"Sample page {n}", "CMUSerif-Bold.ttf", 104, TINTA, "lt")

    def terminar(self):
        im = self.im.resize((self.W, self.H), Image.Resampling.LANCZOS).convert("RGBA")   # opaque alpha
        buf = io.BytesIO()
        im.save(buf, "PNG", optimize=True)
        return buf.getvalue()


def flecha(pg, a, b, color, ancho, punta=26):
    pg.linea([a, b], color, ancho)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    for d in (+0.45, -0.45):
        pg.linea([b, (b[0] - punta * math.cos(ang + d), b[1] - punta * math.sin(ang + d))], color, ancho)


def figura_curva(pg, x0, y0, x1, y1):
    """Axes, an S curve (smoothstep 3t^2-2t^3) and its tangent at a point, with the dashed vertical down to the axis."""
    ox, oy, ancho, alto = x0 + 70, y1 - 60, x1 - x0 - 120, y1 - y0 - 100
    flecha(pg, (ox - 20, oy), (ox + ancho + 30, oy), BARRA, 6)
    flecha(pg, (ox, oy + 20), (ox, oy - alto - 30), BARRA, 6)
    f = lambda t: 0.08 + 0.88 * (3 * t * t - 2 * t ** 3)
    df = lambda t: 0.88 * (6 * t - 6 * t * t)
    xy = lambda t: (ox + t * ancho, oy - f(t) * alto)
    pg.linea([xy(i / 120) for i in range(121)], TINTA, 10)
    t0 = 0.36
    px, py = xy(t0)
    pend = -df(t0) * alto / ancho                      # slope in pixels (y downwards)
    xa, xb = px - 150, px + 190
    pg.linea([(xa, py + pend * (xa - px)), (xb, py + pend * (xb - px))], ACENTO, 8)
    pg.linea([(px, py), (px, oy)], BARRA, 5, discontinua=True)
    pg.punto(px, py, 13, TINTA)
    pg.texto((px - 28, py - 34), "P", "CMUSerif-Italic.ttf", 56, TINTA, "mm")
    pg.texto((ox + ancho + 48, oy + 4), "t", "CMUSerif-Italic.ttf", 56, TINTA, "lm")
    pg.texto((ox + 36, oy - alto - 36), "y", "CMUSerif-Italic.ttf", 56, TINTA, "lm")


def figura_circulo(pg, cx, cy, r):
    """Circle with its radius to P, the tangent at P and the right-angle mark."""
    a = math.radians(-38)
    u = (math.cos(a), math.sin(a))                     # from the center to P
    t = (-u[1], u[0])                                  # direction of the tangent
    px, py = cx + r * u[0], cy + r * u[1]
    pg.dr.ellipse(pg._p(cx - r, cy - r, cx + r, cy + r), outline=TINTA, width=10 * pg.K)
    pg.linea([(px - 1.0 * r * t[0], py - 1.0 * r * t[1]), (px + 1.3 * r * t[0], py + 1.3 * r * t[1])], ACENTO, 8)
    pg.linea([(cx, cy), (px, py)], BARRA, 6)
    m = 30                                             # right-angle mark at P
    pg.linea([(px - m * u[0], py - m * u[1]), (px - m * u[0] + m * t[0], py - m * u[1] + m * t[1]),
              (px + m * t[0], py + m * t[1])], TINTA, 4)
    pg.punto(cx, cy, 12, TINTA)
    pg.punto(px, py, 13, TINTA)
    pg.texto((cx - 10, cy + 42), "O", "CMUSerif-Italic.ttf", 56, TINTA, "mm")
    pg.texto((px + 38 * u[0] + 20, py + 38 * u[1] - 6), "P", "CMUSerif-Italic.ttf", 56, TINTA, "mm")


def hacer_pagina(n):
    """Generic sample page of a mathematics book (nothing from the real book): header, title, paragraphs of bars
    (simulated words with random lengths, fixed seed) and, on pages 2 and 3, a figure of our own."""
    W, H = ORIGINALES[f"raster_images/IP_Sample_Page{n}.png"]["size"]
    pg = Pagina((W, H), semilla=2019 * 10 + n)
    pg.cabecera(n)
    x0, x1 = MARGEN, W - MARGEN
    y = 400
    if n == 1:
        pg.rect(x0, y, x0 + 0.52 * (x1 - x0), y + 36, fill=TINTA, radio=12)          # subtitulo
        y += 120
        for lineas in (5, 4, 4, 3):
            y = pg.parrafo(x0, x1, y, lineas) + 40
    elif n == 2:
        y = 370
        y = pg.parrafo(x0, x1, y, 2) + 40
        figura_curva(pg, x0 + 140, y, x1 - 140, y + 360)
        y += 360 + 20
        pg.texto((x0 + 140, y + 14), "Fig. 2", "JetBrainsMono-Regular.ttf", 38, BARRA)
        pg.rect(x0 + 330, y, x0 + 330 + 420, y + 26, fill=BARRA, radio=9)
        y += 70
        y = pg.parrafo(x0, x1, y, 3)
    else:
        y = 370
        y = pg.parrafo(x0, x1, y, 2) + 50
        figura_circulo(pg, x0 + 260, y + 210, 170)
        col = x0 + 640
        yy = y + 20
        for lineas in (3, 3):
            yy = pg.parrafo(col, x1, yy, lineas, sangria=0) + 36
        pg.texto((x0 + 260, y + 450), "Fig. 3", "JetBrainsMono-Regular.ttf", 38, BARRA, "mm")
        y = max(yy, y + 480) + 20
        y = pg.parrafo(x0, x1, y, 3)
    assert y <= H - 170, f"la pagina {n} desborda el cuerpo (y={y}, limite {H - 170})"
    figura = {1: "ninguna", 2: "una curva en S con su tangente y los ejes", 3: "un circulo con su radio y su tangente"}[n]
    return pg.terminar(), dict(
        subject=f"Página de muestra genérica {n} de un libro de matemáticas (cabecera «Infinite Powers», título «Sample page {n}», "
                f"párrafos de barras grises; figura: {figura}); no contiene texto del libro real",
        note="Páginas propias que sustituyen las capturas del libro «Infinite Powers» (StrogatzMention las muestra con "
             "match_height(book) a la derecha de la portada genérica InfinitePowers.jpg). Mismo estilo de tarjeta que esa portada: "
             "papel beige-gris claro, marco #879C9C, JetBrains Mono y CMU Serif (OFL, assets/fonts). Alfa totalmente opaco.")


# ------------------------------------------------------------------ validacion, registro, instalacion

ESPECIFICACIONES = {
    "imo_logo": ("svg_images/imo_logo.svg", lambda d, a: hacer_imo_logo(), False),
    "sun": ("svg_images/sun.svg", lambda d, a: hacer_sun(), False),
    "windmill": ("raster_images/windmill.svg", lambda d, a: hacer_windmill(), False),
    "google_logo": ("raster_images/google_logo.png", lambda d, a: hacer_google_logo(), False),
    "us": ("raster_images/flags/us.png", lambda d, a: hacer_us(d), True),
    "riemann": ("raster_images/Riemann.jpg", lambda d, a: hacer_riemann(d, a.riemann_tarjeta), True),
    "ip_page1": ("raster_images/IP_Sample_Page1.png", lambda d, a: hacer_pagina(1), False),
    "ip_page2": ("raster_images/IP_Sample_Page2.png", lambda d, a: hacer_pagina(2), False),
    "ip_page3": ("raster_images/IP_Sample_Page3.png", lambda d, a: hacer_pagina(3), False),
}


def validar(asset, datos):
    """Checks size/mode (raster) or viewBox (SVG) against the original and returns the data for the record."""
    ref = ORIGINALES[asset]
    if asset.endswith(".svg"):
        import xml.etree.ElementTree as ET
        raiz = ET.fromstring(datos)
        assert raiz.get("viewBox") == ref["viewbox"], f"{asset}: viewBox {raiz.get('viewBox')} != {ref['viewbox']}"
        return dict(viewbox=ref["viewbox"], svg_paths=datos.count(b"<path"))
    im = Image.open(io.BytesIO(datos))
    assert im.size == ref["size"] and im.mode == ref["mode"], f"{asset}: {im.size} {im.mode} != {ref['size']} {ref['mode']}"
    return dict(size=list(im.size), mode=im.mode)


def revision_escena(asset):
    patron, archivo = REVISION[asset]
    ruta = ROOT / "_work/_2019" / archivo
    out = []
    if ruta.is_file():
        lineas = ruta.read_text(errors="replace").splitlines()
        for i, linea in enumerate(lineas, 1):
            if re.search(patron, linea):
                out.append({"line": i, "context": "\n".join(lineas[max(0, i - 3):i + 2])})
    return {"scene": "_work/_2019/" + archivo, "matches": out[:3]}


def entrada(asset, datos, extra):
    ref = ORIGINALES[asset]
    e = dict(
        asset=asset, name=Path(asset).name, subject=extra.pop("subject"),
        author=extra.pop("author", "propio (código)"), license=extra.pop("license", "CC0"),
        license_url=extra.pop("license_url", CC0), page_url=extra.pop("page_url", ""),
        changes=extra.pop("changes", "Recreación independiente desde cero, no deriva del original."),
        status=extra.pop("status", "generated"), via=extra.pop("via", "código"), recipe_version=VERSION,
        verified_at=ahora(), scene_review=revision_escena(asset), scenes_2019=ESCENAS[asset],
        note=extra.pop("note", ""), old_sha256=ref["sha256"])
    e.update(extra)
    e.update(validar(asset, datos))
    e.update(delivery_state="hecha", sha256=sha(datos), final_size_bytes=len(datos),
             original=dict((k, v) for k, v in ref.items() if k != "sha256"))
    return e


def instalar(asset, datos):
    destino = ASSETS / asset
    previo = PREVIOS / asset
    if destino.is_file() and not previo.exists():
        if sha(destino.read_bytes()) == ORIGINALES[asset]["sha256"]:
            previo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destino, previo)
            print(f"  original guardado en {previo.relative_to(ROOT)}", flush=True)
        else:
            print(f"  AVISO: {asset} ya no es el original de Grant y no hay copia previa; no se guarda", flush=True)
    escribir(destino, datos)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(Path(tempfile.gettempdir()) / "assets2019_extra"))
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--only", nargs="+", choices=sorted(ESPECIFICACIONES))
    ap.add_argument("--riemann-tarjeta", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    nombres = args.only or list(ESPECIFICACIONES)
    d = cargar_descargas() if any(ESPECIFICACIONES[n][2] for n in nombres) else None

    registro_out = out / "assets2019_extra_sources.json"
    base = REGISTRO if args.install else registro_out
    registro = json.loads(base.read_text()) if base.is_file() else {}
    for nombre in nombres:
        asset, hacer, _ = ESPECIFICACIONES[nombre]
        print(f"{asset}", flush=True)
        datos, extra = hacer(d, args)
        e = entrada(asset, datos, dict(extra))
        escribir(out / asset, datos)
        if args.install:
            instalar(asset, datos)
        registro[asset] = e
        print(f"  {e['final_size_bytes']} bytes, {e.get('size') or e.get('viewbox')} {e.get('mode', '')} "
              f"[{e['status']}, {e['license']}]", flush=True)
    escribir_json(registro_out, registro)
    if args.install:
        escribir_json(REGISTRO, registro)
        print(f"registro: {REGISTRO.relative_to(ROOT)}")
    print(f"salida: {out}")


if __name__ == "__main__":
    main()
