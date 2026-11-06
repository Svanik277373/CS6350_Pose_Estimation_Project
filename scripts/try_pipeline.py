"""Quick Phase-1 check: run the classical pipeline on a sample of pairs from each dataset."""
import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.loaders import LOADERS  # noqa: E402
from src.pipeline import estimate_pose, rotation_error_deg, translation_angle_deg  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matcher", default="sift")
    ap.add_argument("--model", default="auto", choices=["auto", "H", "E"])
    ap.add_argument("--pairs", type=int, default=15, help="pairs per dataset")
    args = ap.parse_args()

    for name, loader in LOADERS.items():
        pairs = loader.load_pairs(per_bin=4, seed=0)
        rng = np.random.default_rng(1)
        pairs = [pairs[k] for k in rng.choice(len(pairs), size=min(args.pairs, len(pairs)), replace=False)]
        print(f"\n[{name}] matcher={args.matcher} model={args.model}")
        rot, tra, fails = [], [], 0
        for pair in pairs:
            img1, img2, m1, m2 = pair.load()
            res = estimate_pose(img1, img2, pair.frame1.K, pair.frame2.K, m1, m2,
                                matcher=args.matcher, model=args.model)
            if not res.ok:
                fails += 1
                print(f"  {pair.name:38s} angle={pair.angle_deg:5.1f}  FAILED ({res.reason})")
                continue
            re, te = rotation_error_deg(res.R, pair.R_gt), translation_angle_deg(res.t, pair.t_gt)
            rot.append(re)
            tra.append(te)
            print(f"  {pair.name:38s} angle={pair.angle_deg:5.1f}  model={res.model}  "
                  f"inliers={res.n_inliers:4d}/{res.n_matches:4d}  rot_err={re:6.2f} deg  "
                  f"t_err={te:6.1f} deg  reproj={res.reproj_rms_px:5.2f}px  {res.seconds:4.1f}s")
        if rot:
            print(f"  -> median rot err {np.median(rot):.2f} deg, median t-dir err {np.nanmedian(tra):.1f} deg, "
                  f"failed {fails}/{len(pairs)}")


if __name__ == "__main__":
    main()
