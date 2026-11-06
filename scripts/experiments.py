"""Phase 9: experiments that explain the results (test split everywhere).

    venv\\Scripts\\python.exe scripts\\experiments.py models      # H vs E vs GRIC
    venv\\Scripts\\python.exe scripts\\experiments.py masks       # object only vs with surroundings
    venv\\Scripts\\python.exe scripts\\experiments.py angles      # accuracy vs viewpoint change
    venv\\Scripts\\python.exe scripts\\experiments.py mast3r      # MASt3R gain: seen (CO3D) vs unseen data
    venv\\Scripts\\python.exe scripts\\experiments.py timing      # all methods timed in one session
    venv\\Scripts\\python.exe scripts\\experiments.py all

models  re-uses cached matches (scripts/matchcache.py) and runs only the geometry with the
        model forced to H (homography: planar object) or E (essential matrix: general 3D),
        or chosen per pair by GRIC -- is the near-planar assumption worth making?
masks   compares matching on the object only (mask) with matching on the whole image. In
        these datasets the object stands still in a static scene, so the background moves
        consistently with the object and can only help; a labelled comparison, not the
        main result (the task is the object's pose).
angles  AUC per viewpoint-change bin for every method (from results/*/pairs.csv).
mast3r  MASt3R was trained on CO3Dv2 (among others), not on Objectron, TUM or MVImgNet:
        if its gain over the classical/learned matchers is much larger on CO3D, that part
        of the gain is likely memorisation.
timing  the same 24 test pairs through every method, back to back, so seconds are
        comparable (earlier runs were timed hours apart, under different CPU load).
Writes results/experiments/<name>.md (+ figures).
"""
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from tqdm import tqdm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from matchcache import cached_matches  # noqa: E402
from src.loaders import LOADERS, split_of  # noqa: E402
from src.pipeline import (estimate_pose, estimate_pose_cascade, estimate_pose_shape, pose_from_matches,  # noqa: E402
                          rotation_error_deg, translation_angle_deg)
from src.pipeline.metrics import pose_auc  # noqa: E402

OUT = ROOT / "results" / "experiments"
PER_BIN = {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}
SEED = 0
METHODS = {   # label -> results folder (refined, all four datasets)
    "SIFT": "sift_ref", "XFeat": "xfeat_ref", "XFeat+LG": "xfeat_lg_ref", "ALIKED+LG": "aliked_lg_ref",
    "DISK+LG": "disk_lg_ref", "LoFTR": "loftr_ref", "shape": "shape_ref", "MASt3R": ["mast3r_crop", "mast3r_mvimgnet"],
}


def test_pairs(datasets=None):
    out = []
    for ds in datasets or LOADERS:
        out += [p for p in LOADERS[ds].load_pairs(per_bin=PER_BIN[ds], seed=SEED) if split_of(p.name) == "test"]
    return out


def pose_error(res, pair):
    if not res.ok:
        return np.inf
    rot, tra = rotation_error_deg(res.R, pair.R_gt), translation_angle_deg(res.t, pair.t_gt)
    return rot if np.isnan(tra) else max(rot, tra)


def load_runs():
    runs = {}
    for label, folders in METHODS.items():
        folders = [folders] if isinstance(folders, str) else folders
        parts = [pd.read_csv(ROOT / "results" / f / "pairs.csv") for f in folders
                 if (ROOT / "results" / f / "pairs.csv").exists()]
        if parts:
            d = pd.concat(parts).drop_duplicates("pair")
            runs[label] = d[d.split == "test"]
    return runs


def auc10(errs):
    return pose_auc(np.asarray(errs, float))[10]


def write(name, lines):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


# ---------------------------------------------------------------------------------------------
def models(matchers=("aliked_lg", "xfeat_lg")):
    rows = []
    for pair in tqdm(test_pairs(), desc="models"):
        for m in matchers:
            p1, p2, scale = cached_matches(m, pair, crop=True)
            for model in ("auto", "H", "E"):
                res = pose_from_matches(p1, p2, scale, pair.frame1.K, pair.frame2.K, model=model)
                rows.append(dict(dataset=pair.dataset, object=pair.sequence.split("/")[0], matcher=m, model=model,
                                 chosen=res.model if res.ok else "", err=pose_error(res, pair)))
    df = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "models.csv", index=False)
    lines = ["# Homography (planar) vs essential matrix (3D) vs GRIC choice", "",
             "Same matches, only the geometric model changes. AUC@10 (%), test split.", ""]
    for m in matchers:
        d = df[df.matcher == m]
        objs = list(dict.fromkeys(d.object))
        lines += [f"## {m}", "", "| model | " + " | ".join(objs) + " | all |", "|---" * (len(objs) + 2) + "|"]
        for model in ("H", "E", "auto"):
            s = d[d.model == model]
            lines.append(f"| {model if model != 'auto' else 'GRIC'} | "
                         + " | ".join(f"{auc10(s[s.object == o].err):.1f}" for o in objs) + f" | {auc10(s.err):.1f} |")
        g = d[(d.model == "auto") & (d.chosen != "")]
        lines += ["", f"GRIC chose H for {100 * (g.chosen == 'H').mean():.1f}% of the pairs it solved.", ""]
    write("models", lines)


def masks():
    pairs_obj = {"ALIKED+LG": "aliked_lg_ref", "SIFT": "sift_ref"}
    pairs_full = {"ALIKED+LG": "aliked_lg_full", "SIFT": "sift_full"}
    lines = ["# Object only vs with surroundings (labelled comparison)", "",
             "Object only = matches restricted to the object mask (the task). With surroundings = whole image.",
             "The objects here are static in a static scene, so background matches follow the same camera motion.",
             "AUC@10 (%), test split.", "", "| method | input | " + " | ".join(LOADERS) + " |",
             "|---" * (len(LOADERS) + 2) + "|"]
    for label in pairs_obj:
        for kind, folder in (("object only", pairs_obj[label]), ("with surroundings", pairs_full[label])):
            path = ROOT / "results" / folder / "pairs.csv"
            if not path.exists():
                lines.append(f"| {label} | {kind} | " + " | ".join("-" for _ in LOADERS) + " |")
                continue
            d = pd.read_csv(path)
            d = d[d.split == "test"]
            lines.append(f"| {label} | {kind} | " + " | ".join(f"{auc10(d[d.dataset == ds].pose_err_deg):.1f}"
                                                           for ds in LOADERS) + " |")
    write("masks", lines)


def angles():
    runs = load_runs()
    bins = ["5-15", "15-30", "30-60"]
    lines = ["# Accuracy vs viewpoint change", "", "AUC@10 (%) per rotation-angle bin, test split, all datasets.", "",
             "| method | " + " | ".join(f"{b} deg" for b in bins) + " |", "|---" * (len(bins) + 1) + "|"]
    fig, ax = plt.subplots(figsize=(6, 4))
    for label, d in runs.items():
        vals = [auc10(d[d.angle_bin == b].pose_err_deg) for b in bins]
        lines.append(f"| {label} | " + " | ".join(f"{v:.1f}" for v in vals) + " |")
        ax.plot(range(len(bins)), vals, marker="o", linewidth=2, label=label)
    ax.set_xticks(range(len(bins)), [f"{b} deg" for b in bins])
    ax.set_ylabel("AUC@10 (%)")
    ax.set_xlabel("viewpoint change")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, fontsize=8, ncol=2)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "angles.png", dpi=150)
    write("angles", lines)


def mast3r():
    runs = load_runs()
    if "MASt3R" not in runs:
        raise SystemExit("MASt3R results missing")
    others = [m for m in runs if m not in ("MASt3R", "shape")]
    lines = ["# MASt3R: gain on data it was trained on (CO3D) vs unseen data", "",
             "AUC@10 (%), test split. 'best other' = best of the other matchers on that dataset.", "",
             "| dataset | in MASt3R training? | MASt3R | best other | gain |", "|---|---|---|---|---|"]
    seen = {"co3d": "yes (CO3Dv2)", "objectron": "no", "tum": "no", "mvimgnet": "no"}
    for ds in LOADERS:
        if not (runs["MASt3R"].dataset == ds).any():
            lines.append(f"| {ds} | {seen[ds]} | - | - | - |")
            continue
        m = auc10(runs["MASt3R"].pipe(lambda d: d[d.dataset == ds]).pose_err_deg)
        best = max(auc10(runs[o][runs[o].dataset == ds].pose_err_deg) for o in others)
        lines.append(f"| {ds} | {seen[ds]} | {m:.1f} | {best:.1f} | {m - best:+.1f} |")
    lines += ["", "A much larger gain on CO3D than on the unseen sets would point to memorisation; similar "
              "gains mean the advantage is general (dense matching, learned 3D priors)."]
    write("mast3r", lines)


def timing(n_pairs=24):
    rng = np.random.default_rng(SEED)
    pool = test_pairs()
    pairs = [pool[k] for k in rng.choice(len(pool), size=n_pairs, replace=False)]
    loaded = [(p, p.load()) for p in pairs]
    methods = {f"{m}": (lambda a, b, K1, K2, m1, m2, m=m: estimate_pose(a, b, K1, K2, m1, m2, matcher=m, crop=True))
               for m in ["sift", "xfeat", "xfeat_lg", "aliked_lg", "disk_lg", "loftr", "mast3r"]}
    methods["shape"] = lambda a, b, K1, K2, m1, m2: estimate_pose_shape(a, b, K1, K2, m1, m2)
    methods["cascade fast"] = lambda a, b, K1, K2, m1, m2: estimate_pose_cascade(a, b, K1, K2, m1, m2, preset="fast")
    methods["cascade accurate"] = lambda a, b, K1, K2, m1, m2: estimate_pose_cascade(a, b, K1, K2, m1, m2,
                                                                                    preset="accurate")
    lines = ["# Run time on CPU (same pairs, one session)", "",
             f"{n_pairs} random test pairs from all datasets; images already in memory; first call per method "
             "(model loading) excluded.", "", "| method | median s/pair | mean s/pair |", "|---|---|---|"]
    for label, fn in methods.items():
        p, (a, b, m1, m2) = loaded[0]
        fn(a, b, p.frame1.K, p.frame2.K, m1, m2)          # warm-up: loads weights
        secs = []
        for p, (a, b, m1, m2) in tqdm(loaded, desc=label):
            t0 = time.perf_counter()
            fn(a, b, p.frame1.K, p.frame2.K, m1, m2)
            secs.append(time.perf_counter() - t0)
        lines.append(f"| {label} | {np.median(secs):.2f} | {np.mean(secs):.2f} |")
    import os
    lines += ["", f"CPU threads available: {os.cpu_count()}."]
    write("timing", lines)


TASKS = {"models": models, "masks": masks, "angles": angles, "mast3r": mast3r, "timing": timing}

if __name__ == "__main__":
    names = sys.argv[1:] or ["all"]
    for name in (list(TASKS) if names == ["all"] else names):
        TASKS[name]()
