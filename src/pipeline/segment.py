"""Automatic object mask from a rough box (run.py --auto-mask).

A hand-drawn box always contains some background. On a dark, low-texture object (a black
wallet on a steel table) the background can hold most of the texture, so the matches -- and
the pose -- end up describing the table, not the object. A tight mask fixes that.

Two methods, both prompted by the box:
  sam     SAM 2.1 (Ravi et al., "SAM 2: Segment Anything in Images and Videos", 2024),
          tiny model via the ultralytics package. The box is a true prompt: the network
          predicts the mask for that box. Weights (~40 MB) go to models/sam/ on first use.
  grabcut OpenCV GrabCut (Rother et al., SIGGRAPH 2004): colour models of object and
          background inside/outside the box, refined by graph cuts. Classical, nothing to
          install; weaker when object and background have similar colours.

The idea of segmenting the object before matching follows the CS6350 TPA-12 report by
Anirudh and Harshavardhan, who used FastSAM; SAM 2.1 is used here because its box prompt
conditions the mask directly instead of choosing among masks made for the whole image.
"""
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SAM_WEIGHTS = ROOT / "models" / "sam" / "sam2.1_t.pt"
METHODS = ("sam", "grabcut")
MIN_FILL = 0.05     # a mask covering less than this share of its box is treated as a failure

_sam = None


def _clean(mask, box):
    """Largest connected component, holes filled, clipped to the box."""
    x0, y0, x1, y1 = box
    m = np.zeros_like(mask)
    m[y0:y1, x0:x1] = mask[y0:y1, x0:x1]
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    if n <= 1:
        return m
    keep = lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    contours, _ = cv2.findContours(keep.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    filled = np.zeros(m.shape, np.uint8)
    cv2.drawContours(filled, contours, -1, 1, thickness=cv2.FILLED)
    return filled.astype(bool)


def _sam_mask(img_rgb, box):
    global _sam
    if _sam is None:
        try:
            from ultralytics import SAM
        except ImportError as e:
            raise RuntimeError("SAM needs the ultralytics package (pip install ultralytics)") from e
        SAM_WEIGHTS.parent.mkdir(parents=True, exist_ok=True)
        # ultralytics downloads a missing checkpoint into the current folder; fetch it into models/sam
        if not SAM_WEIGHTS.exists():
            from ultralytics.utils.downloads import attempt_download_asset
            attempt_download_asset(str(SAM_WEIGHTS))
        _sam = SAM(str(SAM_WEIGHTS))
    res = _sam(cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR), bboxes=[list(box)], device="cpu", verbose=False)
    if not res or res[0].masks is None or len(res[0].masks.data) == 0:
        return None
    m = res[0].masks.data[0].cpu().numpy() > 0.5
    if m.shape != img_rgb.shape[:2]:
        m = cv2.resize(m.astype(np.uint8), (img_rgb.shape[1], img_rgb.shape[0]),
                       interpolation=cv2.INTER_NEAREST).astype(bool)
    return m


def _grabcut_mask(img_rgb, box, iters=5):
    x0, y0, x1, y1 = box
    m = np.zeros(img_rgb.shape[:2], np.uint8)
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR), m, (x0, y0, x1 - x0, y1 - y0), bgd, fgd,
                iters, cv2.GC_INIT_WITH_RECT)
    return (m == cv2.GC_FGD) | (m == cv2.GC_PR_FGD)


def auto_mask(img_rgb, box, method="sam"):
    """Mask of the object inside `box` (x0, y0, x1, y1). Returns (mask, note); if the method
    fails or finds almost nothing, the mask is the box itself and the note says so."""
    h, w = img_rgb.shape[:2]
    x0, y0, x1, y1 = box
    box = (max(0, x0), max(0, y0), min(w, x1), min(h, y1))
    raw = None
    note = ""
    try:
        raw = _sam_mask(img_rgb, box) if method == "sam" else _grabcut_mask(img_rgb, box)
    except Exception as e:      # missing package/weights, download failure, ...
        note = f"{method} failed ({type(e).__name__}: {e})"
    box_area = (box[2] - box[0]) * (box[3] - box[1])
    if raw is not None:
        m = _clean(raw, box)
        fill = m.sum() / max(box_area, 1)
        if fill >= MIN_FILL:
            return m, f"{method} mask covers {100 * fill:.0f}% of the box"
        note = f"{method} found almost nothing in the box ({100 * fill:.1f}%)"
    m = np.zeros((h, w), bool)
    m[box[1]:box[3], box[0]:box[2]] = True
    return m, note + "; using the box instead"


def draw_mask(img_rgb, mask, path, note=""):
    """The image with the mask's outline and a light tint, to check the segmentation."""
    out = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR).copy()
    tint = out.copy()
    tint[mask] = (0.5 * tint[mask] + 0.5 * np.array([60, 200, 60])).astype(np.uint8)
    out = cv2.addWeighted(tint, 0.6, out, 0.4, 0)
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(out, contours, -1, (60, 220, 60), 2, cv2.LINE_AA)
    if note:
        cv2.rectangle(out, (0, 0), (out.shape[1], 36), (30, 30, 30), -1)
        cv2.putText(out, note, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 1, cv2.LINE_AA)
    cv2.imwrite(str(path), out)
