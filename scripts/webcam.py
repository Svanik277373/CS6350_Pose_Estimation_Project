"""Phase 11: live relative pose from the laptop webcam.

    venv\\Scripts\\python.exe scripts\\webcam.py                            live, focal guessed from --hfov
    venv\\Scripts\\python.exe scripts\\webcam.py --K results\\calibration\\webcam.json --size 0.15
    venv\\Scripts\\python.exe scripts\\webcam.py --make-board              checkerboard to print / show on a phone
    venv\\Scripts\\python.exe scripts\\webcam.py --calibrate               Zhang calibration of the webcam
    venv\\Scripts\\python.exe scripts\\webcam.py --replay co3d/handbag/seq08   dataset video instead of the camera,
                                                                          scored against ground truth

Live keys:
    r        freeze the frame and draw a box around the object: this is the reference view
    m        next method (xfeat_lg -> sift -> aliked_lg -> fast)
    s        save a snapshot of the window to results/webcam/
    q / Esc  quit

On screen: the object's rotation since the reference (angle, and about the camera's x / y / z
axes), the translation direction (in metres with --size), inliers, reprojection error, and
the time per estimate. The pose is computed in a background thread, so the video stays
smooth; the numbers refresh as fast as the method allows (~2 per second with xfeat_lg).
With the camera still and the object moved by hand, R and t are the object's own motion in
camera axes (x right, y down, z forward); see src/pipeline/live.py.

Calibration (--calibrate): show a checkerboard (--make-board; on paper or a phone/tablet
screen) and move it so the camera sees it at many *tilts* -- face-on views alone leave the
focal length undetermined (results/calibration/summary.md). Views are captured
automatically when the board is found in a new orientation; press c to calibrate once
enough are collected. Two models are fitted (with and without lens distortion) and the one
with the lower error on held-out views is saved to results/calibration/webcam.json.
"""
import argparse
import json
import sys
import threading
import time
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.pipeline import calibration as C  # noqa: E402
from src.pipeline.live import LiveTracker, mask_box  # noqa: E402

OUT = ROOT / "results" / "webcam"
CAL = ROOT / "results" / "calibration"
METHODS = ["xfeat_lg", "sift", "aliked_lg", "fast"]
AXIS_BGR = [(60, 60, 230), (60, 200, 60), (230, 120, 40)]     # x red, y green, z blue
FONT = cv2.FONT_HERSHEY_SIMPLEX


# --------------------------------------------------------------------------------------------- drawing
def intrinsics(args, w, h):
    if args.K:
        cam = json.loads(Path(args.K).read_text())
        K = np.array(cam["K"], float)
        cw, ch = cam.get("image_size", [w, h])
        K[0] *= w / cw
        K[1] *= h / ch
        return K, np.array(cam.get("dist", [0] * 5), float), f"K from {Path(args.K).name}"
    f = args.focal or (w / 2) / np.tan(np.radians(args.hfov) / 2)
    note = f"focal {f:.0f} px" + ("" if args.focal else f" guessed from hfov {args.hfov:g} deg (calibrate for accuracy)")
    return np.array([[f, 0, (w - 1) / 2], [0, f, (h - 1) / 2], [0, 0, 1.0]]), np.zeros(5), note


def panel(img, lines, origin=(10, 10)):
    """Dark box with text lines (text stays readable on any background)."""
    x, y = origin
    scale, th = 0.55, 1
    widest = max(cv2.getTextSize(s, FONT, scale, th)[0][0] for s in lines) + 16
    scale *= min(1.0, (img.shape[1] - 2 * x) / widest)          # narrow (portrait) frames: smaller text
    lh = int(round(40 * scale))
    width = max(cv2.getTextSize(s, FONT, scale, th)[0][0] for s in lines) + 16
    if y < 0:                                                   # negative y: from the bottom edge
        y = img.shape[0] + y - (lh * len(lines) + 10)
    over = img.copy()
    cv2.rectangle(over, (x, y), (x + width, y + lh * len(lines) + 10), (25, 25, 25), -1)
    cv2.addWeighted(over, 0.75, img, 0.25, 0, img)
    for i, s in enumerate(lines):
        cv2.putText(img, s, (x + 8, y + lh - 2 + lh * i), FONT, scale, (240, 240, 240), th, cv2.LINE_AA)


def draw_axes(img, R, centre, length):
    """Reference axes (faint) and the same axes rotated by R, drawn from the object's centre.
    Each axis end is the 3D direction's x/y components; the z component (towards / away from
    the camera) shows as the end's size."""
    c = np.asarray(centre, float)
    for i in range(3):
        e = np.eye(3)[i]
        cv2.line(img, tuple(np.int32(c)), tuple(np.int32(c + length * e[:2])), (150, 150, 150), 1, cv2.LINE_AA)
    for i in np.argsort(-R[2]):                      # far axes first, near ones drawn on top
        d = R[:, i]
        end = c + length * d[:2]
        cv2.line(img, tuple(np.int32(c)), tuple(np.int32(end)), AXIS_BGR[i], 3, cv2.LINE_AA)
        cv2.circle(img, tuple(np.int32(end)), int(4 + 3 * max(0.0, -d[2])), AXIS_BGR[i], -1, cv2.LINE_AA)


def overlay(frame_bgr, out, method, note, fps=None, height=None):
    """height: draw at this display height (coordinates scaled), so text and marks stay legible."""
    s = 1.0 if height is None else height / frame_bgr.shape[0]
    img = frame_bgr.copy() if s == 1.0 else cv2.resize(frame_bgr, (round(frame_bgr.shape[1] * s), height),
                                                       interpolation=cv2.INTER_AREA)
    if out is None:
        panel(img, ["press r: draw a box around the object (reference view)", f"method {method}  |  {note}"])
        return img
    res = out.res
    if out.box_used is not None:
        x0, y0, x1, y1 = (int(v * s) for v in out.box_used)
        cv2.rectangle(img, (x0, y0), (x1, y1), (0, 200, 255), 2)
    if res.ok and res.pts2 is not None:
        for p in res.pts2[:: max(1, len(res.pts2) // 200)] * s:
            cv2.circle(img, tuple(np.int32(p)), 2, (60, 220, 60), -1)
        box = np.array(out.box_used or (0, 0, frame_bgr.shape[1], frame_bgr.shape[0])) * s
        centre = np.median(res.pts2, axis=0) * s
        draw_axes(img, res.R, centre, 0.3 * min(box[2] - box[0], box[3] - box[1]))
        ex, ey, ez = out.euler_deg
        t = np.asarray(res.t, float)
        lines = [f"rotation {out.angle_deg:5.1f} deg   (x {ex:+5.1f}, y {ey:+5.1f}, z {ez:+5.1f})",
                 "t direction [" + ", ".join(f"{v:+.2f}" for v in t) + "]"]
        if out.t_metres is not None:
            lines.append("t = [" + ", ".join(f"{v:+.3f}" for v in out.t_metres) + f"] m  (|t| {np.linalg.norm(out.t_metres):.3f} m)")
        lines.append(f"{res.model}  inliers {res.n_inliers}/{res.n_matches}  reproj {res.reproj_rms_px:.2f} px")
    else:
        lines = [f"no pose: {res.reason}"]
    lines.append(f"{method}  {1000 * out.seconds:.0f} ms/estimate" + (f"  |  video {fps:.0f} fps" if fps else ""))
    panel(img, lines)
    return img


# --------------------------------------------------------------------------------------------- live
class Worker(threading.Thread):
    """Runs the tracker on the newest frame whenever it is free; the display never waits for it."""

    def __init__(self, tracker):
        super().__init__(daemon=True)
        self.tracker, self.frame, self.out, self.lock = tracker, None, None, threading.Lock()
        self.stop, self.generation = False, 0

    def submit(self, frame_rgb, tag=None):
        with self.lock:
            self.frame, self.tag = frame_rgb, tag

    def reset(self):
        with self.lock:
            self.out, self.frame = None, None
            self.generation += 1

    def run(self):
        while not self.stop:
            with self.lock:
                frame, self.frame, gen, tag = self.frame, None, self.generation, getattr(self, "tag", None)
            if frame is None or self.tracker.ref is None:
                time.sleep(0.01)
                continue
            out = self.tracker.update(frame)
            out.tag = tag                            # which frame this pose belongs to
            with self.lock:
                if gen == self.generation:          # drop results computed for an old reference
                    self.out = out


def open_camera(index):
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) if sys.platform == "win32" else cv2.VideoCapture(index)
    if not cap.isOpened():
        raise SystemExit(f"cannot open camera {index}")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return cap


def live(args):
    """--video plays a file through the same loop (testing without a camera); --box sets the
    reference on the first frame; --frames N stops after N frames without opening a window."""
    cap = cv2.VideoCapture(args.video) if args.video else open_camera(args.camera)
    ok, frame = cap.read()
    if not ok:
        raise SystemExit("no frames from " + (args.video or f"camera {args.camera}"))
    h, w = frame.shape[:2]
    K, dist, note = intrinsics(args, w, h)
    undistort = np.any(dist != 0)
    print(f"{'video' if args.video else 'camera'} {w}x{h}; {note}")
    methods = METHODS if args.method in METHODS else [args.method] + METHODS
    k = methods.index(args.method)
    tracker = LiveTracker(K, method=methods[k], size_m=args.size)
    worker = Worker(tracker)
    worker.start()
    headless = args.frames is not None
    win = "TPA-12 live pose (r: reference, m: method, s: snapshot, q: quit)"
    if not headless:
        cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    if args.box:
        tracker.set_reference(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), box=tuple(args.box))
    last, fps, n, seen = time.perf_counter(), None, 0, set()
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        n += 1
        if undistort:
            frame = cv2.undistort(frame, K, dist)
        worker.submit(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), tag=n)
        if headless:
            time.sleep(1 / 30)                     # play the file at camera speed
            with worker.lock:
                out = worker.out
            if out is not None and id(out) not in seen:
                seen.add(id(out))
                print(f"frame {out.tag:4d} (shown at {n:4d}): " + (f"rotation {out.angle_deg:5.1f} deg, inliers {out.res.n_inliers}, "
                                           f"{1000 * out.seconds:.0f} ms" if out.res.ok else f"no pose ({out.res.reason})"))
            if n >= args.frames:
                break
            continue
        now = time.perf_counter()
        fps = 1 / (now - last) if fps is None else 0.9 * fps + 0.1 / max(now - last, 1e-3)
        last = now
        with worker.lock:
            out = worker.out
        shown = overlay(frame, out if tracker.ref is not None else None, tracker.method, note, fps)
        cv2.imshow(win, shown)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break
        if key == ord("r"):
            x, y, bw, bh = cv2.selectROI(win, frame, showCrosshair=False)
            box = (x, y, x + bw, y + bh) if bw > 10 and bh > 10 else None
            worker.reset()
            tracker.set_reference(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), box=box)
        if key == ord("m"):
            k = (k + 1) % len(methods)
            tracker.method = methods[k]
            worker.reset()
        if key == ord("s"):
            OUT.mkdir(parents=True, exist_ok=True)
            path = OUT / f"snapshot_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(str(path), shown)
            print("saved", path)
    worker.stop = True
    cap.release()
    cv2.destroyAllWindows()
    if headless:
        print(f"{n} frames shown, {len(seen)} pose estimates ({len(seen) / max(n / 30, 1e-9):.1f} per second of video)")


# --------------------------------------------------------------------------------------------- calibration
def make_board(args):
    cols, rows = args.pattern                      # inner corners
    sq = 100
    img = np.full(((rows + 3) * sq, (cols + 3) * sq), 255, np.uint8)
    for r in range(rows + 1):
        for c in range(cols + 1):
            if (r + c) % 2 == 0:
                img[(r + 1) * sq:(r + 2) * sq, (c + 1) * sq:(c + 2) * sq] = 0
    CAL.mkdir(parents=True, exist_ok=True)
    path = CAL / f"board_{cols}x{rows}.png"
    cv2.imwrite(str(path), img)
    print(f"wrote {path}: {cols + 1}x{rows + 1} squares = {cols}x{rows} inner corners. Print it flat, "
          "or show it full-screen on a phone or tablet.")


def heldout_rms(detections, pattern, size, flags, folds=4):
    """Corner RMS on views left out of the calibration (k-fold): a model that only fits noise
    (e.g. distortion terms from a few views) scores worse here than on its own views."""
    obj = C.board_points(pattern)
    errs = []
    idx = np.arange(len(detections))
    for f in range(folds):
        test, train = idx[f::folds], np.setdiff1d(idx, idx[f::folds])
        cal = C.calibrate([detections[i] for i in train], pattern, size, flags=flags)
        for i in test:
            img = detections[i].corners.astype(np.float32)
            ok, rv, tv = cv2.solvePnP(obj, img, cal.K, cal.dist)
            proj = cv2.projectPoints(obj, rv, tv, cal.K, cal.dist)[0].reshape(-1, 2)
            errs.append(np.mean(np.sum((proj - img) ** 2, axis=1)))
    return float(np.sqrt(np.mean(errs)))


def calibrate_live(args):
    pattern = tuple(args.pattern)
    cap = open_camera(args.camera)
    win = "calibration (move the board to many tilts; c: calibrate, q: quit)"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    detections, feats, size, last_try = [], [], None, 0.0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        size = (frame.shape[1], frame.shape[0])
        shown = frame.copy()
        if time.perf_counter() - last_try > 0.3:            # detection is slow; a few tries per second
            last_try = time.perf_counter()
            corners = C.detect(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), pattern)
            if corners is not None:
                cv2.drawChessboardCorners(shown, pattern, corners.reshape(-1, 1, 2).astype(np.float32), True)
                f = C._view_features(corners, pattern, size)
                if not feats or np.min(np.linalg.norm(np.array(feats) - f, axis=1)) > 0.25:   # a new view
                    detections.append(C.Detection(len(detections), corners))
                    feats.append(f)
        tilts = [C.tilt_deg(d, pattern, size) for d in detections]
        panel(shown, [f"views {len(detections)} (want >= 15)   max tilt {max(tilts, default=0):.0f} deg (want >= 30)",
                      "tilt the board left/right/up/down, near and far; c: calibrate, q: quit"])
        cv2.imshow(win, shown)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break
        if key == ord("c") and len(detections) >= 8:
            break
    cap.release()
    cv2.destroyAllWindows()
    if len(detections) < 8:
        raise SystemExit(f"only {len(detections)} views; need at least 8 (15+ is better)")

    no_dist = cv2.CALIB_FIX_K1 | cv2.CALIB_FIX_K2 | cv2.CALIB_FIX_K3 | cv2.CALIB_ZERO_TANGENT_DIST
    models = {"no distortion": no_dist, "radial + tangential distortion": cv2.CALIB_FIX_K3}
    scores = {name: heldout_rms(detections, pattern, size, fl) for name, fl in models.items()}
    best = min(scores, key=scores.get)
    cal = C.calibrate(detections, pattern, size, flags=models[best])
    for name, s in scores.items():
        print(f"{name:32s} held-out corner RMS {s:.3f} px" + ("   <- chosen" if name == best else ""))
    print(f"K =\n{np.round(cal.K, 1)}\nfx std {cal.K_std[0]:.1f} px, corner RMS {cal.rms_px:.3f} px, "
          f"{len(detections)} views, max tilt {max(C.tilt_deg(d, pattern, size) for d in detections):.0f} deg")
    CAL.mkdir(parents=True, exist_ok=True)
    path = CAL / "webcam.json"
    path.write_text(json.dumps(dict(source=f"webcam {args.camera}, Zhang calibration ({best}), {len(detections)} views",
                                    image_size=list(size), K=cal.K.tolist(), dist=cal.dist.tolist(),
                                    rms_px=cal.rms_px, heldout_rms_px=scores[best]), indent=2))
    print("saved", path)


# --------------------------------------------------------------------------------------------- replay
def replay(args):
    """A dataset sequence as a stand-in for the camera: same tracker, frames in order, the first
    frame (its mask's box) as reference; every estimate is compared with the ground truth."""
    from src.loaders import co3d, mvimgnet, objectron
    from src.loaders.common import relative_pose
    from src.pipeline import rotation_error_deg, translation_angle_deg
    from src.pipeline.metrics import pose_auc
    ds, obj, seq = args.replay.split("/")
    mod = {"co3d": co3d, "mvimgnet": mvimgnet, "objectron": objectron}[ds]
    seq_dir = ROOT / "data" / ds / obj / seq
    frames = sorted(mod.load_frames(seq_dir), key=lambda f: f.index)
    if ds == "objectron":
        frames = [f for f in frames if (seq_dir / "frames" / f"{f.index:04d}.jpg").exists()]
    frames = frames[args.start::args.every][: args.max_frames]
    ref = frames[0]
    ref_img = ref.load_image()
    tracker = LiveTracker(ref.K, method=args.method, size_m=args.size)
    tracker.set_reference(ref_img, box=mask_box(ref.load_mask()))
    name = f"replay_{ds}_{obj}_{seq}_{args.method}"
    OUT.mkdir(parents=True, exist_ok=True)
    h = 720
    writer, rows = None, []
    for f in frames[1:]:
        img = f.load_image()
        out = tracker.update(img, K2=f.K)
        R_gt, t_gt = relative_pose(ref.R, ref.t, f.R, f.t)
        angle = float(np.degrees(np.arccos(np.clip((np.trace(R_gt) - 1) / 2, -1, 1))))
        res = out.res
        rot = rotation_error_deg(res.R, R_gt) if res.ok else np.inf
        tra = translation_angle_deg(res.t, t_gt) if res.ok else np.inf
        err = rot if np.isnan(tra) else max(rot, tra)
        rows.append(dict(frame=f.index, gt_angle=angle, err=err, rot_err=rot, t_err=tra, ok=res.ok, inliers=res.n_inliers,
                         seconds=out.seconds, searched_full=out.box_used is None))
        shown = overlay(cv2.cvtColor(img, cv2.COLOR_RGB2BGR), out, args.method, f"replay {args.replay}", height=h)
        panel(shown, [f"truth: rotation {angle:5.1f} deg", f"error: rotation {rot:5.1f}, pose {err:5.1f} deg"],
              origin=(10, -10))
        if writer is None:
            writer = cv2.VideoWriter(str(OUT / f"{name}.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), 8,
                                     (shown.shape[1], shown.shape[0]))
        writer.write(shown)
        if args.show:
            cv2.imshow("replay", shown)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
        print(f"frame {f.index:4d}  gt {angle:5.1f} deg  err {err:6.2f} deg  inliers {res.n_inliers:4d}  "
              f"{1000 * out.seconds:5.0f} ms" + ("  [full frame]" if out.box_used is None else ""))
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()

    import pandas as pd
    d = pd.DataFrame(rows)
    d.to_csv(OUT / f"{name}.csv", index=False)
    lines = [f"# Live tracker replay: {args.replay}, {args.method}", "",
             f"{len(d)} frames after the reference (every {args.every}th from {args.start}); "
             "pose of each frame relative to the first, error vs ground truth.", "",
             "Pose error = max(rotation error, translation-direction error). With almost no camera motion "
             "(first frames) the translation direction is undefined, so the rotation error is shown separately.", "",
             "| ground-truth rotation | frames | AUC@10 | median pose error (deg) | median rotation error (deg) "
             "| within 10 deg | median ms |",
             "|---|---|---|---|---|---|---|"]
    for lo, hi in [(0, 5), (5, 15), (15, 30), (30, 60), (60, 180)]:
        s = d[(d.gt_angle >= lo) & (d.gt_angle < hi)]
        if len(s):
            lines.append(f"| {lo}-{hi} deg | {len(s)} | {pose_auc(s.err.to_numpy())[10]:.1f} | {s.err.median():.2f} | "
                         f"{s.rot_err.median():.2f} | {100 * (s.err < 10).mean():.0f}% | {1000 * s.seconds.median():.0f} |")
    lines += ["", f"Whole frame searched (object lost) on {100 * d.searched_full.mean():.0f}% of frames.",
              f"Video: {name}.mp4"]
    (OUT / f"{name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--K", help="camera JSON (from --calibrate)")
    ap.add_argument("--focal", type=float, help="focal length in pixels")
    ap.add_argument("--hfov", type=float, default=70.0, help="horizontal field of view guess when no K/focal")
    ap.add_argument("--method", default="xfeat_lg")
    ap.add_argument("--size", type=float, help="object's longest dimension in metres -> metric t")
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--make-board", action="store_true")
    ap.add_argument("--pattern", type=int, nargs=2, default=[9, 6], metavar=("COLS", "ROWS"),
                    help="inner corners of the checkerboard")
    ap.add_argument("--replay", help="dataset/object/seq, e.g. co3d/handbag/seq08")
    ap.add_argument("--every", type=int, default=2, help="replay: use every n-th frame")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--max-frames", type=int, default=60)
    ap.add_argument("--show", action="store_true", help="replay: show the window as well")
    ap.add_argument("--video", help="live mode from a video file instead of the camera (testing)")
    ap.add_argument("--box", type=int, nargs=4, metavar=("X0", "Y0", "X1", "Y1"),
                    help="live: reference box on the first frame (instead of pressing r)")
    ap.add_argument("--frames", type=int, help="live: stop after N frames, no window (testing)")
    args = ap.parse_args()
    if args.make_board:
        make_board(args)
    elif args.calibrate:
        calibrate_live(args)
    elif args.replay:
        replay(args)
    else:
        live(args)


if __name__ == "__main__":
    main()
