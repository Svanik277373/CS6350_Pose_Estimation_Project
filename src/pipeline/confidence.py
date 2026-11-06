"""Run-time side of the learned confidence (trained by scripts/confidence.py).

For each stage of a confidence-gated cascade, a classifier predicts P(pose error < 10 deg)
from evidence available without ground truth. The features must match the ones the
classifier was trained on (scripts/confidence.py: stage_features and Data.features):

    per stage:  succeeded?, log(1 + #matches), log(1 + #inliers), inlier ratio,
                reprojection RMS (NaN if failed), (GRIC_E - GRIC_H) / #matches, planar model?
    agreement:  for stage k > 0, the min and median over earlier stages of
                max(rotation difference, translation-direction difference) in degrees
                (180 when either pose is missing)
"""
import pickle
from pathlib import Path

import numpy as np

MODELS = Path(__file__).resolve().parents[2] / "models" / "confidence"


def stage_vector(res):
    matches, inliers = float(res.n_matches or 0), float(res.n_inliers or 0)
    ok = float(bool(res.ok))
    return np.array([ok, np.log1p(matches), np.log1p(inliers), inliers / max(matches, 1),
                     res.reproj_rms_px if res.ok else np.nan,
                     (res.gric_E - res.gric_H) / max(matches, 1), float(res.model == "H")])


def pose_difference_deg(a, b):
    if not (a.ok and b.ok):
        return 180.0
    rot = np.degrees(np.arccos(np.clip((np.trace(a.R.T @ b.R) - 1) / 2, -1, 1)))
    ta, tb = np.asarray(a.t, float), np.asarray(b.t, float)
    ta, tb = ta / np.linalg.norm(ta), tb / np.linalg.norm(tb)
    tra = np.degrees(np.arccos(np.clip(ta @ tb, -1, 1)))
    return float(max(rot, tra))


def features(results):
    """Features for trusting results[-1], given results[:-1] were computed before it."""
    x = stage_vector(results[-1])
    if len(results) > 1:
        agr = np.array([pose_difference_deg(results[-1], r) for r in results[:-1]])
        x = np.r_[x, agr.min(), np.median(agr)]
    return x


def load_design(name):
    path = MODELS / f"{name}.pkl"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing: run scripts/confidence.py first")
    with open(path, "rb") as f:
        return pickle.load(f)


def stage_confidence(stage, results):
    if not results[-1].ok:
        return 0.0
    x = features(results)[stage["keep"]]
    m = stage["model"]
    if isinstance(m, float):
        return m
    return float(m.predict_proba(x[None])[0, 1])
