"""Zhang calibration on the TUM fr3 checkerboard sequence, compared with TUM's official K.

    venv\Scripts\python.exe scripts\calibrate.py

Steps:
  1. detect the 9x7 inner corners in every STEP-th frame;
  2. calibrate with several model variants (which parameters are free, which views);
  3. stability of each: bootstrap (resample the views with replacement, recalibrate);
  4. the ambiguity check: a badly-off K still explains held-out views almost as well as the
     official K -- the board here is nearly always seen face-on (tilt <= 25 deg), which is
     Zhang's degenerate case (focal length trades off against board distance);
  5. board square size in metres: camera motion between views in board units (calibration)
     vs in metres (motion capture ground truth).

The chosen calibration (all views, no distortion -- TUM says fr3 images are already
undistorted) is saved to results/calibration/camera.json, with summary.md and coverage.jpg.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.loaders import tum  # noqa: E402
from src.pipeline import calibration as C  # noqa: E402

PATTERN = (9, 7)
STEP = 5
N_VIEWS = 40
SUBSETS, SUBSET_SIZE = 30, 25
SEED = 0


def heldout_rms(K, dist, dets):
    obj = C.board_points(PATTERN)
    errs = []
    for d in dets:
        ok, rvec, tvec = cv2.solvePnP(obj, d.corners, K, dist, flags=cv2.SOLVEPNP_ITERATIVE)
        proj, _ = cv2.projectPoints(obj, rvec, tvec, K, dist)
        errs.append(np.sum((proj.reshape(-1, 2) - d.corners) ** 2, axis=1))
    return float(np.sqrt(np.mean(np.concatenate(errs))))


NO_DIST = cv2.CALIB_FIX_K1 | cv2.CALIB_FIX_K2 | cv2.CALIB_FIX_K3 | cv2.CALIB_ZERO_TANGENT_DIST
F_ONLY = NO_DIST | cv2.CALIB_FIX_PRINCIPAL_POINT | cv2.CALIB_FIX_ASPECT_RATIO
BOOTSTRAPS = 30
CHOSEN = "no distortion, all views"


def main():
    out = ROOT / "results" / "calibration"
    out.mkdir(parents=True, exist_ok=True)
    frames = tum.load_frames("checkerboard")
    w, h = 640, 480

    dets = []
    for f in tqdm(frames[::STEP], desc="corners"):
        corners = C.detect(cv2.cvtColor(f.load_image(), cv2.COLOR_RGB2GRAY), PATTERN)
        if corners is not None:
            dets.append(C.Detection(f.index, corners))
    tilts = np.array([C.tilt_deg(d, PATTERN, (w, h)) for d in dets])
    diverse = [dets[i] for i in C.select_diverse(dets, PATTERN, (w, h), N_VIEWS)]
    tilted = [dets[i] for i in np.argsort(-tilts)[:N_VIEWS]]

    variants = {   # name -> (views, flags)
        f"full model (k1 k2 p1 p2), {N_VIEWS} diverse views": (diverse, cv2.CALIB_FIX_K3),
        "full model (k1 k2 p1 p2), all views": (dets, cv2.CALIB_FIX_K3),
        "no distortion, all views": (dets, NO_DIST),
        "focal only (centre pp, fx=fy, no distortion), all views": (dets, F_ONLY),
        f"focal only, {N_VIEWS} most tilted views": (tilted, F_ONLY),
    }
    K_tum = tum.K_FR3
    rng = np.random.default_rng(SEED)
    rows, results = [], {}
    for name, (views, flags) in tqdm(variants.items(), desc="variants"):
        cal = C.calibrate(views, PATTERN, (w, h), flags=flags)
        boot = []
        for _ in range(BOOTSTRAPS):
            idx = rng.integers(0, len(views), len(views))
            boot.append(C.calibrate([views[i] for i in idx], PATTERN, (w, h), flags=flags).K[0, 0])
        results[name] = cal
        rows.append((name, len(views), cal, float(np.std(boot))))

    cal = results[CHOSEN]
    # Ambiguity check: K from the 40 diverse views vs official K, on the views it didn't use
    bad = results[f"full model (k1 k2 p1 p2), {N_VIEWS} diverse views"]
    held = [d for d in dets if d.index not in set(bad.used)]
    rms_bad, rms_tum = heldout_rms(bad.K, bad.dist, held), heldout_rms(K_tum, np.zeros(5), held)

    # Square size: camera centres in board units vs motion-capture metres
    by_index = {f.index: f for f in frames}
    cam_board = [(-cv2.Rodrigues(r)[0].T @ t) for r, t in zip(cal.rvecs, cal.tvecs)]
    cam_world = [-by_index[i].R.T @ by_index[i].t for i in cal.used]
    ratios = []
    for a in range(len(cam_board)):
        for b in range(a + 1, len(cam_board)):
            db, dw = np.linalg.norm(cam_board[a] - cam_board[b]), np.linalg.norm(cam_world[a] - cam_world[b])
            if db > 2:   # ignore near-identical views (ratio dominated by noise)
                ratios.append(dw / db)
    square_m = float(np.median(ratios))

    # Coverage image: every corner used, over one frame
    cov = by_index[dets[0].index].load_image().copy() // 3
    for d in dets:
        for p in d.corners:
            cv2.circle(cov, tuple(np.round(p).astype(int)), 1, (80, 220, 120), -1)
    cv2.imwrite(str(out / "coverage.jpg"), cv2.cvtColor(cov, cv2.COLOR_RGB2BGR))

    def pct(a, b):
        return f"{100 * (a - b) / b:+.1f}%"

    lines = ["# Zhang calibration: TUM fr3 checkerboard", "",
             f"{len(dets)} of {len(frames[::STEP])} sampled frames show the full {PATTERN[0]}x{PATTERN[1]} board. "
             f"Board tilt: median {np.median(tilts):.0f} deg, max {np.max(tilts):.0f} deg (nearly face-on).", "",
             f"TUM official: fx {K_tum[0, 0]}, fy {K_tum[1, 1]}, cx {K_tum[0, 2]}, cy {K_tum[1, 2]}, no distortion.", "",
             "| variant | views | fx | fy | cx | cy | fx vs official | fx bootstrap std | corner RMS (px) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for name, n, c, sd in rows:
        mark = " **(chosen)**" if name == CHOSEN else ""
        lines.append(f"| {name}{mark} | {n} | {c.K[0, 0]:.1f} | {c.K[1, 1]:.1f} | {c.K[0, 2]:.1f} | {c.K[1, 2]:.1f} | "
                     f"{pct(c.K[0, 0], K_tum[0, 0])} | {sd:.1f} | {c.rms_px:.3f} |")
    lines += ["", "Ambiguity check (views not used for calibration):", "",
              f"- K from {N_VIEWS} diverse views (fx {bad.K[0, 0]:.0f}, {pct(bad.K[0, 0], K_tum[0, 0])}): "
              f"corner RMS {rms_bad:.3f} px",
              f"- TUM official K (fx {K_tum[0, 0]:.0f}): corner RMS {rms_tum:.3f} px",
              "- Nearly equal: face-on views cannot tell a long focal length + far board from a short "
              "focal length + near board, so a low reprojection error alone does not prove a good K.", "",
              f"Board square size from calibration vs motion capture: {1000 * square_m:.1f} mm "
              f"(median of {len(ratios)} view pairs; IQR {1000 * np.percentile(ratios, 25):.1f}-"
              f"{1000 * np.percentile(ratios, 75):.1f} mm).", ""]
    (out / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    (out / "camera.json").write_text(json.dumps({
        "source": f"TUM fr3 checkerboard_large, Zhang calibration ({CHOSEN})", "image_size": [w, h],
        "K": cal.K.tolist(), "dist": cal.dist.tolist(), "rms_px": cal.rms_px, "square_m": square_m}, indent=2))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
