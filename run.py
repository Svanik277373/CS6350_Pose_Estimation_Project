"""Relative 3D pose of an object between two photos.

    venv\\Scripts\\python.exe run.py view1.jpg view2.jpg --K results\\calibration\\camera.json
    venv\\Scripts\\python.exe run.py a.jpg b.jpg --focal 1450 --mask1 a_mask.png --mask2 b_mask.png
    venv\\Scripts\\python.exe run.py a.jpg b.jpg --focal 1450 --box1 300 200 900 700 --box2 350 180 950 690
    venv\\Scripts\\python.exe run.py a.jpg b.jpg --K cam.json --method mast3r --size 0.15 --save out.jpg

Output: the rotation R and translation direction t that map camera-1 coordinates to camera-2
coordinates (OpenCV convention, X_cam2 = R X_cam1 + t), the rotation angle, the
reprojection error of the inlier matches, and -- with --size, the object's longest dimension
in metres -- the translation in metres.

Object only: give the object's region in each image (--mask*/--box*), so only points on the
object are used. Without them the whole image is used ("with surroundings"), which is a
different problem when the background moves differently from the object.

Methods (--method): fast (~0.5 s on CPU), accurate (~1-3 s; default), confident (XFeat+LightGlue,
SIFT, outline; MASt3R only when a learned confidence says the pose is doubtful: ~0.5 s typical,
~8 s mean), mast3r (~20 s, most accurate), or a single matcher: sift, orb, xfeat, xfeat_lg,
aliked_lg, disk_lg, loftr.
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.pipeline import (ALL_PRESETS, CONFIDENT, PRESETS, estimate_pose, estimate_pose_cascade,  # noqa: E402
                          estimate_pose_confident)
from src.pipeline.match import MATCHERS  # noqa: E402
from src.pipeline.scale import size_scale  # noqa: E402


def read_rgb(path):
    img = cv2.imread(str(path))
    if img is None:
        raise SystemExit(f"cannot read image {path}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def read_K(args, shape):
    h, w = shape[:2]
    if args.K:
        cam = json.loads(Path(args.K).read_text())
        K = np.array(cam["K"], float)
        cw, ch = cam.get("image_size", [w, h])
        if (cw, ch) != (w, h):   # calibrated at another resolution: scale K with the image
            K[0] *= w / cw
            K[1] *= h / ch
        return K
    if args.focal:
        return np.array([[args.focal, 0, (w - 1) / 2], [0, args.focal, (h - 1) / 2], [0, 0, 1.0]])
    raise SystemExit("give the camera intrinsics: --K camera.json (scripts/calibrate.py) or --focal <pixels>")


def read_mask(mask_path, box, shape):
    if mask_path:
        m = cv2.imread(str(mask_path), cv2.IMREAD_UNCHANGED)
        if m is None:
            raise SystemExit(f"cannot read mask {mask_path}")
        if m.ndim == 3:
            m = m[..., 3] if m.shape[2] == 4 else m[..., 0]
        if m.shape[:2] != shape[:2]:
            m = cv2.resize(m, (shape[1], shape[0]), interpolation=cv2.INTER_NEAREST)
        return m > 127 if m.max() > 1 else m > 0
    if box:
        x0, y0, x1, y1 = box
        m = np.zeros(shape[:2], bool)
        m[max(0, y0):y1, max(0, x0):x1] = True
        return m
    return None


def draw(img1, img2, res, path, max_lines=150):
    h = 600
    s1, s2 = h / img1.shape[0], h / img2.shape[0]
    a = cv2.resize(img1, (round(img1.shape[1] * s1), h))
    b = cv2.resize(img2, (round(img2.shape[1] * s2), h))
    canvas = cv2.cvtColor(np.hstack([a, b]), cv2.COLOR_RGB2BGR)
    if res.ok and res.pts1 is not None:
        idx = np.random.default_rng(0).permutation(len(res.pts1))[:max_lines]
        for p, q in zip(res.pts1[idx] * s1, res.pts2[idx] * s2):
            q = q + [a.shape[1], 0]
            cv2.line(canvas, tuple(np.round(p).astype(int)), tuple(np.round(q).astype(int)), (60, 200, 60), 1, cv2.LINE_AA)
    text = (f"{res.model}  inliers {res.n_inliers}  reproj {res.reproj_rms_px:.2f}px" if res.ok
            else f"FAILED: {res.reason}")
    cv2.rectangle(canvas, (0, 0), (canvas.shape[1], 40), (30, 30, 30), -1)
    cv2.putText(canvas, text, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (240, 240, 240), 1, cv2.LINE_AA)
    cv2.imwrite(str(path), canvas)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image1")
    ap.add_argument("image2")
    ap.add_argument("--K", help="camera JSON with 'K' (and 'image_size'), e.g. from scripts/calibrate.py")
    ap.add_argument("--K2", help="second camera's JSON if the views come from different cameras")
    ap.add_argument("--focal", type=float, help="focal length in pixels (principal point = image centre)")
    ap.add_argument("--mask1")
    ap.add_argument("--mask2")
    ap.add_argument("--box1", type=int, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--box2", type=int, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--method", default="accurate", choices=ALL_PRESETS + MATCHERS)
    ap.add_argument("--size", type=float, help="object's longest dimension in metres -> metric translation")
    ap.add_argument("--save", help="write a picture of the inlier matches here")
    ap.add_argument("--json", help="write the result as JSON here")
    args = ap.parse_args()

    img1, img2 = read_rgb(args.image1), read_rgb(args.image2)
    K1 = read_K(args, img1.shape)
    K2 = read_K(argparse.Namespace(K=args.K2 or args.K, focal=args.focal), img2.shape)
    m1 = read_mask(args.mask1, args.box1, img1.shape)
    m2 = read_mask(args.mask2, args.box2, img2.shape)
    if (m1 is None) != (m2 is None):
        raise SystemExit("give the object region for both images, or for neither")
    if m1 is None:
        print("note: no object region given -- using the whole images (object + surroundings)")

    if args.method in CONFIDENT:
        res = estimate_pose_confident(img1, img2, K1, K2, m1, m2, preset=args.method)
    elif args.method in PRESETS:
        res = estimate_pose_cascade(img1, img2, K1, K2, m1, m2, preset=args.method)
    else:
        res = estimate_pose(img1, img2, K1, K2, m1, m2, matcher=args.method, crop=m1 is not None)

    out = dict(ok=bool(res.ok), method=args.method, reason=res.reason, seconds=round(res.seconds, 2))
    if res.ok:
        angle = float(np.degrees(np.arccos(np.clip((np.trace(res.R) - 1) / 2, -1, 1))))
        out |= dict(R=res.R.round(6).tolist(), t_direction=np.asarray(res.t).round(6).tolist(),
                    rotation_deg=round(angle, 3), model=res.model, inliers=res.n_inliers, matches=res.n_matches,
                    reprojection_rms_px=round(float(res.reproj_rms_px), 3))
        if args.size and res.pts1 is not None:
            # extent of the matched 3D points (measured more accurate than the mask outline, results/scale)
            s = size_scale(res.R, res.t, K1, K2, res.pts1, res.pts2, args.size)[0]
            if np.isfinite(s):
                out["t_metres"] = (s * np.asarray(res.t)).round(4).tolist()
                out["baseline_m"] = round(float(s), 4)

    if res.ok:
        print(f"pose ({out['model']}, {out['inliers']}/{out['matches']} inliers, {out['seconds']} s)")
        print("R =\n" + "\n".join("  " + "  ".join(f"{v:+.4f}" for v in row) for row in res.R))
        print("t direction = [" + ", ".join(f"{v:+.4f}" for v in res.t) + "]")
        print(f"rotation {out['rotation_deg']:.2f} deg, reprojection RMS {out['reprojection_rms_px']:.2f} px")
        if "t_metres" in out:
            print(f"t = {out['t_metres']} m  (baseline {out['baseline_m']} m, from --size {args.size} m)")
        print(f"answered by: {res.reason}" if res.reason else "")
    else:
        print(f"no pose: {res.reason}")
    if args.save:
        draw(img1, img2, res, args.save)
    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
