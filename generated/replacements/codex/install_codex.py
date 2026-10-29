"""Installs the images that the author generated with Codex (level 1 of the assets policy: own work, "generated with AI by the
repo's author") in place of the procedural markers.

How it works
  - List of images: `codex_items.csv` (next to this script; it is a copy of `_tools/assets_licencias/codex/para_codex.csv`,
    which is the list that was given to the user). Columns used: asset, archivo_entrega, destino, ancho, alto, ajuste, alfa.
  - Deliveries: `entregas/<archivo_entrega>` (PNG; .jpg/.jpeg/.webp with the same base name are also accepted).
  - For each delivery present it converts it to the destination's format and size and writes it to `_lib/assets/<asset>`:
        cover    crops to the center up to the destination's ratio and resizes (LANCZOS)
        contain  fits it whole with padding (transparent if there is alpha; otherwise, the color of the image's border)
        exacto   resizes without keeping the ratio; if the destination is <= 64 px on a side (pixel art) it uses nearest neighbor
    Alpha is respected: if the destination has alpha and the delivery has no transparency, the flat background is removed
    (magenta #FF00FF or, failing that, the corner color) with fill from the borders. If the destination has no alpha
    (or is JPEG) the delivery is flattened to RGB.
  - Those that are missing are skipped without error (the marker stays).
  - It records everything in `codex_sources.json` (next to this script): file, origin, date, hash of the delivery.
  - It is idempotent: if the delivery has not changed (same hash) and the destination exists with that hash, it does not rewrite it.
  - It also derives `Stationary_fade_right.png` (alpha gradient to the right) when `Stationary.png` is installed.

Usage:  python install_codex.py [--dest FOLDER] [--entregas FOLDER] [--only Name.png ...] [--force] [--list]
  --dest   writes to FOLDER/<asset> instead of _lib/assets/ (to test without overwriting the real assets;
           the test codex_sources.json also goes to FOLDER)
  --list   shows which deliveries there are and which are missing
Requires only Pillow. It goes in GENERATORS of _tools/setup_assets.py AFTER misc_placeholders.py."""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import sys
from collections import deque
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]                       # _lib/assets
ITEMS_CSV = HERE / "codex_items.csv"
ENTREGAS = HERE / "entregas"
SOURCES_JSON = HERE / "codex_sources.json"
ORIGEN = "generada con Codex por el autor del repo"
EXTS = (".png", ".jpg", ".jpeg", ".webp")


# ----------------------------------------------------------------------------- utilities

def find_delivery(name: str, folder: Path = ENTREGAS) -> Path | None:
    stem = Path(name).stem
    for ext in EXTS:
        p = folder / (stem + ext)
        if p.exists():
            return p
    return None


def sha1(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def has_real_alpha(im: Image.Image) -> bool:
    if im.mode != "RGBA":
        return False
    lo, _ = im.getchannel("A").getextrema()
    return lo < 250


def remove_flat_background(im: Image.Image, tol: int = 40) -> Image.Image:
    """Removes a flat background: fill from the borders with tolerance (magenta or corner color)."""
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    corners = [px[0, 0][:3], px[w - 1, 0][:3], px[0, h - 1][:3], px[w - 1, h - 1][:3]]
    bg = tuple(sorted(c[i] for c in corners)[1] for i in range(3))    # median per channel

    def close(c):
        return sum(abs(c[i] - bg[i]) for i in range(3)) <= tol * 3 // 2

    seen = bytearray(w * h)
    dq = deque()
    for x in range(w):
        dq.append((x, 0)); dq.append((x, h - 1))
    for y in range(h):
        dq.append((0, y)); dq.append((w - 1, y))
    alpha = Image.new("L", (w, h), 255)
    ap = alpha.load()
    while dq:
        x, y = dq.popleft()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y * w + x]:
            continue
        seen[y * w + x] = 1
        if not close(px[x, y][:3]):
            continue
        ap[x, y] = 0
        dq.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    # soft edge: erodes the residual background by 1 px (fades the halo)
    from PIL import ImageFilter
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.8)).point(lambda v: 0 if v < 64 else min(255, int((v - 64) * 255 / 191)))
    im.putalpha(alpha)
    return im


def fit(im: Image.Image, size: tuple[int, int], mode: str, pixel: bool, has_alpha: bool) -> Image.Image:
    W, H = size
    resample = Image.NEAREST if pixel else Image.LANCZOS
    if mode == "exacto":
        return im.resize((W, H), resample)
    if mode == "contain":
        scale = min(W / im.width, H / im.height)
        nw, nh = max(1, round(im.width * scale)), max(1, round(im.height * scale))
        small = im.resize((nw, nh), resample)
        if has_alpha:
            bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        else:
            edge = im.convert("RGB").getpixel((0, 0))
            bg = Image.new("RGBA", (W, H), edge + (255,))
        bg.alpha_composite(small, ((W - nw) // 2, (H - nh) // 2))
        return bg
    # cover (default)
    scale = max(W / im.width, H / im.height)
    nw, nh = max(W, round(im.width * scale)), max(H, round(im.height * scale))
    big = im.resize((nw, nh), resample)
    left, top = (nw - W) // 2, (nh - H) // 2
    return big.crop((left, top, left + W, top + H))


def convert(src: Path, row: dict, dst: Path) -> None:
    W, H = int(row["ancho"]), int(row["alto"])
    want_alpha = row["alfa"].strip().lower() in ("sí", "si", "yes", "1", "true")
    im = Image.open(src)
    im.load()
    if im.mode in ("P", "LA", "PA"):
        im = im.convert("RGBA")
    if want_alpha and not has_real_alpha(im):
        im = remove_flat_background(im)
    elif im.mode != "RGBA":
        im = im.convert("RGBA") if want_alpha else im.convert("RGB")
    pixel = max(W, H) <= 64
    out = fit(im.convert("RGBA") if want_alpha else im.convert("RGB"), (W, H), row["ajuste"].strip().lower() or "cover",
              pixel, want_alpha)
    suffix = dst.suffix.lower()
    dst.parent.mkdir(parents=True, exist_ok=True)
    if suffix in (".jpg", ".jpeg"):
        out.convert("RGB").save(dst, quality=95, subsampling=0)
    elif suffix in (".tif", ".tiff"):
        out.convert("RGBA" if want_alpha else "RGB").save(dst, compression="tiff_lzw")
    else:
        if want_alpha:
            out = out.convert("RGBA")
        else:
            out = out.convert("RGB")
        out.save(dst, optimize=True)


def derive_fade_right(stationary: Path, dst: Path) -> None:
    """Same formula as make_cross_entropy_placeholders.py: the right edge fades to transparent."""
    im = Image.open(stationary).convert("RGBA")
    W = im.width
    a = im.getchannel("A")
    ramp = Image.new("L", (W, 1))
    ramp.putdata([int(255 * min(1.0, max(0.0, (0.82 - x / W) / 0.14))) for x in range(W)])
    ramp = ramp.resize(im.size)
    from PIL import ImageChops
    im.putalpha(ImageChops.multiply(a, ramp))
    im.save(dst, optimize=True)


# ----------------------------------------------------------------------------- principal

def main() -> int:
    ap = argparse.ArgumentParser(description="Instala las imágenes generadas con Codex.")
    ap.add_argument("--dest", type=Path, help="escribir en esta carpeta en lugar de _lib/assets (para pruebas)")
    ap.add_argument("--entregas", type=Path, help="carpeta de entregas alternativa (por defecto ./entregas)")
    ap.add_argument("--only", nargs="*", help="solo estos archivos de entrega (p. ej. Sprite_Horizontal.png)")
    ap.add_argument("--force", action="store_true", help="reescribir aunque la entrega no haya cambiado")
    ap.add_argument("--list", action="store_true", help="solo listar entregas presentes y ausentes")
    args = ap.parse_args()

    if not ITEMS_CSV.exists():
        print(f"no encuentro {ITEMS_CSV}", file=sys.stderr)
        return 1
    rows = list(csv.DictReader(open(ITEMS_CSV, encoding="utf-8")))
    base = (args.dest.resolve() if args.dest else ASSETS)
    sources_path = (base / "codex_sources.json") if args.dest else SOURCES_JSON
    sources = json.loads(sources_path.read_text(encoding="utf-8")) if sources_path.exists() else {}

    done = skipped = missing = unchanged = 0
    for row in rows:
        name = row["archivo_entrega"]
        if args.only and name not in args.only:
            continue
        src = find_delivery(name, args.entregas.resolve() if args.entregas else ENTREGAS)
        if src is None:
            missing += 1
            if args.list:
                print(f"  falta     {name}")
            continue
        if args.list:
            print(f"  presente  {name}")
            continue
        dst = base / row["asset"]
        digest = sha1(src)
        prev = sources.get(row["asset"], {})
        if not args.force and dst.exists() and prev.get("sha1") == digest and prev.get("ancho") == int(row["ancho"]) \
                and prev.get("alto") == int(row["alto"]):
            unchanged += 1
            continue
        try:
            convert(src, row, dst)
        except Exception as e:  # corrupt image: it is skipped and the marker stays
            print(f"  ! {name}: {e}", file=sys.stderr)
            skipped += 1
            continue
        if Path(row["asset"]).name == "Stationary.png":
            derive_fade_right(dst, dst.with_name("Stationary_fade_right.png"))
        sources[row["asset"]] = {
            "archivo": f"entregas/{src.name}",
            "destino": row["asset"],
            "origen": ORIGEN,
            "licencia": "obra propia del autor del repo",
            "fecha": datetime.date.today().isoformat(),
            "ajuste": row["ajuste"],
            "ancho": int(row["ancho"]),
            "alto": int(row["alto"]),
            "sha1": digest,
        }
        done += 1
        print(f"  {name} -> {row['asset']}")

    if not args.list:
        if sources:
            sources_path.parent.mkdir(parents=True, exist_ok=True)
            sources_path.write_text(json.dumps(dict(sorted(sources.items())), indent=1, ensure_ascii=False) + "\n",
                                    encoding="utf-8")
        print(f"codex: {done} instaladas, {unchanged} sin cambios, {missing} sin entregar (se queda el marcador)"
              + (f", {skipped} con error" if skipped else ""))
    else:
        print(f"{len(rows) - missing} presentes, {missing} faltan")
    return 0


if __name__ == "__main__":
    sys.exit(main())
