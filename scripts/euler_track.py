"""Frame-wise roll / pitch / yaw of the two-image pipeline against ground truth (as CS6350.pdf,
Figs 12-13): a run of TUM frame pairs (i, i + gap), i = start, start + gap, ... from the test part
of one sequence, each solved with only the two images (MASt3R focal, region2 region, MASt3R pose).

    venv\\Scripts\\python.exe scripts\\euler_track.py --sequence struct_near --gap 20 --pairs 40

Writes results/euler_track/<sequence>_gap<gap>.csv and report/final/figures/euler_<sequence>_gap<gap>.png.
New file only.
"""
import argparse
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.loaders import tum  # noqa: E402
from src.loaders.common import make_pair  # noqa: E402
from src.pipeline import estimate_pose, rotation_error_deg, translation_angle_deg  # noqa: E402
from src.pipeline import region2  # noqa: E402
from src.pipeline.focal import K_from_focal, auto_focals  # noqa: E402


def euler_xyz(R):
    return np.degrees([np.arctan2(R[2, 1], R[2, 2]), -np.arcsin(np.clip(R[2, 0], -1, 1)),
                       np.arctan2(R[1, 0], R[0, 0])])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sequence", default="struct_near")
    ap.add_argument("--gap", type=int, default=20)
    ap.add_argument("--pairs", type=int, default=40)
    args = ap.parse_args()

    frames = tum.load_frames(args.sequence)
    start = int(np.ceil(0.3 * len(frames)))                    # test part only
    idx = [start + k * args.gap for k in range(args.pairs) if start + (k + 1) * args.gap < len(frames)]
    out_csv = ROOT / "results" / "euler_track" / f"{args.sequence}_gap{args.gap}.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for n, i in enumerate(idx, 1):
        t0 = time.perf_counter()
        pair = make_pair("tum", args.sequence, frames[i], frames[i + args.gap], metric=True)
        img1, img2, _, _ = pair.load()
        f1, f2, _ = auto_focals(None, img1, None, img2)
        K1, K2 = K_from_focal(f1, img1.shape), K_from_focal(f2, img2.shape)
        m1, m2, note, mode = region2.find_regions(img1, img2)
        res = estimate_pose(img1, img2, K1, K2, m1, m2, matcher="mast3r", crop=m1 is not None)
        if not res.ok and m1 is not None:
            res = estimate_pose(img1, img2, K1, K2, None, None, matcher="mast3r", crop=False)
        gt = euler_xyz(pair.R_gt)
        est = euler_xyz(res.R) if res.ok else np.full(3, np.nan)
        rows.append(dict(i=i, j=i + args.gap, angle=pair.angle_deg, mode=mode, ok=res.ok,
                         f_err_pct=100 * (0.5 * (f1 + f2) - pair.frame1.K[0, 0]) / pair.frame1.K[0, 0],
                         roll_gt=gt[0], pitch_gt=gt[1], yaw_gt=gt[2], roll=est[0], pitch=est[1], yaw=est[2],
                         rot_err=rotation_error_deg(res.R, pair.R_gt) if res.ok else np.inf,
                         t_err=translation_angle_deg(res.t, pair.t_gt) if res.ok else np.inf,
                         reproj=res.reproj_rms_px))
        pd.DataFrame(rows).to_csv(out_csv, index=False)
        r = rows[-1]
        print(f"[{n}/{len(idx)}] {i}-{i + args.gap} angle {r['angle']:.1f}  {mode:11s} rot err {r['rot_err']:.2f}  "
              f"t err {r['t_err']:.1f}  ({time.perf_counter() - t0:.0f} s)", flush=True)

    d = pd.DataFrame(rows)
    fig, axes = plt.subplots(3, 1, figsize=(9, 8), sharex=True)
    for ax, name in zip(axes, ["roll", "pitch", "yaw"]):
        ax.plot(range(len(d)), d[f"{name}_gt"], "-o", ms=3, lw=1.2, color="#1f77b4", label="Ground truth")
        ax.plot(range(len(d)), d[name], "-o", ms=3, lw=1.2, color="#ff7f0e", label="Estimated (two images only)")
        ax.set_ylabel(f"{name.capitalize()} (deg)")
        ax.set_title(f"{name.capitalize()} angle: ground truth vs estimated", fontsize=10)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8, loc="best")
    axes[-1].set_xlabel("Pair index")
    fig.tight_layout()
    fig_dir = ROOT / "report" / "final" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(fig_dir / f"euler_{args.sequence}_gap{args.gap}.png", dpi=200)
    print("written", out_csv)


if __name__ == "__main__":
    main()
