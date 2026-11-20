"""Relative 3D pose of an object from two photos, with nothing known about camera or object.

    venv\\Scripts\\python.exe auto_run.py a.jpg b.jpg --object "wallet" --method mast3r --save out.jpg
    venv\\Scripts\\python.exe auto_run.py a.jpg b.jpg --select --save out.jpg
    venv\\Scripts\\python.exe auto_run.py a.jpg b.jpg --save out.jpg

For photos you are handed without calibration or annotations (e.g. a live demo). Uses the
same pose pipeline as run.py -- which is left unchanged, as the benchmark results come from
it -- and adds, in new modules only:

  focal length   --K / --focal if given; else EXIF; else estimated by MASt3R from the image
                 content; else a 70 deg field-of-view guess (src/pipeline/focal.py)
  object region  --mask / --box if given; else --select (draw a box with the mouse); else
                 fully automatic (src/pipeline/region.py): SAM 2.1 segments the image, the
                 compact segment not touching the border is the object, and the same object
                 is found in image 2 by matching; if there is no separate object (it fills
                 the frame) the whole images are used. --object "name" lets the YOLO-World
                 detector try first (used only when confident). --region v2 (default) uses
                 the rule tuned on the tuning split (src/pipeline/region2.py), as in the final
                 report; --region v1 is the original rule.
  object mask    boxes are cut down to the object's outline by SAM 2.1, or GrabCut if SAM
                 is unavailable (src/pipeline/segment.py)
  verdict        RELIABLE / UNCERTAIN / NO RESULT from inliers, reprojection error, rotation
                 size and how the focal length was obtained

With --save out.jpg it also writes out_mask1.jpg and out_mask2.jpg: check that the green area
is the object before trusting the pose.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from run import draw, read_mask, read_rgb  # noqa: E402  (unchanged helpers of run.py)
from src.pipeline import (ALL_PRESETS, CONFIDENT, PRESETS, estimate_pose, estimate_pose_cascade,  # noqa: E402
                          estimate_pose_confident)
from src.pipeline.detect import find_box, select_box  # noqa: E402
from src.pipeline.focal import K_from_focal, auto_focals  # noqa: E402
from src.pipeline.match import MATCHERS  # noqa: E402
from src.pipeline.region import find_regions as auto_regions  # noqa: E402
from src.pipeline import region2  # noqa: E402  (tuned region rule, the default: --region v2)
from src.pipeline.scale import size_scale  # noqa: E402
from src.pipeline.segment import auto_mask, draw_mask  # noqa: E402


def given_K(args, which, shape):
    """K from --K/--K2 (scaled to the image size) or --focal; None if neither was given."""
    path = (args.K2 or args.K) if which == 2 else args.K
    h, w = shape[:2]
    if path:
        cam = json.loads(Path(path).read_text())
        K = np.array(cam["K"], float)
        cw, ch = cam.get("image_size", [w, h])
        if (cw, ch) != (w, h):
            K[0] *= w / cw
            K[1] *= h / ch
        return K
    if args.focal:
        return K_from_focal(args.focal, shape)
    return None


def is_box(mask):
    """The mask fills its bounding rectangle: a box, not an object outline."""
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return False
    return len(xs) / ((xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1)) > 0.995


def find_regions(args, img1, img2):
    """Boxes for both images: mouse (--select) or detector, with the mouse as fallback."""
    boxes, want = [], None
    for i, img in enumerate((img1, img2), 1):
        box, label = None, ""
        if not args.select:
            box, label, conf = find_box(img, args.object, want_class=want)
            if box is None:
                print(f"image {i}: {label} -- draw the box with the mouse instead")
            else:
                want = label
                label = f"'{label}' detected, confidence {conf:.2f}"
        if box is None:
            box = select_box(img, f"image {i}: drag a box around the object, then press ENTER")
            label = "box drawn by hand"
        if box is None:
            raise SystemExit(f"no object region for image {i}")
        boxes.append(box)
        print(f"image {i}: box {box[0]} {box[1]} {box[2]} {box[3]}  ({label})")
    return boxes


def make_masks(img1, img2, box1, box2, save):
    """SAM 2.1 masks from the boxes; GrabCut if SAM fails; the box itself as a last resort."""
    masks = []
    for i, (img, box) in enumerate(((img1, box1), (img2, box2)), 1):
        m, note = auto_mask(img, box, "sam")
        if is_box(m):
            m, note = auto_mask(img, box, "grabcut")
        print(f"mask {i}: {note}")
        masks.append(m)
        if save:
            stem = Path(save)
            draw_mask(img, m, stem.with_name(f"{stem.stem}_mask{i}.jpg"), note)
    return masks


def verdict(res, focal_src, method, box_masks, region_mode="given"):
    """Trust level from the internal checks. A pose can be self-consistent and still describe
    the wrong thing (e.g. matches on the table), so also look at the saved pictures."""
    if not res.ok:
        return "NO RESULT -- " + res.reason
    if box_masks and "shape" in (res.reason or ""):
        return "NO RESULT -- the outline stage answered, but the mask is only a box (no real outline)"
    notes, level = [], "RELIABLE"
    if res.n_inliers < 30:
        level = "UNCERTAIN"
        notes.append(f"only {res.n_inliers} inliers")
    if not np.isfinite(res.reproj_rms_px) or res.reproj_rms_px > 2.0:
        level = "UNCERTAIN"
        notes.append(f"reprojection error {res.reproj_rms_px:.1f} px")
    angle = np.degrees(np.arccos(np.clip((np.trace(res.R) - 1) / 2, -1, 1)))
    if angle > 60 and method != "mast3r":
        level = "UNCERTAIN"
        notes.append(f"{angle:.0f} deg rotation: matchers are unreliable beyond ~60 deg, try --method mast3r")
    if region_mode in ("scene", "none"):
        level = "SCENE MOTION ONLY"
        notes.append("whole images used: this is the camera's motion relative to the scene; it is the "
                     "object's pose change only if the object did not move relative to its surroundings")
    elif region_mode == "unconfirmed":
        notes.append("object chosen by size/position, not confirmed by its motion")
    elif region_mode == "moved":
        notes.append("object confirmed: it moved differently from the background")
    if focal_src.startswith("DEFAULT"):
        level = "UNCERTAIN"
        notes.append("focal length is only a guess")
    elif "MASt3R" in focal_src or "GeoCalib" in focal_src:
        notes.append("focal length estimated, not measured -- a 15% error was seen on close-up photos")
    return level + (" -- " + "; ".join(notes) if notes else "")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image1")
    ap.add_argument("image2")
    ap.add_argument("--object", help='what the object is, e.g. "calculator" (helps the detector)')
    ap.add_argument("--select", action="store_true", help="draw the boxes with the mouse instead of detecting")
    ap.add_argument("--box1", type=int, nargs=4, metavar=("X0", "Y0", "X1", "Y1"), help="optional: known box")
    ap.add_argument("--box2", type=int, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--mask1", help="optional: known mask (then no detection/segmentation)")
    ap.add_argument("--mask2")
    ap.add_argument("--K", help="optional: camera JSON (skips focal estimation)")
    ap.add_argument("--K2", help="optional: second camera's JSON")
    ap.add_argument("--focal", type=float, help="optional: focal length in pixels (skips estimation)")
    ap.add_argument("--focal-method", default="mast3r", choices=["mast3r", "geocalib"],
                    help="how to estimate the focal length when there is no EXIF (default mast3r)")
    ap.add_argument("--method", default="mast3r", choices=ALL_PRESETS + MATCHERS,
                    help="pose method (default mast3r: most accurate, handles large viewpoint changes)")
    ap.add_argument("--region", default="v2", choices=["v2", "v1"],
                    help="automatic region rule: v2 (default, tuned on the tuning split, as in the final report) "
                         "or v1 (the original region.py rule)")
    ap.add_argument("--size", type=float, help="object's longest dimension in metres -> metric translation")
    ap.add_argument("--save", help="picture of the matches (+ _mask1/_mask2 pictures)")
    ap.add_argument("--json", help="write the result as JSON here")
    args = ap.parse_args()

    img1, img2 = read_rgb(args.image1), read_rgb(args.image2)

    # 1. focal length
    K1, K2 = given_K(args, 1, img1.shape), given_K(args, 2, img2.shape)
    focal_src = "given"
    if K1 is None or K2 is None:
        print(f"estimating the focal length (EXIF, else {args.focal_method}) ...")
        f1, f2, focal_src = auto_focals(args.image1, img1, args.image2, img2, method=args.focal_method)
        K1 = K1 if K1 is not None else K_from_focal(f1, img1.shape)
        K2 = K2 if K2 is not None else K_from_focal(f2, img2.shape)
    print(f"focal length: image 1 {K1[0, 0]:.0f} px, image 2 {K2[0, 0]:.0f} px  ({focal_src})")

    # 2. object region -> mask
    region_mode = "given"
    if args.mask1 and args.mask2:
        m1 = read_mask(args.mask1, None, img1.shape)
        m2 = read_mask(args.mask2, None, img2.shape)
    elif (args.box1 and args.box2) or args.select:
        box1, box2 = (args.box1, args.box2) if args.box1 and args.box2 else find_regions(args, img1, img2)
        m1, m2 = make_masks(img1, img2, box1, box2, args.save)
    else:
        # fully automatic: SAM 2.1 segments, same object in both images by matching (region.py)
        print(f"finding the object automatically (SAM 2.1, region rule {args.region}, ~15 s) ...")
        if args.region == "v2":
            # detector first if a name was given (as region.py does), else the tuned rule of region2.py
            m1 = None
            if args.object:
                m1, m2, note, region_mode = auto_regions(img1, img2, name=args.object)
                if region_mode != "detector":
                    m1 = None
            if m1 is None:
                m1, m2, note, region_mode = region2.find_regions(img1, img2)
        else:
            m1, m2, note, region_mode = auto_regions(img1, img2, name=args.object)
        print(f"object: {note}")
        if args.save and m1 is not None:
            stem = Path(args.save)
            for i, (img, m) in enumerate(((img1, m1), (img2, m2)), 1):
                draw_mask(img, m, stem.with_name(f"{stem.stem}_mask{i}.jpg"), note[:90])
    box_masks = m1 is not None and (is_box(m1) or is_box(m2))

    # 3. pose (the unchanged pipeline)
    if m1 is None:
        print("no separate object: using the whole images")
    print(f"estimating the pose with {args.method} ...")
    if args.method in CONFIDENT:
        res = estimate_pose_confident(img1, img2, K1, K2, m1, m2, preset=args.method)
    elif args.method in PRESETS:
        res = estimate_pose_cascade(img1, img2, K1, K2, m1, m2, preset=args.method)
    else:
        res = estimate_pose(img1, img2, K1, K2, m1, m2, matcher=args.method, crop=m1 is not None)
    if not res.ok and m1 is not None and region_mode in ("unconfirmed", "moved"):
        # the automatic region gave too little to work with: retry on the whole images
        print(f"no pose from the object region ({res.reason}); retrying with the whole images ...")
        m1 = m2 = None
        region_mode = "scene"
        if args.method in CONFIDENT:
            res = estimate_pose_confident(img1, img2, K1, K2, None, None, preset=args.method)
        elif args.method in PRESETS:
            res = estimate_pose_cascade(img1, img2, K1, K2, None, None, preset=args.method)
        else:
            res = estimate_pose(img1, img2, K1, K2, None, None, matcher=args.method, crop=False)

    # 4. report
    out = dict(ok=bool(res.ok), method=args.method, reason=res.reason, seconds=round(res.seconds, 2),
               focal_px=[round(float(K1[0, 0]), 1), round(float(K2[0, 0]), 1)], focal_source=focal_src)
    print()
    if res.ok:
        angle = float(np.degrees(np.arccos(np.clip((np.trace(res.R) - 1) / 2, -1, 1))))
        out |= dict(R=res.R.round(6).tolist(), t_direction=np.asarray(res.t).round(6).tolist(),
                    rotation_deg=round(angle, 3), model=res.model, inliers=res.n_inliers, matches=res.n_matches,
                    reprojection_rms_px=round(float(res.reproj_rms_px), 3))
        if args.size and res.pts1 is not None:
            s = size_scale(res.R, res.t, K1, K2, res.pts1, res.pts2, args.size)[0]
            if np.isfinite(s):
                out["t_metres"] = (s * np.asarray(res.t)).round(4).tolist()
        print(f"pose ({res.model}, {res.n_inliers}/{res.n_matches} inliers, {out['seconds']} s)")
        print("R =\n" + "\n".join("  " + "  ".join(f"{v:+.4f}" for v in row) for row in res.R))
        print("t direction = [" + ", ".join(f"{v:+.4f}" for v in res.t) + "]")
        print(f"rotation {angle:.2f} deg, reprojection RMS {res.reproj_rms_px:.2f} px")
        if "t_metres" in out:
            print(f"t = {out['t_metres']} m  (from --size {args.size} m)")
        if res.reason:
            print(f"answered by: {res.reason}")
    else:
        print(f"no pose: {res.reason}")
    out["verdict"] = verdict(res, focal_src, args.method, box_masks, region_mode)
    out["region_mode"] = region_mode
    print(f"verdict: {out['verdict']}")
    if args.save:
        draw(img1, img2, res, args.save)
        print(f"pictures: {args.save} (matches)" +
              (", plus the two mask pictures" if not (args.mask1 and args.mask2) else ""))
    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
