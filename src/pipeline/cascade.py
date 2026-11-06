"""Cascade: try methods in order, stop at the first pose that looks reliable.

No single method is best everywhere (scripts/evaluate.py): cheap matchers are enough for
textured objects, learned matchers rescue harder ones, and plain rectangles (phones) need
the outline. A stage's pose is accepted when it has at least `min_inliers` inliers; the shape
stage is accepted whenever its rectangle checks pass. If nothing is accepted, the matcher
pose with the most inliers is returned (it may be wrong, but it's the best evidence there is).

The designs below were chosen by scripts/tune_cascade.py on the tuning split only
(268k designs searched); see results/cascade/summary.md for test-split scores.
"""
import time

from .estimate import PoseResult, estimate_pose
from .shape import estimate_pose_shape

SHAPE = "shape"
PRESETS = {
    # budget 0.5 s/pair (mean on the tuning pairs)
    "fast": [("xfeat_lg", 30), ("sift", 15), (SHAPE, None)],
    # budget 2 s/pair
    "accurate": [("xfeat_lg", 200), (SHAPE, None), ("sift", 50), ("loftr", 120)],
}


def estimate_pose_cascade(img1, img2, K1, K2, mask1=None, mask2=None, preset="accurate",
                          max_side=800, refine=True) -> PoseResult:
    start = time.perf_counter()
    best, tried = None, []
    for method, min_inliers in PRESETS[preset]:
        if method == SHAPE:
            res = estimate_pose_shape(img1, img2, K1, K2, mask1, mask2, matcher="xfeat", max_side=max_side)
            accept = res.ok
        else:
            res = estimate_pose(img1, img2, K1, K2, mask1, mask2, matcher=method, max_side=max_side, crop=True,
                                refine=refine)
            accept = res.ok and res.n_inliers >= min_inliers
            if res.ok and (best is None or res.n_inliers > best[1].n_inliers):
                best = (method, res)
        tried.append(method)
        if accept:
            res.reason = f"cascade: {method} accepted"
            break
    else:
        if best is None:
            res = PoseResult(False, reason=f"cascade: no stage succeeded ({', '.join(tried)})")
        else:
            res = best[1]
            res.reason = f"cascade: none confident, best was {best[0]} ({res.n_inliers} inliers)"
    res.seconds = time.perf_counter() - start
    return res


# Confidence-gated cascades (scripts/confidence.py chose them on the tuning split): accept a
# stage's pose when a learned classifier gives P(error < 10 deg) >= tau; otherwise run the
# next stage; if none is confident, the final stage (MASt3R) answers, or the most confident pose.
CONFIDENT = {"confident": "budget_8s"}   # preset -> models/confidence/<file>; ~8 s/pair mean, see results/confidence
ALL_PRESETS = list(PRESETS) + list(CONFIDENT)


def _run_stage(method, img1, img2, K1, K2, mask1, mask2, max_side, refine):
    if method == SHAPE:   # as evaluated (results/shape_ref): outline + XFeat
        return estimate_pose_shape(img1, img2, K1, K2, mask1, mask2, matcher="xfeat", max_side=max_side)
    return estimate_pose(img1, img2, K1, K2, mask1, mask2, matcher=method, max_side=max_side, crop=True,
                         refine=refine)


def estimate_pose_confident(img1, img2, K1, K2, mask1=None, mask2=None, preset="confident",
                            max_side=800, refine=True) -> PoseResult:
    from .confidence import load_design, stage_confidence
    design = load_design(CONFIDENT[preset])
    start = time.perf_counter()
    results, best, best_p = [], None, -1.0
    for method, stage in zip(design["order"], design["stages"]):
        res = _run_stage(method, img1, img2, K1, K2, mask1, mask2, max_side, refine)
        results.append(res)
        p = stage_confidence(stage, results)
        if res.ok and p > best_p:
            best, best_p = (method, res), p
        if p >= design["tau"]:
            res.reason = f"{preset}: {method} accepted (confidence {p:.2f})"
            res.seconds = time.perf_counter() - start
            return res
    if design["final"]:
        res = _run_stage(design["final"], img1, img2, K1, K2, mask1, mask2, max_side, refine)
        if res.ok:
            res.reason = f"{preset}: no cheap stage confident (best {best_p:.2f}), {design['final']} answered"
            res.seconds = time.perf_counter() - start
            return res
    if best is None:
        res = PoseResult(False, reason=f"{preset}: no stage succeeded")
    else:
        res = best[1]
        res.reason = f"{preset}: none confident, most confident was {best[0]} ({best_p:.2f})"
    res.seconds = time.perf_counter() - start
    return res
