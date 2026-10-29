"""Replacement photos for the third-party images that the scenes used (level 3 of the assets policy).

Each photo is downloaded from its source (Wikimedia Commons or NASA), its license is checked with the Commons API
(only public domain, CC0, CC BY and CC BY-SA are accepted) and it is written with the SAME name the scenes' code uses in
`_lib/assets/raster_images/`. It also leaves `photos_sources.json` (next to this script) with the author,
license, URL and changes of each photo: `converted/ATTRIBUTIONS.md` comes from there.

  - Andrey_Kolmogorov.jpg      Commons, Konrad Jacobs / MFO, CC BY-SA 2.0 de
  - Claude_Shannon.jpg         Commons, Tekniska museet (Flickr), CC BY 2.0 (cropped version, 900 px wide)
  - Richard_Hamming.png        There is NO free photo (Wikipedia's is fair use): illustration drawn by code
  - Principia_equal_area.jpg   Commons/Internet Archive: Principia 1687 (Burndy copy), Book I, Sect. II, Prop. I; public domain
  - Tom_In_Bowtie.jpg          Commons, George Kartanos, CC0 (cat with a bow tie)
  - Lion.jpg                   Commons, Kevin Pluck, CC BY 2.0 ("Lion waiting in Namibia"; byte for byte the same photo as before)
  - EarthTextureMap.jpg        NASA Visible Earth 57752 (Blue Marble), public domain, reduced to 4096x2048
  - NightEarthTextureMap.jpg   NASA Earth Observatory 79765 (Black Marble 2012), public domain, 4096x2048
  - JupiterTexture.jpg         NASA/JPL Cassini PIA07782 (cylindrical map of Jupiter), public domain, 1440x720
  - Cow.jpg / Puppy.jpg / Fork.jpg  example photos that were from ImageNet: cow (USDA, public domain), puppy (CC0), fork (CC BY-SA 4.0)
  - Cauchy.png                 Commons, c. 1840 lithograph (Dibner Collection, Smithsonian Libraries), public domain, crop

The public-domain portraits that were in Grant's assets/ (Euler, Gauss, Newton, Riemann, ...) are no longer left as
they were: they are downloaded from Commons by replacements/downloads/make_downloaded_assets.py (rows 44-59).

Usage:  python make_replacement_photos.py [--only Name.jpg ...] [--no-verify] [--sources-only]
  --sources-only  does not write photos, only regenerates photos_sources.json (verifies licenses on Commons).
  --no-verify     does not query the license API (uses what is already saved in photos_sources.json).
Requires Pillow. Fails without Internet. It runs AFTER copying the original assets: it overwrites those names."""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

Image.MAX_IMAGE_PIXELS = None
HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]                      # _lib/assets
RASTER = ASSETS / "raster_images"
FONTS = ASSETS / "fonts"
SOURCES_JSON = HERE / "photos_sources.json"
UA = {"User-Agent": "ManimLearningPhotoFetcher/1.0 (educational; theoremofbeethoven@gmail.com)"}
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

# Accepted licenses (Commons' LicenseShortName)
ALLOWED = re.compile(r"^(public domain|pd[- ].*|cc0.*|cc[- ]by([- ]sa)?[- ]\d(\.\d)?( [a-z]{2,3})?|no restrictions)$", re.I)


# ----------------------------------------------------------------------------- red

def http_get(url: str, retries: int = 5) -> bytes:
    last = None
    for k in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                return r.read()
        except Exception as e:  # 429, 5xx, cut-offs
            last = e
            time.sleep(4 * (k + 1))
    raise RuntimeError(f"no se pudo descargar {url}: {last}")


def commons_api(**params) -> dict:
    params["format"] = "json"
    return json.loads(http_get(COMMONS_API + "?" + urllib.parse.urlencode(params)))


def strip_html(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def commons_info(title: str) -> dict:
    """License, author and URL of a Commons file, read from its page (extmetadata)."""
    r = commons_api(action="query", prop="imageinfo", iiprop="extmetadata|url|size", titles=title)
    page = next(iter(r["query"]["pages"].values()))
    if "imageinfo" not in page:
        raise RuntimeError(f"{title}: no existe en Commons")
    ii = page["imageinfo"][0]
    m = ii["extmetadata"]
    g = lambda k: strip_html(m.get(k, {}).get("value", ""))
    info = {
        "commons_title": title,
        "page_url": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe="/:,'"),
        "file_url": ii["url"].split("?")[0],
        "width": ii.get("width"), "height": ii.get("height"),
        "license": g("LicenseShortName"),
        "license_url": g("LicenseUrl"),
        "author_commons": g("Artist"),
        "credit_commons": g("Credit")[:200],
        "date": g("DateTimeOriginal")[:60],
    }
    if not ALLOWED.match(info["license"]):
        raise RuntimeError(f"{title}: licencia no admitida ({info['license']!r})")
    return info


def commons_download(info: dict) -> Image.Image:
    return Image.open(io.BytesIO(http_get(info["file_url"])))


def commons_pdf_page(title: str, page: int, width: int) -> Image.Image:
    r = commons_api(action="query", prop="imageinfo", iiprop="url", titles=title,
                    iiurlwidth=width, iiurlparam=f"page{page}-{width}px")
    ii = next(iter(r["query"]["pages"].values()))["imageinfo"][0]
    return Image.open(io.BytesIO(http_get(ii["thumburl"])))


# ----------------------------------------------------------------------------- Hamming illustration

def draw_hamming() -> Image.Image:
    """Stylized bust of R. W. Hamming drawn with PIL (there is no free photo). 340x484, ratio like the original."""
    S, W, H = 4, 340, 484
    w, h = W * S, H * S
    img = Image.new("RGB", (w, h))
    px = img.load()
    top, bot = (176, 188, 202), (118, 132, 150)
    d = ImageDraw.Draw(img)
    for y in range(h):                                  # background with a vertical gradient
        t = y / (h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bot)))
    P = lambda x, y: (x * S, y * S)
    poly = lambda pts, fill: d.polygon([P(*p) for p in pts], fill=fill)
    ell = lambda x0, y0, x1, y1, fill, **k: d.ellipse([P(x0, y0), P(x1, y1)], fill=fill, **k)

    suit, suit_hi, shirt, skin, skin_sh = (38, 42, 54), (54, 59, 74), (238, 240, 244), (232, 190, 160), (208, 164, 134)
    hair, tie = (52, 40, 33), (118, 38, 52)
    # shoulders / jacket
    poly([(0, 484), (0, 372), (46, 338), (118, 316), (222, 316), (294, 338), (340, 372), (340, 484)], suit)
    poly([(118, 316), (170, 440), (222, 316), (196, 306), (144, 306)], shirt)       # V-neck shirt
    poly([(118, 316), (170, 484), (132, 484), (96, 340)], suit_hi)                  # lapels
    poly([(222, 316), (170, 484), (208, 484), (244, 340)], suit_hi)
    poly([(150, 326), (190, 326), (200, 340), (180, 352), (160, 352), (140, 340)], shirt)  # shirt collar
    poly([(162, 346), (178, 346), (184, 366), (196, 484), (144, 484), (156, 366)], tie)    # tie
    poly([(160, 340), (180, 340), (184, 356), (156, 356)], (140, 48, 64))                  # knot
    # neck
    poly([(145, 262), (195, 262), (200, 322), (170, 346), (140, 322)], skin_sh)
    # head (everything on the head goes down `dy` px to shorten the neck)
    dy = 20
    E = lambda x0, y0, x1, y1, fill: ell(x0, y0 + dy, x1, y1 + dy, fill)
    L = lambda pts, fill: poly([(x, y + dy) for x, y in pts], fill)
    E(98, 176, 122, 224, skin_sh)                         # ears
    E(218, 176, 242, 224, skin_sh)
    E(110, 92, 230, 262, skin)                            # head
    E(106, 78, 234, 186, hair)                            # hair: cap with sideburns
    E(116, 116, 224, 262, skin)                           # the face covers the inside of the cap -> hairline
    L([(124, 112), (150, 100), (196, 96), (224, 112), (220, 122), (190, 110), (150, 114), (128, 126)], hair)  # bangs with a part
    d.line([P(150, 101 + dy), P(158, 112 + dy)], fill=skin_sh, width=S)
    # eyebrows, eyes
    for sx in (0, 1):
        ox = 0 if sx == 0 else 63
        d.line([P(129 + ox, 168 + dy), P(144 + ox, 164 + dy), P(160 + ox, 168 + dy)], fill=hair, width=3 * S)
        E(133 + ox, 174, 157 + ox, 188, (248, 248, 250))
        E(141 + ox, 175, 151 + ox, 187, (62, 48, 40))
        E(144 + ox, 178, 148 + ox, 183, (14, 12, 12))
    # nose, mouth
    d.line([P(170, 182 + dy), P(166, 212 + dy), P(176, 220 + dy)], fill=skin_sh, width=2 * S)
    d.arc([P(150, 226 + dy), P(190, 252 + dy)], 18, 162, fill=(150, 80, 76), width=2 * S)
    d.line([P(150, 232 + dy), P(146, 228 + dy)], fill=skin_sh, width=S)
    d.line([P(190, 232 + dy), P(194, 228 + dy)], fill=skin_sh, width=S)
    img = img.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.4))

    # label
    d = ImageDraw.Draw(img, "RGBA")
    try:
        f = ImageFont.truetype(str(FONTS / "Nunito[wght].ttf"), 17)
        try:
            f.set_variation_by_name("Bold")
        except Exception:
            pass
    except Exception:
        f = ImageFont.load_default()
    txt = "Richard W. Hamming"
    tw = d.textlength(txt, font=f)
    d.rounded_rectangle([(W - tw) / 2 - 10, 14, (W + tw) / 2 + 10, 44], radius=10, fill=(20, 24, 32, 175))
    d.text((W / 2, 29), txt, font=f, fill=(240, 242, 246), anchor="mm")
    return img


# ----------------------------------------------------------------------------- table of photos

def save(img: Image.Image, name: str, quality: int = 92):
    RASTER.mkdir(parents=True, exist_ok=True)
    dest = RASTER / name
    img = img.convert("RGB")
    if name.lower().endswith((".jpg", ".jpeg")):
        img.save(dest, quality=quality, optimize=True)
    else:
        img.save(dest, optimize=True)
    print(f"   {name}: {img.size[0]}x{img.size[1]}  {dest.stat().st_size // 1024} KB", flush=True)


def fit_width(img: Image.Image, width: int) -> Image.Image:
    if img.width <= width:
        return img
    return img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)


# Each entry: "name" is the file in raster_images/. "kind": replace_commons | replace_commons_pdf | replace_nasa |
# replace_code | kept (attribution only). "author" and "changes" are the texts that go in ATTRIBUTIONS.md.
PHOTOS = [
    dict(name="Andrey_Kolmogorov.jpg", kind="replace_commons", title="File:Andrej Nikolajewitsch Kolmogorov.jpg",
         subject="Andrey Kolmogorov", author="Konrad Jacobs (Oberwolfach Photo Collection, MFO)",
         changes="Sin cambios (230x333 px, tamaño original).",
         process=lambda im: im),
    dict(name="Claude_Shannon.jpg", kind="replace_commons", title="File:C.E. Shannon. Tekniska museet 43069 (cropped).jpg",
         subject="Claude Shannon", author="Tekniska museet (Suecia), vía Flickr / Wikimedia Commons",
         changes="Reducida a 900 px de ancho (Commons ya ofrece una versión recortada del original).",
         process=lambda im: fit_width(im, 900)),
    dict(name="Richard_Hamming.png", kind="replace_code", subject="Richard W. Hamming",
         author="Ilustración propia (código: este script)", license="CC0 (dibujo por código, sin foto)",
         note="No existe foto libre de Hamming en Commons (la de Wikipedia es de uso justo): se dibuja un busto estilizado.",
         changes="No es una foto: ilustración dibujada con Pillow.",
         make=draw_hamming),
    dict(name="Principia_equal_area.jpg", kind="replace_commons_pdf",
         title="File:Philosophiae naturalis principia mathematica (IA philosophiaenat00newt).pdf", page=51, width=1050,
         subject="Principia, Libro I, Sect. II, Prop. I (áreas iguales)", author="Isaac Newton (1687); escaneo de Internet Archive, ejemplar de la Burndy Library",
         changes="Página 51 del PDF (p. [37] impresa), exportada como JPEG a 1050 px de ancho; sin otros cambios.",
         process=lambda im: im),
    dict(name="Tom_In_Bowtie.jpg", kind="replace_commons", title="File:Male 5-year-old Tuxedo Cat with pink bowtie.jpg",
         subject="Gato con moño", author="George Kartanos", changes="Sin cambios (474x662 px).",
         process=lambda im: im),
    dict(name="Lion.jpg", kind="replace_commons", title="File:Lion waiting in Namibia.jpg",
         subject="León", author="Kevin Pluck (Flickr, \"The King\")",
         changes="Sin cambios (es el archivo original de Commons, 1280x960).",
         process=lambda im: im),
    dict(name="Cauchy.png", kind="replace_commons",
         title="File:Cauchy Augustin Louis dibner coll SIL14-C2-03a.jpg",
         subject="Augustin-Louis Cauchy", author="Louis Grégoire y Deneux (litografía, c. 1840), Colección Dibner, Smithsonian Libraries",
         changes="Recortada al busto (caja 120,110 a 880,930), sin la firma ni el pie de imprenta.",
         process=lambda im: im.crop((120, 110, 880, 930))),
    dict(name="Cow.jpg", kind="replace_commons", title="File:Cow female black white.jpg",
         subject="Vaca Holstein", author="Keith Weller, USDA Agricultural Research Service",
         changes="Reducida a 900 px de ancho.",
         process=lambda im: fit_width(im, 900)),
    dict(name="Puppy.jpg", kind="replace_commons", title="File:Golden-retriever-1827903 1920.jpg",
         subject="Cachorro de golden retriever", author="RetyiRetyi (Pixabay) / Wikimedia Commons",
         changes="Recortada a formato vertical 3:4 alrededor del cachorro (caja 493,0 a 1457,1285) y reducida a 540x720 px.",
         process=lambda im: im.crop((493, 0, 1457, 1285)).resize((540, 720), Image.LANCZOS)),
    dict(name="Fork.jpg", kind="replace_commons", title="File:Gabel -- 2021 -- 7220.jpg",
         subject="Tenedor", author="Dietmar Rabich / Wikimedia Commons",
         changes="Reducida a 900 px de ancho.",
         process=lambda im: fit_width(im, 900)),
    dict(name="JupiterTexture.jpg", kind="replace_commons",
         title="File:Jupiter Cylindrical Map - Dec 2000 PIA07782.jpg",
         subject="Mapa cilíndrico de Júpiter (Cassini)", author="NASA/JPL/Space Science Institute (PIA07782)",
         changes="Reducido a 1440x720 px.",
         process=lambda im: im.resize((1440, 720), Image.LANCZOS)),
    dict(name="EarthTextureMap.jpg", kind="replace_nasa",
         url="https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57752/land_shallow_topo_8192.tif",
         page_url="https://visibleearth.nasa.gov/images/57752/blue-marble-land-surface-shallow-water-and-shaded-topography",
         commons_title="File:Land shallow topo 2048.jpg",
         subject="Blue Marble: superficie terrestre, aguas someras y topografía sombreada",
         author="NASA Goddard Space Flight Center: Reto Stöckli (superficie terrestre, aguas someras, nubes); Robert Simmon (color del océano, composición); MODIS Land/Atmosphere/Ocean Groups; USGS EROS Data Center",
         license="Dominio público (NASA)", license_url="https://www.nasa.gov/nasa-brand-center/images-and-media/",
         changes="Reducida de 8192x4096 a 4096x2048 px (JPEG).",
         process=lambda im: im.resize((4096, 2048), Image.LANCZOS)),
    dict(name="NightEarthTextureMap.jpg", kind="replace_nasa",
         url="https://eoimages.gsfc.nasa.gov/images/imagerecords/79000/79765/dnb_land_ocean_ice.2012.13500x6750.jpg",
         page_url="https://earthobservatory.nasa.gov/images/79765/night-lights-2012-map",
         subject="Black Marble 2012: luces nocturnas de la Tierra (mapa plano)",
         author="NASA Earth Observatory, imagen de Robert Simmon con datos VIIRS de Suomi NPP cedidos por Chris Elvidge (NOAA National Geophysical Data Center)",
         license="Dominio público (NASA)", license_url="https://www.nasa.gov/nasa-brand-center/images-and-media/",
         changes="Reducida de 13500x6750 a 4096x2048 px (JPEG).",
         process=lambda im: im.resize((4096, 2048), Image.LANCZOS)),
]

# Public-domain portraits that were in Grant's assets/: they used to be left as they were ("kept"); since 2026-10-24
# make_downloaded_assets.py downloads them from Commons (rows 44-59), so none remain here.
KEPT = []


# ----------------------------------------------------------------------------- execution

def run(only: set[str] | None, write: bool, verify: bool):
    old = json.loads(SOURCES_JSON.read_text()) if SOURCES_JSON.exists() else {}
    out: dict[str, dict] = {}
    for p in PHOTOS:
        name = p["name"]
        if only and name not in only:
            out[name] = old.get(name, {})
            continue
        print(f" * {name}", flush=True)
        rec = {"name": name, "status": "replaced", "subject": p["subject"], "author": p["author"], "changes": p["changes"]}
        kind = p["kind"]
        if kind in ("replace_commons", "replace_commons_pdf"):
            info = commons_info(p["title"]) if verify else old[name]
            rec.update({k: info[k] for k in ("commons_title", "page_url", "file_url", "license", "license_url", "date")})
            if write:
                if kind == "replace_commons":
                    im = commons_download(info)
                else:
                    im = commons_pdf_page(p["title"], p["page"], p["width"])
                save(p["process"](im), name)
        elif kind == "replace_nasa":
            rec.update(page_url=p["page_url"], file_url=p["url"], license=p["license"], license_url=p["license_url"])
            if verify and p.get("commons_title"):
                ci = commons_info(p["commons_title"])          # confirms that Commons also has it as public domain
                rec["commons_mirror"] = {"title": ci["commons_title"], "license": ci["license"], "page_url": ci["page_url"]}
            if write:
                save(p["process"](Image.open(io.BytesIO(http_get(p["url"])))), name)
        elif kind == "replace_code":
            rec.update(license=p["license"], license_url="", note=p["note"], page_url="", file_url="")
            if write:
                save(p["make"](), name)
        out[name] = rec

    for name, title, subject, author in KEPT:
        if only and name not in only:
            out[name] = old.get(name, {})
            continue
        if verify:
            info = commons_info(title)
        else:
            info = old[name]
        out[name] = {"name": name, "status": "kept", "subject": subject, "author": author,
                     "commons_title": title, "page_url": info["page_url"], "license": info["license"],
                     "license_url": info.get("license_url", ""), "date": info.get("date", ""),
                     "changes": "Sin cambios respecto a la copia usada; la fuente se identificó comparando con el archivo de Commons."}
        print(f" . {name}: {info['license']}  ({title})", flush=True)
    SOURCES_JSON.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--no-verify", action="store_true")
    ap.add_argument("--sources-only", action="store_true")
    a = ap.parse_args()
    run(set(a.only) if a.only else None, write=not a.sources_only, verify=not a.no_verify)
