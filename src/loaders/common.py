"""Shared types and pose helpers used by every dataset loader.

Convention used everywhere in this project (OpenCV):
  - camera axes: x right, y down, z forward
  - poses are world-to-camera:  X_cam = R @ X_world + t
  - K is in pixels for the image as returned by the loader
"""
from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np


@dataclass
class Frame:
    """One image of a sequence with its ground-truth camera."""
    index: int
    K: np.ndarray                     # 3x3, pixels
    R: np.ndarray                     # 3x3 world-to-camera rotation
    t: np.ndarray                     # (3,) world-to-camera translation
    load_image: Callable[[], np.ndarray]                    # -> HxWx3 RGB uint8
    load_mask: Optional[Callable[[], np.ndarray]] = None    # -> HxW bool (object pixels)
    extra: dict = field(default_factory=dict)               # dataset-specific facts (e.g. object size)


@dataclass
class Pair:
    """Two views plus the ground-truth relative pose that maps camera-1 coords to camera-2 coords."""
    dataset: str
    sequence: str
    frame1: Frame
    frame2: Frame
    R_gt: np.ndarray
    t_gt: np.ndarray
    angle_deg: float                  # rotation angle between the two views
    metric: bool                      # True if t_gt is in metres (scale is known)
    meta: dict = field(default_factory=dict)

    @property
    def name(self) -> str:
        return f"{self.dataset}/{self.sequence}/{self.frame1.index}-{self.frame2.index}"

    def load(self):
        """Read images and masks from disk: (img1, img2, mask1, mask2); masks may be None."""
        m1 = self.frame1.load_mask() if self.frame1.load_mask else None
        m2 = self.frame2.load_mask() if self.frame2.load_mask else None
        return self.frame1.load_image(), self.frame2.load_image(), m1, m2


def invert_pose(R: np.ndarray, t: np.ndarray):
    """Camera-to-world <-> world-to-camera."""
    return R.T, -R.T @ t


def relative_pose(R1, t1, R2, t2):
    """Relative pose camera 1 -> camera 2 from two world-to-camera poses."""
    R = R2 @ R1.T
    return R, t2 - R @ t1


def rotation_angle_deg(R: np.ndarray) -> float:
    cos = np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0)
    return float(np.degrees(np.arccos(cos)))


def make_pair(dataset, sequence, f1: Frame, f2: Frame, metric: bool, **meta) -> Pair:
    R, t = relative_pose(f1.R, f1.t, f2.R, f2.t)
    return Pair(dataset, sequence, f1, f2, R, t, rotation_angle_deg(R), metric, meta)


# Viewpoint-change bins (degrees) used to sample test pairs
ANGLE_BINS = [(5, 15), (15, 30), (30, 60)]


def sample_pairs(frames: list, per_bin: int, rng: np.random.Generator,
                 max_index_gap: Optional[int] = None) -> list:
    """Pick up to `per_bin` frame-index pairs (i, j) from each rotation-angle bin.

    max_index_gap limits how far apart the frames can be in the sequence; used for
    scene datasets (TUM) where far-apart frames may not see the same area.
    """
    Rs = np.stack([f.R for f in frames]).reshape(len(frames), 9)
    # trace(R_i R_j^T) = sum of elementwise products, giving all pairwise angles at once
    cos = np.clip((Rs @ Rs.T - 1.0) / 2.0, -1.0, 1.0)
    angles = np.degrees(np.arccos(cos))

    i, j = np.triu_indices(len(frames), k=1)
    if max_index_gap is not None:
        keep = (j - i) <= max_index_gap
        i, j = i[keep], j[keep]
    a = angles[i, j]

    chosen = []
    for lo, hi in ANGLE_BINS:
        idx = np.flatnonzero((a >= lo) & (a < hi))
        if len(idx) == 0:
            continue
        pick = rng.choice(idx, size=min(per_bin, len(idx)), replace=False)
        chosen += [(int(i[k]), int(j[k])) for k in pick]
    return chosen
