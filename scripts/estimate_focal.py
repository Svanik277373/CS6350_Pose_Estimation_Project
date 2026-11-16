"""Estimate each image's focal length (pixels) from MASt3R's 3D point map -- no EXIF, no
calibration. (run.py does this automatically when neither --K nor --focal is given.)

    venv\\Scripts\\python.exe scripts\\estimate_focal.py testing_sample_wallet\\0.jpeg testing_sample_wallet\\45.jpeg testing_sample_wallet\\90.jpeg --expected 1110

Each image is paired with every other one; per image the median over its pairs is reported.
See src/pipeline/focal.py for the method. --expected: a known focal length (e.g. from the
phone's specs) to report the error against.
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.pipeline.focal import exif_focal, geocalib_focal, mast3r_focal  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+", help="two or more photos from the same camera (same zoom)")
    ap.add_argument("--expected", type=float, help="known focal length in pixels, to compare against")
    ap.add_argument("--method", default="mast3r", choices=["mast3r", "geocalib"],
                    help="mast3r (needs 2+ images: works on pairs) or geocalib (one image at a time)")
    args = ap.parse_args()
    if args.method == "mast3r" and len(args.images) < 2:
        raise SystemExit("give at least two images (MASt3R works on pairs)")
    imgs = []
    for p in args.images:
        bgr = cv2.imread(p)
        if bgr is None:
            raise SystemExit(f"cannot read image {p}")
        imgs.append(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))

    def err(f):
        return f"  error {100 * (f - args.expected) / args.expected:+.1f}%" if args.expected else ""

    all_f = []
    for i, (path, a) in enumerate(zip(args.images, imgs)):
        ex = exif_focal(path, a.shape)
        if args.method == "geocalib":
            fs = [geocalib_focal(path, a.shape)]
        else:
            fs = [mast3r_focal(a, b) for j, b in enumerate(imgs) if j != i]
        f = float(np.median(fs))
        all_f.append(f)
        hfov = np.degrees(2 * np.arctan(a.shape[1] / 2 / f))
        print(f"{Path(path).name}: f = {f:.0f} px  (horizontal FOV {hfov:.1f} deg; pairs: "
              + ", ".join(f"{x:.0f}" for x in fs) + ")" + err(f)
              + (f"  [EXIF says {ex:.0f}]" if ex else ""))
    f = float(np.median(all_f))
    print(f"\nmedian over images: f = {f:.0f} px{err(f)}")
    print(f"use it as:  run.py ... --focal {f:.0f}")


if __name__ == "__main__":
    main()
