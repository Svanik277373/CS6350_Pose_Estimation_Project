"""Learned confidence: decide per pair whether a pose can be trusted or a slower method is needed.

    venv\\Scripts\\python.exe scripts\\confidence.py

Phase 6 showed the inlier-count rule accepts many wrong poses (17% of test poses accepted
while > 20 deg off). This script replaces it with a small classifier that predicts
P(pose error < 10 deg) from evidence available at run time -- no ground truth:

    per stage:   succeeded?, log #matches, log #inliers, inlier ratio, reprojection RMS,
                 GRIC preference H vs E per match, planar model chosen?
    agreement:   rotation / translation-direction angle between this stage's pose and each
                 earlier stage's pose (two independent methods agreeing is strong evidence)

Policy (a cascade): run the stages in order; accept stage k's pose as soon as its predicted
confidence >= tau. If no stage is confident, the final stage answers: MASt3R (slow, strongest)
when it is in the design, otherwise the most confident pose so far.

Honesty rules, as everywhere in this project:
  * classifiers are trained on "tune" pairs only, with out-of-fold predictions (folds grouped by
    sequence) used to choose tau, so tau is not fitted to the classifier's own training data;
  * designs are ranked on tune; the chosen ones are scored once on "test" pairs.
  * MASt3R was trained on CO3Dv2, so its CO3D numbers may be optimistic (Objectron, TUM and
    MVImgNet are not in its training data).

Inputs: per-pair results of scripts/evaluate.py (with pose columns rx..tz). Writes
results/confidence/{search.csv, summary.md} and, for run time (src/pipeline/cascade.py preset
"confident"), models/confidence/<budget>.pkl: the chosen design and, per stage, the classifier
fitted on all tune pairs -- the same model that produced the test scores.
"""
import itertools
import pickle
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.loaders import split_of  # noqa: E402
from src.pipeline.metrics import pose_auc  # noqa: E402

RUNS = {   # method -> results folders with its per-pair results (all on the same pairs)
    "sift": ["sift_ref"], "xfeat_lg": ["xfeat_lg_ref"], "aliked_lg": ["aliked_lg_ref"],
    "disk_lg": ["disk_lg_ref"], "loftr": ["loftr_ref"], "shape": ["shape_ref"],
    "mast3r": ["mast3r_crop", "mast3r_mvimgnet"],
}
CHEAP = ["sift", "xfeat_lg", "aliked_lg", "disk_lg", "loftr", "shape"]
FINAL = "mast3r"
GOOD_DEG = 10.0
TAUS = np.round(np.arange(0.3, 0.96, 0.05), 2)
BUDGETS = [1.0, 3.0, 8.0, np.inf]           # mean seconds per pair
DATASETS = ["tum", "objectron", "co3d", "mvimgnet"]
FOLDS = 5


def load():
    frames = {}
    for method, folders in RUNS.items():
        parts = [pd.read_csv(ROOT / "results" / f / "pairs.csv") for f in folders
                 if (ROOT / "results" / f / "pairs.csv").exists()]
        frames[method] = pd.concat(parts).drop_duplicates("pair").set_index("pair")
    pairs = frames["sift"].index
    base = frames["sift"][["dataset", "object"]].copy()
    base["split"] = [split_of(p) for p in pairs]
    base["group"] = ["/".join(p.split("/")[:3]) if not p.startswith("tum/") else p.split("/")[1] for p in pairs]
    runs = {m: d.reindex(pairs) for m, d in frames.items()}
    return base, runs


def poses(d):
    """Rotation matrices and unit translations (NaN where the method failed)."""
    rv = d[["rx", "ry", "rz"]].to_numpy(float) if "rx" in d else np.full((len(d), 3), np.nan)
    tv = d[["tx", "ty", "tz"]].to_numpy(float) if "tx" in d else np.full((len(d), 3), np.nan)
    R = np.full((len(d), 3, 3), np.nan)
    for i, r in enumerate(rv):
        if np.isfinite(r).all():
            R[i] = cv2.Rodrigues(r)[0]
    return R, tv / np.linalg.norm(tv, axis=1, keepdims=True)


def agreement(Ra, ta, Rb, tb):
    """Per pair: max(rotation difference, translation-direction difference) in degrees."""
    cos_r = (np.einsum("nij,nij->n", Ra, Rb) - 1) / 2
    rot = np.degrees(np.arccos(np.clip(cos_r, -1, 1)))
    tra = np.degrees(np.arccos(np.clip(np.einsum("ni,ni->n", ta, tb), -1, 1)))
    return np.fmax(rot, tra)    # NaN only if either is missing


def stage_features(d):
    ok = d.ok.fillna(False).to_numpy(float)
    matches, inliers = d.matches.fillna(0).to_numpy(float), d.inliers.fillna(0).to_numpy(float)
    gh, ge = d.get("gric_H", pd.Series(np.nan, d.index)).to_numpy(float), \
        d.get("gric_E", pd.Series(np.nan, d.index)).to_numpy(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.column_stack([
            ok, np.log1p(matches), np.log1p(inliers), inliers / np.maximum(matches, 1),
            np.where(ok > 0, d.reproj_rms_px.to_numpy(float), np.nan),
            (ge - gh) / np.maximum(matches, 1), (d.model == "H").to_numpy(float),
        ])


class Data:
    def __init__(self, base, runs):
        self.base, self.n = base, len(base)
        self.err = {m: d.pose_err_deg.fillna(np.inf).to_numpy(float) for m, d in runs.items()}
        self.ok = {m: d.ok.fillna(False).to_numpy(bool) for m, d in runs.items()}
        self.sec = {m: d.seconds.fillna(0).to_numpy(float) for m, d in runs.items()}
        self.feat = {m: stage_features(d) for m, d in runs.items()}
        self.pose = {m: poses(d) for m, d in runs.items()}
        self.tune = (base.split == "tune").to_numpy()
        self.groups = base.group.to_numpy()

    def features(self, order, k):
        """Features for trusting stage order[k], given stages order[:k] already ran."""
        m = order[k]
        cols = [self.feat[m]]
        if k:
            agr = np.column_stack([agreement(*self.pose[m], *self.pose[p]) for p in order[:k]])
            agr = np.where(np.isnan(agr), 180.0, agr)
            cols += [agr.min(axis=1, keepdims=True), np.median(agr, axis=1, keepdims=True)]
        return np.column_stack(cols)


def classifier():
    return HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=150,
                                          min_samples_leaf=15, l2_regularization=1.0, random_state=0)


_cache = {}
_models = {}   # stage prefix -> (kept feature columns, classifier fitted on all tune pairs | constant)


def confidence(data, order, k):
    """P(stage order[k] is within GOOD_DEG): out-of-fold on tune pairs, fitted-on-tune for test."""
    key = (tuple(order[:k + 1]))
    if key in _cache:
        return _cache[key]
    X, y = data.features(order, k), data.err[order[k]] < GOOD_DEG
    p = np.zeros(data.n)
    tune = np.flatnonzero(data.tune)
    keep = ~np.isnan(X[tune]).all(axis=0)        # e.g. GRIC columns of the shape method
    X = X[:, keep]
    if y[tune].all() or not y[tune].any():
        p[:] = y[tune].mean()
        _models[key] = (keep, float(y[tune].mean()))
    else:
        for tr, va in GroupKFold(FOLDS).split(tune, groups=data.groups[tune]):
            tr, va = tune[tr], tune[va]
            if y[tr].all() or not y[tr].any():
                p[va] = y[tr].mean()
                continue
            p[va] = classifier().fit(X[tr], y[tr]).predict_proba(X[va])[:, 1]
        test = np.flatnonzero(~data.tune)
        clf = classifier().fit(X[tune], y[tune])
        p[test] = clf.predict_proba(X[test])[:, 1]
        _models[key] = (keep, clf)
    p[~data.ok[order[k]]] = 0.0
    _cache[key] = p
    return p


def simulate(data, order, tau, final):
    """Per-pair error, seconds and answering stage for one design."""
    n = data.n
    err, sec = np.full(n, np.inf), np.zeros(n)
    used = np.full(n, "fail", dtype=object)
    done = np.zeros(n, bool)
    best_p, best_err, best_m = np.full(n, -1.0), np.full(n, np.inf), np.full(n, "fail", dtype=object)
    for k, m in enumerate(order):
        todo = ~done
        sec[todo] += data.sec[m][todo]
        p = confidence(data, order, k)
        better = todo & data.ok[m] & (p > best_p)
        best_p[better], best_err[better], best_m[better] = p[better], data.err[m][better], m
        take = todo & (p >= tau)
        err[take], used[take] = data.err[m][take], m
        done |= take
    rest = ~done
    if final:
        sec[rest] += data.sec[final][rest]
        fin = rest & data.ok[final]
        err[fin], used[fin] = data.err[final][fin], final
        rest = rest & ~data.ok[final]
    err[rest], used[rest] = best_err[rest], best_m[rest]
    return err, sec, used


def score(data, err, sec, mask):
    aucs = {d: pose_auc(err[mask & (data.base.dataset == d).to_numpy()])[10] for d in DATASETS}
    return float(np.mean(list(aucs.values()))), aucs, float(sec[mask].mean())


def describe(order, tau, final):
    return " -> ".join(order) + f" (conf >= {tau:g})" + (f" -> {final}" if final else " -> most confident")


def main():
    base, runs = load()
    data = Data(base, runs)
    rows = []
    for k in (1, 2, 3):
        for order in itertools.permutations(CHEAP, k):
            for final in (FINAL, None):
                for tau in TAUS:
                    err, sec, _ = simulate(data, list(order), tau, final)
                    mean, aucs, s = score(data, err, sec, data.tune)
                    rows.append(dict(order=order, tau=tau, final=final or "", tune_auc10=mean, tune_sec=s,
                                     **{f"tune_{d}": v for d, v in aucs.items()}))
    search = pd.DataFrame(rows)
    out = ROOT / "results" / "confidence"
    out.mkdir(parents=True, exist_ok=True)
    search.assign(design=[describe(list(r.order), r.tau, r.final) for r in search.itertuples()]) \
        .drop(columns=["order"]).sort_values("tune_auc10", ascending=False).to_csv(out / "search.csv", index=False)

    test = ~data.tune
    header = "| design (budget) | tune mean | " + " | ".join(f"test {d}" for d in DATASETS) + " | test mean | test s/pair |"
    lines = ["# Confidence-gated cascade: chosen on the tuning split, scored on the test split", "",
             f"{len(search)} designs searched on {data.tune.sum()} tuning pairs; scored on {test.sum()} test pairs.",
             f"Confidence = P(pose error < {GOOD_DEG:g} deg) from a gradient-boosted classifier "
             "(out-of-fold on tune). AUC@10 in %, failures count as infinite error.", "",
             header, "|---" * (len(DATASETS) + 4) + "|"]
    chosen = {}
    for budget in BUDGETS:
        ok = search[search.tune_sec <= budget]
        if ok.empty:
            continue
        c = ok.loc[ok.tune_auc10.idxmax()]
        order, final = list(c.order), c.final or None
        err, sec, used = simulate(data, order, c.tau, final)
        mean, aucs, s = score(data, err, sec, test)
        label = "no limit" if np.isinf(budget) else f"<= {budget:g} s"
        chosen[label] = (order, c.tau, final, err, used)
        lines.append(f"| {describe(order, c.tau, final)} ({label}) | {c.tune_auc10:.1f} | "
                     + " | ".join(f"{aucs[d]:.1f}" for d in DATASETS) + f" | {mean:.1f} | {s:.2f} |")

    lines += ["", "Single methods on the same test pairs:", "",
              "| method | " + " | ".join(DATASETS) + " | mean | s/pair |", "|---" * (len(DATASETS) + 3) + "|"]
    for m in CHEAP + [FINAL]:
        mean, aucs, s = score(data, data.err[m], data.sec[m], test)
        lines.append(f"| {m} | " + " | ".join(f"{aucs[d]:.1f}" for d in DATASETS) + f" | {mean:.1f} | {s:.2f} |")

    objects = list(dict.fromkeys(base.object))
    lines += ["", "Per object, test split (AUC@10):", "",
              "| design | " + " | ".join(objects) + " |", "|---" * (len(objects) + 1) + "|"]
    for label, (_, _, _, err, _) in chosen.items():
        vals = [pose_auc(err[test & (base.object == o).to_numpy()])[10] for o in objects]
        lines.append(f"| {label} | " + " | ".join(f"{v:.1f}" for v in vals) + " |")
    for m in ("aliked_lg", FINAL):
        vals = [pose_auc(data.err[m][test & (base.object == o).to_numpy()])[10] for o in objects]
        lines.append(f"| {m} alone | " + " | ".join(f"{v:.1f}" for v in vals) + " |")

    lines += ["", "Accepted-but-wrong poses (> 20 deg off), test split:", ""]
    for label, (_, _, _, err, used) in chosen.items():
        bad = np.isfinite(err) & (err > 20) & test
        lines.append(f"- {label}: {bad.sum()} of {test.sum()} ({100 * bad.sum() / test.sum():.0f}%); "
                     "answered by " + ", ".join(f"{k} {v}" for k, v in pd.Series(used[test]).value_counts().items()))

    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    save_models(chosen)
    save_pairs(chosen, base, runs, data)


def save_pairs(chosen, base, runs, data):
    """Per chosen design, a pairs.csv like scripts/evaluate.py writes (read by scripts/report.py):
    the answering method's row, with the design's total seconds. src/pipeline/cascade.py
    reproduces these decisions at run time (checked pair by pair)."""
    cols = ["ok", "model", "matches", "inliers", "rot_err_deg", "t_err_deg", "reproj_rms_px"]
    for label, (order, tau, final, err, used) in chosen.items():
        _, sec, _ = simulate(data, order, tau, final)
        name = "unlimited" if label == "no limit" else "budget_" + label.replace("<= ", "").replace(" s", "s")
        d = base[["dataset", "object", "split"]].copy()
        for c in cols:
            d[c] = [runs[m].iloc[i][c] if m in runs else np.nan for i, m in enumerate(used)]
        d["ok"] = d.ok.fillna(False).astype(bool)
        d["pose_err_deg"], d["seconds"], d["answered_by"] = err, sec, used
        d.rename_axis("pair").reset_index().to_csv(ROOT / "results" / "confidence" / f"pairs_{name}.csv", index=False)


def save_models(chosen):
    """Per chosen design: what src/pipeline/cascade.py needs to run it on new images."""
    folder = ROOT / "models" / "confidence"
    folder.mkdir(parents=True, exist_ok=True)
    index = []
    for label, (order, tau, final, _, _) in chosen.items():
        stages = [_models[tuple(order[:k + 1])] for k in range(len(order))]
        name = "unlimited" if label == "no limit" else "budget_" + label.replace("<= ", "").replace(" s", "s")
        with open(folder / f"{name}.pkl", "wb") as f:
            pickle.dump(dict(order=order, tau=float(tau), final=final, good_deg=GOOD_DEG,
                             stages=[dict(keep=k, model=m) for k, m in stages]), f)
        index.append(f"{name}: {describe(order, tau, final)}")
    (folder / "designs.txt").write_text("\n".join(index) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
