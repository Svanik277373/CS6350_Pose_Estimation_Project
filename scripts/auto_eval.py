"""Evaluation of the main pipeline (auto_run.py): two images in, nothing else known.

    venv\\Scripts\\python.exe scripts\\auto_eval.py --max-minutes 165

For every test pair the exact auto_run.py steps run: focal length estimated (no EXIF on the
dataset images -> MASt3R), object region found automatically (region.py), then the pose with
three methods on the SAME focal and region: mast3r (auto_run's default), accurate, confident.
For reference, "true" is MASt3R with the dataset K and dataset region (the benchmark setting).

Pairs (test split only, nothing here was used for tuning):
  main   3 per object x viewpoint bin (5-15, 15-30, 30-60 deg), the 11 objects/scenes,
         drawn from the benchmark's test pairs
  tiny   consecutive TUM frames (< ~1 deg; the "successive frames" case)
  large  60-90 deg pairs from CO3D, MVImgNet and Objectron (the "arbitrary view" case)
Pairs are processed round-robin over the cells, so a run stopped by --max-minutes is still
balanced; results are appended per pair and a rerun resumes where it stopped.

Writes results/auto_eval/pairs.csv (one row per pair and method). Summaries: scripts/auto_report.py.
New file only; the benchmark code and results are unchanged.
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
from src.loaders import co3d, mvimgnet, objectron, tum  # noqa: E402
from src.loaders.common import make_pair  # noqa: E402
from src.pipeline import (estimate_pose, estimate_pose_cascade, estimate_pose_confident,  # noqa: E402
                          pose_from_matches, rotation_error_deg, translation_angle_deg)
from src.pipeline import estimate as estimate_mod  # noqa: E402
from src.pipeline import match as match_mod  # noqa: E402
from src.pipeline.focal import K_from_focal, auto_focals  # noqa: E402
from src.pipeline.region import find_regions  # noqa: E402
import auto_run  # noqa: E402  (verdict(), unchanged)

OUT = ROOT / "results" / "auto_eval"
PER_BIN = {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}   # as the benchmark (scripts/evaluate.py)
METHODS = ["mast3r", "accurate", "confident"]
SHAPE = {  # dominant geometry of each object/scene
    "checkerboard": "planar", "flat_far": "planar", "flat_near": "planar", "book": "planar",
    "cellphone": "planar", "key": "planar", "watch": "planar",
    "struct_far": "3D", "struct_near": "3D", "cereal_box": "3D", "laptop": "3D", "handbag": "3D"}


# ---------------------------------------------------------------- per-pair match memo
# accurate and confident share stages (XFeat+LG, SIFT), and confident's last stage is MASt3R,
# which the mast3r method already ran on the same crops: compute each once per pair. The time
# of a re-used result is added back so the reported seconds are what a single run would take.
_memo, _reused = {}, [0.0]
_orig_match = match_mod.match


def _memo_match(img1, img2, mask1=None, mask2=None, matcher="sift", max_side=800, crop=False, min_side=0):
    key = (matcher, bool(crop and mask1 is not None), max_side, min_side, id(mask1), id(mask2))
    if key in _memo:
        res, sec = _memo[key]
        _reused[0] += sec
        return res
    t0 = time.perf_counter()
    res = _orig_match(img1, img2, mask1, mask2, matcher=matcher, max_side=max_side, crop=crop, min_side=min_side)
    _memo[key] = (res, time.perf_counter() - t0)
    return res


estimate_mod.match = _memo_match
try:
    from src.pipeline import shape as shape_mod
    if hasattr(shape_mod, "match"):
        shape_mod.match = _memo_match
except ImportError:
    pass


# ---------------------------------------------------------------- pairs
def obj_of(pair):
    return pair.sequence.split("/")[0]


def bin_of(angle):
    for lo, hi in [(0, 5), (5, 15), (15, 30), (30, 60), (60, 90)]:
        if lo <= angle < hi:
            return f"{lo}-{hi}"
    return ">=90"


def main_pairs(per_cell, rng):
    cells = {}
    for ds in ["tum", "objectron", "co3d", "mvimgnet"]:
        pairs = [p for p in LOADERS[ds].load_pairs(per_bin=PER_BIN[ds], seed=0) if split_of(p.name) == "test"]
        for p in pairs:
            cells.setdefault(("main", obj_of(p), bin_of(p.angle_deg)), []).append(p)
    for k, v in cells.items():
        idx = rng.choice(len(v), size=min(per_cell, len(v)), replace=False)
        cells[k] = [v[i] for i in sorted(idx)]
    return cells


def tiny_pairs(per_seq, rng):
    """Consecutive frames from the test part of each TUM sequence (as CS6350's small regime)."""
    cells = {}
    for seq in tum.SEQUENCES:
        frames = tum.load_frames(seq)
        start = int(np.ceil(0.3 * len(frames)))           # test part: after the first 30%
        idx = rng.choice(np.arange(start, len(frames) - 1), size=per_seq, replace=False)
        cells[("tiny", seq, "0-5")] = [make_pair("tum", seq, frames[i], frames[i + 1], metric=True)
                                       for i in sorted(idx)]
    return cells


def large_pairs(per_obj, rng):
    """60-90 deg pairs from test sequences (seq04+) of the object datasets."""
    cells = {}
    for name, mod in [("co3d", co3d), ("mvimgnet", mvimgnet), ("objectron", objectron)]:
        for cat in mod.CATEGORIES:
            cands = []
            for seq_dir in sorted((mod.ROOT / cat).glob("seq*")):
                if seq_dir.name in {"seq01", "seq02", "seq03"}:
                    continue
                if name == "mvimgnet" and not mvimgnet.is_complete(seq_dir):
                    continue
                frames = mod.load_frames(seq_dir)
                Rs = np.stack([f.R for f in frames]).reshape(len(frames), 9)
                ang = np.degrees(np.arccos(np.clip((Rs @ Rs.T - 1) / 2, -1, 1)))
                i, j = np.triu_indices(len(frames), k=1)
                ok = (ang[i, j] >= 60) & (ang[i, j] < 90)
                cands += [(seq_dir, frames, int(a), int(b)) for a, b in zip(i[ok], j[ok])]
            if not cands:
                continue
            picks = rng.choice(len(cands), size=min(per_obj, len(cands)), replace=False)
            chosen = []
            for k in sorted(picks):
                seq_dir, frames, a, b = cands[k]
                if name == "objectron":
                    objectron.extract_frames(seq_dir, {frames[a].index, frames[b].index})
                chosen.append(make_pair(name, f"{cat}/{seq_dir.name}", frames[a], frames[b],
                                        metric=name == "objectron"))
            cells[("large", cat, "60-90")] = chosen
    return cells


def round_robin(cells):
    order, k = [], 0
    while any(k < len(v) for v in cells.values()):
        for key in sorted(cells):
            if k < len(cells[key]):
                order.append((key, cells[key][k]))
        k += 1
    return order


# ---------------------------------------------------------------- metrics
def euler_xyz(R):
    """(roll, pitch, yaw) in degrees, XYZ convention (as CS6350.pdf)."""
    return np.degrees([np.arctan2(R[2, 1], R[2, 2]), -np.arcsin(np.clip(R[2, 0], -1, 1)),
                       np.arctan2(R[1, 0], R[0, 0])])


def wrap(a):
    return (a + 180.0) % 360.0 - 180.0


def score(res, pair):
    if not res.ok:
        return dict(ok=False, rot=np.inf, tra=np.inf, err=np.inf, roll_e=np.inf, pitch_e=np.inf, yaw_e=np.inf)
    rot = rotation_error_deg(res.R, pair.R_gt)
    tra = translation_angle_deg(res.t, pair.t_gt)
    de = np.abs(wrap(euler_xyz(res.R) - euler_xyz(pair.R_gt)))
    return dict(ok=True, rot=rot, tra=tra, err=rot if np.isnan(tra) else max(rot, tra),
                roll_e=de[0], pitch_e=de[1], yaw_e=de[2])


def run_method(method, img1, img2, K1, K2, m1, m2, mode):
    """auto_run.py step 3 for one method, including its whole-image retry."""
    def once(a, b):
        if method == "confident":
            return estimate_pose_confident(img1, img2, K1, K2, a, b, preset=method)
        if method in ("fast", "accurate"):
            return estimate_pose_cascade(img1, img2, K1, K2, a, b, preset=method)
        return estimate_pose(img1, img2, K1, K2, a, b, matcher=method, crop=a is not None)
    res = once(m1, m2)
    if not res.ok and m1 is not None and mode in ("unconfirmed", "moved"):
        res, mode = once(None, None), "scene"
    return res, mode


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-cell", type=int, default=3)
    ap.add_argument("--tiny-per-seq", type=int, default=2)
    ap.add_argument("--large-per-obj", type=int, default=2)
    ap.add_argument("--max-minutes", type=float, default=165)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    cells = main_pairs(args.per_cell, rng)
    cells |= tiny_pairs(args.tiny_per_seq, rng)
    cells |= large_pairs(args.large_per_obj, rng)
    order = round_robin(cells)
    OUT.mkdir(parents=True, exist_ok=True)
    csv = OUT / "pairs.csv"
    done = set(pd.read_csv(csv).pair) if csv.exists() else set()
    print(f"{len(order)} pairs planned ({sum(k[0] == 'main' for k, _ in order)} main, "
          f"{sum(k[0] == 'tiny' for k, _ in order)} tiny, {sum(k[0] == 'large' for k, _ in order)} large); "
          f"{len(done)} already done", flush=True)

    t_start = time.perf_counter()
    for n, ((group, obj, abin), pair) in enumerate(order, 1):
        if pair.name in done:
            continue
        if (time.perf_counter() - t_start) / 60 > args.max_minutes:
            print(f"time budget of {args.max_minutes:.0f} min reached; stopping (rerun to resume)", flush=True)
            break
        t0 = time.perf_counter()
        _memo.clear()
        img1, img2, gm1, gm2 = pair.load()
        base = dict(pair=pair.name, dataset=pair.dataset, object=obj, group=group, bin=abin,
                    angle_deg=pair.angle_deg, shape=SHAPE.get(obj, "?"),
                    true_f=0.25 * (pair.frame1.K[0, 0] + pair.frame1.K[1, 1] + pair.frame2.K[0, 0] + pair.frame2.K[1, 1]))
        rows = []

        # reference: dataset K and region, MASt3R (cached for benchmark pairs)
        p1, p2, s = cached_matches("mast3r", pair, crop=True, images=(img1, img2, gm1, gm2))
        ref = pose_from_matches(p1, p2, s, pair.frame1.K, pair.frame2.K)
        rows.append(base | dict(method="true_K_mask", reproj=ref.reproj_rms_px, inliers=ref.n_inliers,
                                matches=ref.n_matches, model=ref.model, seconds=np.nan) | score(ref, pair))

        # 1. focal length (no EXIF on dataset images -> MASt3R), as auto_run.py
        tf = time.perf_counter()
        f1, f2, fsrc = auto_focals(None, img1, None, img2)
        K1, K2 = K_from_focal(f1, img1.shape), K_from_focal(f2, img2.shape)
        t_focal = time.perf_counter() - tf
        base |= dict(est_f=0.5 * (f1 + f2), f_err_pct=100 * (0.5 * (f1 + f2) - base["true_f"]) / base["true_f"],
                     focal_source=fsrc[:40], t_focal=t_focal)

        # 2. object region, as auto_run.py
        tr = time.perf_counter()
        m1, m2, note, mode = find_regions(img1, img2)
        base |= dict(region_mode=mode, region_note=note[:120], t_region=time.perf_counter() - tr,
                     cover1=np.nan if m1 is None else float(m1.mean()))
        box_masks = m1 is not None and (auto_run.is_box(m1) or auto_run.is_box(m2))

        # 3. pose, three methods on the same focal and region
        for method in METHODS:
            _reused[0] = 0.0
            tm = time.perf_counter()
            res, mode_m = run_method(method, img1, img2, K1, K2, m1, m2, mode)
            sec = time.perf_counter() - tm + _reused[0]
            rows.append(base | dict(method=method, reproj=res.reproj_rms_px, inliers=res.n_inliers,
                                    matches=res.n_matches, model=res.model, seconds=sec,
                                    final_mode=mode_m, reason=(res.reason or "")[:80],
                                    verdict=auto_run.verdict(res, fsrc, method, box_masks, mode_m)[:100])
                        | score(res, pair))
        pd.DataFrame(rows).to_csv(csv, mode="a", header=not csv.exists(), index=False)
        e = {r["method"]: r["err"] for r in rows}
        print(f"[{n}/{len(order)}] {group:5s} {pair.name:38s} {pair.angle_deg:5.1f} deg  f {base['f_err_pct']:+5.1f}%  "
              f"{mode:11s} err true {e['true_K_mask']:6.2f}  mast3r {e['mast3r']:6.2f}  accurate {e['accurate']:6.2f}  "
              f"confident {e['confident']:6.2f}  ({time.perf_counter() - t0:.0f} s, "
              f"total {(time.perf_counter() - t_start) / 60:.0f} min)", flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
