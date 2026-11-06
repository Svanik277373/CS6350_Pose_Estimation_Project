"""Shape-based relative pose for plain rectangular objects (phones, books, cards, ...).

When an object has too little texture to match (a phone: black reflective screen, plain back),
its outline still carries the pose. A rectangle seen by a calibrated camera fixes its own
3D pose up to scale (planar PnP, IPPE: Collins & Bartoli 2014), so:

  1. fit a quadrilateral to the object mask in each view -> 4 corners;
  2. estimate the rectangle's aspect ratio and pose in each view (both views share one
     object model, so the two poses have the same scale);
  3. relative pose = pose2 * pose1^-1.

The outline is symmetric: corner i in view 1 could be any corner of view 2 (4 cyclic
shifts). Shifts by 90 deg swap width and height, so they are ruled out when the aspect
ratios disagree; the remaining 180 deg ambiguity is broken by the image content: the
candidate whose homography lines up the most feature matches / pixels wins.

Tried and rejected (made poses worse on CO3D phones): snapping the sides to image edges
(Phase 4) and refining the corner homography photometrically with ECC (Phase 6) -- phone
screens are mirrors, so their pixels do not move like the phone.
"""
import time

import cv2
import numpy as np

from .estimate import PoseResult
from .match import match

MIN_QUAD_IOU = 0.85      # quadrilateral vs mask overlap; below this the object isn't a rectangle
MIN_AREA_PX = 400        # outlines smaller than this are too coarse to give a pose
ASPECT_TOL = 0.25        # |log(aspect1 / aspect2)| below this counts as the same aspect ratio
MAX_SKEW_DEG = 15.0      # a real rectangle's sides are perpendicular in 3D; allowed deviation
VOTE_TOL = 0.03          # match agrees with a candidate if within this fraction of the object size


# ---------------------------------------------------------------- outline -> corners

def _line_intersection(l1, l2):
    """Lines as (vx, vy, x0, y0) from cv2.fitLine."""
    d1, p1 = l1[:2], l1[2:]
    d2, p2 = l2[:2], l2[2:]
    A = np.array([d1, -d2]).T
    if abs(np.linalg.det(A)) < 1e-9:
        return None
    s = np.linalg.solve(A, p2 - p1)[0]
    return p1 + s * d1


def _side_lines(quad, pts, iters=3):
    """Fit a line to the outline points along each side of `quad`; re-select and refit a few
    times so a slightly wrong starting side still converges onto the real edge."""
    for _ in range(iters):
        lines = []
        for i in range(4):
            a, b = quad[i], quad[(i + 1) % 4]
            d = b - a
            L = np.linalg.norm(d)
            u = (pts - a) @ d / L ** 2                                          # position along the side
            dist = np.abs(d[0] * (pts[:, 1] - a[1]) - d[1] * (pts[:, 0] - a[0])) / L   # distance from it
            # skip the ends: rounded corners bend away from the straight side
            near = (u > 0.15) & (u < 0.85) & (dist < max(3.0, 0.04 * L))
            if near.sum() < 5:
                lines.append(np.r_[d / L, a])
            else:
                lines.append(cv2.fitLine(pts[near].astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel())
        corners = [_line_intersection(lines[i - 1], lines[i]) for i in range(4)]
        if any(c is None for c in corners):
            return None
        quad = np.array(corners)
    return quad


def _iou(quad, m):
    poly = np.zeros_like(m)
    cv2.fillConvexPoly(poly, np.round(quad).astype(np.int32), 1)
    return np.logical_and(poly, m).sum() / max(np.logical_or(poly, m).sum(), 1)


def fit_quad(mask):
    """Four corners (4x2, clockwise in the image) of the object outline, and how well a
    quadrilateral explains the mask (IoU). Returns (None, 0) if no sensible quad exists.

    (Snapping the sides to image edges was tried and made poses worse: on phones the
    strongest nearby edge is often the screen border or a shadow, not the outline.)"""
    m = (mask > 0).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not cs:
        return None, 0.0
    c = max(cs, key=cv2.contourArea)
    if cv2.contourArea(c) < MIN_AREA_PX:
        return None, 0.0
    pts = c.reshape(-1, 2).astype(np.float64)
    # An outline cut by the image border is not the object's real edge
    h, w = m.shape
    if pts[:, 0].min() <= 1 or pts[:, 1].min() <= 1 or pts[:, 0].max() >= w - 2 or pts[:, 1].max() >= h - 2:
        return None, 0.0
    hull = cv2.convexHull(c)
    peri = cv2.arcLength(hull, True)

    # Several simplifications of the hull give 4 vertices; refine each, keep the best fit
    best, best_iou = None, 0.0
    for eps in np.linspace(0.005, 0.15, 59):
        approx = cv2.approxPolyDP(hull, eps * peri, True)
        if len(approx) < 4:
            break
        if len(approx) != 4:
            continue
        quad = _side_lines(approx.reshape(4, 2).astype(np.float64), pts)
        if quad is None or np.max(np.linalg.norm(quad - quad.mean(0), axis=1)) > peri:
            continue
        iou = _iou(quad, m)
        if iou > best_iou:
            best, best_iou = quad, iou
    if best is None:
        return None, 0.0
    quad = best

    # Clockwise in image coordinates (y down) => positive signed area with this formula
    area = 0.5 * np.sum(quad[:, 0] * np.roll(quad[:, 1], -1) - np.roll(quad[:, 0], -1) * quad[:, 1])
    if area < 0:
        quad = quad[::-1].copy()
    return quad, float(best_iou)


# ---------------------------------------------------------------- corners -> pose

def _skew_deg(quad, K):
    """How far the quad's sides are from perpendicular once back-projected with K (degrees).
    Any 4 points fit *some* plane, but only a rectangle gives 90 deg in 3D."""
    unit = np.float32([[0, 0], [1, 0], [1, 1], [0, 1]])
    M = np.linalg.inv(K) @ cv2.getPerspectiveTransform(unit, quad.astype(np.float32))
    c = M[:, 0] @ M[:, 1] / (np.linalg.norm(M[:, 0]) * np.linalg.norm(M[:, 1]))
    return abs(90.0 - np.degrees(np.arccos(np.clip(c, -1, 1))))


def _aspect(quad, K):
    """Width/height of the rectangle (side 0-1 over side 1-2), from the plane homography."""
    unit = np.float64([[0, 0], [1, 0], [1, 1], [0, 1]])
    H = cv2.getPerspectiveTransform(unit.astype(np.float32), quad.astype(np.float32))
    M = np.linalg.inv(K) @ H
    return np.linalg.norm(M[:, 0]) / np.linalg.norm(M[:, 1])


def _rect_pose(quad, K, aspect):
    """Object-to-camera pose of a rectangle aspect x 1 (corner 0 at the origin)."""
    obj = np.float64([[0, 0, 0], [aspect, 0, 0], [aspect, 1, 0], [0, 1, 0]])
    ok, rvecs, tvecs, errs = cv2.solvePnPGeneric(obj, quad, K, None, flags=cv2.SOLVEPNP_IPPE)
    if not ok:
        return None
    best = int(np.argmin(np.ravel(errs)))        # IPPE returns the two planar solutions
    R, _ = cv2.Rodrigues(rvecs[best])
    return R, tvecs[best].ravel(), obj


def _project(R, t, K, X):
    x = (X @ R.T + t) @ K.T
    return x[:, :2] / x[:, 2:3]


# ---------------------------------------------------------------- 180 deg tie-break

def _ncc(a, b, valid):
    a, b = a[valid].astype(np.float64), b[valid].astype(np.float64)
    if len(a) < 50:
        return -1.0
    a, b = a - a.mean(), b - b.mean()
    return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-9))


def _photo_score(img1, img2, H, mask2):
    """Normalised cross-correlation of image 1 warped onto image 2, on the object."""
    g1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
    g2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
    warped = cv2.warpPerspective(g1, H, (g2.shape[1], g2.shape[0]))
    inside = cv2.warpPerspective(np.ones_like(g1), H, (g2.shape[1], g2.shape[0])) > 0
    valid = cv2.erode((mask2 > 0).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & inside
    return _ncc(warped, g2, valid)


def estimate_pose_shape(img1, img2, K1, K2, mask1, mask2, matcher="xfeat", max_side=800) -> PoseResult:
    """Relative pose from the object outline. `matcher` only breaks the 180 deg symmetry."""
    start = time.perf_counter()

    def fail(reason, **kw):
        return PoseResult(False, model="shape", seconds=time.perf_counter() - start, reason=reason, **kw)

    if mask1 is None or mask2 is None:
        return fail("shape pose needs object masks")
    q1, iou1 = fit_quad(mask1)
    q2, iou2 = fit_quad(mask2)
    if q1 is None or q2 is None or min(iou1, iou2) < MIN_QUAD_IOU:
        return fail(f"outline is not a quadrilateral (IoU {min(iou1, iou2):.2f})")

    skew = max(_skew_deg(q1, K1), _skew_deg(q2, K2))
    if skew > MAX_SKEW_DEG:
        return fail(f"outline is not a rectangle in 3D (corners {skew:.0f} deg off square)")

    a1 = _aspect(q1, K1)
    shifts = []
    for k in range(4):
        q2k = np.roll(q2, -k, axis=0)
        if abs(np.log(a1 / _aspect(q2k, K2))) < ASPECT_TOL:
            shifts.append(k)
    if not shifts:   # aspect ratios disagree for every pairing (bad outline): try all
        shifts = list(range(4))

    p1 = p2 = np.empty((0, 2))
    if len(shifts) > 1:
        p1, p2, _ = match(img1, img2, mask1, mask2, matcher=matcher, max_side=max_side, crop=True)
    size = np.sqrt(cv2.contourArea(q2.astype(np.float32)))

    candidates = []
    for k in shifts:
        q2k = np.roll(q2, -k, axis=0)
        aspect = np.sqrt(a1 * _aspect(q2k, K2))   # one object model shared by both views
        s1, s2 = _rect_pose(q1, K1, aspect), _rect_pose(q2k, K2, aspect)
        if s1 is None or s2 is None:
            continue
        (R1, t1, obj), (R2, t2, _) = s1, s2
        R = R2 @ R1.T
        t = t2 - R @ t1
        H = cv2.getPerspectiveTransform(q1.astype(np.float32), q2k.astype(np.float32))
        votes = 0
        if len(p1):
            h = np.hstack([p1, np.ones((len(p1), 1))]) @ H.T
            votes = int((np.linalg.norm(h[:, :2] / h[:, 2:3] - p2, axis=1) < VOTE_TOL * size).sum())
        photo = _photo_score(img1, img2, H, mask2) if len(shifts) > 1 else 0.0
        res = np.vstack([_project(R1, t1, K1, obj) - q1, _project(R2, t2, K2, obj) - q2k])
        rms = float(np.sqrt(np.mean(np.sum(res ** 2, axis=1))))
        candidates.append(dict(k=k, R=R, t=t, votes=votes, photo=photo, rms=rms))
    if not candidates:
        return fail("PnP failed")

    # Matches decide (even a few are reliable: on 88 test pairs the vote was never wrong,
    # pixel correlation was wrong 13 times); pixels only break exact ties
    best = max(candidates, key=lambda c: (c["votes"], c["photo"]))

    t = best["t"] / max(np.linalg.norm(best["t"]), 1e-12)
    return PoseResult(ok=True, R=best["R"], t=t, model="shape", n_matches=len(p1), n_inliers=best["votes"],
                      reproj_rms_px=best["rms"], seconds=time.perf_counter() - start,
                      reason=f"shift {best['k']} of {shifts}", pts1=q1, pts2=np.roll(q2, -best["k"], axis=0))
