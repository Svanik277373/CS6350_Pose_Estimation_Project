"""Phase 8: how sensitive is the pose to errors in the camera intrinsics K?

    venv\\Scripts\\python.exe scripts\\sensitivity.py [--matchers xfeat_lg aliked_lg]

The pipeline assumes K is known. In practice K comes from a calibration (our Zhang
calibration of a webcam: focal within ~2% of the reference, bootstrap spread ~6%), or from
metadata. This experiment feeds the *same* matches (scripts/matchcache.py) through the
geometry with a deliberately wrong K and measures what the error costs:

    focal length   f -> f * (1 + e),   e in {-10, -5, -2, 0, +2, +5, +10} %
    principal pt   (cx, cy) -> (cx + e*W, cy + e*H),  e in {2, 5, 10} %  (worst case: both axes)

The same wrong K is used for both views (one miscalibrated camera). Only test-split pairs.
Writes results/sensitivity/{summary.md, sensitivity.csv, focal.png}.
"""
import argparse
import sys
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
from src.pipeline import pose_from_matches, rotation_error_deg, translation_angle_deg  # noqa: E402
from src.pipeline.metrics import pose_auc  # noqa: E402

PER_BIN = {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}   # as scripts/evaluate.py
SEED = 0
FOCAL = [-10, -5, -2, 0, 2, 5, 10]
CENTRE = [2, 5, 10]
OUT = ROOT / "results" / "sensitivity"


def perturb(K, shape, focal=0.0, centre=0.0):
    K = K.copy()
    K[0, 0] *= 1 + focal / 100
    K[1, 1] *= 1 + focal / 100
    h, w = shape
    K[0, 2] += centre / 100 * w
    K[1, 2] += centre / 100 * h
    return K


def errors(res, pair):
    if not res.ok:
        return np.inf, np.inf, np.inf
    rot = rotation_error_deg(res.R, pair.R_gt)
    tra = translation_angle_deg(res.t, pair.t_gt)
    return rot, tra, rot if np.isnan(tra) else max(rot, tra)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matchers", nargs="+", default=["xfeat_lg", "aliked_lg"])
    ap.add_argument("--datasets", nargs="+", default=list(LOADERS))
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    settings = [("focal", e) for e in FOCAL] + [("centre", e) for e in CENTRE]
    rows = []
    for ds in args.datasets:
        pairs = [p for p in LOADERS[ds].load_pairs(per_bin=PER_BIN[ds], seed=SEED) if split_of(p.name) == "test"]
        for pair in tqdm(pairs, desc=ds):
            images = None
            shape = None
            for matcher in args.matchers:
                try:
                    p1, p2, scale = cached_matches(matcher, pair, crop=True, images=images)
                except Exception:   # not cached yet: load once, share between matchers
                    images = pair.load()
                    p1, p2, scale = cached_matches(matcher, pair, crop=True, images=images)
                if shape is None:
                    shape = (images[0] if images is not None else pair.frame1.load_image()).shape[:2]
                for kind, e in settings:
                    K1 = perturb(pair.frame1.K, shape, **{kind: e})
                    K2 = perturb(pair.frame2.K, shape, **{kind: e})
                    res = pose_from_matches(p1, p2, scale, K1, K2)
                    rot, tra, pose = errors(res, pair)
                    rows.append(dict(dataset=ds, object=pair.sequence.split("/")[0], pair=pair.name, matcher=matcher,
                                     kind=kind, error_pct=e, ok=res.ok, rot_err_deg=rot, t_err_deg=tra,
                                     pose_err_deg=pose))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "sensitivity.csv", index=False)

    def stats(g):
        ok = g[np.isfinite(g.pose_err_deg)]
        auc = pose_auc(g.pose_err_deg.to_numpy())
        return pd.Series(dict(pairs=len(g), auc5=auc[5], auc10=auc[10], auc20=auc[20],
                              med_rot=ok.rot_err_deg.median(), med_t=ok.t_err_deg.median()))

    lines = ["# Sensitivity of the pose to errors in K (test split)", "",
             "Same matches for every setting; only K changes. AUC in %, failures count as infinite error.", ""]
    for matcher in args.matchers:
        d = df[df.matcher == matcher]
        lines += [f"## {matcher}", "", "| K error | " + " | ".join(f"{ds} AUC@10" for ds in args.datasets)
                  + " | mean AUC@10 | median rot (deg) | median t-dir (deg) |", "|---" * (len(args.datasets) + 4) + "|"]
        for kind, e in settings:
            s = d[(d.kind == kind) & (d.error_pct == e)]
            per = [stats(s[s.dataset == ds]).auc10 for ds in args.datasets]
            st = stats(s)
            label = f"focal {e:+d}%" if kind == "focal" else f"centre +{e}% (x and y)"
            lines.append(f"| {label} | " + " | ".join(f"{v:.1f}" for v in per)
                         + f" | {np.mean(per):.1f} | {st.med_rot:.2f} | {st.med_t:.2f} |")
        lines.append("")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

    fig, ax = plt.subplots(figsize=(6, 4))
    for matcher in args.matchers:
        d = df[(df.matcher == matcher) & (df.kind == "focal")]
        ys = [np.mean([stats(d[(d.error_pct == e) & (d.dataset == ds)]).auc10 for ds in args.datasets]) for e in FOCAL]
        ax.plot(FOCAL, ys, marker="o", linewidth=2, label=matcher)
    ax.set_xlabel("focal length error (%)")
    ax.set_ylabel("mean AUC@10 (%)")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "focal.png", dpi=150)


if __name__ == "__main__":
    main()
