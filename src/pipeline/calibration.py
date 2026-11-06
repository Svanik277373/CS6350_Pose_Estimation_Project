"""Camera calibration from checkerboard images (Zhang 2000), via OpenCV.

Each view of a planar board gives a homography between the board and the image, and each
homography gives two constraints on the camera intrinsics K; with enough views at different
tilts K is solved in closed form, then everything (K, distortion, board poses) is refined
by minimising the reprojection error of the corners.

The views must differ in *tilt*, not only in distance: fronto-parallel views all give
nearly the same constraint and leave the focal length poorly determined. select_diverse
therefore picks views spread out in board orientation and image position.
"""
from dataclasses import dataclass

import cv2
import numpy as np

DETECT_FLAGS = cv2.CALIB_CB_EXHAUSTIVE | cv2.CALIB_CB_ACCURACY


@dataclass
class Detection:
    index: int                 # which image
    corners: np.ndarray        # Nx2 sub-pixel corner positions


@dataclass
class Calibration:
    K: np.ndarray
    dist: np.ndarray           # k1, k2, p1, p2, k3
    rms_px: float              # reprojection RMS over all corners
    K_std: np.ndarray          # standard deviations of fx, fy, cx, cy
    per_view_rms: np.ndarray
    rvecs: list
    tvecs: list                # board-to-camera, in board-square units
    used: list                 # Detection indices used
    image_size: tuple          # (w, h)


def board_points(pattern, square=1.0):
    """3D corner coordinates on the board plane (z = 0), in units of `square`."""
    cols, rows = pattern
    g = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2).astype(np.float32)
    return np.hstack([g * square, np.zeros((len(g), 1), np.float32)])


def detect(gray, pattern):
    """Sub-pixel inner-corner positions (Nx2) or None if the board isn't fully visible."""
    ok, corners = cv2.findChessboardCornersSB(gray, pattern, flags=DETECT_FLAGS)
    return corners.reshape(-1, 2) if ok else None


def _view_features(corners, pattern, image_size):
    """Board orientation and position from one view, for picking diverse views:
    the board's outer quad -> homography with a nominal K -> board normal; plus image centre."""
    cols, rows = pattern
    quad = corners[[0, cols - 1, cols * rows - 1, cols * (rows - 1)]]
    w, h = image_size
    K0 = np.array([[w, 0, w / 2], [0, w, h / 2], [0, 0, 1.0]])   # rough guess is enough here
    src = np.float32([[0, 0], [cols - 1, 0], [cols - 1, rows - 1], [0, rows - 1]])
    M = np.linalg.inv(K0) @ cv2.getPerspectiveTransform(src, quad.astype(np.float32))
    n = np.cross(M[:, 0], M[:, 1])
    n = n / np.linalg.norm(n) * np.sign(n[2] or 1)
    c = corners.mean(0) / np.array([w, h])
    return np.r_[3 * n[:2], c]           # tilt weighted above position


def select_diverse(detections, pattern, image_size, n):
    """Greedy farthest-point choice of n views spread out in tilt and image position."""
    if len(detections) <= n:
        return list(range(len(detections)))
    F = np.array([_view_features(d.corners, pattern, image_size) for d in detections])
    chosen = [int(np.argmax(np.linalg.norm(F[:, :2], axis=1)))]    # start from the most tilted
    dist = np.linalg.norm(F - F[chosen[0]], axis=1)
    while len(chosen) < n:
        i = int(np.argmax(dist))
        chosen.append(i)
        dist = np.minimum(dist, np.linalg.norm(F - F[i], axis=1))
    return chosen


def tilt_deg(detection, pattern, image_size):
    f = _view_features(detection.corners, pattern, image_size)
    return float(np.degrees(np.arcsin(min(1.0, np.linalg.norm(f[:2]) / 3))))


def calibrate(detections, pattern, image_size, flags=cv2.CALIB_FIX_K3) -> Calibration:
    obj = board_points(pattern)
    objs = [obj] * len(detections)
    imgs = [d.corners.astype(np.float32).reshape(-1, 1, 2) for d in detections]
    rms, K, dist, rvecs, tvecs, std_in, _, per_view = cv2.calibrateCameraExtended(
        objs, imgs, image_size, None, None, flags=flags)
    return Calibration(K=K, dist=dist.ravel(), rms_px=float(rms), K_std=std_in.ravel()[:4],
                       per_view_rms=per_view.ravel(), rvecs=list(rvecs), tvecs=[t.ravel() for t in tvecs],
                       used=[d.index for d in detections], image_size=image_size)
