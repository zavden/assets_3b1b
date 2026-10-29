"""Regenerates ALL the _2022/wordle data that depends on the word lists, over the FREE lists of
`make_wordle_wordlists.py` (ENABLE/SCOWL + wordfreq) instead of the NYT ones that the 3b1b repo ships
(`videos/_2022/wordle/data/*.txt`, `freq_map.json`, `second_guess_map.json`, `simulation_results/*`: those
are not used either, because they contain the NYT answer list inside).

It uses 3b1b's own `simulations.py` (loaded by path from $THREEB1B_VIDEOS), with the lists and all the
output files redirected here. It takes ~1 h in total (a single thread per process); each step is skipped if its
file already exists (`--force` to redo). With `--only` the steps can be split between two processes
(e.g. `--only matrix,entropies,scores,ent_score` and, when the matrix exists, `--only sgm,brute,sims`).

Output:
  _lib/data/wordle/                       (what the code reads with get_directories()["data"] / "wordle")
    pattern_matrix.npy                    pattern matrix 12972 x 12972 (uint8, 168 MB). The original
                                          computes it in a single block of 13000 (needs > 5 GB);
                                          here it is computed in blocks of 1000 and the result is the same.
    best_entropies.json, best_double_entropies.json
                                          find_best_two_step_entropy()
    best_scores_with_entropy_method.json  find_top_scorers(): simulated games for the best
                                          first guesses of best_double_entropies.json
    salet_with_brute_force_guess_map.json copy of data/simulation_results/salet_guess_map_brute_force.json
                                          (from the brute-force simulation below)
  _lib/assets/generated/2022/wordle/data/ (copied next to the scenes with `data_files`)
    possible_words.txt, allowed_words.txt, freq_map.json   (written by make_wordle_wordlists.py)
    second_guess_map.json                 best 2nd guess by brute force for each pattern of the 1st
                                          (crane, salet, crate, slate, trace); it is what Grant computed over hours
    ent_score_pairs.json                  gather_entropy_to_score_data("crane")
    simulation_results/*.json             simulate_games(...) with different configurations; all of them
                                          are reproduced (crane_with_wordle_prior, tares_*, soare_*,
                                          crane_hard_mode, *_exclude_seen, crane_brute_force,
                                          least/slate/weary/adieu/audio_results) and, in the `brute` step,
                                          {crate,salet,trace}_brute_force.json and *_guess_map_brute_force.json
                                          (in the 3b1b repo they were data computed with the NYT list).
                                          Grant's exact configurations are not known: they are
                                          the ones suggested by the file names.

Usage: THREEB1B_VIDEOS=../videos python make_wordle_data.py [--force] [--only step[,step]]
  steps: lists, matrix, entropies, scores, ent_score, sgm, brute, sims"""
import argparse
import importlib.util
import json
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]
DATA_OUT = LIB / "data" / "wordle"
GEN_OUT = HERE / "data"
SIM_OUT = GEN_OUT / "simulation_results"

VIDEOS = Path(os.environ.get("THREEB1B_VIDEOS", LIB.parent.parent / "videos")).resolve()
WORDLE_SRC = VIDEOS / "_2022" / "wordle"


def load_simulations():
    spec = importlib.util.spec_from_file_location("wordle_simulations", WORDLE_SRC / "simulations.py")
    sim = importlib.util.module_from_spec(spec)
    sys.modules["wordle_simulations"] = sim
    spec.loader.exec_module(sim)
    # Everything that is read and written goes to our folders, never to the videos clone (whose lists are the NYT's)
    sim.PATTERN_MATRIX_FILE = str(DATA_OUT / "pattern_matrix.npy")
    sim.ENT_SCORE_PAIRS_FILE = str(GEN_OUT / "ent_score_pairs.json")
    sim.DATA_DIR = str(GEN_OUT)  # simulate_games(results_file=...) writes to DATA_DIR/simulation_results
    sim.SHORT_WORD_LIST_FILE = str(GEN_OUT / "possible_words.txt")
    sim.LONG_WORD_LIST_FILE = str(GEN_OUT / "allowed_words.txt")
    sim.WORD_FREQ_MAP_FILE = str(GEN_OUT / "freq_map.json")
    sim.SECOND_GUESS_MAP_FILE = str(GEN_OUT / "second_guess_map.json")
    return sim


def timed(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)
    return time.time()


FIRST_GUESSES_SGM = ("crane", "salet", "crate", "slate", "trace")
FIRST_GUESSES_BRUTE = ("salet", "crate", "trace")  # the *_brute_force.json files that the 3b1b repo had


def step_lists(sim, force):
    """Writes the free lists if they are missing (make_wordle_wordlists.py)."""
    names = ("possible_words.txt", "allowed_words.txt", "freq_map.json")
    if all((GEN_OUT / n).exists() for n in names) and not force:
        return
    import subprocess
    subprocess.run([sys.executable, str(HERE / "make_wordle_wordlists.py")], check=True)


def step_sgm(sim, force):
    """second_guess_map.json: for each pattern of the first guess, the second guess that comes out of simulating
    the full game with the 10 best options (brute_force_optimal_guess), as Grant did."""
    path = Path(sim.SECOND_GUESS_MAP_FILE)
    if not path.exists() or force:
        path.write_text("{}")
    for first in FIRST_GUESSES_SGM:
        with open(path) as fp:
            if first in json.load(fp):
                continue
        t0 = timed(f"get_optimal_second_guess_map({first!r})")
        sim.get_optimal_second_guess_map(first)  # it saves it in second_guess_map.json
        timed(f"  listo en {time.time() - t0:.0f} s")


def step_brute(sim, force):
    """{first}_brute_force.json and {first}_guess_map_brute_force.json: games with the second guess from
    second_guess_map and then minimizing the score with a uniform distribution."""
    SIM_OUT.mkdir(parents=True, exist_ok=True)
    wordle_prior = sim.get_true_wordle_prior()
    with open(GEN_OUT / "second_guess_map.json") as fp:
        sgms = json.load(fp)
    for first in FIRST_GUESSES_BRUTE:
        out = SIM_OUT / f"{first}_brute_force.json"
        if out.exists() and not force:
            continue
        t0 = timed(f"simulate_games {first} (fuerza bruta)")
        result, _ = sim.simulate_games(
            quiet=True, first_guess=first, priors=wordle_prior,
            optimize_for_uniform_distribution=True, second_guess_map=sgms[first],
            results_file=f"{first}_brute_force.json",
            next_guess_map_file=f"{first}_guess_map_brute_force.json",
        )
        timed(f"  listo en {time.time() - t0:.0f} s, promedio {result['average_score']:.4f}")


def step_matrix(sim, force):
    out = Path(sim.PATTERN_MATRIX_FILE)
    if out.exists() and not force:
        return
    t0 = timed("pattern_matrix.npy")
    words = sim.get_word_list()
    matrix = sim.generate_pattern_matrix_in_blocks(words, words, block_length=1000)
    np.save(out, matrix)
    timed(f"  listo en {time.time() - t0:.0f} s, forma {matrix.shape}")


def step_entropies(sim, force):
    files = [DATA_OUT / "best_entropies.json", DATA_OUT / "best_double_entropies.json"]
    if all(f.exists() for f in files) and not force:
        return
    t0 = timed("find_best_two_step_entropy")
    sim.find_best_two_step_entropy()
    timed(f"  listo en {time.time() - t0:.0f} s")


def step_scores(sim, force):
    out = DATA_OUT / "best_scores_with_entropy_method.json"
    if out.exists() and not force:
        return
    t0 = timed("find_top_scorers (30 mejores primeros intentos)")
    sim.find_top_scorers(n_top_candidates=30, file_ext="_with_entropy_method")
    # find_top_scorers writes best_scores<ext>.json
    timed(f"  listo en {time.time() - t0:.0f} s")


def step_ent_score(sim, force):
    out = GEN_OUT / "ent_score_pairs.json"
    if out.exists() and not force:
        return
    t0 = timed("gather_entropy_to_score_data('crane')")
    sim.gather_entropy_to_score_data("crane")
    timed(f"  listo en {time.time() - t0:.0f} s")


def step_sims(sim, force):
    SIM_OUT.mkdir(parents=True, exist_ok=True)
    wordle_prior = sim.get_true_wordle_prior()
    freq_prior = sim.get_frequency_based_priors()
    uniform_prior = dict((w, 1) for w in sim.get_word_list())
    with open(GEN_OUT / "second_guess_map.json") as fp:  # step `sgm`
        sgms = json.load(fp)

    configs = {
        "crane_with_wordle_prior": dict(first_guess="crane", priors=wordle_prior),
        "soare_with_wordle_prior": dict(first_guess="soare", priors=wordle_prior),
        "tares_with_uniform_prior": dict(first_guess="tares", priors=uniform_prior),
        "tares_with_freq_prior": dict(first_guess="tares", priors=freq_prior),
        "crane_hard_mode": dict(first_guess="crane", priors=wordle_prior, hard_mode=True),
        "crane_with_wordle_prior_exclude_seen": dict(
            first_guess="crane", priors=wordle_prior, exclude_seen_words=True),
        "tares_with_freq_prior_exclude_seen": dict(
            first_guess="tares", priors=freq_prior, exclude_seen_words=True),
        # Same method as the repo's *_brute_force.json: second guess from second_guess_map.json
        # (which Grant computed by brute force) and then minimize the score with a uniform
        # distribution
        "crane_brute_force": dict(
            first_guess="crane", priors=wordle_prior,
            optimize_for_uniform_distribution=True, second_guess_map=sgms["crane"]),
    }
    for first in ("least", "slate", "weary", "adieu", "audio"):
        configs[f"{first}_results"] = dict(
            first_guess=first, priors=wordle_prior, optimize_for_uniform_distribution=True)

    for name, kw in configs.items():
        out = SIM_OUT / f"{name}.json"
        if out.exists() and not force:
            continue
        t0 = timed(f"simulate_games {name}")
        result, _ = sim.simulate_games(quiet=True, **kw)
        with open(out, "w") as fp:
            json.dump(result, fp)
        timed(f"  listo en {time.time() - t0:.0f} s, promedio {result['average_score']:.4f}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true")
    p.add_argument("--only", default="lists,matrix,entropies,scores,ent_score,sgm,brute,sims")
    args = p.parse_args()

    DATA_OUT.mkdir(parents=True, exist_ok=True)
    GEN_OUT.mkdir(parents=True, exist_ok=True)
    sys.argv = sys.argv[:1]  # manimlib reads sys.argv when imported
    sim = load_simulations()

    steps = dict(lists=step_lists, matrix=step_matrix, entropies=step_entropies, scores=step_scores,
                 ent_score=step_ent_score, sgm=step_sgm, brute=step_brute, sims=step_sims)
    for name in args.only.split(","):
        steps[name](sim, args.force)
    # The scenes read this map with get_directories()["data"]/wordle/...
    src = SIM_OUT / "salet_guess_map_brute_force.json"
    if src.exists():
        shutil.copy2(src, DATA_OUT / "salet_with_brute_force_guess_map.json")
    timed("terminado")


if __name__ == "__main__":
    main()
