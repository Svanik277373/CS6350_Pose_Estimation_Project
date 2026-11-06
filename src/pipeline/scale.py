"""Metric scale: turn the unit translation direction into metres.

Two calibrated views fix the pose only up to scale: shrinking the whole scene and the camera
baseline together gives identical images. One extra piece of metric information fixes it:

  depth_scale   a metric depth map of view 1 -- here from MASt3R's metric checkpoint, which
                predicts depth in metres from a single image pair (a learned prior on how big
                things usually are). Triangulating the inliers with |t| = 1 gives depths z_i;
                the metric depths d_i at the same pixels give s = median(d_i / z_i), and
                t_metric = s * t. The spread of log(d_i / z_i) says how consistent that is.
  size_scale    a known object size (e.g. a phone's length, typed in by the user): the
                triangulated points' extent along their main axis is matched to it. The
                matched points cover the visible surface only, so this is a lower bound on
                the object's extent -- best for flat objects seen face-on.

Both return (scale, spread): t_metric = scale * t_unit, spread = robust std of log-ratios.
"""
import cv2
import numpy as np

from . import geometry as G
from .match import LAST_MAST3R


def _triangulated(R, t, K1, K2, p1, p2):
    X = G.triangulate(R, t, G.to_normalized(p1, K1), G.to_normalized(p2, K2))
    X2 = X @ R.T + t
    return X[(X[:, 2] > 0) & (X2[:, 2] > 0)], (X[:, 2] > 0) & (X2[:, 2] > 0)


def mast3r_depth_at(pts):
    """Metric depth (m) and confidence of the last MASt3R prediction at original-image pixels."""
    if not LAST_MAST3R:
        raise RuntimeError("no MASt3R prediction available; run the mast3r matcher first")
    d = LAST_MAST3R
    q = (np.asarray(pts, float) - d["view_offset"]) * d["view_scale"] * d["resize"]
    h, w = d["depth"].shape
    u, v = np.round(q[:, 0]).astype(int), np.round(q[:, 1]).astype(int)
    inside = (u >= 0) & (u < w) & (v >= 0) & (v < h)
    depth, conf = np.full(len(q), np.nan), np.zeros(len(q))
    depth[inside], conf[inside] = d["depth"][v[inside], u[inside]], d["conf"][v[inside], u[inside]]
    return depth, conf


def mast3r_focal():
    """Focal length (in MASt3R input pixels) implied by the last point map, assuming the
    principal point at the image centre (DUSt3R's convention): least squares on
    (u - cx, v - cy) = f * (X / Z, Y / Z) over confident pixels."""
    d = LAST_MAST3R
    P, conf = d["pts3d"], d["conf"]
    h, w = P.shape[:2]
    v, u = np.mgrid[0:h, 0:w]
    keep = (conf > np.median(conf)) & (P[..., 2] > 0)
    a = np.concatenate([P[..., 0][keep] / P[..., 2][keep], P[..., 1][keep] / P[..., 2][keep]])
    b = np.concatenate([u[keep] - (w - 1) / 2, v[keep] - (h - 1) / 2])
    return float(a @ b / (a @ a))


def mast3r_metric_depth_at(pts, K1):
    """MASt3R depth corrected to our camera: the network only sees the (cropped, resized)
    image, so it assumes its own focal length f_m; with the real focal f the same image
    region means the object is f / f_m times as far away."""
    depth, conf = mast3r_depth_at(pts)
    d = LAST_MAST3R
    f_real = 0.5 * (K1[0, 0] + K1[1, 1]) * d["view_scale"] * d["resize"]
    return depth * f_real / mast3r_focal(), conf


def depth_scale(R, t, K1, K2, p1, p2, depth):
    """depth: metric depth of view 1 at p1 (NaN where unknown)."""
    X, ok = _triangulated(R, t, K1, K2, p1, p2)
    d = np.asarray(depth, float)[ok]
    valid = np.isfinite(d) & (d > 0)
    if valid.sum() < 5:
        return np.nan, np.nan
    log_ratio = np.log(d[valid] / X[valid, 2])
    med = np.median(log_ratio)
    return float(np.exp(med)), float(1.4826 * np.median(np.abs(log_ratio - med)))


def _outline_on_plane(X, K1, mask1):
    """The mask's outline in 3D (camera-1 frame, unit-baseline units): fit a plane to the
    triangulated points, intersect the rays through the outline pixels with it."""
    # robust plane: drop points far from the median (badly triangulated, e.g. tiny parallax),
    # fit, then refit on the points closest to the first plane
    c0 = np.median(X, axis=0)
    d = np.linalg.norm(X - c0, axis=1)
    X = X[d <= 3 * np.median(d) + 1e-12]
    for _ in range(2):
        c0 = np.median(X, axis=0)
        n = np.linalg.svd(X - c0, full_matrices=False)[2][2]
        r = np.abs((X - c0) @ n)
        if len(X) > 10:
            X = X[r <= np.percentile(r, 80)]
    contours, _ = cv2.findContours(mask1.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return None
    uv = max(contours, key=cv2.contourArea).reshape(-1, 2).astype(float)
    rays = np.column_stack([uv, np.ones(len(uv))]) @ np.linalg.inv(K1).T
    denom = rays @ n
    lam = np.full(len(rays), -1.0)
    ok = np.abs(denom) > 1e-9
    lam[ok] = (c0 @ n) / denom[ok]
    front = lam > 0
    if front.mean() < 0.9:   # plane nearly edge-on to the camera: outline not measurable
        return None
    return rays[front] * lam[front][:, None]


def size_scale(R, t, K1, K2, p1, p2, size_m, mask1=None):
    """size_m: the object's longest dimension in metres.

    With mask1 (the object's region in view 1) the object's extent is measured on its outline
    projected onto the plane through the triangulated points -- independent of where matches
    happen to be. Without it, the extent of the triangulated points is used (a lower bound:
    matches rarely reach the object's ends, so the scale comes out too large)."""
    X, _ = _triangulated(R, t, K1, K2, p1, p2)
    if len(X) < 5:
        return np.nan, np.nan
    pts = X
    if mask1 is not None and mask1.any():
        outline = _outline_on_plane(X, K1, mask1)
        if outline is not None and len(outline) >= 4:
            pts = outline
    c = pts - np.median(pts, axis=0)
    axis = np.linalg.svd(c, full_matrices=False)[2][0]
    proj = c @ axis
    lo, hi = (0, 100) if pts is not X else (2, 98)
    extent = np.percentile(proj, hi) - np.percentile(proj, lo)
    if extent <= 0:
        return np.nan, np.nan
    return float(size_m / extent), np.nan
