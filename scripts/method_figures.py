"""Method comparison figure: one example per method where THAT method beats all the others,
with every method's result shown for each example. Two images only (MASt3R focal, region2).

    venv\\Scripts\\python.exe scripts\\method_figures.py

1. Shortlist: on the 751 benchmark test pairs (all six methods were run there, with dataset K
   and masks), rank pairs by how clearly each method beats the best of the others.
2. Confirm: run all six methods on the shortlisted pairs with only the two images; keep the first
   pair where the method still wins (error <= 5 deg and the best other method at least
   max(2x, +3 deg) worse). Runs are cached in results/cases/method_runs.json.
3. Draw: rows = winning examples, columns = SIFT, XFeat+LightGlue, LoFTR, MASt3R, accurate,
   confident; inlier lines, errors, the winner's panel framed in green.
Writes report/final/figures/methods.png and results/cases/methods.json. New file only.
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import auto_eval as AE  # noqa: E402,F401  (its match memo: methods share matches within a pair)
from report_figures import pair_from_name, side  # noqa: E402
from src.pipeline import (estimate_pose, estimate_pose_cascade, estimate_pose_confident, region2,  # noqa: E402
                          rotation_error_deg, translation_angle_deg)
from src.pipeline.focal import K_from_focal, auto_focals  # noqa: E402

METHODS = [("SIFT", "sift"), ("XFeat+LightGlue", "xfeat_lg"), ("LoFTR", "loftr"), ("MASt3R", "mast3r"),
           ("accurate", "accurate"), ("confident", "confident")]
BENCH = {"sift": "sift_ref/pairs.csv", "xfeat_lg": "xfeat_lg_ref/pairs.csv", "loftr": "loftr_ref/pairs.csv",
         "mast3r": "mast3r_crop/pairs.csv", "accurate": "cascade_accurate_ref/pairs.csv",
         "confident": "confidence/pairs_budget_8s.csv"}
ORDER = ["mast3r", "confident", "accurate", "sift", "xfeat_lg", "loftr"]   # rows, in this order
TRIES = 4
PRESETS = ("accurate", "confident")
CACHE = ROOT / "results" / "cases" / "method_runs.json"


def shortlist():
    errs = {}
    for k, f in BENCH.items():
        d = pd.read_csv(ROOT / "results" / f)
        d = d[d.split == "test"] if "split" in d else d
        errs[k] = d.set_index("pair").pose_err_deg.replace([np.nan], np.inf)
    E = pd.DataFrame(errs).dropna()
    out = {}
    for k in ORDER:
        rest = E.drop(columns=k)
        same = (rest.sub(E[k], axis=0)).abs() <= 0.05
        # a preset returns one stage's answer: ignore methods whose answer it copied (or that copied it)
        copy = same if k in PRESETS else same & pd.DataFrame({c: c in PRESETS for c in rest.columns}, index=rest.index)
        rest = rest.where(~copy)
        others = rest.min(axis=1)          # NaN where every other method agrees: not a win
        ok = (E[k] <= 3) & (others >= np.maximum(2 * E[k], E[k] + 3))
        margin = (others - E[k])[ok].sort_values(ascending=False)
        out[k] = list(margin.index[:TRIES])
    return out


def run_all(name, cache):
    if name in cache:
        # earlier runs retried a failed preset with MASt3R instead of the same preset on the whole
        # images (as auto_run does); those entries have an empty reason -- recompute them
        bad = [k for k in PRESETS if not cache[name][k]["reason"]]
        if not bad:
            return cache[name]
        todo = bad
    else:
        todo = [key for _, key in METHODS]
    pair = pair_from_name(name)
    img1, img2, _, _ = pair.load()
    if name in EST_F:      # the focal auto_eval estimated for this pair (same computation, saved)
        f1 = f2 = EST_F[name]
    else:
        f1, f2, _ = auto_focals(None, img1, None, img2)
    K1, K2 = K_from_focal(f1, img1.shape), K_from_focal(f2, img2.shape)
    m1, m2, note, mode = region2.find_regions(img1, img2)
    AE._memo.clear()
    res_all = cache.get(name, {}) | {"angle": pair.angle_deg, "region": mode,
                                     "f_err_pct": 100 * (f1 - pair.frame1.K[0, 0]) / pair.frame1.K[0, 0]}

    def solve(key, a, b):
        if key == "accurate":
            return estimate_pose_cascade(img1, img2, K1, K2, a, b, preset="accurate")
        if key == "confident":
            return estimate_pose_confident(img1, img2, K1, K2, a, b, preset="confident")
        return estimate_pose(img1, img2, K1, K2, a, b, matcher=key, crop=a is not None)
    for key in todo:
        res = solve(key, m1, m2)
        if not res.ok and m1 is not None:       # auto_run.py: same method, whole images
            res = solve(key, None, None)
            if key in PRESETS and not res.reason:
                res.reason = f"{key}: whole images"
        rot = rotation_error_deg(res.R, pair.R_gt) if res.ok else float("inf")
        tra = translation_angle_deg(res.t, pair.t_gt) if res.ok else float("inf")
        res_all[key] = dict(ok=bool(res.ok), inliers=int(res.n_inliers), matches=int(res.n_matches), model=res.model,
                            rot=float(rot), tra=float(tra), err=float(max(rot, tra) if np.isfinite(tra) else rot),
                            reproj=float(res.reproj_rms_px), reason=res.reason or "",
                            p1=res.pts1[::max(1, len(res.pts1) // 80)].tolist() if res.ok else [],
                            p2=res.pts2[::max(1, len(res.pts2) // 80)].tolist() if res.ok else [])
    cache[name] = res_all
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, default=float))
    print(name, {k: round(v["err"], 2) for k, v in res_all.items() if isinstance(v, dict)}, flush=True)
    return res_all


def _others(r, k):
    """Errors of the methods k competes with: a preset returns one stage's answer, so a preset is
    compared only with methods that answered differently, and a matcher ignores a preset that
    copied its answer; matchers always compete with each other."""
    own = r[k]["err"]
    out = []
    for _, o in METHODS:
        if o == k:
            continue
        same = abs(r[o]["rot"] - r[k]["rot"]) < 0.01 and (abs(r[o]["tra"] - r[k]["tra"]) < 0.01
                                                             or not np.isfinite(r[o]["tra"] + r[k]["tra"]))
        copied = same and (k in PRESETS or o in PRESETS)
        if not copied:
            out.append(r[o]["err"])
    return out


def wins(r, k):
    own = r[k]["err"]
    others = _others(r, k)
    if not others:       # every method agrees: nobody wins
        return False
    best_other = min(others, default=float("inf"))
    return own <= 5 and best_other >= max(2 * own, own + 3)


def main():
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    # all six methods on the 56 two-image test pairs (also a results table for the report)
    for name in EVAL_PAIRS:
        run_all(name, cache)
    tab = [dict(pair=n, method=key, **{c: cache[n][key][c] for c in ("ok", "rot", "tra", "err", "reproj", "inliers")})
           for n in EVAL_PAIRS for _, key in METHODS]
    pd.DataFrame(tab).to_csv(ROOT / "results" / "cases" / "methods_all56.csv", index=False)

    def margin(r, k):
        return min(_others(r, k), default=0) - r[k]["err"]
    cand = shortlist()
    rows = []
    for k in ORDER:
        eval_wins = sorted((n for n in EVAL_PAIRS if wins(cache[n], k)), key=lambda n: -margin(cache[n], k))
        for name in eval_wins + cand[k]:
            if any(name == n for _, n, _ in rows):
                continue
            r = run_all(name, cache)
            if wins(r, k):
                rows.append((k, name, r))
                print(f"example for {k}: {name}", flush=True)
                break
        else:
            print(f"no confirmed example for {k} among {cand[k]}", flush=True)

    fig, ax = plt.subplots(len(rows), len(METHODS), figsize=(22, 3.3 * len(rows)), squeeze=False)
    for i, (k, name, r) in enumerate(rows):
        pair = pair_from_name(name)
        img1, img2, _, _ = pair.load()
        im, off = side(img1, img2)
        for j, (title, key) in enumerate(METHODS):
            a, res = ax[i, j], r[key]
            a.imshow(im)
            a.set_xticks([])
            a.set_yticks([])
            for u, w in zip(res["p1"], res["p2"]):
                a.plot([u[0], w[0] + off], [u[1], w[1]], "-", lw=0.6,
                       color="#2ca02c" if res["rot"] < 5 else "#d62728", alpha=0.8)
            win = key == k
            for s in a.spines.values():
                s.set_edgecolor("#2ca02c" if win else "#cccccc")
                s.set_linewidth(4 if win else 0.8)
            head = f"{title}" + ("  (best)" if win else "")
            a.set_title(head, fontsize=10, fontweight="bold" if win else "normal")
            txt = (f"rot {res['rot']:.2f}°  t {res['tra']:.1f}°\n{res['inliers']} inl, {res['model'] or '-'}, "
                   f"{res['reproj']:.2f} px" if res["ok"] else f"failed")
            a.text(0.01, -0.03, txt, transform=a.transAxes, va="top", fontsize=8.5, family="monospace")
            if j == 0:
                a.set_ylabel(f"{dict(METHODS_INV)[k]} wins\n{name}\n{r['angle']:.0f}°, region {r['region']}",
                             fontsize=9)
    fig.tight_layout()
    out = ROOT / "report" / "final" / "figures"
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "methods.png", dpi=120, bbox_inches="tight", facecolor="white")
    summary = [dict(winner=k, pair=n, angle=r["angle"], region=r["region"],
                    errors={key: dict(rot=r[key]["rot"], t=r[key]["tra"], reproj=r[key]["reproj"],
                                      inliers=r[key]["inliers"], answered_by=r[key]["reason"])
                            for _, key in METHODS}) for k, n, r in rows]
    (ROOT / "results" / "cases" / "methods.json").write_text(json.dumps(summary, indent=2, default=float))
    print("written", out / "methods.png", flush=True)


METHODS_INV = [(k, t) for t, k in METHODS]
_EV = pd.read_csv(ROOT / "results" / "auto_eval" / "pairs_v2.csv")
_EV = _EV[(_EV.method == "mast3r") & (_EV.group != "tiny")]   # consecutive frames: translation unobservable, no winners
EST_F = dict(zip(_EV.pair, _EV.est_f))
EVAL_PAIRS = list(_EV.pair)

if __name__ == "__main__":
    main()
