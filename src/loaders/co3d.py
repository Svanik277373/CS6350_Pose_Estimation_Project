"""CO3Dv2 loader (cellphone, handbag).

cameras.json stores PyTorch3D cameras: X_cam = X_world @ R + T (row vectors), camera axes
x left / y up / z forward, and intrinsics in "ndc_isotropic" units. Converted to OpenCV with
  R_cv = F @ R.T,  t_cv = F @ T,  F = diag(-1, -1, 1)
  s = min(H, W) / 2,  f_px = f_ndc * s,  c_px = (W/2, H/2) - p_ndc * s
Poses come from COLMAP, so translation is only known up to scale (metric=False).
"""
import json
from pathlib import Path

import cv2
import numpy as np

from .common import Frame, make_pair, sample_pairs

ROOT = Path(__file__).resolve().parents[2] / "data" / "co3d"
CATEGORIES = ["cellphone", "handbag"]

FLIP_XY = np.diag([-1.0, -1.0, 1.0])


def _to_opencv(viewpoint: dict, height: int, width: int):
    R = FLIP_XY @ np.array(viewpoint["R"]).T
    t = FLIP_XY @ np.array(viewpoint["T"])

    assert viewpoint["intrinsics_format"] == "ndc_isotropic"
    s = min(height, width) / 2.0
    fx, fy = np.array(viewpoint["focal_length"]) * s
    px, py = np.array(viewpoint["principal_point"])
    K = np.array([[fx, 0.0, width / 2.0 - px * s],
                  [0.0, fy, height / 2.0 - py * s],
                  [0.0, 0.0, 1.0]])
    return K, R, t


def _read_rgb(path: Path) -> np.ndarray:
    return cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB)


def _read_mask(path: Path) -> np.ndarray:
    # CO3D masks are soft foreground probabilities stored as 0-255
    return cv2.imread(str(path), cv2.IMREAD_GRAYSCALE) > 127


def load_frames(seq_dir: Path) -> list:
    frames = []
    for ann in json.loads((seq_dir / "cameras.json").read_text()):
        height, width = ann["image"]["size"]
        K, R, t = _to_opencv(ann["viewpoint"], height, width)
        img_path = seq_dir / "images" / Path(ann["image"]["path"]).name
        mask_path = seq_dir / "masks" / Path(ann["mask"]["path"]).name
        frames.append(Frame(
            index=ann["frame_number"], K=K, R=R, t=t,
            load_image=lambda p=img_path: _read_rgb(p),
            load_mask=lambda p=mask_path: _read_mask(p),
        ))
    return frames


def load_pairs(per_bin: int = 10, seed: int = 0, categories=CATEGORIES) -> list:
    rng = np.random.default_rng(seed)
    pairs = []
    for category in categories:
        for seq_dir in sorted((ROOT / category).glob("seq*")):
            frames = load_frames(seq_dir)
            for i, j in sample_pairs(frames, per_bin, rng):
                pairs.append(make_pair("co3d", f"{category}/{seq_dir.name}", frames[i], frames[j], metric=False))
    return pairs
