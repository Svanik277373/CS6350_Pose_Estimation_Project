"""Print-legible versions of the stage-by-stage case figures.

    venv\\Scripts\\python.exe report\\final\\legible_cases.py [label ...]

Same computation as scripts/report_figures.py (MASt3R focal, region2 rule v2, MASt3R pose). Two layouts
are drawn from one run:
  report/final/figures/case_<label>.jpg        3 x 3 panels on a 7.2 in canvas (report, text width)
  report/final/figures/case_<label>_slide.jpg  2 x 3 key panels on a 16:9-friendly canvas (slides)
Reads the case list from results/cases/<label>.json and does not modify any result file; it prints the
re-computed numbers next to the saved ones so any difference is visible.
"""
import json
import sys
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from report_figures import euler_xyz, overlay, pair_from_name, side  # noqa: E402
from src.pipeline import geometry as G  # noqa: E402
from src.pipeline import pose_from_matches, region2, rotation_error_deg, translation_angle_deg  # noqa: E402
from src.pipeline.focal import K_from_focal, auto_focals  # noqa: E402
from src.pipeline.match import _prepare, match  # noqa: E402

FIG = ROOT / "report" / "final" / "figures"
RES = ROOT / "results" / "cases"
LABELS = ["planar", "failure", "3d", "small", "large", "tiny"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})

LAYOUTS = {
    # name: (figsize, grid, panel -> (row, col), title size, footer size, footer lines, suffix)
    "report": ((7.2, 6.4), (3, 3), {1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (1, 0), 5: (1, 1), 6: (1, 2),
                                    7: (2, 0), 8: (2, 1), 9: (2, 2)}, 8, 8, 2, ""),
    "slide": ((6.4, 3.3), (2, 3), {1: (0, 0), 2: (0, 1), 3: (0, 2), 7: (1, 0), 8: (1, 1), 9: (1, 2)},
              9, 8.5, 1, "_slide"),
}


def run_case(label):
    saved = json.loads((RES / f"{label}.json").read_text())
    name = saved["pair"]
    pair = pair_from_name(name)
    img1, img2, _, _ = pair.load()
    f1, f2, _ = auto_focals(None, img1, None, img2)
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

    # ---- panel contents: (title, image, cmap kwargs, lines)
    panels = {}
    pal = plt.get_cmap("tab20")
    im, off = side(img1, img2)
    panels[1] = (f"1. Input pair (true rot. {pair.angle_deg:.1f}°)", im, {}, None)
    o = img1.copy()
    for k, c in enumerate(a["cands"][:20]):
        o = overlay(o, c["mask"], tuple(int(255 * v) for v in pal(k % 20)[:3]), 0.35)
    panels[2] = (f"2. SAM 2.1 candidates ({len(a['cands'])})", o, {}, None)
    o = img1.copy()
    diff = None
    if "p1" in a and a["background"].sum() >= 15:
        bg = a["background"]
        F, _ = cv2.findFundamentalMat(a["p1"][bg], a["p2"][bg], cv2.USAC_MAGSAC, 2.0, 0.999, 10000)
        if F is not None and F.shape == (3, 3):
            outl = G.sampson_sq(F, a["p1"], a["p2"]) > 4.0
            for q, bad in zip(a["p1"].astype(int), outl):
                cv2.circle(o, tuple(q), max(3, img1.shape[1] // 160), (230, 40, 40) if bad else (40, 200, 60), -1)
        H, _ = cv2.findHomography(a["p1"][bg], a["p2"][bg], cv2.USAC_MAGSAC, 3.0)
        g1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY).astype(np.float32)
        g2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY).astype(np.float32)
        diff = np.abs(cv2.warpPerspective(g1, H, (img2.shape[1], img2.shape[0])) - g2) if H is not None else g2 * 0
    if obj is not None:
        o = overlay(o, obj["mask"], (255, 200, 0), 0.0)
    panels[3] = ("3. Motion rule (red: violates F)", o, {}, None)
    panels[4] = ("4. Change rule: |warp(I1) − I2|", diff,
                 dict(cmap="magma", vmin=0, vmax=np.percentile(diff, 99)) if diff is not None else {}, None)
    if m1 is not None:
        im5, _ = side(overlay(img1, m1, (0, 200, 90)), overlay(img2, m2, (0, 200, 90)))
    else:
        im5 = im
    panels[5] = (f"5. Region: {mode}" + ("" if m1 is not None else " (whole images)"), im5, {}, None)
    v1, v2 = _prepare(img1, m1, 800, crop), _prepare(img2, m2, 800, crop)
    panels[6] = ("6. Crops given to MASt3R", side(v1.rgb, v2.rgb)[0], {}, None)
    rng = np.random.default_rng(0)
    sel = rng.permutation(len(p1))[:80]
    panels[7] = (f"7. MASt3R matches ({len(p1)})", im, {}, (p1[sel], p2[sel], off, "#1f77b4"))
    q1, q2 = (res.pts1, res.pts2) if res.ok else (p1[:0], p2[:0])
    sel = rng.permutation(len(q1))[:80]
    panels[8] = (f"8. Inliers of {res.model or '-'} ({res.n_inliers})", im, {}, (q1[sel], q2[sel], off, "#2ca02c"))
    txt = ["pose could not be computed", ""]
    if res.ok:
        x1n, x2n = G.to_normalized(res.pts1, K1), G.to_normalized(res.pts2, K2)
        X = G.triangulate(res.R, res.t, x1n, x2n)
        u2 = (X @ res.R.T + res.t) @ K2.T
        u2 = u2[:, :2] / u2[:, 2:3]
        o = img2.copy()
        lw = max(2, img2.shape[1] // 320)
        for q, r in list(zip(res.pts2, u2))[::max(1, len(u2) // 150)]:
            e = 20 * (r - q)
            cv2.circle(o, tuple(q.astype(int)), lw + 1, (40, 200, 60), -1)
            cv2.line(o, tuple(q.astype(int)), tuple((q + e).astype(int)), (230, 40, 40), lw)
        panels[9] = ("9. Reprojection error (×20)", o, {}, None)
        rot = rotation_error_deg(res.R, pair.R_gt)
        tra = translation_angle_deg(res.t, pair.t_gt)
        ge, ee = euler_xyz(pair.R_gt), euler_xyz(res.R)
        ferr = 100 * (f1 - pair.frame1.K[0, 0]) / pair.frame1.K[0, 0]
        txt = [f"roll / pitch / yaw: estimated {ee[0]:+.2f} / {ee[1]:+.2f} / {ee[2]:+.2f}°,  "
               f"true {ge[0]:+.2f} / {ge[1]:+.2f} / {ge[2]:+.2f}°",
               f"rotation error {rot:.2f}°,  translation-direction error {tra:.2f}°,  "
               f"reprojection RMS {res.reproj_rms_px:.2f} px,  model {res.model},  focal error {ferr:+.1f}%"]
        print(f"{label}: rot err {rot:.3f} (saved {saved.get('rot_err', float('nan')):.3f})  "
              f"reproj {res.reproj_rms_px:.3f} (saved {saved.get('reproj_px', float('nan')):.3f})", flush=True)

    for lay, (size, grid, where, tsize, fsize, nlines, suffix) in LAYOUTS.items():
        fig, ax = plt.subplots(*grid, figsize=size)
        for x in ax.ravel():
            x.axis("off")
        for n, (r, c) in where.items():
            if n not in panels or panels[n][1] is None:
                continue
            title, img, kw, lines = panels[n]
            axx = ax[r, c]
            axx.imshow(img, **kw)
            if lines is not None:
                u1, u2_, o_, col = lines
                for u, w in zip(u1, u2_):
                    axx.plot([u[0], w[0] + o_], [u[1], w[1]], "-", lw=0.7, color=col, alpha=0.9)
            axx.set_title(title, fontsize=tsize, pad=3)
        if lay == "report":
            fig.suptitle(f"{name}  ({label})", fontsize=9, fontweight="bold", y=0.995)
            fig.tight_layout(rect=(0, 0.06, 1, 0.985), h_pad=0.6, w_pad=0.4)
            fig.text(0.01, 0.005, "\n".join(txt), fontsize=fsize, va="bottom", linespacing=1.4)
        else:
            fig.tight_layout(pad=0.2, h_pad=0.5, w_pad=0.3)    # numbers are written on the slide itself
        out = FIG / f"case_{label}{suffix}.jpg"
        fig.savefig(str(out), dpi=300, facecolor="white", pil_kwargs={"quality": 90})
        plt.close(fig)
        print("written", out, flush=True)


if __name__ == "__main__":
    for lab in (sys.argv[1:] or LABELS):
        run_case(lab)
