"""Relative pose of an object between two views: the full pipeline in one call.

    match points -> fit homography H and essential matrix E (MAGSAC++) -> pick the model
    with GRIC -> recover (R, t) -> reprojection error

t is a unit vector (direction only): two views alone cannot tell how far the camera moved.
"""
import time
from dataclasses import dataclass, field

import numpy as np

from . import geometry as G
from .refine import refine_essential, refine_homography
from .match import match

MIN_MATCHES = 15
# With fewer inliers a wrong model can fit them almost perfectly, so the pose (and its
# near-zero reprojection error) can't be trusted; report a failure instead
MIN_INLIERS = 15
BASE_THRESH_PX = 1.5   # inlier threshold at matching resolution
REFINE_ROUNDS = 2      # refine -> re-select inliers -> refine
MIN_SIGMA_PX = 0.3     # floor for the data-driven GRIC noise estimate


@dataclass
class PoseResult:
    ok: bool
    R: np.ndarray = field(default_factory=lambda: np.eye(3))
    t: np.ndarray = field(default_factory=lambda: np.zeros(3))
    model: str = ""                  # "H" (planar) or "E" (general 3D)
    n_matches: int = 0
    n_inliers: int = 0
    reproj_rms_px: float = float("nan")
    gric_H: float = float("nan")
    gric_E: float = float("nan")
    seconds: float = 0.0
    reason: str = ""                 # why it failed, if it did
    refined: bool = False            # pose polished by non-linear refinement (refine.py)
    pts1: np.ndarray = None          # inlier correspondences (full-res pixels), for refinement/plots
    pts2: np.ndarray = None


def estimate_pose(img1, img2, K1, K2, mask1=None, mask2=None,
                  matcher="sift", max_side=800, model="auto", crop=False, refine=True,
                  min_side=0, gric_sigma="fixed", planar_twin=True) -> PoseResult:
    """model: "auto" (GRIC chooses), "H" or "E". crop: match on a crop around the object mask.
    refine: polish the pose on all inliers (Levenberg-Marquardt, refine.py).
    min_side: enlarge crops smaller than this (pixels) before matching (0 = never).
    gric_sigma: "fixed" (1 px at matching resolution) or "robust" (estimated from the E
    inliers' residuals, so each matcher's real localisation noise is used)."""
    start = time.perf_counter()
    p1, p2, scale = match(img1, img2, mask1, mask2, matcher=matcher, max_side=max_side, crop=crop,
                          min_side=min_side)
    return pose_from_matches(p1, p2, scale, K1, K2, model=model, refine=refine, gric_sigma=gric_sigma,
                             start=start, planar_twin=planar_twin)


def pose_from_matches(p1, p2, scale, K1, K2, model="auto", refine=True, gric_sigma="fixed",
                      start=None, planar_twin=True) -> PoseResult:
    """The geometric half of estimate_pose: matched points (full-res pixels) -> pose.
    Split out so saved matches can be re-used, e.g. with a perturbed K (scripts/sensitivity.py).
    scale: the matcher's resize factor (sets the inlier threshold and GRIC noise)."""
    start = time.perf_counter() if start is None else start
    scale = min(scale, 1.0)
    n = len(p1)
    if n < MIN_MATCHES:
        return PoseResult(False, n_matches=n, seconds=time.perf_counter() - start,
                          reason=f"only {n} matches")

    # Matching was done on shrunk images, so localisation noise is larger in full-res pixels
    thresh_px = BASE_THRESH_PX / scale
    sigma = 1.0 / scale
    focal = 0.25 * (K1[0, 0] + K1[1, 1] + K2[0, 0] + K2[1, 1])
    x1n, x2n = G.to_normalized(p1, K1), G.to_normalized(p2, K2)

    H, inl_H = G.estimate_homography(p1, p2, thresh_px)
    E, inl_E = G.estimate_essential(x1n, x2n, thresh_px / focal)

    res_E = G.sampson_sq(np.linalg.inv(K2).T @ E @ np.linalg.inv(K1), p1, p2) if E is not None else None
    if gric_sigma == "robust" and E is not None and inl_E.sum() >= 8:
        # Sampson distance ~ point-to-manifold distance; MAD-style scale of the inliers
        sigma = max(MIN_SIGMA_PX, 1.4826 * float(np.median(np.sqrt(res_E[inl_E]))))
    gric_H = G.gric(G.homography_transfer_sq(H, p1, p2), sigma, "H") if H is not None else np.inf
    gric_E = G.gric(res_E, sigma, "E") if E is not None else np.inf

    chosen = model if model != "auto" else ("H" if gric_H <= gric_E else "E")
    if chosen == "H" and H is not None and inl_H.sum() >= 4:
        R, t, normal = G.pose_from_homography(H, K1, K2, p1, p2, inl_H)
        inliers = inl_H
    elif E is not None and inl_E.sum() >= 5:
        chosen = "E"
        R, t, inliers = G.pose_from_essential(E, x1n, x2n, inl_E)
        if planar_twin and inl_H is not None and inl_H.sum() >= 4:
            twin = G.planar_twin(R, t, H, K1, K2, p1, p2, inl_H)
            if twin is not None:
                R, t = twin
                inliers = inl_E
    else:
        return PoseResult(False, n_matches=n, gric_H=gric_H, gric_E=gric_E,
                          seconds=time.perf_counter() - start, reason="no model could be fitted")

    if inliers.sum() < MIN_INLIERS:
        return PoseResult(False, model=chosen, n_matches=n, n_inliers=int(inliers.sum()),
                          gric_H=gric_H, gric_E=gric_E, seconds=time.perf_counter() - start,
                          reason=f"only {int(inliers.sum())} inliers")

    refined = False
    if refine:
        # Refine, then re-select inliers among *all* matches with the refined pose (some that
        # RANSAC rejected now fit) and refine once more on the new set
        for _ in range(REFINE_ROUNDS):
            q1, q2 = p1[inliers], p2[inliers]
            if chosen == "H":
                R_ref, t_ref, ok, td, n_ref = refine_homography(R, normal, H, K1, K2, q1, q2)
            else:
                R_ref, t_ref, ok = refine_essential(R, t, K1, K2, q1, q2)
            if not ok:
                break
            R, t, refined = R_ref, t_ref, True
            if chosen == "E":
                res = G.sampson_sq(G.fundamental_from_pose(R, t, K1, K2), p1, p2)
            else:
                normal = n_ref
                H = K2 @ (R + np.outer(td, normal)) @ np.linalg.inv(K1)
                res = G.homography_transfer_sq(H, p1, p2)
            new = res < thresh_px ** 2
            if new.sum() < inliers.sum() or np.array_equal(new, inliers):
                break
            inliers = new
    q1, q2 = p1[inliers], p2[inliers]
    return PoseResult(
        refined=refined, ok=True, R=R, t=t, model=chosen, n_matches=n, n_inliers=int(inliers.sum()),
        reproj_rms_px=G.reprojection_rms(R, t, K1, K2, q1, q2),
        gric_H=gric_H, gric_E=gric_E, seconds=time.perf_counter() - start, pts1=q1, pts2=q2,
    )
