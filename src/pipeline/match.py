"""Feature matching between two views.

Every matcher goes through the same preparation:
  1. optional crop to the object (mask bounding box + margin), so a small object fills the
     image the matcher sees instead of being a tiny patch;
  2. shrink to at most `max_side` pixels (CPU only); optionally enlarge a small crop to at
     least `min_side` pixels (at most MAX_UPSCALE times), so keypoint detectors -- which
     work at fixed pixel scales -- find detail on tiny objects;
  3. match, keeping only points on the object (inside the mask) when a mask is given;
  4. map the matched points back to full-resolution pixel coordinates, so the rest of the
     pipeline always works with the original images' K.

Matchers:
  sift, orb            classical (Lowe 2004; Rublee et al. 2011), OpenCV
  loftr                detector-free transformer matcher (Sun et al. 2021), kornia
  disk_lg, aliked_lg   learned keypoints + LightGlue matcher (Lindenberger et al. 2023), kornia
  xfeat                lightweight CPU-oriented features, mutual nearest neighbours (Potje et al. 2024)
  xfeat_lg             XFeat keypoints + LightGlue ("LighterGlue")
  mast3r               3D foundation model, dense matches (Leroy et al. 2024); code in external/mast3r
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

# Keep downloaded network weights inside the project (models/hub/checkpoints)
os.environ.setdefault("TORCH_HOME", str(Path(__file__).resolve().parents[2] / "models"))

CROP_MARGIN = 0.2      # extra context around the object, as a fraction of its bounding box
MAX_KEYPOINTS = 2048
MAX_UPSCALE = 3.0


@dataclass
class View:
    """An image as the matcher sees it, and how to map its pixels back to the original."""
    rgb: np.ndarray                 # HxWx3 uint8
    mask: Optional[np.ndarray]      # HxW uint8 (1 = object) or None
    scale: float                    # prepared pixels = (original pixels - offset) * scale
    offset: np.ndarray              # (x, y) of the crop's top-left corner in the original image

    def to_original(self, pts):
        return pts / self.scale + self.offset


def _prepare(img, mask, max_side, crop, min_side=0) -> View:
    offset = np.zeros(2)
    if crop and mask is not None and mask.any():
        ys, xs = np.nonzero(mask)
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        mx, my = CROP_MARGIN * (x1 - x0 + 1), CROP_MARGIN * (y1 - y0 + 1)
        x0, y0 = int(max(0, x0 - mx)), int(max(0, y0 - my))
        x1, y1 = int(min(img.shape[1], x1 + mx + 1)), int(min(img.shape[0], y1 + my + 1))
        img, mask = img[y0:y1, x0:x1], mask[y0:y1, x0:x1]
        offset = np.array([x0, y0], float)

    scale = min(1.0, max_side / max(img.shape[:2]))
    if min_side and max(img.shape[:2]) < min_side:
        scale = min(MAX_UPSCALE, min_side / max(img.shape[:2]))
    if scale != 1.0:
        size = (round(img.shape[1] * scale), round(img.shape[0] * scale))
        img = cv2.resize(img, size, interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
        if mask is not None:
            mask = cv2.resize(mask.astype(np.uint8), size, interpolation=cv2.INTER_NEAREST)
    return View(np.ascontiguousarray(img), None if mask is None else mask.astype(np.uint8), scale, offset)


def _inside(mask, pts):
    """Boolean per point: is it on the object? (all True without a mask)"""
    if mask is None or len(pts) == 0:
        return np.ones(len(pts), bool)
    x = np.clip(np.round(pts[:, 0]).astype(int), 0, mask.shape[1] - 1)
    y = np.clip(np.round(pts[:, 1]).astype(int), 0, mask.shape[0] - 1)
    return mask[y, x] > 0


# ---------------------------------------------------------------- classical (OpenCV)

def _ratio_test(knn, ratio):
    """Lowe's ratio test: keep a match only if it is clearly better than the second-best candidate."""
    return [m for m, n in (p for p in knn if len(p) == 2) if m.distance < ratio * n.distance]


def _opencv(detector, norm, ratio):
    def run(v1: View, v2: View):
        g1 = cv2.cvtColor(v1.rgb, cv2.COLOR_RGB2GRAY)
        g2 = cv2.cvtColor(v2.rgb, cv2.COLOR_RGB2GRAY)
        k1, d1 = detector().detectAndCompute(g1, v1.mask)
        k2, d2 = detector().detectAndCompute(g2, v2.mask)
        if d1 is None or d2 is None or len(k1) < 2 or len(k2) < 2:
            return np.empty((0, 2)), np.empty((0, 2))
        good = _ratio_test(cv2.BFMatcher(norm).knnMatch(d1, d2, k=2), ratio)
        return (np.float64([k1[m.queryIdx].pt for m in good]).reshape(-1, 2),
                np.float64([k2[m.trainIdx].pt for m in good]).reshape(-1, 2))
    return run


# ---------------------------------------------------------------- learned (kornia, CPU)

_models = {}


def _model(key, build):
    """Load each network once and reuse it."""
    if key not in _models:
        _models[key] = build()
    return _models[key]


def _tensor(rgb, gray=False):
    import torch
    if gray:
        g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        return torch.from_numpy(g)[None, None].float() / 255.0
    return torch.from_numpy(rgb).permute(2, 0, 1)[None].float() / 255.0


def _lightglue_match(feature, k1, d1, k2, d2, hw1, hw2):
    """Match two keypoint sets with LightGlue; returns index pairs (N, 2)."""
    import kornia.feature as KF
    import torch
    lg = _model(f"lg_{feature}", lambda: KF.LightGlue(features=feature).eval())
    if len(k1) < 2 or len(k2) < 2:
        return np.empty((0, 2), int)

    def side(k, d, hw):
        return {"keypoints": k[None].float(), "descriptors": d[None].float(),
                "image_size": torch.tensor([[hw[1], hw[0]]], dtype=torch.float32)}

    with torch.inference_mode():
        out = lg({"image0": side(k1, d1, hw1), "image1": side(k2, d2, hw2)})
    return out["matches"][0].numpy()


def _keypoint_lightglue(feature, extract):
    """Detector + descriptor network, object-only keypoints, matched by LightGlue."""
    def run(v1: View, v2: View):
        import torch
        out = []
        for v in (v1, v2):
            k, d = extract(v.rgb)
            keep = torch.from_numpy(_inside(v.mask, k.numpy()))
            out.append((k[keep], d[keep]))
        (k1, d1), (k2, d2) = out
        idx = _lightglue_match(feature, k1, d1, k2, d2, v1.rgb.shape[:2], v2.rgb.shape[:2])
        return k1.numpy()[idx[:, 0]].astype(np.float64), k2.numpy()[idx[:, 1]].astype(np.float64)
    return run


def _disk_extract(rgb):
    import kornia.feature as KF
    import torch
    disk = _model("disk", lambda: KF.DISK.from_pretrained("depth").eval())
    with torch.inference_mode():
        f = disk(_tensor(rgb), n=MAX_KEYPOINTS, pad_if_not_divisible=True)[0]
    return f.keypoints, f.descriptors


def _aliked_extract(rgb):
    import kornia.feature as KF
    import torch
    aliked = _model("aliked", lambda: KF.ALIKED.from_pretrained("aliked-n16", max_num_keypoints=MAX_KEYPOINTS).eval())
    with torch.inference_mode():
        f = aliked(_tensor(rgb))[0]
    return f.keypoints, f.descriptors


def _xfeat_extract(rgb):
    import kornia.feature as KF
    xfeat = _model("xfeat", lambda: KF.XFeat.from_pretrained(top_k=MAX_KEYPOINTS).eval())
    f = xfeat.detectAndCompute(_tensor(rgb))[0]
    return f["keypoints"], f["descriptors"]


def _xfeat_mnn(v1: View, v2: View):
    """XFeat descriptors matched by mutual nearest neighbour (its fast default)."""
    import torch
    out = []
    for v in (v1, v2):
        k, d = _xfeat_extract(v.rgb)
        keep = torch.from_numpy(_inside(v.mask, k.numpy()))
        out.append((k[keep], d[keep]))
    (k1, d1), (k2, d2) = out
    if len(k1) < 2 or len(k2) < 2:
        return np.empty((0, 2)), np.empty((0, 2))
    sim = d1 @ d2.T
    nn12, nn21 = sim.argmax(1), sim.argmax(0)
    mutual = nn21[nn12] == torch.arange(len(k1))
    i1 = torch.nonzero(mutual).squeeze(1)
    return k1[i1].numpy().astype(np.float64), k2[nn12[i1]].numpy().astype(np.float64)


def _loftr(v1: View, v2: View):
    """Detector-free: matches regions directly, so it does not need corners or blobs."""
    import kornia.feature as KF
    import torch
    loftr = _model("loftr", lambda: KF.LoFTR(pretrained="outdoor").eval())

    def padded(rgb):   # LoFTR needs sides divisible by 8
        h, w = rgb.shape[:2]
        return cv2.copyMakeBorder(rgb, 0, -h % 8, 0, -w % 8, cv2.BORDER_CONSTANT)

    with torch.inference_mode():
        out = loftr({"image0": _tensor(padded(v1.rgb), gray=True), "image1": _tensor(padded(v2.rgb), gray=True)})
    p1 = out["keypoints0"].numpy().astype(np.float64)
    p2 = out["keypoints1"].numpy().astype(np.float64)
    keep = _inside(v1.mask, p1) & _inside(v2.mask, p2)
    return p1[keep], p2[keep]


MAST3R_ROOT = Path(__file__).resolve().parents[2] / "external" / "mast3r"
# naver/MASt3R_ViTLarge_BaseDecoder_512_catmlpdpt_metric from Hugging Face (config.json + model.safetensors)
MAST3R_WEIGHTS = Path(__file__).resolve().parents[2] / "models" / "mast3r"
MAST3R_SIDE = 512      # the network's training resolution (long side)
# The last MASt3R prediction for view 1: metric depth map (the checkpoint is MASt3R's metric
# model) and how to map original pixels into it. Used by scale.py for metric translation.
LAST_MAST3R = {}


def _mast3r(v1: View, v2: View):
    """3D foundation model (Leroy et al. 2024): predicts a 3D point map per view plus dense
    descriptors, matched by fast reciprocal nearest neighbours. Robust to low texture and
    wide baselines; heavy on CPU. Note: CO3Dv2 is in its training data."""
    import sys
    import torch
    if str(MAST3R_ROOT) not in sys.path:
        sys.path.insert(0, str(MAST3R_ROOT))
    import mast3r.utils.path_to_dust3r  # noqa: F401  (puts dust3r on the path)
    from mast3r.fast_nn import fast_reciprocal_NNs
    from mast3r.model import AsymmetricMASt3R
    from dust3r.inference import inference
    model = _model("mast3r", lambda: AsymmetricMASt3R.from_pretrained(str(MAST3R_WEIGHTS)).eval())

    def view(rgb, idx):
        # long side -> 512 (small objects get enlarged), sides cropped to multiples of 16
        s = MAST3R_SIDE / max(rgb.shape[:2])
        img = cv2.resize(rgb, (round(rgb.shape[1] * s), round(rgb.shape[0] * s)),
                         interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
        h, w = img.shape[0] // 16 * 16, img.shape[1] // 16 * 16
        img = np.ascontiguousarray(img[:h, :w])
        t = torch.from_numpy(img).permute(2, 0, 1)[None].float() / 127.5 - 1.0   # dust3r's ImgNorm
        return dict(img=t, true_shape=np.int32([[h, w]]), idx=idx, instance=str(idx)), s

    (d1, s1), (d2, s2) = view(v1.rgb, 0), view(v2.rgb, 1)
    with torch.inference_mode():
        out = inference([(d1, d2)], model, "cpu", batch_size=1, verbose=False)
    LAST_MAST3R.clear()
    LAST_MAST3R.update(pts3d=out["pred1"]["pts3d"].squeeze(0).numpy().astype(np.float32),
                       depth=out["pred1"]["pts3d"].squeeze(0)[..., 2].numpy().astype(np.float32),
                       conf=out["pred1"]["conf"].squeeze(0).numpy().astype(np.float32),
                       resize=s1, view_scale=v1.scale, view_offset=v1.offset.copy())
    desc1, desc2 = out["pred1"]["desc"].squeeze(0), out["pred2"]["desc"].squeeze(0)
    m1, m2 = fast_reciprocal_NNs(desc1, desc2, subsample_or_initxy1=8, device="cpu", dist="dot", block_size=2 ** 13)
    (h1, w1), (h2, w2) = d1["true_shape"][0], d2["true_shape"][0]
    border = ((m1[:, 0] >= 3) & (m1[:, 0] < w1 - 3) & (m1[:, 1] >= 3) & (m1[:, 1] < h1 - 3) &
              (m2[:, 0] >= 3) & (m2[:, 0] < w2 - 3) & (m2[:, 1] >= 3) & (m2[:, 1] < h2 - 3))
    p1 = m1[border].astype(np.float64) / s1
    p2 = m2[border].astype(np.float64) / s2
    keep = _inside(v1.mask, p1) & _inside(v2.mask, p2)
    return p1[keep], p2[keep]


CORES = {
    "sift": _opencv(lambda: cv2.SIFT_create(4000), cv2.NORM_L2, 0.75),
    "orb": _opencv(lambda: cv2.ORB_create(5000), cv2.NORM_HAMMING, 0.8),
    "loftr": _loftr,
    "disk_lg": _keypoint_lightglue("disk", _disk_extract),
    "aliked_lg": _keypoint_lightglue("aliked", _aliked_extract),
    "xfeat": _xfeat_mnn,
    "xfeat_lg": _keypoint_lightglue("xfeat", _xfeat_extract),
    "mast3r": _mast3r,
}
MATCHERS = list(CORES)


def match(img1, img2, mask1=None, mask2=None, matcher="sift", max_side=800, crop=False, min_side=0):
    """Returns (pts1, pts2, scale): Nx2 full-resolution pixel coordinates of matched points,
    and the smaller of the two resize factors (localisation noise grows as 1/scale when
    shrinking; enlarging adds no real detail, so callers cap it at 1)."""
    v1 = _prepare(img1, mask1, max_side, crop, min_side)
    v2 = _prepare(img2, mask2, max_side, crop, min_side)
    p1, p2 = CORES[matcher](v1, v2)
    p1, p2 = np.asarray(p1, float).reshape(-1, 2), np.asarray(p2, float).reshape(-1, 2)
    return v1.to_original(p1), v2.to_original(p2), min(v1.scale, v2.scale)
