"""Choose region2.RULE_V2 on the TUNING split (never on test pairs).

    venv\\Scripts\\python.exe scripts\\region_tune.py

For 1 tuning pair per object x viewpoint bin: run region2.analyse once, then every rule in the
grid below decides the object region; each distinct region gets one MASt3R pose (dataset K, so
only the region decision differs). Score = AUC@10 of the pose error over the pairs.
Also prints the decision on the project's moved-object photos (no ground truth) as a check that a
rule still finds a hand-moved object.
Writes results/region_tune/{pairs.csv, summary.md}. New file only.
"""
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.loaders import LOADERS, split_of  # noqa: E402
from src.pipeline import estimate_pose, rotation_error_deg, translation_angle_deg  # noqa: E402
from src.pipeline import region2  # noqa: E402
from src.pipeline.metrics import pose_auc  # noqa: E402

OUT = ROOT / "results" / "region_tune"
PER_BIN = {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}
GRID = [dict(change_min_area=a, change_gap=g) for g in (0.30, 0.40, 0.50)
        for a in (0.0, 0.005, 0.01, 0.015, 0.02, 0.03, 0.05)]
PHOTOS = [("coin", "coin_test/0.jpeg", "coin_test/90.jpeg"), ("key", "Key_test/0.jpeg", "Key_test/60.jpeg"),
          ("wallet", "testing_sample_wallet/0.jpeg", "testing_sample_wallet/45.jpeg")]


def bin_of(a):
    return "5-15" if a < 15 else "15-30" if a < 30 else "30-60"


def err(res, pair):
    if not res.ok:
        return np.inf
    r, t = rotation_error_deg(res.R, pair.R_gt), translation_angle_deg(res.t, pair.t_gt)
    return r if np.isnan(t) else max(r, t)


def main():
    rng = np.random.default_rng(0)
    cells = {}
    for ds in ["tum", "objectron", "co3d", "mvimgnet"]:
        for p in LOADERS[ds].load_pairs(per_bin=PER_BIN[ds], seed=0):
            if split_of(p.name) == "tune":
                cells.setdefault((p.sequence.split("/")[0], bin_of(p.angle_deg)), []).append(p)
    pairs = [v[int(rng.integers(len(v)))] for _, v in sorted(cells.items())]
    print(f"{len(pairs)} tuning pairs", flush=True)

    rows = []
    for k, pair in enumerate(pairs, 1):
        t0 = time.perf_counter()
        img1, img2, _, _ = pair.load()
        K1, K2 = pair.frame1.K, pair.frame2.K
        a = region2.analyse(img1, img2)
        poses = {}
        row = dict(pair=pair.name, angle=pair.angle_deg)
        for i, rule in enumerate(GRID):
            obj, mode, why = region2.decide(a, rule)
            key = None if obj is None else id(obj)
            if key not in poses:
                m1, m2, note, mode2 = region2.finish(a, obj, mode, why)
                res = estimate_pose(img1, img2, K1, K2, m1, m2, matcher="mast3r", crop=m1 is not None)
                if not res.ok and m1 is not None:
                    res = estimate_pose(img1, img2, K1, K2, None, None, matcher="mast3r", crop=False)
                poses[key] = (err(res, pair), mode2, 0.0 if m1 is None else float(m1.mean()))
            e, mode2, cover = poses[key]
            row |= {f"err_{i}": e, f"mode_{i}": mode2, f"cover_{i}": cover}
        rows.append(row)
        print(f"[{k}/{len(pairs)}] {pair.name:40s} {pair.angle_deg:5.1f} deg  original {row['err_0']:7.2f} "
              f"({row['mode_0']}, {100 * row['cover_0']:.1f}%)  distinct regions {len(poses)}  "
              f"({time.perf_counter() - t0:.0f} s)", flush=True)

    d = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT / "pairs.csv", index=False)
    lines = ["# Region rule tuning (tuning split, MASt3R pose, dataset K)", "",
             f"{len(d)} pairs, 1 per object x viewpoint bin.", "",
             "| change_min_area | change_gap | AUC@10 | moved decisions | pairs > 20 deg |", "|---|---|---|---|---|"]
    for i, rule in enumerate(GRID):
        e = d[f"err_{i}"].to_numpy()
        lines.append(f"| {rule['change_min_area']} | {rule['change_gap']} | {pose_auc(e)[10]:.1f} | "
                     f"{(d[f'mode_{i}'] == 'moved').sum()} | {(e > 20).sum()} |")

    lines += ["", "Moved-object photos (no ground truth): decision per rule", "",
              "| photo | " + " | ".join(f"{r['change_min_area']}/{r['change_gap']}" for r in GRID) + " |",
              "|---|" + "---|" * len(GRID)]
    for name, f1, f2 in PHOTOS:
        if not (ROOT / f1).exists():
            continue
        im1 = cv2.cvtColor(cv2.imread(str(ROOT / f1)), cv2.COLOR_BGR2RGB)
        im2 = cv2.cvtColor(cv2.imread(str(ROOT / f2)), cv2.COLOR_BGR2RGB)
        a = region2.analyse(im1, im2)
        cells_ = []
        for rule in GRID:
            obj, mode, _ = region2.decide(a, rule)
            cells_.append(mode if obj is None else f"{mode} {100 * obj['area']:.1f}%")
        lines.append(f"| {name} | " + " | ".join(cells_) + " |")
        print(name, cells_, flush=True)
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
