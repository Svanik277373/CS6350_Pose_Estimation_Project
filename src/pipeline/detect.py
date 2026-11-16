"""Find the object's box in an image, for run.py when no --mask/--box is given.

  find_box(img, "calculator")   YOLO-World (Cheng et al., CVPR 2024), an open-vocabulary
                                detector: the text names the object. Weights (~25 MB) go to
                                models/yolo/ on first use; ultralytics may also fetch its CLIP
                                text encoder the first time (needs internet once).
  find_box(img, None)           the same detector with a list of common small objects; the
                                most confident detection that is not huge is kept.
  select_box(img, title)        draw the box with the mouse (cv2.selectROI) -- the fallback
                                that always works when a screen is available.

The box only has to contain the object; segment.py then cuts the exact outline (SAM 2.1).
"""
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
YOLO_WEIGHTS = ROOT / "models" / "yolo" / "yolov8s-worldv2.pt"
# used when no object name is given: small, hand-held things this project is about
GENERIC = ["wallet", "calculator", "mobile phone", "key", "coin", "watch", "book", "remote control",
           "card", "box", "cup", "plate", "clock", "purse", "bag", "toy car", "bottle", "notebook",
           "glasses case", "mouse", "pen", "charger", "headphones case"]
MAX_AREA = 0.6      # boxes covering more of the image are background (table, wall)
PAD = 0.08          # grow the detected box by this fraction of its size on each side

_yolo = {}


def _detector(classes):
    key = tuple(classes)
    if key not in _yolo:
        from ultralytics import YOLOWorld
        YOLO_WEIGHTS.parent.mkdir(parents=True, exist_ok=True)
        if not YOLO_WEIGHTS.exists():
            from ultralytics.utils.downloads import attempt_download_asset
            attempt_download_asset(str(YOLO_WEIGHTS))
        m = YOLOWorld(str(YOLO_WEIGHTS))
        m.set_classes(list(classes))
        _yolo.clear()
        _yolo[key] = m
    return _yolo[key]


def pad_box(box, shape, pad=PAD):
    h, w = shape[:2]
    x0, y0, x1, y1 = box
    dx, dy = pad * (x1 - x0), pad * (y1 - y0)
    return (int(max(0, x0 - dx)), int(max(0, y0 - dy)), int(min(w, x1 + dx)), int(min(h, y1 + dy)))


def find_box(img_rgb, name=None, want_class=None):
    """(box, label, confidence) or (None, reason, 0). want_class: prefer this label (keeps
    the same object in both images when no name is given)."""
    classes = [name] if name else GENERIC
    try:
        model = _detector(classes)
        res = model.predict(cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR), conf=0.03, device="cpu", verbose=False)
    except Exception as e:
        return None, f"detector unavailable ({type(e).__name__}: {e})", 0.0
    boxes = res[0].boxes if res else None
    if boxes is None or len(boxes) == 0:
        return None, f"no '{name or 'object'}' detected", 0.0
    h, w = img_rgb.shape[:2]
    xyxy = boxes.xyxy.cpu().numpy()
    conf = boxes.conf.cpu().numpy()
    cls = boxes.cls.cpu().numpy().astype(int)
    area = (xyxy[:, 2] - xyxy[:, 0]) * (xyxy[:, 3] - xyxy[:, 1]) / (w * h)
    ok = area < MAX_AREA
    if want_class is not None:
        same = np.array([classes[c] == want_class for c in cls])
        if (ok & same).any():
            ok &= same
    if not ok.any():
        return None, "only background-sized detections", 0.0
    i = int(np.argmax(np.where(ok, conf, -1)))
    return pad_box(xyxy[i], img_rgb.shape), classes[cls[i]], float(conf[i])


def select_box(img_rgb, title="draw a box around the object, then press ENTER"):
    """Let the user drag a box; returns (x0, y0, x1, y1) in image pixels, or None."""
    h, w = img_rgb.shape[:2]
    s = min(1.0, 1100 / w, 750 / h)
    disp = cv2.resize(cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR), (round(w * s), round(h * s)))
    x, y, bw, bh = cv2.selectROI(title, disp, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow(title)
    if bw == 0 or bh == 0:
        return None
    return (int(x / s), int(y / s), int((x + bw) / s), int((y + bh) / s))
