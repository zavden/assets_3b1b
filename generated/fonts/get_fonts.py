"""Downloads the free fonts (SIL Open Font License) that replace the ones some scenes asked for:
Consolas (Microsoft, proprietary) -> JetBrains Mono, Better Grade -> Caveat, Simplo Soft Medium -> Nunito.
They end up in _lib/assets/fonts/ with their license; _lib/manim_imports_ext.py registers them and translates the names.

It also downloads the three free fonts that the scenes ask for by their real name (level 2: they are not redistributed, they are
downloaded from their official source in the setup), so that the renders do not depend on what the system has installed:
  - CMU Serif (Computer Modern Unicode 0.7.0, OFL 1.1): the project's base font (`manim_config.text.font`).
    From the project's TTF archive (cm-unicode.sourceforge.io) only the four variants of the "CMU Serif"
    family (Roman, Bold, Italic, BoldItalic) and its OFL.txt are kept.
  - Kalam (OFL 1.1, Indian Type Foundry): google/fonts repository; asked for by _2021/shadows (AliceWords, BobWords, BobName).
  - Roboto (OFL 1.1, The Roboto Project Authors): google/fonts repository, variable version; asked for by _2024/antp (CrankEmail).
The family names that fc-list and manimpango see are "CMU Serif", "Kalam" and "Roboto", the same ones the scenes use."""
import hashlib
import io
import tarfile
import urllib.request
from pathlib import Path

FONTS = Path(__file__).resolve().parents[2] / "fonts"
FILES = {
    "JetBrainsMono-Regular.ttf": "https://github.com/JetBrains/JetBrainsMono/raw/master/fonts/ttf/JetBrainsMono-Regular.ttf",
    "JetBrainsMono-Bold.ttf": "https://github.com/JetBrains/JetBrainsMono/raw/master/fonts/ttf/JetBrainsMono-Bold.ttf",
    "JetBrainsMono-OFL.txt": "https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/OFL.txt",
    "Caveat[wght].ttf": "https://github.com/google/fonts/raw/main/ofl/caveat/Caveat%5Bwght%5D.ttf",
    "Caveat-OFL.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/OFL.txt",
    "Nunito[wght].ttf": "https://github.com/google/fonts/raw/main/ofl/nunito/Nunito%5Bwght%5D.ttf",
    "Nunito-OFL.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/OFL.txt",
    "Kalam-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Regular.ttf",
    "Kalam-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Bold.ttf",
    "Kalam-OFL.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/kalam/OFL.txt",
    "Roboto[wdth,wght].ttf": "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto%5Bwdth%2Cwght%5D.ttf",
    "Roboto-OFL.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/roboto/OFL.txt",
}

# CMU Serif: official project file (SourceForge, linked from cm-unicode.sourceforge.io). Only the tar members with
# these exact names are read (nothing else is extracted), and they are saved under our own name.
CMU_URL = "https://downloads.sourceforge.net/project/cm-unicode/cm-unicode/0.7.0/cm-unicode-0.7.0-ttf.tar.xz"
CMU_SHA256 = "2609c14450f42d0bcd40203900afcb1d693521a9b24a18c65e14b6b0585ff150"
CMU_MEMBERS = {
    "cm-unicode-0.7.0/cmunrm.ttf": "CMUSerif-Roman.ttf",
    "cm-unicode-0.7.0/cmunbx.ttf": "CMUSerif-Bold.ttf",
    "cm-unicode-0.7.0/cmunti.ttf": "CMUSerif-Italic.ttf",
    "cm-unicode-0.7.0/cmunbi.ttf": "CMUSerif-BoldItalic.ttf",
    "cm-unicode-0.7.0/OFL.txt": "CMUSerif-OFL.txt",
}

FONTS.mkdir(parents=True, exist_ok=True)
for name, url in FILES.items():
    dest = FONTS / name
    if not dest.exists():
        urllib.request.urlretrieve(url, dest)
    print(name, dest.stat().st_size)

if not all((FONTS / n).exists() for n in CMU_MEMBERS.values()):
    data = urllib.request.urlopen(CMU_URL, timeout=120).read()
    digest = hashlib.sha256(data).hexdigest()
    if CMU_SHA256 and digest != CMU_SHA256:
        raise SystemExit(f"CMU Serif: el archivo descargado no coincide con el esperado ({digest})")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:xz") as tar:
        for member, name in CMU_MEMBERS.items():
            (FONTS / name).write_bytes(tar.extractfile(member).read())
for name in CMU_MEMBERS.values():
    print(name, (FONTS / name).stat().st_size)
