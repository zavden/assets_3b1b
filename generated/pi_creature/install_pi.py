"""Installs the own character "Π" (capital Pi letter) in place of 3Blue1Brown's pi creatures.

Grant deleted the pi creatures from his repo (commit 90be589, "Remove assets folder"); respecting that decision, this
project does not redistribute them (level 3 of the assets policy). `generar_expresiones.py`, next to this script,
draws all the expressions parametrically; here it is run in a temporary folder and these are copied:

  - `<mode>.svg` (12-part format that `PiCreature` reads)        -> `_lib/assets/PiCreature/`
  - `sueltos/EscherPiCreature.svg`                               -> `_lib/assets/svg_images/`
  - `sueltos/pi_creature_dizzy.svg`                              -> `generated/2026/print_gallery/`
  - `tau/TauCreatures_<mode>.svg` (TauCreature: Tau letter)       -> `_lib/assets/svg_images/` (where the class looks for it)
  - `tres_piernas/ThreeLeggedPiCreatures_<mode>.svg`             -> `_lib/assets/PiCreature/` (ThreeLeggedPiCreature)

Beforehand it deletes from `_lib/assets/PiCreature/` the 3b1b files (`PiCreatures*.svg`, the old `<mode>.svg`...), so that
no mode falls back on the original drawing (including `TauCreatures_*` and `ThreeLeggedPiCreatures_*`, which are replaced by
our own), and from `svg_images/` the old `TauCreatures_*`. It goes FIRST in `GENERATORS`: other generators read `PiCreature/happy.svg`.

Usage:  python install_pi.py"""
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent.parent
PI_DIR = ASSETS / "PiCreature"

sys.path.insert(0, str(HERE))
import generar_expresiones as gen  # noqa: E402


def main():
    with tempfile.TemporaryDirectory() as tmp:
        gen.OUT = Path(tmp)
        sys.argv = sys.argv[:1]
        gen.main()
        PI_DIR.mkdir(parents=True, exist_ok=True)
        for old in PI_DIR.iterdir():
            if old.is_file():
                old.unlink()
        SVG_DIR = ASSETS / "svg_images"
        SVG_DIR.mkdir(exist_ok=True)
        for old in SVG_DIR.glob("TauCreatures_*.svg"):
            old.unlink()
        modes = sorted(p for p in Path(tmp).glob("*.svg") if not p.stem.endswith("_6partes"))
        for svg in modes:
            shutil.copy(svg, PI_DIR / svg.name)
        for svg in sorted((Path(tmp) / "tres_piernas").glob("*.svg")):
            shutil.copy(svg, PI_DIR / svg.name)
        taus = sorted((Path(tmp) / "tau").glob("*.svg"))
        for svg in taus:
            shutil.copy(svg, SVG_DIR / svg.name)
        shutil.copy(Path(tmp) / "sueltos" / "EscherPiCreature.svg", ASSETS / "svg_images" / "EscherPiCreature.svg")
        dizzy_dir = ASSETS / "generated" / "2026" / "print_gallery"
        dizzy_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(Path(tmp) / "sueltos" / "pi_creature_dizzy.svg", dizzy_dir / "pi_creature_dizzy.svg")
    print(f"{len(modes)} modos instalados en {PI_DIR} (+{len(modes)} de tres piernas); {len(taus)} Tau en {SVG_DIR}")


if __name__ == "__main__":
    main()
