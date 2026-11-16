"""Fully automatic object region for two photos: no box, no name, no clicks.

    find_regions(img1, img2, name=None) -> (mask1, mask2, note, mode)

  1. If a name is given and YOLO-World finds it confidently in both images (>= DET_CONF),
     its boxes are cut to the object's outline by SAM 2.1 (detect.py, segment.py).
  2. SAM 2.1 is prompted at an 8 x 8 grid of points on image 1; each point gives one segment.
     Segments touching the image border (table, wall, floor) are background; the others are
     object candidates.
  3. MOTION RULE. The two whole images are matched (XFeat+LightGlue) and the background's
     motion is fitted robustly (fundamental matrix, MAGSAC++) to the matches outside all
     candidates. A candidate whose matches mostly do NOT follow that motion was moved on
     its own -- that is the object, whatever its size (a mouse at 2.8% of the image).
     CHANGE DETECTION does the same without needing matches on the object: image 1 is warped
     by the background's local motion and compared with image 2; a segment that no longer
     lines up (while its surroundings do) was moved -- a shiny key or a black wallet.
     If every candidate moves with the background, the scene moved as one piece (static
     scene, moving camera): the whole images are used, which is right for that case.
  4. If the best-sized candidate has too few matches to judge its motion (a black,
     textureless object), it is used anyway -- the note says it was not confirmed.
  5. The same object is found in image 2 by where its matches land (or, with too few
     matches, by size and position).

mode: "detector", "moved" (object confirmed by its own motion), "unconfirmed" (chosen by
size and position only), "scene" (whole images, everything moved together) or "none".
Design choices were set on TUM's tuning split and the project's own wallet/calculator
photos, not on test pairs.
"""
import cv2
import numpy as np

from . import segment
from .detect import find_box

GRID = 12               # SAM point prompts per image side (12 x 12: small objects like a key get hit)
MIN_AREA_ANY = 0.002    # smallest segment considered at all (a key far away)
MIN_AREA_MOVED = 0.015  # a segment shown "moved" by MATCHES alone must be this large (smaller ones with
                        # ~20 matches were noise on Objectron); change detection has no such limit
MIN_AREA_UNJUDGED = 0.01  # without any motion evidence, smaller segments are likely fragments
CHANGE_GAP = 0.30       # "changed": the region lines up this much worse than its surroundings (NCC)
RING_MIN = 0.40         # ... and only if the surroundings themselves line up at least this well
SHIFT_PX = 12           # tolerated misalignment (parallax of a low object, residual blur)
MAX_CHANGE_CANDS = 15   # change detection is run on at most this many candidates
MAX_AREA = 0.60         # larger segments are background
SIZE_RATIO = 3.0        # the object's area may change at most this much between the two images
DET_CONF = 0.25         # trust the detector above this confidence
MIN_MATCHES = 8         # matches needed inside a segment to judge its motion
MOVED_GAP = 0.5         # outlier share must exceed the background's by this much
MIN_VOTES = 10          # matches needed to identify the object in image 2 by matching
PLANAR_SHARE = 0.9      # background is "one flat surface" if a homography keeps this share of F's inliers
BORDER_PX = 3


def _sam_segments(img_rgb):
    """Unique SAM 2.1 segments from a grid of single-point prompts: list of (mask, hits)."""
    if segment._sam is None:                      # load SAM 2.1 (same weights as segment.py)
        segment._sam_mask(np.zeros((64, 64, 3), np.uint8), (0, 0, 32, 32))
    h, w = img_rgb.shape[:2]
    pts = [[w * (i + 0.5) / GRID, h * (j + 0.5) / GRID] for j in range(GRID) for i in range(GRID)]
    res = segment._sam(cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR), points=pts, labels=[1] * len(pts),
                       device="cpu", verbose=False)
    masks = res[0].masks.data.cpu().numpy() > 0.5 if res and res[0].masks is not None else []
    segs = []
    for m in masks:
        if m.shape != (h, w):
            m = cv2.resize(m.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST).astype(bool)
        if not m.any():
            continue
        for k, (other, hits) in enumerate(segs):          # merge near-duplicates (IoU > 0.8)
            inter = (m & other).sum()
            if inter / ((m | other).sum() + 1e-9) > 0.8:
                segs[k] = (other, hits + 1)
                break
        else:
            segs.append((m, 1))
    return segs


def _describe(m):
    h, w = m.shape
    ys, xs = np.nonzero(m)
    touches = (xs.min() < BORDER_PX or ys.min() < BORDER_PX or xs.max() >= w - BORDER_PX or ys.max() >= h - BORDER_PX)
    centre = np.array([xs.mean() / w, ys.mean() / h])
    return m.mean(), touches, centre


def _candidates(segs, min_area):
    out = []
    for m, hits in segs:
        area, touches, centre = _describe(m)
        if touches or not (min_area <= area <= MAX_AREA):
            continue
        centrality = 1.0 - np.linalg.norm(centre - 0.5) / np.sqrt(0.5)   # 1 at the centre, 0 in a corner
        out.append(dict(mask=m, area=area, centre=centre, score=area * (0.25 + centrality)))
    return sorted(out, key=lambda c: -c["score"])


def _clean(m):
    """Fill holes (e.g. a logo SAM left out) and keep the largest component."""
    ys, xs = np.nonzero(m)
    box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    return segment._clean(m, box)


def _pixels(p, shape):
    h, w = shape[:2]
    return np.clip(np.round(p).astype(int), 0, [w - 1, h - 1])


def _ncc(a, b):
    a, b = a - a.mean(), b - b.mean()
    return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-9))


def change_score(img1, img2, mask, p1, p2, background, thresh):
    """Does the region still look the same after the background's local motion is undone?

    The background around the region (matches in a ring of about the region's size) gives a
    local homography; image 1 is warped by it onto image 2 and the region's pixels are compared
    (normalised cross-correlation) -- and so is the ring itself, as the reference for blur,
    lighting and parallax. Returns (ncc_region, ncc_ring) or None if there is too little
    background around the region. A static object scores about as high as its ring; a moved
    one much lower, even without a single match on it (shiny metal, black leather)."""
    h2, w2 = img2.shape[:2]
    ys, xs = np.nonzero(mask)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    bw, bh = x1 - x0, y1 - y0
    near = ((p1[:, 0] > x0 - 1.5 * bw) & (p1[:, 0] < x1 + 1.5 * bw) &
            (p1[:, 1] > y0 - 1.5 * bh) & (p1[:, 1] < y1 + 1.5 * bh) & background)
    if near.sum() < 15:
        near = background
    if near.sum() < 15:
        return None
    H, _ = cv2.findHomography(p1[near], p2[near], cv2.USAC_MAGSAC, thresh, maxIters=5000, confidence=0.999)
    if H is None:
        return None
    g1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY).astype(np.float32)
    g2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY).astype(np.float32)
    warped = cv2.warpPerspective(g1, H, (w2, h2))
    region = cv2.warpPerspective(mask.astype(np.uint8), H, (w2, h2), flags=cv2.INTER_NEAREST) > 0
    valid = cv2.warpPerspective(np.ones_like(g1, np.uint8), H, (w2, h2), flags=cv2.INTER_NEAREST) > 0
    k = max(5, int(0.5 * max(bw, bh)))
    ring = cv2.dilate(region.astype(np.uint8), np.ones((k, k), np.uint8)) > 0
    ring &= ~cv2.dilate(region.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool) & valid
    region &= valid
    if region.sum() < 60 or ring.sum() < 60:
        return None

    def best_ncc(m):
        # best over small shifts: tolerates a few pixels of parallax (a low object above the
        # surface) and of homography error, but not a turned or moved object
        ys_, xs_ = np.nonzero(m)
        a = warped[ys_, xs_]
        best = -1.0
        for dy in range(-SHIFT_PX, SHIFT_PX + 1, 3):
            for dx in range(-SHIFT_PX, SHIFT_PX + 1, 3):
                yy, xx = ys_ + dy, xs_ + dx
                ok = (yy >= 0) & (yy < h2) & (xx >= 0) & (xx < w2)
                if ok.sum() < 0.8 * len(ok):
                    continue
                best = max(best, _ncc(a[ok], g2[yy[ok], xx[ok]]))
        return best
    return best_ncc(region), best_ncc(ring)


def _counterpart(obj1, img2, i2, from_obj):
    """The image-2 segment that is the same object: (candidate dict, how) or (None, reason)."""
    c2 = []
    for m, _ in _sam_segments(img2):
        area, _, centre = _describe(m)
        if area <= MAX_AREA and 1 / SIZE_RATIO <= area / obj1["area"] <= SIZE_RATIO:
            c2.append(dict(mask=m, area=area, centre=centre))
    if not c2:
        return None, "object not found in image 2"
    votes = [int(c["mask"][i2[from_obj, 1], i2[from_obj, 0]].sum()) for c in c2]
    if from_obj.sum() >= MIN_VOTES and max(votes) >= max(MIN_VOTES, 0.3 * from_obj.sum()):
        return c2[int(np.argmax(votes))], f"found in image 2 by {max(votes)} of {int(from_obj.sum())} matches"

    def cost(c):   # few matches (dark, textureless object): most similar size and position
        return abs(np.log(c["area"] / obj1["area"])) + 2.0 * np.linalg.norm(c["centre"] - obj1["centre"])
    return min(c2, key=cost), "found in image 2 by size and position (too few matches to vote)"


def find_regions(img1, img2, name=None):
    """(mask1, mask2, note, mode); masks are None when the whole images should be used."""
    # 1. detector, only when named and confident in both images
    if name:
        b1, lab1, c1 = find_box(img1, name)
        b2, _, c2 = find_box(img2, name, want_class=lab1 if b1 is not None else None)
        if b1 is not None and b2 is not None and min(c1, c2) >= DET_CONF:
            m1, _ = segment.auto_mask(img1, b1, "sam")
            m2, _ = segment.auto_mask(img2, b2, "sam")
            return m1, m2, f"'{name}' detected ({c1:.2f} / {c2:.2f}), outline by SAM 2.1", "detector"

    # 2. candidate segments in image 1 (small ones too: the motion rule may confirm them)
    segs1 = _sam_segments(img1)
    cands = _candidates(segs1, MIN_AREA_ANY)
    if not cands:
        return None, None, "no separate object in image 1: whole images used", "none"

    # 3. motion rule: does a candidate move differently from the background?
    from .match import match
    p1, p2, scale = match(img1, img2, None, None, matcher="xfeat_lg", max_side=800)
    i1, i2 = _pixels(p1, img1.shape), _pixels(p2, img2.shape)
    inside = np.zeros(len(p1), bool)
    for c in cands:
        c["sel"] = c["mask"][i1[:, 1], i1[:, 0]]
        inside |= c["sel"]
    background = ~inside
    moved, bg_out = [], None
    thresh = 2.0 / min(scale, 1.0)
    if background.sum() >= 15:
        F, inl = cv2.findFundamentalMat(p1[background], p2[background], cv2.USAC_MAGSAC, thresh, 0.999, 10000)
        if F is not None and F.shape == (3, 3):
            bg_out = 1.0 - inl.ravel().astype(bool).mean()
            res = G_sampson(F, p1, p2)
            outlier = res > thresh ** 2
            for c in cands:
                n = int(c["sel"].sum())
                c["n"] = n
                c["out"] = float(outlier[c["sel"]].mean()) if n else 0.0
                if n >= MIN_MATCHES and c["out"] - bg_out >= MOVED_GAP and c["area"] >= MIN_AREA_MOVED:
                    moved.append(c)
            # A background that is one flat surface (a table, a floor) leaves its 3D motion ambiguous,
            # and a STATIC object standing on it can then look "moved". Only in that case, check
            # whether one motion fitted to background + object together explains the object too.
            H, inl_H = cv2.findHomography(p1[background], p2[background], cv2.USAC_MAGSAC, thresh,
                                          maxIters=10000, confidence=0.999)
            planar_bg = H is not None and inl_H.ravel().mean() >= PLANAR_SHARE * (1.0 - bg_out)
            if moved and planar_bg:
                F_all, _ = cv2.findFundamentalMat(p1, p2, cv2.USAC_MAGSAC, thresh, 0.999, 10000)
                if F_all is not None and F_all.shape == (3, 3):
                    out_all = G_sampson(F_all, p1, p2) > thresh ** 2
                    moved = [c for c in moved if out_all[c["sel"]].mean() >= MOVED_GAP]

    # 3b. change detection: undo the background's local motion; a segment that no longer lines up
    # with image 2 was moved -- works without matches on it (shiny key, black wallet) and at any size
    changed = []
    if background.sum() >= 15:
        for c in sorted(cands, key=lambda c: -c["score"])[:MAX_CHANGE_CANDS]:
            cs = change_score(img1, img2, c["mask"], p1, p2, background, thresh)
            if cs is None:
                continue
            c["ncc"], c["ring"] = cs
            c["static"] = cs[1] >= RING_MIN and cs[1] - cs[0] < CHANGE_GAP
            if cs[1] >= RING_MIN and cs[1] - cs[0] >= CHANGE_GAP:
                changed.append(c)

    if moved or changed:
        pool = {id(c): c for c in moved + changed}.values()
        # the largest moved segment: the whole object rather than a part of it (key head vs key)
        obj1 = max(pool, key=lambda c: c["area"])
        mode = "moved"
        parts = []
        if any(c is obj1 for c in changed):
            parts.append(f"it no longer lines up after the background's motion is undone "
                         f"(similarity {obj1['ncc']:.2f} vs {obj1['ring']:.2f} around it)")
        if any(c is obj1 for c in moved):
            parts.append(f"{100 * obj1['out']:.0f}% of its {obj1['n']} matches do not follow the background, "
                         f"vs {100 * bg_out:.0f}% elsewhere")
        why = "moved differently from the background: " + "; ".join(parts)
    else:
        # all followed the background, by matches or by lining up
        judged = [c for c in cands if c.get("n", 0) >= MIN_MATCHES or c.get("static")]
        unjudged = [c for c in cands if c.get("n", 0) < MIN_MATCHES and not c.get("static")
                    and c["area"] >= MIN_AREA_UNJUDGED]
        static_area = max((c["area"] for c in judged), default=0.0)
        if unjudged and unjudged[0]["area"] > static_area:
            # a region too dark/plain to judge by motion (black wallet) or seen after a very large
            # turn, and larger than anything shown to be static (stains on the table): the object
            obj1, mode = unjudged[0], "unconfirmed"
            why = "chosen by size and position; too few matches on it to confirm by motion"
        elif judged:
            # the largest compact regions followed the background: a static scene
            return (None, None, "everything moved together (static scene, moving camera): whole images used "
                    "-- the result is the camera's motion relative to the scene", "scene")
        elif unjudged:
            obj1, mode = unjudged[0], "unconfirmed"
            why = "chosen by size and position; too few matches on it to confirm by motion"
        else:
            return None, None, "no separate object found: whole images used", "none"

    # 4. the same object in image 2
    from_obj = obj1["mask"][i1[:, 1], i1[:, 0]]
    obj2, how = _counterpart(obj1, img2, i2, from_obj)
    if obj2 is None:
        return None, None, f"{how}: whole images used", "none"
    return (_clean(obj1["mask"]), _clean(obj2["mask"]),
            f"object found by SAM 2.1 ({100 * obj1['area']:.1f}% / {100 * obj2['area']:.1f}% of the image): "
            f"{why}; {how}", mode)


def G_sampson(F, p1, p2):
    from .geometry import sampson_sq
    return sampson_sq(F, p1, p2)
