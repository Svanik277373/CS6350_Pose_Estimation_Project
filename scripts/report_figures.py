"""Stage-by-stage figures of the two-image pipeline for the report's example cases.

    venv\\Scripts\\python.exe scripts\\report_figures.py --case planar tum/flat_near/611-700 --case ...

For each pair: the exact auto_run steps (MASt3R focal, region2 region, MASt3R pose), drawn as
one 3 x 3 panel figure:
  1 input pair            2 SAM 2.1 candidate segments     3 motion rule (matches vs background F)
  4 change rule (|warp(I1) - I2|)                          5 object masks in both images
  6 crops given to MASt3R 7 MASt3R matches                 8 inliers of the chosen model (H or E)
  9 reprojection error vectors (x20) + the numbers against ground truth
Writes report/final/figures/case_<name>.png and results/cases/<name>.json. New file only.
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.loaders import co3d, mvimgnet, objectron, tum  # noqa: E402
from src.loaders.common import make_pair  # noqa: E402
from src.pipeline import geometry as G  # noqa: E402
from src.pipeline import pose_from_matches, region as R, region2, rotation_error_deg, translation_angle_deg  # noqa: E402
from src.pipeline.focal import K_from_focal, auto_focals  # noqa: E402
from src.pipeline.match import _prepare, match  # noqa: E402

FIG = ROOT / "report" / "final" / "figures"
RES = ROOT / "results" / "cases"


def pair_from_name(name):
    ds, *mid, ij = name.split("/")
    a, b = (int(x) for x in ij.split("-"))
    if ds == "tum":
        fr = tum.load_frames(mid[0])
        return make_pair("tum", mid[0], fr[a], fr[b], metric=True)
    mod = {"co3d": co3d, "mvimgnet": mvimgnet, "objectron": objectron}[ds]
    seq_dir = mod.ROOT / mid[0] / mid[1]
    fr = {f.index: f for f in mod.load_frames(seq_dir)}
    if ds == "objectron":
        objectron.extract_frames(seq_dir, {a, b})
    return make_pair(ds, f"{mid[0]}/{mid[1]}", fr[a], fr[b], metric=ds == "objectron")


def euler_xyz(Rm):
    return np.degrees([np.arctan2(Rm[2, 1], Rm[2, 2]), -np.arcsin(np.clip(Rm[2, 0], -1, 1)),
                       np.arctan2(Rm[1, 0], Rm[0, 0])])


def side(a, b):
    h = max(a.shape[0], b.shape[0])
    pad = lambda x: np.pad(x, ((0, h - x.shape[0]), (0, 0), (0, 0)), constant_values=255)  # noqa: E731
    return np.hstack([pad(a), np.full((h, 12, 3), 255, np.uint8), pad(b)]), a.shape[1] + 12


def overlay(img, mask, color, alpha=0.45):
    out = img.copy()
    out[mask] = (alpha * np.array(color) + (1 - alpha) * out[mask]).astype(np.uint8)
    cnts, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(out, cnts, -1, color, max(2, img.shape[1] // 300))
    return out


def run_case(label, name):
    pair = pair_from_name(name)
    img1, img2, _, _ = pair.load()
    f1, f2, fsrc = auto_focals(None, img1, None, img2)
    K1, K2 = K_from_focal(f1, img1.shape), K_from_focal(f2, img2.shape)
    a = region2.analyse(img1, img2)
    obj, mode, why = region2.decide(a, region2.RULE_V2)
    m1, m2, note, mode = region2.finish(a, obj, mode, why)
    crop = m1 is not None
    p1, p2, s = match(img1, img2, m1, m2, matcher="mast3r", max_side=800, crop=crop)
    res = pose_from_matches(p1, p2, s, K1, K2)
    if not res.ok and crop:
        m1 = m2 = None
        crop, mode = False, "scene"
        p1, p2, s = match(img1, img2, None, None, matcher="mast3r", max_side=800, crop=False)
        res = pose_from_matches(p1, p2, s, K1, K2)

    fig, ax = plt.subplots(3, 3, figsize=(15, 10.5))
    for x in ax.ravel():
        x.axis("off")
    pal = plt.get_cmap("tab20")

    # 1 input
    im, _ = side(img1, img2)
    ax[0, 0].imshow(im)
    ax[0, 0].set_title(f"1. Input pair (true rotation {pair.angle_deg:.1f}°)", fontsize=10)
    # 2 SAM candidates
    o = img1.copy()
    for k, c in enumerate(a["cands"][:20]):
        o = overlay(o, c["mask"], tuple(int(255 * v) for v in pal(k % 20)[:3]), 0.35)
    ax[0, 1].imshow(o)
    ax[0, 1].set_title(f"2. SAM 2.1 candidates in image 1 ({len(a['cands'])} after filters)", fontsize=10)
    # 3 motion rule
    o = img1.copy()
    if "p1" in a and a["background"].sum() >= 15:
        bg = a["background"]
        F, inl = cv2.findFundamentalMat(a["p1"][bg], a["p2"][bg], cv2.USAC_MAGSAC, 2.0, 0.999, 10000)
        if F is not None and F.shape == (3, 3):
            outl = G.sampson_sq(F, a["p1"], a["p2"]) > 4.0
            for q, bad in zip(a["p1"].astype(int), outl):
                cv2.circle(o, tuple(q), max(2, img1.shape[1] // 250), (230, 40, 40) if bad else (40, 200, 60), -1)
    if obj is not None:
        o = overlay(o, obj["mask"], (255, 200, 0), 0.0)
    ax[0, 2].imshow(o)
    ax[0, 2].set_title("3. Motion rule: green follows background F, red does not", fontsize=10)
    # 4 change rule
    if "p1" in a and a["background"].sum() >= 15:
        bg = a["background"]
        H, _ = cv2.findHomography(a["p1"][bg], a["p2"][bg], cv2.USAC_MAGSAC, 3.0)
        g1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY).astype(np.float32)
        g2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY).astype(np.float32)
        diff = np.abs(cv2.warpPerspective(g1, H, (img2.shape[1], img2.shape[0])) - g2) if H is not None else g2 * 0
        ax[1, 0].imshow(diff, cmap="magma", vmin=0, vmax=np.percentile(diff, 99))
    ax[1, 0].set_title("4. Change rule: |warp(I1) - I2| after undoing background motion", fontsize=10)
    # 5 masks
    if m1 is not None:
        im, _ = side(overlay(img1, m1, (0, 200, 90)), overlay(img2, m2, (0, 200, 90)))
    else:
        im, _ = side(img1, img2)
    ax[1, 1].imshow(im)
    ax[1, 1].set_title(f"5. Region: {mode}" + ("" if m1 is not None else " (whole images used)"), fontsize=10)
    # 6 crops
    v1, v2 = _prepare(img1, m1, 800, crop), _prepare(img2, m2, 800, crop)
    im, _ = side(v1.rgb, v2.rgb)
    ax[1, 2].imshow(im)
    ax[1, 2].set_title("6. Crops (box + 20% margin, long side ≤ 800 px)", fontsize=10)
    # 7 matches / 8 inliers on the full images
    im, off = side(img1, img2)
    rng = np.random.default_rng(0)
    for axx, pts, title, col in [(ax[2, 0], (p1, p2), f"7. MASt3R matches ({len(p1)})", "#1f77b4"),
                                 (ax[2, 1], (res.pts1, res.pts2) if res.ok else (p1[:0], p2[:0]),
                                  f"8. Inliers of {res.model or '-'} ({res.n_inliers})", "#2ca02c")]:
        axx.imshow(im)
        q1, q2 = pts
        sel = rng.permutation(len(q1))[:120]
        for u, w in zip(q1[sel], q2[sel]):
            axx.plot([u[0], w[0] + off], [u[1], w[1]], "-", lw=0.6, color=col, alpha=0.8)
        axx.set_title(title, fontsize=10)
    # 9 reprojection + numbers
    if res.ok:
        x1n, x2n = G.to_normalized(res.pts1, K1), G.to_normalized(res.pts2, K2)
        X = G.triangulate(res.R, res.t, x1n, x2n)
        u2 = (X @ res.R.T + res.t) @ K2.T
        u2 = u2[:, :2] / u2[:, 2:3]
        o = img2.copy()
        for q, r in list(zip(res.pts2, u2))[::max(1, len(u2) // 150)]:
            e = 20 * (r - q)
            cv2.circle(o, tuple(q.astype(int)), 2, (40, 200, 60), -1)
            cv2.line(o, tuple(q.astype(int)), tuple((q + e).astype(int)), (230, 40, 40), 1)
        ax[2, 2].imshow(o)
        rot = rotation_error_deg(res.R, pair.R_gt)
        tra = translation_angle_deg(res.t, pair.t_gt)
        ge, ee = euler_xyz(pair.R_gt), euler_xyz(res.R)
        txt = (f"roll/pitch/yaw  est {ee[0]:+.2f} {ee[1]:+.2f} {ee[2]:+.2f}°\n"
               f"                true {ge[0]:+.2f} {ge[1]:+.2f} {ge[2]:+.2f}°\n"
               f"rotation error {rot:.2f}°   t-direction error {tra:.2f}°\n"
               f"reprojection RMS {res.reproj_rms_px:.2f} px   model {res.model}   focal error "
               f"{100 * (f1 - pair.frame1.K[0, 0]) / pair.frame1.K[0, 0]:+.1f}%")
        ax[2, 2].text(0.01, -0.02, txt, transform=ax[2, 2].transAxes, va="top", fontsize=8.5, family="monospace")
        ax[2, 2].set_title("9. Reprojection error vectors (x20) in image 2", fontsize=10)
    fig.suptitle(f"Case: {label} — {name}", fontsize=12, fontweight="bold")
    fig.tight_layout()
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"case_{label}.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    RES.mkdir(parents=True, exist_ok=True)
    info = dict(label=label, pair=name, angle_deg=pair.angle_deg, focal_source=fsrc, f_est=f1,
                f_true=float(pair.frame1.K[0, 0]), region_mode=mode, region_note=note, ok=bool(res.ok))
    if res.ok:
        info |= dict(model=res.model, inliers=res.n_inliers, matches=res.n_matches, reproj_px=res.reproj_rms_px,
                     rot_err=rot, t_err=tra, R=res.R.round(5).tolist(), t=np.asarray(res.t).round(5).tolist(),
                     R_gt=pair.R_gt.round(5).tolist(), euler_est=ee.round(3).tolist(), euler_gt=ge.round(3).tolist())
    (RES / f"{label}.json").write_text(json.dumps(info, indent=2))
    print(label, name, mode, "rot err", info.get("rot_err"), "reproj", info.get("reproj_px"), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", nargs=2, action="append", metavar=("LABEL", "PAIR"), required=True)
    args = ap.parse_args()
    for label, name in args.case:
        run_case(label, name)


if __name__ == "__main__":
    main()
