"""Sanity check of the ground truth produced by each loader.

For a few pairs per dataset, SIFT points are matched and their distance to the epipolar
lines predicted by the ground-truth pose is measured. With correct conventions the median
distance is about a pixel; a wrong axis flip or transpose gives tens to hundreds of pixels.
As a control the same is computed with a deliberately wrong pose (R transposed).
Also saves one epipolar-line image per dataset to results/checks/.
"""
import csv
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.loaders import LOADERS  # noqa: E402

OUT = ROOT / "results" / "checks"
PAIRS_PER_DATASET = 12


def skew(v):
    return np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


def sift_matches(img1, img2, mask1, mask2):
    sift = cv2.SIFT_create(4000)
    g1, g2 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY), cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
    m1 = mask1.astype(np.uint8) if mask1 is not None else None
    m2 = mask2.astype(np.uint8) if mask2 is not None else None
    k1, d1 = sift.detectAndCompute(g1, m1)
    k2, d2 = sift.detectAndCompute(g2, m2)
    if d1 is None or d2 is None:
        return np.empty((0, 2)), np.empty((0, 2))
    good = [m for m, n in cv2.BFMatcher().knnMatch(d1, d2, k=2) if m.distance < 0.75 * n.distance]
    return (np.float64([k1[m.queryIdx].pt for m in good]),
            np.float64([k2[m.trainIdx].pt for m in good]))


def epipolar_distance(p1, p2, F):
    """Symmetric point-to-epipolar-line distance in pixels."""
    h1 = np.hstack([p1, np.ones((len(p1), 1))])
    h2 = np.hstack([p2, np.ones((len(p2), 1))])
    l2 = h1 @ F.T          # lines in image 2
    l1 = h2 @ F            # lines in image 1
    num = np.abs(np.sum(h2 * l2, axis=1))
    return 0.5 * (num / np.linalg.norm(l2[:, :2], axis=1) + num / np.linalg.norm(l1[:, :2], axis=1))


def fundamental(K1, K2, R, t):
    return np.linalg.inv(K2).T @ skew(t) @ R @ np.linalg.inv(K1)


def draw_epilines(img1, img2, p1, p2, F, path, n=25):
    rng = np.random.default_rng(0)
    idx = rng.choice(len(p1), size=min(n, len(p1)), replace=False)
    a, b = img1.copy(), img2.copy()
    lines = (np.hstack([p1[idx], np.ones((len(idx), 1))]) @ F.T)
    w = b.shape[1]
    for k, (l, q1, q2) in enumerate(zip(lines, p1[idx], p2[idx])):
        color = tuple(int(c) for c in cv2.applyColorMap(np.uint8([[k * 10 % 255]]), cv2.COLORMAP_HSV)[0, 0])
        if abs(l[1]) > 1e-9:
            cv2.line(b, (0, int(-l[2] / l[1])), (w, int(-(l[2] + l[0] * w) / l[1])), color, 2)
        cv2.circle(a, tuple(int(x) for x in q1), 8, color, -1)
        cv2.circle(b, tuple(int(x) for x in q2), 8, color, -1)
    h = max(a.shape[0], b.shape[0])
    pad = lambda im: cv2.copyMakeBorder(im, 0, h - im.shape[0], 0, 0, cv2.BORDER_CONSTANT)
    vis = np.hstack([pad(a), pad(b)])
    scale = 1600 / vis.shape[1]
    cv2.imwrite(str(path), cv2.cvtColor(cv2.resize(vis, None, fx=scale, fy=scale), cv2.COLOR_RGB2BGR))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, loader in LOADERS.items():
        pairs = loader.load_pairs(per_bin=4, seed=0)
        print(f"\n[{name}] {len(pairs)} pairs sampled, checking {min(PAIRS_PER_DATASET, len(pairs))}")
        rng = np.random.default_rng(1)
        sel = rng.choice(len(pairs), size=min(PAIRS_PER_DATASET, len(pairs)), replace=False)
        drawn = False
        for k in sel:
            pair = pairs[k]
            img1, img2, m1, m2 = pair.load()
            p1, p2 = sift_matches(img1, img2, m1, m2)
            if len(p1) < 20:
                print(f"  {pair.name}: only {len(p1)} matches, skipped")
                continue
            # Keep only geometrically consistent matches, found WITHOUT using the ground truth,
            # so wrong SIFT matches don't get blamed on the ground truth
            _, inl = cv2.findFundamentalMat(p1, p2, cv2.USAC_MAGSAC, 2.0, 0.999)
            if inl is None or inl.sum() < 15:
                print(f"  {pair.name}: too few consistent matches, skipped")
                continue
            inl = inl.ravel().astype(bool)
            q1, q2 = p1[inl], p2[inl]

            K1, K2 = pair.frame1.K, pair.frame2.K
            F_gt = fundamental(K1, K2, pair.R_gt, pair.t_gt)
            F_bad = fundamental(K1, K2, pair.R_gt.T, pair.t_gt)
            d_gt, d_bad = epipolar_distance(q1, q2, F_gt), epipolar_distance(q1, q2, F_bad)
            # Error relative to image size, since a pixel means less on a 1920px image than a 640px one
            diag = np.hypot(*img1.shape[:2])
            row = dict(dataset=name, pair=pair.name, angle_deg=round(pair.angle_deg, 1),
                       matches=len(p1), consistent=int(inl.sum()),
                       median_px_gt=round(float(np.median(d_gt)), 2),
                       median_pct_diag_gt=round(float(100 * np.median(d_gt) / diag), 3),
                       median_px_wrong=round(float(np.median(d_bad)), 2))
            rows.append(row)
            print(f"  {pair.name:38s} angle={row['angle_deg']:5.1f}  consistent={row['consistent']:4d}/{len(p1):4d}  "
                  f"median GT={row['median_px_gt']:7.2f}px ({row['median_pct_diag_gt']:.2f}% of diag)  "
                  f"wrong-pose={row['median_px_wrong']:8.2f}px")
            if not drawn:
                draw_epilines(img1, img2, q1, q2, F_gt, OUT / f"{name}.jpg")
                drawn = True

    with open(OUT / "summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("\n=== per-dataset median of per-pair median epipolar distance (px) ===")
    for name in LOADERS:
        r = [x for x in rows if x["dataset"] == name]
        if r:
            print(f"{name:10s} GT: {np.median([x['median_px_gt'] for x in r]):7.2f}px "
                  f"({np.median([x['median_pct_diag_gt'] for x in r]):.2f}% of diag)   "
                  f"wrong pose: {np.median([x['median_px_wrong'] for x in r]):8.2f}px   pairs: {len(r)}")


if __name__ == "__main__":
    main()
