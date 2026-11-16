"""Blind evaluation of auto_run.py's pipeline: how much is lost when the camera's K and the
object region are NOT given (e.g. photos handed over in a live demo).

    venv\\Scripts\\python.exe scripts\\blind_eval.py --dataset tum --per-sequence 4

Three versions on the same test pairs, all with MASt3R for the pose:
  A  benchmark   dataset K,              dataset mask (TUM: whole image)  -- as reported
  B  est. focal  focal estimated by MASt3R (principal point at the centre), same region as A
  C  automatic   estimated focal + region found by YOLO-World (object name given) + SAM 2.1
  D  automatic   estimated focal + region found without any name (region.py: SAM 2.1 segments,
                 the same object in both images by matching, whole image if none)
Writes results/blind/<dataset>_pairs.csv and summary.md. Uses only new modules; the
benchmark code is unchanged (A re-uses the cached benchmark matches).
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from matchcache import cached_matches  # noqa: E402
from src.loaders import LOADERS, split_of  # noqa: E402
from src.pipeline import rotation_error_deg, translation_angle_deg  # noqa: E402
from src.pipeline.detect import find_box  # noqa: E402
from src.pipeline.estimate import pose_from_matches  # noqa: E402
from src.pipeline.focal import K_from_focal, mast3r_focal  # noqa: E402
from src.pipeline.match import match  # noqa: E402
from src.pipeline.metrics import pose_auc  # noqa: E402
from src.pipeline.region import find_regions  # noqa: E402
from src.pipeline.segment import auto_mask  # noqa: E402

PER_BIN = {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}
# what a presenter would type for each sequence's object
OBJECT_NAME = {"flat_far": "poster", "flat_near": "poster", "struct_far": "poster", "struct_near": "poster",
               "checkerboard": "checkerboard", "book": "book", "laptop": "laptop", "cereal_box": "cereal box",
               "cellphone": "mobile phone", "handbag": "handbag", "key": "key", "watch": "watch"}


def errors(res, pair):
    if not res.ok:
        return np.inf, np.inf, np.inf
    rot = rotation_error_deg(res.R, pair.R_gt)
    tra = translation_angle_deg(res.t, pair.t_gt)
    return rot, tra, (rot if np.isnan(tra) else max(rot, tra))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="tum", choices=list(LOADERS))
    ap.add_argument("--per-sequence", type=int, default=4, help="pairs per object (TUM: per sequence)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--versions", default="ABCD", help="which versions to run (A and B are always run)")
    ap.add_argument("--tag", default="", help="suffix for the output files")
    args = ap.parse_args()

    pairs = [p for p in LOADERS[args.dataset].load_pairs(per_bin=PER_BIN[args.dataset], seed=0)
             if split_of(p.name) == "test"]
    rng = np.random.default_rng(args.seed)
    chosen = []
    for obj in sorted({p.sequence.split("/")[0] for p in pairs}):
        group = [p for p in pairs if p.sequence.split("/")[0] == obj]
        idx = rng.choice(len(group), size=min(args.per_sequence, len(group)), replace=False)
        chosen += [group[i] for i in sorted(idx)]
    print(f"{len(chosen)} test pairs from {args.dataset}")

    rows = []
    for k, pair in enumerate(chosen, 1):
        t0 = time.perf_counter()
        img1, img2, m1, m2 = pair.load()
        K1, K2 = pair.frame1.K, pair.frame2.K
        obj = OBJECT_NAME.get(pair.sequence.split("/")[0], None)
        row = dict(pair=pair.name, sequence=pair.sequence, angle_deg=pair.angle_deg, object_name=obj,
                   true_f=0.5 * (K1[0, 0] + K1[1, 1]))

        # A: benchmark (cached matches of the reported MASt3R run, dataset K and region)
        p1, p2, s = cached_matches("mast3r", pair, crop=True, images=(img1, img2, m1, m2))
        resA = pose_from_matches(p1, p2, s, K1, K2)
        row.update(zip(["A_rot", "A_tra", "A_err"], errors(resA, pair)))

        # B: same matches, focal estimated by MASt3R, principal point at the image centre
        f1, f2 = mast3r_focal(img1, img2), mast3r_focal(img2, img1)
        f = 0.5 * (f1 + f2)            # same camera (as auto_run.py assumes for same-size images)
        Ke1, Ke2 = K_from_focal(f, img1.shape), K_from_focal(f, img2.shape)
        row.update(est_f=f, est_f1=f1, est_f2=f2, f_err_pct=100 * (f - row["true_f"]) / row["true_f"])
        resB = pose_from_matches(p1, p2, s, Ke1, Ke2)
        row.update(zip(["B_rot", "B_tra", "B_err"], errors(resB, pair)))

        # D: estimated focal + region found with no name at all (region.py) + new MASt3R matching
        if "D" in args.versions:
            d1, d2, note, mode = find_regions(img1, img2)
            row.update(D_note=note, D_whole=d1 is None, D_mode=mode)
            if d1 is not None:
                row.update(D_cover1=d1.mean(), D_cover2=d2.mean())
            q1, q2, sc = match(img1, img2, d1, d2, matcher="mast3r", max_side=800, crop=d1 is not None)
            resD = pose_from_matches(q1, q2, sc, Ke1, Ke2)
            if not resD.ok and d1 is not None:     # as auto_run.py: retry on the whole images
                w1, w2, sw = match(img1, img2, None, None, matcher="mast3r", max_side=800, crop=False)
                resD = pose_from_matches(w1, w2, sw, Ke1, Ke2)
                row.update(D_retry=True)
            row.update(zip(["D_rot", "D_tra", "D_err"], errors(resD, pair)))

        # C: estimated focal + automatic region (YOLO-World box -> SAM mask) + new MASt3R matching
        b1, lab1, c1 = (find_box(img1, obj) if "C" in args.versions else (None, "", 0.0))
        b2, lab2, c2 = (find_box(img2, obj, want_class=lab1 if b1 is not None else None)
                        if "C" in args.versions else (None, "", 0.0))
        row.update(det1=c1, det2=c2, found=b1 is not None and b2 is not None)
        if row["found"]:
            a1, n1 = auto_mask(img1, b1, "sam")
            a2, n2 = auto_mask(img2, b2, "sam")
            row.update(mask_cover1=a1.mean(), mask_cover2=a2.mean())
            q1, q2, sc = match(img1, img2, a1, a2, matcher="mast3r", max_side=800, crop=True)
            resC = pose_from_matches(q1, q2, sc, Ke1, Ke2)
            row.update(zip(["C_rot", "C_tra", "C_err"], errors(resC, pair)))
            row.update(C_inliers=resC.n_inliers, C_matches=resC.n_matches)
        else:
            row.update(C_rot=np.inf, C_tra=np.inf, C_err=np.inf)
        rows.append(row)
        print(f"[{k}/{len(chosen)}] {pair.name:32s} angle {pair.angle_deg:5.1f}  f {row['true_f']:.0f}->{f:.0f} "
              f"({row['f_err_pct']:+.1f}%)  err A {row['A_err']:.2f}  B {row['B_err']:.2f}  C {row['C_err']:.2f}"
              f"  D {row.get('D_err', np.nan):.2f}"
              f"  det {c1:.2f}/{c2:.2f}  ({time.perf_counter() - t0:.0f} s)", flush=True)

    d = pd.DataFrame(rows)
    out = ROOT / "results" / "blind"
    out.mkdir(parents=True, exist_ok=True)
    d.to_csv(out / f"{args.dataset}{args.tag}_pairs.csv", index=False)

    def stats(col):
        e = d[col].to_numpy()
        auc = pose_auc(e)
        fin = np.isfinite(e)
        return (f"{auc[5]:.1f} / {auc[10]:.1f} / {auc[20]:.1f} | "
                f"{np.median(d[col.replace('_err', '_rot')][fin]):.2f} | "
                f"{np.median(d[col.replace('_err', '_tra')][fin]):.2f} | {100 * (~fin).mean():.0f}%")

    lines = [f"# Blind evaluation on {args.dataset} ({len(d)} test pairs, MASt3R pose)", "",
             "| version | AUC@5 / @10 / @20 | median rot err (deg) | median t-dir err (deg) | failed |",
             "|---|---|---|---|---|",
             f"| A benchmark (dataset K, dataset region) | {stats('A_err')} |",
             f"| B estimated focal, dataset region | {stats('B_err')} |",
             (f"| C estimated focal + detector region (name given) | {stats('C_err')} |"
              if "C" in args.versions else ""),
             (f"| D estimated focal + automatic region, no name | {stats('D_err')} |" if "D_err" in d else ""),
             "",
             (f"D used the whole images on {int(d.D_whole.sum())} of {len(d)} pairs (no separate object)."
              if "D_whole" in d else ""),
             f"Focal estimate (MASt3R, pair-averaged) vs dataset focal: median error "
             f"{d.f_err_pct.median():+.1f}%, median |error| {d.f_err_pct.abs().median():.1f}%, "
             f"range {d.f_err_pct.min():+.1f}% .. {d.f_err_pct.max():+.1f}%.",
             f"Object found in both images: {int(d.found.sum())} of {len(d)} pairs.", "",
             "Per sequence (median pose error, deg):", "",
             "| object | pairs | f error | A | B | C | D |", "|---|---|---|---|---|---|---|"]
    for obj, g in d.groupby(d.sequence.str.split("/").str[0]):
        lines.append(f"| {obj} | {len(g)} | {g.f_err_pct.median():+.1f}% | {g.A_err.median():.2f} | "
                     f"{g.B_err.median():.2f} | {g.C_err.median():.2f} | "
                     f"{g.D_err.median() if 'D_err' in g else float('nan'):.2f} |")
    (out / f"{args.dataset}{args.tag}_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n" + "\n".join(lines))


if __name__ == "__main__":
    main()
