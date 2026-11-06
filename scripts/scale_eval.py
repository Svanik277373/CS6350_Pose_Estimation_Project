"""Phase 7: how well can the translation's length (metres) be recovered?

    venv\\Scripts\\python.exe scripts\\scale_eval.py [--mast3r-pairs 30]

Only datasets with metric ground truth: TUM (motion capture) and Objectron (ARKit). Test split.

  size prior   pose from ALIKED+LightGlue (cached matches), scale from the object's longest
               dimension. Objectron's annotated 3D box gives that dimension, standing in for a
               size the user types in (e.g. a phone's length); TUM has no object size.
  MASt3R depth pose and metric depth from MASt3R (src/pipeline/scale.py), raw and corrected
               for the focal length MASt3R implicitly assumed. Expensive on CPU, so a
               random subset of pairs per dataset.

Error = |t_est| / |t_gt| (1 = perfect). Reported: median of |log ratio| as a percentage,
and share of pairs within 10% / 25% / factor 2. Writes results/scale/{summary.md, scale.csv}.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from matchcache import cached_matches  # noqa: E402
from src.loaders import LOADERS, split_of  # noqa: E402
from src.pipeline import estimate_pose, pose_from_matches, rotation_error_deg  # noqa: E402
from src.pipeline.scale import depth_scale, mast3r_depth_at, mast3r_metric_depth_at, size_scale  # noqa: E402

PER_BIN = {"tum": 20, "objectron": 3}
SEED = 0
OUT = ROOT / "results" / "scale"


def ratio_stats(r):
    r = np.asarray(r, float)
    ok = np.isfinite(r) & (r > 0)
    lr = np.abs(np.log(r[ok]))
    return dict(pairs=len(r), solved=ok.mean(), median_err_pct=100 * (np.exp(np.median(lr)) - 1) if ok.any() else np.nan,
                within10=np.mean(np.where(ok, np.abs(np.log(np.where(ok, r, 1))) < np.log(1.10), False)),
                within25=np.mean(np.where(ok, np.abs(np.log(np.where(ok, r, 1))) < np.log(1.25), False)),
                within2x=np.mean(np.where(ok, np.abs(np.log(np.where(ok, r, 1))) < np.log(2.0), False)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matcher", default="aliked_lg")
    ap.add_argument("--mast3r-pairs", type=int, default=30, help="per dataset (0 = skip MASt3R)")
    ap.add_argument("--from-csv", action="store_true", help="only rebuild summary.md from scale.csv")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.from_csv:
        return summarise(pd.read_csv(OUT / "scale.csv"))
    rng = np.random.default_rng(SEED)
    rows = []
    for ds in PER_BIN:
        pairs = [p for p in LOADERS[ds].load_pairs(per_bin=PER_BIN[ds], seed=SEED) if split_of(p.name) == "test"]
        subset = set(rng.choice(len(pairs), size=min(args.mast3r_pairs, len(pairs)), replace=False).tolist())
        for k, pair in enumerate(tqdm(pairs, desc=ds)):
            gt = np.linalg.norm(pair.t_gt)
            K1, K2 = pair.frame1.K, pair.frame2.K
            base = dict(dataset=ds, object=pair.sequence.split("/")[0], pair=pair.name, t_gt_m=gt)
            if "box_size_m" in pair.frame1.extra:
                p1, p2, scale = cached_matches(args.matcher, pair, crop=True)
                res = pose_from_matches(p1, p2, scale, K1, K2)
                mask1 = pair.frame1.load_mask()
                size = pair.frame1.extra["box_size_m"][0]
                rot = rotation_error_deg(res.R, pair.R_gt) if res.ok else np.inf
                for name, m in [("size prior (mask outline)", mask1), ("size prior (matched points)", None)]:
                    s = size_scale(res.R, res.t, K1, K2, res.pts1, res.pts2, size, mask1=m)[0] if res.ok else np.nan
                    rows.append(base | dict(method=name, rot_err_deg=rot, t_est_m=s, ratio=s / gt))
            if k in subset:
                img1, img2, m1, m2 = pair.load()
                res = estimate_pose(img1, img2, K1, K2, m1, m2, matcher="mast3r", crop=True)
                rot = rotation_error_deg(res.R, pair.R_gt) if res.ok else np.inf
                for name, depth in [("MASt3R depth (raw)", lambda: mast3r_depth_at(res.pts1)[0]),
                                    ("MASt3R depth (focal-corrected)", lambda: mast3r_metric_depth_at(res.pts1, K1)[0])]:
                    s = depth_scale(res.R, res.t, K1, K2, res.pts1, res.pts2, depth())[0] if res.ok else np.nan
                    rows.append(base | dict(method=name, rot_err_deg=rot, t_est_m=s, ratio=s / gt))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "scale.csv", index=False)
    summarise(df)


def summarise(df):
    lines = ["# Metric scale: length of the translation (test split, metric datasets)", "",
             "ratio = estimated |t| / true |t|. 'median error' = typical factor off, as a percentage.", "",
             "| method | dataset | pairs | median error | within 10% | within 25% | within 2x |", "|---|---|---|---|---|---|---|"]
    for (m, ds), g in df.groupby(["method", "dataset"], sort=False):
        st = ratio_stats(g.ratio)
        lines.append(f"| {m} | {ds} | {st['pairs']} | {st['median_err_pct']:.1f}% | {100 * st['within10']:.0f}% | "
                     f"{100 * st['within25']:.0f}% | {100 * st['within2x']:.0f}% |")
    lines += ["", "Size prior per object (Objectron). Median ratio > 1: scale too large (extent measured too short).", "",
              "| method | object | pairs | median ratio | median error | within 10% | within 25% |",
              "|---|---|---|---|---|---|---|"]
    for (m, o), g in df[df.method.str.startswith("size prior")].groupby(["method", "object"]):
        st = ratio_stats(g.ratio)
        r = g.ratio[np.isfinite(g.ratio) & (g.ratio > 0)]
        lines.append(f"| {m} | {o} | {st['pairs']} | {np.median(r):.2f} | {st['median_err_pct']:.1f}% | "
                     f"{100 * st['within10']:.0f}% | {100 * st['within25']:.0f}% |")
    lines += ["", "Objectron's masks are the projected 3D box, not the object's silhouette: for an open laptop the "
              "box hull is much larger than the laptop, so the outline method measures too long an extent. "
              "With true silhouettes (CO3D, MVImgNet, a phone held up to a webcam) the outline would not have this bias; "
              "run.py uses the matched points."]
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
