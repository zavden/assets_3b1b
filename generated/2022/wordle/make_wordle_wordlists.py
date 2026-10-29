"""FREE word lists for the _2022/wordle scenes (they replace the NYT / Wordle ones).

The 3b1b repo ships in `videos/_2022/wordle/data/` Wordle's lists (`possible_words.txt` = answers,
`allowed_words.txt` = accepted words) and the frequencies (`freq_map.json`, `wordle_words_freqs_full.txt`).
That data belongs to the NYT / third parties and is not redistributed. This script replaces it with free data:

  source                         license                       use
  ENABLE (enable1.txt)           public domain                 valid 5-letter words
  SCOWL / ESDB (app.aspell.net)  permissive (copyright notice) valid 5-letter words (broad)
  wordfreq 3.1.1 (pip)           data CC BY-SA 4.0, code Apache-2.0   frequency of each word

Output, in `_lib/assets/generated/2022/wordle/data/` (the scenes receive it with `data_files`, with the same
names the files by Grant had):
  possible_words.txt   2315 common 5-letter words (the "answers"). It is 2315 on purpose: some
                       scenes say "2,315 words, equally likely" and comment on log2(2315) = 11.177 bits.
  allowed_words.txt    all the words accepted as a guess (~11.7 thousand; ENABLE + SCOWL size 95 + the
                       ones the scenes show explicitly). It contains possible_words.
  freq_map.json        {word: relative frequency} for each word of allowed_words (wordfreq, 'en').
  SOURCES.txt          sources, versions and licenses of what was used.

How the "answers" are chosen: words that are in ENABLE *and* in SCOWL (size 60: everyday vocabulary,
without proper names or oddities), without plurals or regular third persons (-s / -es / -ies), without a
short list of insults, sorted by frequency (wordfreq); the 2315 most frequent are taken, plus the
answers that the scenes show (SCENE_ANSWERS).

After running this, the derived data must be regenerated (pattern matrix, simulations, entropies):
    python make_wordle_data.py            # ~1 h, see that script
The files are downloaded to `_tools/.cache/wordle_sources/` the first time.

Usage: python make_wordle_wordlists.py [--force]"""
import argparse
import codecs
import json
import re
import urllib.request
from importlib import metadata
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]
OUT = HERE / "data"
CACHE = LIB.parent / "_tools" / ".cache" / "wordle_sources"

N_POSSIBLE = 2315

ENABLE_URL = "https://raw.githubusercontent.com/dolph/dictionary/master/enable1.txt"
SCOWL_URL = (
    "https://app.aspell.net/create?max_size={size}&spelling=US&spelling=GBs&spelling=CA"
    "&max_variant=2&diacritic=strip&download=wordlist&encoding=utf-8&format=inline"
)

# Answers (secret_word / answer) that the scenes show explicitly: they have to be "possible" for the
# example to make sense (see `scenes.py` / `footnote.py` in _2022/wordle).
SCENE_ANSWERS = """
abide aging baker brown crepe elder erase graph start steal thump words
crane crate slate trace speed
""".split()

# Words that the scenes type as guesses or show in lists (accepted, but not necessarily answers). They
# are added to allowed_words if ENABLE/SCOWL do not include them. "onnne" is deliberately absent: the
# scene uses it to show an invalid guess.
SCENE_WORDS = """
adieu after angry arise arles asked audio avoid blues braid brute carle carse carte crine dance dorms
enter favor final first force guess happy ideal ideas irate kayak knows lares large least limit makes
maths maybe nails naive nares orate other phone picks plain print prior raile raise rales rates reais
reals reast right roast roate saint salet saner sassy scene score sigma slane soare stare steps tales
tares tears tease teras there thing three tired today toile tores torse tousy trone using value video
weary which width wonky wonts wordy write
""".split()

# Extra words that the scenes need for their mechanics to work. EntropyOfWordDistributionExample (secret
# "graph", guesses "other" and "nails") is written so that 16 accepted words match, of which exactly 4 are
# possible answers ("4 matches", log2(4) = 2, "+ 12 (0.001...)", ChangeDecimal(16)). With these lists 14 matched
# (5 possible): two dictionary words are added to the accepted ones and "chard" is removed from the answers
# (EXCLUDE_ANSWERS); it is still accepted.
SCENE_EXTRA_ALLOWED = "ruach umrah".split()
EXCLUDE_ANSWERS = {"chard"}

# Insults and vulgarities that must not come out as an "answer" (rot13 so as not to write them as is).
BLOCKED_ROT13 = """
fdhnj jrapu ihyin ynovn juber ovgpu chffl qlxrf sntbg arteb avttn puvax tvcfl tlcfl tbbxf pbbaf
xvxrf fcvpx phagf ovzob fuvgr shpxf gjngf
""".split()
BLOCKED = {codecs.decode(w, "rot13") for w in BLOCKED_ROT13}


def fetch(url, name, force=False):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / name
    if force or not path.exists() or path.stat().st_size == 0:
        print(f"descargando {name} ...", flush=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (wordle-wordlists generator)"})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    return path.read_text(encoding="utf-8", errors="replace")


def five(words):
    return {w for w in words if len(w) == 5 and re.fullmatch(r"[a-z]{5}", w)}


def lines(text):
    return [l.strip() for l in text.split("\n")]


def esdb_revision(text):
    m = re.search(r"ESDB Git Revision: (.*)", text)
    return m.group(1).strip() if m else "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="volver a descargar las fuentes")
    args = ap.parse_args()

    from wordfreq import word_frequency

    enable_text = fetch(ENABLE_URL, "enable1.txt", args.force)
    scowl95_text = fetch(SCOWL_URL.format(size=95), "scowl95.txt", args.force)
    scowl60_text = fetch(SCOWL_URL.format(size=60), "scowl60.txt", args.force)

    enable = set(lines(enable_text))
    s95, s60 = set(lines(scowl95_text)), set(lines(scowl60_text))
    enable5, s95_5, s60_5 = five(enable), five(s95), five(s60)
    print(f"ENABLE: {len(enable5)}  SCOWL95: {len(s95_5)}  SCOWL60: {len(s60_5)}  (palabras de 5 letras)")

    # ---------------------------------------------------------------- allowed
    allowed = enable5 | s95_5 | set(SCENE_WORDS) | set(SCENE_ANSWERS) | set(SCENE_EXTRA_ALLOWED)

    # ---------------------------------------------------------------- possible
    stems4 = {w for w in (enable | s95 | s60) if len(w) == 4 and w.isalpha() and w.islower()}
    stems3 = {w for w in enable if len(w) == 3}

    def is_inflected_plural(w):
        if not w.endswith("s") or w.endswith(("ss", "us", "is")):
            return False
        return w[:-1] in stems4 or w.endswith("ies") or (w.endswith("es") and w[:-2] in stems3)

    common = {w for w in enable5 & s60_5 if not is_inflected_plural(w) and w not in BLOCKED | EXCLUDE_ANSWERS}
    ranked = sorted(common | set(SCENE_ANSWERS), key=lambda w: (-word_frequency(w, "en"), w))
    possible = list(dict.fromkeys(SCENE_ANSWERS))  # without repeats, in order
    for w in ranked:
        if len(possible) >= N_POSSIBLE:
            break
        if w not in possible:
            possible.append(w)
    possible = sorted(possible)
    assert len(possible) == N_POSSIBLE, len(possible)
    assert set(possible) <= allowed

    allowed = sorted(allowed)

    # ---------------------------------------------------------------- frequencies
    freq_map = {}
    for w in allowed:
        f = word_frequency(w, "en")
        if f <= 0:
            # Words that wordfreq does not know: a tiny but distinct frequency for each
            # (deterministic), so that the order by frequency does not depend on chance.
            f = 1e-10 * (0.5 + (sum(ord(c) * 31 ** i for i, c in enumerate(w)) % 1000) / 1000.0)
        freq_map[w] = f

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "possible_words.txt").write_text("\n".join(possible) + "\n")
    (OUT / "allowed_words.txt").write_text("\n".join(allowed) + "\n")
    with open(OUT / "freq_map.json", "w") as fp:
        json.dump(freq_map, fp)
    (OUT / "SOURCES.txt").write_text(
        "Listas de palabras de _2022/wordle (generadas por make_wordle_wordlists.py)\n\n"
        "- ENABLE (enable1.txt, dominio publico): " + ENABLE_URL + "\n"
        "- SCOWL / English Speller Database, tamano 60 y 95, ortografia US+GB(-ise)+CA, nivel de variantes 2\n"
        f"  (revision ESDB: {esdb_revision(scowl95_text)}). Copyright 2000-2026 Kevin Atkinson; se permite usar,\n"
        "  copiar, modificar y distribuir las listas derivadas conservando el aviso de copyright\n"
        "  (https://wordlist.aspell.net). La mayor parte de sus fuentes son de dominio publico.\n"
        f"- wordfreq {metadata.version('wordfreq')} (Robyn Speer; codigo Apache-2.0, datos CC BY-SA 4.0):\n"
        "  frecuencias de freq_map.json. Ese archivo es una obra derivada de datos CC BY-SA 4.0.\n"
    )

    n_unknown = sum(1 for w in allowed if word_frequency(w, "en") <= 0)
    print(f"possible_words.txt: {len(possible)}   allowed_words.txt: {len(allowed)}   "
          f"sin frecuencia en wordfreq: {n_unknown}")
    print("  escritos en", OUT)


if __name__ == "__main__":
    main()
