"""Live pose tracking: relative pose of an object between a reference frame and each new frame.

Frame-agnostic (no camera code here): scripts/webcam.py feeds it webcam frames, and its
--replay mode feeds dataset video frames with ground truth to measure how well it works.

    tracker = LiveTracker(K, method="xfeat_lg")
    tracker.set_reference(img, box=(x0, y0, x1, y1))     # the object's region in the reference
    out = tracker.update(frame)                            # pose of frame relative to reference

Object only: matching uses the object's box in the reference and a box around the object in
the current frame. That box is tracked: after a good estimate it becomes the bounding box of
the inlier matches in the current frame, enlarged by `pad`; after `lost_after` failures in a
row the whole frame is searched until the object is found again.

Meaning of the pose (OpenCV convention, X_2 = R X_1 + t in camera coordinates):
  camera still, object moved  -> R, t are the object's own rotation and translation, seen in
                                 the camera's axes (x right, y down, z forward);
  object still, camera moved  -> R, t are the camera's motion (the usual two-view meaning).
t is a direction only (unit length) unless the object's size is given (size_m).
"""
import time
from dataclasses import dataclass, field

import cv2
import numpy as np

from .cascade import PRESETS, estimate_pose_cascade
from .estimate import PoseResult, estimate_pose
from .scale import size_scale


@dataclass
class LiveResult:
    res: PoseResult
    box_used: tuple = None          # region searched in the current frame (None = whole frame)
    box_next: tuple = None          # region to search in the next frame
    seconds: float = 0.0
    angle_deg: float = float("nan")
    euler_deg: np.ndarray = field(default_factory=lambda: np.full(3, np.nan))  # about camera x, y, z
    t_metres: np.ndarray = None


def box_mask(shape, box):
    m = np.zeros(shape[:2], bool)
    if box is not None:
        x0, y0, x1, y1 = (int(round(v)) for v in box)
        m[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True
    return m


def mask_box(mask):
    ys, xs = np.nonzero(mask)
    return (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1) if len(xs) else None


def _grow(box, pad, shape, min_wh=(0, 0)):
    x0, y0, x1, y1 = box
    w, h = max(x1 - x0, min_wh[0]), max(y1 - y0, min_wh[1])
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = w * (1 + 2 * pad), h * (1 + 2 * pad)
    H, W = shape[:2]
    return (max(0.0, cx - w / 2), max(0.0, cy - h / 2), min(W, cx + w / 2), min(H, cy + h / 2))


class LiveTracker:
    def __init__(self, K, method="xfeat_lg", max_side=640, size_m=None, pad=0.25, lost_after=3,
                 min_inliers=15):
        self.K, self.method, self.max_side, self.size_m = np.asarray(K, float), method, max_side, size_m
        self.pad, self.lost_after, self.min_inliers = pad, lost_after, min_inliers
        self.ref = None

    def set_reference(self, img, box=None, mask=None):
        """box: (x0, y0, x1, y1) around the object; or a mask; neither = whole image."""
        if mask is None:
            mask = box_mask(img.shape, box) if box is not None else np.ones(img.shape[:2], bool)
        self.ref, self.ref_mask = img, mask
        self.ref_box = mask_box(mask)
        self.box, self.lost = self.ref_box, 0     # the object starts where it was in the reference

    def update(self, img, K2=None) -> LiveResult:
        if self.ref is None:
            raise RuntimeError("set_reference first")
        K2 = self.K if K2 is None else np.asarray(K2, float)
        start = time.perf_counter()
        box = self.box
        cur_mask = box_mask(img.shape, box) if box is not None else np.ones(img.shape[:2], bool)
        if self.method in PRESETS:
            res = estimate_pose_cascade(self.ref, img, self.K, K2, self.ref_mask, cur_mask, preset=self.method,
                                        max_side=self.max_side)
        else:
            res = estimate_pose(self.ref, img, self.K, K2, self.ref_mask, cur_mask, matcher=self.method,
                                max_side=self.max_side, crop=True)
        out = LiveResult(res, box_used=box, seconds=time.perf_counter() - start)
        good = res.ok and res.n_inliers >= self.min_inliers and res.pts2 is not None and len(res.pts2) >= 4
        if good:
            self.lost = 0
            lo, hi = np.percentile(res.pts2, 2, axis=0), np.percentile(res.pts2, 98, axis=0)
            rw, rh = self.ref_box[2] - self.ref_box[0], self.ref_box[3] - self.ref_box[1]
            # never let the box collapse onto a small textured patch of the object
            self.box = _grow((lo[0], lo[1], hi[0], hi[1]), self.pad, img.shape, min_wh=(0.5 * rw, 0.5 * rh))
            out.angle_deg = float(np.degrees(np.arccos(np.clip((np.trace(res.R) - 1) / 2, -1, 1))))
            out.euler_deg = np.array(cv2.RQDecomp3x3(res.R)[0], float)
            if self.size_m:
                s = size_scale(res.R, res.t, self.K, K2, res.pts1, res.pts2, self.size_m)[0]
                if np.isfinite(s):
                    out.t_metres = s * np.asarray(res.t, float)
        else:
            self.lost += 1
            if self.lost >= self.lost_after:
                self.box = None                    # search the whole frame until found again
        out.box_next = self.box
        return out
