"""Objectron loader (book, laptop, cereal_box).

annotation.pbdata holds, per video frame, the ARKit camera: a camera-to-world transform,
pixel intrinsics for the 1920x1440 landscape image, and the 3D box keypoints in camera
coordinates. ARKit cameras use x right / y up / z backward, so poses are converted with
F = diag(1, -1, -1). The .MOV stores frames as portrait (1440x1920), i.e. the landscape
image rotated 90 deg clockwise, so frames are rotated back before use. ARKit works in
metres, so translations are metric.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

from .common import Frame, invert_pose, make_pair, sample_pairs

sys.path.insert(0, str(Path(__file__).resolve().parent / "schema"))
import annotation_data_pb2  # noqa: E402  (generated from Objectron's .proto files)

ROOT = Path(__file__).resolve().parents[2] / "data" / "objectron"
CATEGORIES = ["book", "laptop", "cereal_box"]

FLIP_YZ = np.diag([1.0, -1.0, -1.0])
TRACKING_NORMAL = 3


def _read_sequence(seq_dir: Path):
    seq = annotation_data_pb2.Sequence()
    seq.ParseFromString((seq_dir / "annotation.pbdata").read_bytes())
    return seq


def _box_mask(corners_cam: np.ndarray, K: np.ndarray, shape) -> np.ndarray:
    """Fill the convex hull of the projected 3D box corners (OpenCV camera coords)."""
    uv = (K @ corners_cam.T).T
    uv = uv[:, :2] / uv[:, 2:3]
    mask = np.zeros(shape, np.uint8)
    cv2.fillConvexPoly(mask, cv2.convexHull(uv.astype(np.int32)), 1)
    return mask.astype(bool)


def extract_frames(seq_dir: Path, indices) -> None:
    """Decode the video once and cache the requested frames, rotated to landscape."""
    out_dir = seq_dir / "frames"
    todo = {i for i in indices if not (out_dir / f"{i:04d}.jpg").exists()}
    if not todo:
        return
    out_dir.mkdir(exist_ok=True)
    video = cv2.VideoCapture(str(seq_dir / "video.MOV"))
    i = 0
    while todo:
        ok, frame = video.read()
        if not ok:
            break
        if i in todo:
            landscape = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            cv2.imwrite(str(out_dir / f"{i:04d}.jpg"), landscape, [cv2.IMWRITE_JPEG_QUALITY, 95])
            todo.discard(i)
        i += 1
    video.release()


def _box_size(corners: np.ndarray) -> list:
    """Edge lengths of the annotated 3D box (metres), largest first: extents of the 8 corners
    along their principal axes (exact for a box)."""
    c = corners - corners.mean(axis=0)
    axes = np.linalg.svd(c, full_matrices=False)[2]
    return sorted((np.ptp(c @ axes.T, axis=0)).tolist(), reverse=True)


def load_frames(seq_dir: Path) -> list:
    frames = []
    for ann in _read_sequence(seq_dir).frame_annotations:
        cam = ann.camera
        if cam.tracking_state != TRACKING_NORMAL or not ann.annotations:
            continue
        K = np.array(cam.intrinsics).reshape(3, 3)
        T_c2w = np.array(cam.transform).reshape(4, 4)
        R_arkit, t_arkit = invert_pose(T_c2w[:3, :3], T_c2w[:3, 3])
        R, t = FLIP_YZ @ R_arkit, FLIP_YZ @ t_arkit

        # keypoint 0 is the box centre, 1-8 are its corners (already in camera coords)
        kps = ann.annotations[0].keypoints
        corners = np.array([[k.point_3d.x, k.point_3d.y, k.point_3d.z] for k in kps[1:9]]) @ FLIP_YZ
        shape = (cam.image_resolution_height, cam.image_resolution_width)

        img_path = seq_dir / "frames" / f"{ann.frame_id:04d}.jpg"
        frames.append(Frame(
            index=ann.frame_id, K=K, R=R, t=t,
            load_image=lambda p=img_path: cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB),
            load_mask=lambda c=corners, k=K, s=shape: _box_mask(c, k, s),
            extra=dict(box_size_m=_box_size(corners)),
        ))
    return frames


def load_pairs(per_bin: int = 10, seed: int = 0, categories=CATEGORIES) -> list:
    rng = np.random.default_rng(seed)
    pairs = []
    for category in categories:
        for seq_dir in sorted((ROOT / category).glob("seq*")):
            frames = load_frames(seq_dir)
            chosen = sample_pairs(frames, per_bin, rng)
            extract_frames(seq_dir, {frames[k].index for ij in chosen for k in ij})
            for i, j in chosen:
                pairs.append(make_pair("objectron", f"{category}/{seq_dir.name}", frames[i], frames[j], metric=True))
    return pairs
