"""Pose accuracy metrics against ground truth."""
import numpy as np


def rotation_error_deg(R_est, R_gt) -> float:
    """Angle of the rotation that takes the estimate to the ground truth (geodesic error)."""
    cos = np.clip((np.trace(R_est.T @ R_gt) - 1.0) / 2.0, -1.0, 1.0)
    return float(np.degrees(np.arccos(cos)))


def pose_auc(errors, thresholds=(5, 10, 20)) -> dict:
    """Area under the cumulative pose-error curve up to each threshold, in percent.

    Standard relative-pose summary (SuperGlue / LoFTR papers). `errors` must include
    failed pairs as np.inf so that failing counts against a method instead of being dropped.
    """
    errors = np.sort(np.asarray(errors, float))
    recall = np.arange(1, len(errors) + 1) / len(errors)
    errors, recall = np.r_[0.0, errors], np.r_[0.0, recall]
    out = {}
    for th in thresholds:
        last = np.searchsorted(errors, th)
        e = np.r_[errors[:last], th]
        r = np.r_[recall[:last], recall[last - 1]]
        out[th] = float(100 * np.trapezoid(r, x=e) / th)
    return out


def translation_angle_deg(t_est, t_gt) -> float:
    """Angle between estimated and true translation directions (scale-free).

    Undefined (nan) when either translation is ~zero, e.g. a pure rotation.
    """
    a, b = np.linalg.norm(t_est), np.linalg.norm(t_gt)
    if a < 1e-9 or b < 1e-9:
        return float("nan")
    cos = np.clip(np.dot(t_est, t_gt) / (a * b), -1.0, 1.0)
    return float(np.degrees(np.arccos(cos)))
