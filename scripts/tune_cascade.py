"""Choose the cascade design on the tuning split, then report it on the test split.

    venv\\Scripts\\python.exe scripts\\tune_cascade.py

Every method was already evaluated on exactly the same pairs (scripts/evaluate.py), so a
cascade can be simulated from the saved per-pair results instead of re-running it:

    for each stage (a matcher):  run it; accept its pose if it has >= T inliers
    the shape method can sit between any two stages (accepted whenever it succeeds)
    if no stage accepts:         "best" = keep the matcher pose with most inliers, or "fail"

Time is the sum of the stages that actually ran. The objective is the mean AUC@10 over the
four datasets, with a time budget. Only "tune" pairs are used to choose; the chosen designs
are then scored once on "test" pairs (src/loaders split_of).

Writes results/cascade/{search.csv, summary.md}.
"""
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.loaders import split_of  # noqa: E402
from src.pipeline.metrics import pose_auc  # noqa: E402

RUNS = {   # method -> results folders holding its per-pair results (current geometry, 4 datasets)
    "sift": ["sift_ref"], "xfeat": ["xfeat_ref"], "xfeat_lg": ["xfeat_lg_ref"],
    "aliked_lg": ["aliked_lg_ref"], "disk_lg": ["disk_lg_ref"], "loftr": ["loftr_ref"],
    "shape": ["shape_ref"],
}
MATCHERS = [m for m in RUNS if m != "shape"]
THRESHOLDS = [15, 30, 50, 80, 120, 200]
BUDGETS = [0.5, 1.0, 2.0, np.inf]     # mean seconds per pair
DATASETS = ["tum", "objectron", "co3d", "mvimgnet"]


def load():
    frames = {}
    for method, folders in RUNS.items():
        d = pd.concat([pd.read_csv(ROOT / "results" / f / "pairs.csv") for f in folders])
        frames[method] = d.set_index("pair")
    pairs = frames["sift"].index
    base = frames["sift"][["dataset", "object"]].copy()
    base["split"] = [split_of(p) for p in pairs]
    arr = {}
    for method, d in frames.items():
        d = d.reindex(pairs)
        arr[method] = dict(ok=d.ok.fillna(False).to_numpy(bool), inl=d.inliers.fillna(0).to_numpy(),
                           err=d.pose_err_deg.fillna(np.inf).to_numpy(), sec=d.seconds.fillna(0).to_numpy())
    return base, arr


def simulate(arr, stages, thresholds, shape_at, fallback):
    """Per-pair pose error, seconds and the stage that answered, for one cascade design."""
    n = len(arr["sift"]["ok"])
    err = np.full(n, np.inf)
    sec = np.zeros(n)
    used = np.full(n, "fail", dtype=object)
    done = np.zeros(n, bool)
    best_inl, best_err = np.zeros(n), np.full(n, np.inf)

    def try_shape():
        nonlocal done
        s = arr["shape"]
        todo = ~done
        sec[todo] += s["sec"][todo]
        take = todo & s["ok"]
        err[take], used[take] = s["err"][take], "shape"
        done = done | take

    for i, (m, T) in enumerate(zip(stages, thresholds)):
        if shape_at == i:
            try_shape()
        a = arr[m]
        todo = ~done
        sec[todo] += a["sec"][todo]
        better = todo & a["ok"] & (a["inl"] > best_inl)
        best_inl[better], best_err[better] = a["inl"][better], a["err"][better]
        take = todo & a["ok"] & (a["inl"] >= T)
        err[take], used[take] = a["err"][take], m
        done = done | take
    if shape_at == len(stages):
        try_shape()
    if fallback == "best":
        rest = ~done & (best_inl > 0)
        err[rest], used[rest] = best_err[rest], "best-so-far"
    return err, sec, used


def score(base, err, sec, mask):
    aucs = {d: pose_auc(err[mask & (base.dataset == d).to_numpy()])[10] for d in DATASETS}
    return np.mean(list(aucs.values())), aucs, sec[mask].mean()


def describe(c):
    stages = [f"{m}(>={T})" for m, T in zip(c["stages"], c["thresholds"])]
    if c["shape_at"] >= 0:
        stages.insert(int(c["shape_at"]), "shape")
    return " -> ".join(stages) + f" -> {c['fallback']}"


def main():
    base, arr = load()
    tune = (base.split == "tune").to_numpy()
    test = ~tune

    rows = []
    for k in (1, 2, 3):
        for stages in itertools.permutations(MATCHERS, k):
            for thresholds in itertools.product(THRESHOLDS, repeat=k):
                for shape_at in [-1, *range(k + 1)]:   # -1: no shape stage
                    for fallback in ("best", "fail"):
                        err, sec, _ = simulate(arr, stages, thresholds, shape_at, fallback)
                        mean, aucs, s = score(base, err, sec, tune)
                        rows.append(dict(stages=stages, thresholds=thresholds, shape_at=shape_at,
                                         fallback=fallback, tune_auc10=mean, tune_sec=s,
                                         **{f"tune_{d}": v for d, v in aucs.items()}))
    search = pd.DataFrame(rows)
    out = ROOT / "results" / "cascade"
    out.mkdir(parents=True, exist_ok=True)
    search.assign(design=search.apply(describe, axis=1)).drop(columns=["stages", "thresholds", "shape_at"]) \
        .sort_values("tune_auc10", ascending=False).to_csv(out / "search.csv", index=False)

    lines = ["# Cascade design: chosen on the tuning split, scored on the test split", "",
             f"{len(search)} designs searched on {tune.sum()} tuning pairs; "
             f"scored on {test.sum()} test pairs. AUC@10 in %, failures count as infinite error.", "",
             "| design (budget) | tune mean AUC@10 | " + " | ".join(f"test {d}" for d in DATASETS) + " | test mean | test s/pair |",
             "|---" * (len(DATASETS) + 4) + "|"]
    chosen = {}
    for budget in BUDGETS:
        ok = search[search.tune_sec <= budget]
        c = ok.loc[ok.tune_auc10.idxmax()].to_dict()
        err, sec, used = simulate(arr, c["stages"], c["thresholds"], int(c["shape_at"]), c["fallback"])
        mean, aucs, s = score(base, err, sec, test)
        chosen[budget] = (c, used)
        label = "no limit" if np.isinf(budget) else f"<= {budget:g} s"
        lines.append(f"| {describe(c)} ({label}) | {c['tune_auc10']:.1f} | "
                     + " | ".join(f"{aucs[d]:.1f}" for d in DATASETS) + f" | {mean:.1f} | {s:.2f} |")

    lines += ["", "Single methods on the same test pairs:", "",
              "| method | " + " | ".join(f"test {d}" for d in DATASETS) + " | test mean | test s/pair |",
              "|---" * (len(DATASETS) + 3) + "|"]
    for m in MATCHERS + ["shape"]:
        mean, aucs, s = score(base, arr[m]["err"], arr[m]["sec"], test)
        lines.append(f"| {m} | " + " | ".join(f"{aucs[d]:.1f}" for d in DATASETS) + f" | {mean:.1f} | {s:.2f} |")

    lines += ["", "Per object, test split (AUC@10):", ""]
    objects = list(dict.fromkeys(base.object))
    lines += ["| design | " + " | ".join(objects) + " |", "|---" * (len(objects) + 1) + "|"]
    for budget, (c, _) in chosen.items():
        err, _, _ = simulate(arr, c["stages"], c["thresholds"], int(c["shape_at"]), c["fallback"])
        vals = [pose_auc(err[test & (base.object == o).to_numpy()])[10] for o in objects]
        label = "no limit" if np.isinf(budget) else f"<= {budget:g} s"
        lines.append(f"| cascade {label} | " + " | ".join(f"{v:.1f}" for v in vals) + " |")
    for m in ("aliked_lg", "loftr"):
        vals = [pose_auc(arr[m]["err"][test & (base.object == o).to_numpy()])[10] for o in objects]
        lines.append(f"| {m} alone | " + " | ".join(f"{v:.1f}" for v in vals) + " |")

    lines += ["", "Which stage answered (test split, cascade <= 1 s):", ""]
    used = chosen[1.0][1][test]
    for name, count in pd.Series(used).value_counts().items():
        lines.append(f"- {name}: {count} pairs ({100 * count / len(used):.0f}%)")

    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
