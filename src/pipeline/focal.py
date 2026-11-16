"""Focal length (pixels) without calibration, for run.py when neither --K nor --focal is given.

Tried in order:
  1. EXIF: phones store the 35 mm-equivalent focal length; f = f35 * image diagonal / 43.27 mm
     (43.27 mm = diagonal of a 36 x 24 mm frame). Exact, but messaging apps strip EXIF.
  2. MASt3R: it predicts a 3D point for every pixel in the camera's own frame; with the
     principal point at the image centre, the one unknown f is fitted to all of them
     (dust3r's estimate_focal_knowing_depth, robust Weiszfeld -- the step MASt3R's own scene
     alignment uses). Needs MASt3R (external/mast3r, models/mast3r).
  2b. GeoCalib (Veicht et al., ECCV 2024): a network trained specifically to estimate focal
     length (and gravity) from ONE image, refined by a differentiable optimisation. Install:
       venv\\Scripts\\python.exe -m pip install "git+https://github.com/cvg/GeoCalib#egg=geocalib"
     (weights download on first use). Chosen with method="geocalib" instead of MASt3R.
  3. A typical phone/webcam field of view (70 deg horizontal), with a warning.
Square pixels and the principal point at the image centre are assumed throughout.
"""
import sys

import cv2
import numpy as np

FILM_DIAGONAL_MM = 43.27
DEFAULT_HFOV_DEG = 70.0


def exif_focal(path, shape):
    """Focal length in pixels from EXIF FocalLengthIn35mmFilm, or None."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            exif = im.getexif()
            f35 = exif.get_ifd(0x8769).get(0xA405) or exif.get(0xA405)   # Exif IFD -> FocalLengthIn35mmFilm
    except Exception:
        return None
    if not f35:
        return None
    h, w = shape[:2]          # the diagonal does not depend on EXIF rotation
    return float(f35) * float(np.hypot(w, h)) / FILM_DIAGONAL_MM


def default_focal(shape, hfov_deg=DEFAULT_HFOV_DEG):
    w = shape[1]
    return (w / 2) / np.tan(np.radians(hfov_deg) / 2)


def _mast3r_view(rgb, idx):
    """Long side -> 512, sides cut to multiples of 16 (right/bottom), as in match.py."""
    import torch
    from .match import MAST3R_SIDE
    s = MAST3R_SIDE / max(rgb.shape[:2])
    img = cv2.resize(rgb, (round(rgb.shape[1] * s), round(rgb.shape[0] * s)),
                     interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    full_h, full_w = img.shape[:2]
    h, w = full_h // 16 * 16, full_w // 16 * 16
    img = np.ascontiguousarray(img[:h, :w])
    t = torch.from_numpy(img).permute(2, 0, 1)[None].float() / 127.5 - 1.0
    pp = ((full_w - 1) / 2.0, (full_h - 1) / 2.0)     # centre of the uncut image, in the cut grid
    return dict(img=t, true_shape=np.int32([[h, w]]), idx=idx, instance=str(idx)), s, pp


def _mast3r_model():
    from .match import MAST3R_ROOT, MAST3R_WEIGHTS, _model
    if str(MAST3R_ROOT) not in sys.path:
        sys.path.insert(0, str(MAST3R_ROOT))
    import mast3r.utils.path_to_dust3r  # noqa: F401  (puts dust3r on the path)
    from mast3r.model import AsymmetricMASt3R
    return _model("mast3r", lambda: AsymmetricMASt3R.from_pretrained(str(MAST3R_WEIGHTS)).eval())


def mast3r_focal(rgb_a, rgb_b):
    """Focal length of image a (its own pixels), from MASt3R run on the pair (a, b)."""
    import torch
    model = _mast3r_model()
    from dust3r.inference import inference
    from dust3r.post_process import estimate_focal_knowing_depth
    (va, sa, pp), (vb, _, _) = _mast3r_view(rgb_a, 0), _mast3r_view(rgb_b, 1)
    with torch.inference_mode():
        out = inference([(va, vb)], model, "cpu", batch_size=1, verbose=False)
        pts = out["pred1"]["pts3d"]                       # (1, H, W, 3) in camera a's frame
        f = estimate_focal_knowing_depth(pts, torch.tensor([pp], dtype=pts.dtype), focal_mode="weiszfeld")
    return float(f.reshape(-1)[0]) / sa


_geocalib = {}


def geocalib_focal(path, shape):
    """Focal length (pixels of the image as loaded, `shape`) from GeoCalib on one image."""
    import torch
    from geocalib import GeoCalib
    if "model" not in _geocalib:
        _geocalib["model"] = GeoCalib().to("cpu").eval()
    model = _geocalib["model"]
    image = model.load_image(str(path)).to("cpu")          # 3 x H x W in [0, 1]
    with torch.inference_mode():
        cam = model.calibrate(image)["camera"]
    f = float(cam.f.reshape(-1)[0])
    # GeoCalib reports the camera for the image it loaded; rescale if that size differs from ours
    h_in = float(image.shape[-2])
    return f * shape[0] / h_in


def K_from_focal(f, shape):
    h, w = shape[:2]
    return np.array([[f, 0, (w - 1) / 2], [0, f, (h - 1) / 2], [0, 0, 1.0]])


def auto_focals(path1, img1, path2, img2, same_camera=None, method="mast3r"):
    """(f1, f2, description) for two images. method: "mast3r" or "geocalib" (used when EXIF
    is missing). same_camera: None = assume so when both images have the same size (then the
    two estimates are averaged, which halves the noise)."""
    e1, e2 = exif_focal(path1, img1.shape), exif_focal(path2, img2.shape)
    if e1 and e2:
        return e1, e2, "EXIF"
    name = {"mast3r": "MASt3R", "geocalib": "GeoCalib"}[method]
    try:
        if method == "geocalib":
            m1 = e1 or geocalib_focal(path1, img1.shape)
            m2 = e2 or geocalib_focal(path2, img2.shape)
        else:
            m1 = e1 or mast3r_focal(img1, img2)
            m2 = e2 or mast3r_focal(img2, img1)
        src = f"EXIF + {name}" if (e1 or e2) else f"estimated by {name}"
        if same_camera is None:
            same_camera = img1.shape[:2] == img2.shape[:2]
        if same_camera and not (e1 or e2):
            avg = 0.5 * (m1 + m2)
            return avg, avg, f"{src} (per image {m1:.0f} / {m2:.0f}; same size -> same camera assumed, averaged)"
        return m1, m2, src
    except Exception as e:   # MASt3R not installed, out of memory, ...
        d1, d2 = e1 or default_focal(img1.shape), e2 or default_focal(img2.shape)
        return d1, d2, (f"DEFAULT {DEFAULT_HFOV_DEG:.0f} deg field of view -- a guess, expect larger errors "
                        f"({name} unavailable: {type(e).__name__}: {e})")
