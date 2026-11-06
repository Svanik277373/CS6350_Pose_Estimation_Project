"""MVImgNet loader (key, watch): small everyday objects filmed with a phone.

Each sequence holds ~30 frames, a background-removed cut-out per frame (its alpha channel is
the object mask) and a COLMAP sparse model:
  cameras.bin  SIMPLE_RADIAL camera: f, cx, cy, k (one radial distortion term)
  images.bin   per frame: quaternion (qw, qx, qy, qz) and t, world-to-camera -- already
               the OpenCV convention, X_cam = R X_world + t
Images (and masks) are undistorted on load with K kept as is, so the rest of the pipeline
sees an ideal pinhole camera. Poses come from COLMAP: scale unknown (metric=False), and
less precise than motion capture.
"""
import struct
from pathlib import Path

import cv2
import numpy as np

from .common import Frame, make_pair, sample_pairs

ROOT = Path(__file__).resolve().parents[2] / "data" / "mvimgnet"
CATEGORIES = ["key", "watch"]
SIMPLE_RADIAL = 2


def _read_cameras(path: Path) -> dict:
    """camera_id -> (K, dist, width, height)."""
    b = path.read_bytes()
    n, off, cams = struct.unpack("<Q", b[:8])[0], 8, {}
    for _ in range(n):
        cid, model, w, h = struct.unpack("<iiQQ", b[off:off + 24])
        off += 24
        assert model == SIMPLE_RADIAL, f"unexpected COLMAP camera model {model}"
        f, cx, cy, k = struct.unpack("<4d", b[off:off + 32])
        off += 32
        cams[cid] = (np.array([[f, 0, cx], [0, f, cy], [0, 0, 1.0]]), np.array([k, 0, 0, 0.0]), w, h)
    return cams


def _read_images(path: Path) -> dict:
    """image name -> (R, t, camera_id), world-to-camera."""
    b = path.read_bytes()
    n, off, out = struct.unpack("<Q", b[:8])[0], 8, {}
    for _ in range(n):
        _, qw, qx, qy, qz, tx, ty, tz, cid = struct.unpack("<i7di", b[off:off + 64])
        off += 64
        end = b.index(b"\0", off)
        name = b[off:end].decode()
        off = end + 1
        n_pts = struct.unpack("<Q", b[off:off + 8])[0]
        off += 8 + 24 * n_pts
        R = np.array([
            [1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qw * qz), 2 * (qx * qz + qw * qy)],
            [2 * (qx * qy + qw * qz), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qw * qx)],
            [2 * (qx * qz - qw * qy), 2 * (qy * qz + qw * qx), 1 - 2 * (qx * qx + qy * qy)]])
        out[name] = (R, np.array([tx, ty, tz]), cid)
    return out


def _undistort(img, K, dist, interpolation=cv2.INTER_LINEAR):
    h, w = img.shape[:2]
    mx, my = cv2.initUndistortRectifyMap(K, dist, None, K, (w, h), cv2.CV_32FC1)
    return cv2.remap(img, mx, my, interpolation)


def _read_rgb(path, K, dist):
    return _undistort(cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB), K, dist)


def _read_mask(path, K, dist):
    alpha = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)[..., 3]
    return _undistort(alpha, K, dist, cv2.INTER_NEAREST) > 127


def load_frames(seq_dir: Path) -> list:
    cams = _read_cameras(seq_dir / "sparse" / "0" / "cameras.bin")
    frames = []
    for name, (R, t, cid) in sorted(_read_images(seq_dir / "sparse" / "0" / "images.bin").items()):
        K, dist, _, _ = cams[cid]
        img = seq_dir / "images" / name
        mask = img.with_name(img.stem + "_bg_removed.png")
        frames.append(Frame(
            index=int(img.stem), K=K, R=R, t=t,
            load_image=lambda p=img, K=K, d=dist: _read_rgb(p, K, d),
            load_mask=(lambda p=mask, K=K, d=dist: _read_mask(p, K, d)) if mask.exists() else None,
        ))
    return frames


def is_complete(seq_dir: Path) -> bool:
    """All COLMAP files and every registered frame's image + cut-out are on disk
    (a sequence still being downloaded is skipped)."""
    sparse = seq_dir / "sparse" / "0"
    if not ((sparse / "cameras.bin").exists() and (sparse / "images.bin").exists()):
        return False
    names = _read_images(sparse / "images.bin")
    return all((seq_dir / "images" / n).exists()
               and (seq_dir / "images" / (Path(n).stem + "_bg_removed.png")).exists() for n in names)


def load_pairs(per_bin: int = 5, seed: int = 0, categories=CATEGORIES) -> list:
    rng = np.random.default_rng(seed)
    pairs = []
    for category in categories:
        for seq_dir in sorted((ROOT / category).glob("seq*")):
            if not is_complete(seq_dir):
                continue
            frames = load_frames(seq_dir)
            for i, j in sample_pairs(frames, per_bin, rng):
                pairs.append(make_pair("mvimgnet", f"{category}/{seq_dir.name}", frames[i], frames[j], metric=False))
    return pairs
