"""Propagates the downloaded assets (make_downloaded_assets.py) to their duplicate copies and redoes the derivatives.

Several generators leave the same file in two places: for example make_cosmic_distance_assets.py writes
`generated/2025/cosmic_distance/names/Kepler.png` and copies it to `raster_images/Kepler.png`, which is the one the
scenes find by name. make_downloaded_assets.py replaces only one of the two paths, so this step:
  1. copies each downloaded asset (status "kept" or "replaced" in downloads_sources.json) to the files with the same name in
     `raster_images/` and `generated/` (not counting `generated/replacements/`);
  2. redoes DarkMoonTexture and RedMoonTexture from the new Moon, and DarkMarsTexture from the new Mars, with the same
     formulas as make_cosmic_distance_assets.py (the scene paints the light and the dark Moon on the same sphere).
It goes in setup_assets.py right after make_downloaded_assets.py. The copies in `_work` are refreshed by
`pipeline.py sync-data`. Idempotent."""
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]                                  # _lib/assets
RASTER = ASSETS / "raster_images"
COSMIC = ASSETS / "generated" / "2025" / "cosmic_distance"
REPLACEMENTS = ASSETS / "generated" / "replacements"


def same_file(a: Path, b: Path) -> bool:
    return a.stat().st_size == b.stat().st_size and a.read_bytes() == b.read_bytes()


def mirror_downloads():
    sources = json.loads((HERE / "downloads_sources.json").read_text())
    by_name: dict[str, list[Path]] = {}
    for root in (RASTER, ASSETS / "generated"):
        for p in root.rglob("*"):
            if p.is_file() and REPLACEMENTS not in p.parents:
                by_name.setdefault(p.name, []).append(p)
    copied = 0
    for item in sources.values():
        if item.get("status") not in ("kept", "replaced"):
            continue
        src = ASSETS / item["asset"]
        for dst in by_name.get(src.name, []):
            if dst.resolve() == src.resolve() or same_file(src, dst):
                continue
            shutil.copy2(src, dst)
            print(f"  {item['asset']} -> {dst.relative_to(ASSETS)}")
            copied += 1
    print(f"copias actualizadas: {copied}")


def save_both(img: np.ndarray, name: str):
    for folder in (COSMIC, RASTER):
        Image.fromarray(img).save(folder / name, quality=92)


def derive_textures():
    moon = np.asarray(Image.open(RASTER / "MoonTexture.jpg").convert("RGB")).astype(np.float32) / 255
    dark = np.clip(moon * np.array([0.10, 0.11, 0.14]), 0, 1)        # slight bluish tint ("Earthshine")
    save_both((dark * 255).astype(np.uint8), "DarkMoonTexture.jpg")
    lum = moon.mean(axis=2, keepdims=True)
    red = np.clip(lum * np.array([1.0, 0.33, 0.14]) * 1.25, 0, 1)
    save_both((red * 255).astype(np.uint8), "RedMoonTexture.jpg")
    mars = np.asarray(Image.open(RASTER / "MarsTexture.jpg").convert("RGB"))
    save_both((mars * 0.1).astype(np.uint8), "DarkMarsTexture.jpg")
    print("derivadas: DarkMoonTexture, RedMoonTexture, DarkMarsTexture")


if __name__ == "__main__":
    mirror_downloads()
    derive_textures()
