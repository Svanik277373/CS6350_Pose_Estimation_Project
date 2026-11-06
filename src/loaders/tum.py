"""TUM RGB-D fr3 loader.

groundtruth.txt gives camera-to-world poses (position + quaternion qx qy qz qw) from motion
capture at ~100 Hz; the camera axes already follow OpenCV. RGB frames come at ~30 Hz, so each
frame's pose is interpolated at its timestamp (linear for position, slerp for rotation).
"""
from pathlib import Path

import cv2
import numpy as np
from scipy.spatial.transform import Rotation, Slerp

from .common import Frame, invert_pose, make_pair, sample_pairs

ROOT = Path(__file__).resolve().parents[2] / "data" / "tum"
SEQUENCES = ["flat_far", "flat_near", "struct_far", "struct_near", "checkerboard"]

# Official calibration of the fr3 Kinect; fr3 images are already undistorted
K_FR3 = np.array([[535.4, 0.0, 320.1],
                  [0.0, 539.2, 247.6],
                  [0.0, 0.0, 1.0]])

MAX_TIME_GAP = 3.0   # seconds; frames further apart often look at different parts of the scene
FPS = 30


def _read_table(path: Path):
    rows = [line.split() for line in path.read_text().splitlines() if line and not line.startswith("#")]
    return rows


def load_frames(sequence: str) -> list:
    seq_dir = ROOT / sequence
    rgb = _read_table(seq_dir / "rgb.txt")
    gt = np.array(_read_table(seq_dir / "groundtruth.txt"), dtype=float)

    gt_time, gt_pos, gt_quat = gt[:, 0], gt[:, 1:4], gt[:, 4:8]
    slerp = Slerp(gt_time, Rotation.from_quat(gt_quat))  # scipy quat order is x, y, z, w like TUM

    frames = []
    for ts, rel_path in rgb:
        ts = float(ts)
        if not (gt_time[0] <= ts <= gt_time[-1]):
            continue   # no ground truth to interpolate from
        R_c2w = slerp(ts).as_matrix()
        c = np.array([np.interp(ts, gt_time, gt_pos[:, k]) for k in range(3)])
        R, t = invert_pose(R_c2w, c)
        path = seq_dir / rel_path
        frames.append(Frame(
            index=len(frames), K=K_FR3, R=R, t=t,
            load_image=lambda p=path: cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB),
        ))
    return frames


def load_pairs(per_bin: int = 20, seed: int = 0, sequences=SEQUENCES) -> list:
    rng = np.random.default_rng(seed)
    pairs = []
    for seq in sequences:
        frames = load_frames(seq)
        for i, j in sample_pairs(frames, per_bin, rng, max_index_gap=int(MAX_TIME_GAP * FPS)):
            pairs.append(make_pair("tum", seq, frames[i], frames[j], metric=True))
    return pairs
