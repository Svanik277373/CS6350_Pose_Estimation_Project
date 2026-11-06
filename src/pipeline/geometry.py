"""Two-view geometry: homography (planar) and essential matrix (general 3D) models.

References: Hartley & Zisserman, "Multiple View Geometry" (homography decomposition,
triangulation, Sampson error); Nister 2004 (5-point essential matrix, used by
cv2.findEssentialMat); Torr's GRIC for choosing between the two models.

Point arrays are Nx2 pixel coordinates; "normalized" points are K^-1 [u, v, 1].
Poses map camera-1 coordinates to camera-2 coordinates: X2 = R X1 + t.
"""
import cv2
import numpy as np


def skew(v):
    return np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


def to_normalized(pts, K):
    h = np.hstack([pts, np.ones((len(pts), 1))]) @ np.linalg.inv(K).T
    return h[:, :2] / h[:, 2:3]


def fundamental_from_pose(R, t, K1, K2):
    return np.linalg.inv(K2).T @ skew(t) @ R @ np.linalg.inv(K1)


# ---------------------------------------------------------------- residuals (pixels^2)

def sampson_sq(F, p1, p2):
    """Squared Sampson distance: first-order geometric error to the epipolar constraint."""
    h1 = np.hstack([p1, np.ones((len(p1), 1))])
    h2 = np.hstack([p2, np.ones((len(p2), 1))])
    Fx1, Ftx2 = h1 @ F.T, h2 @ F
    num = np.sum(h2 * Fx1, axis=1) ** 2
    den = Fx1[:, 0] ** 2 + Fx1[:, 1] ** 2 + Ftx2[:, 0] ** 2 + Ftx2[:, 1] ** 2
    return num / np.maximum(den, 1e-12)


def homography_transfer_sq(H, p1, p2):
    """Squared symmetric transfer error, averaged over the two directions."""
    def transfer(M, a):
        h = np.hstack([a, np.ones((len(a), 1))]) @ M.T
        return h[:, :2] / h[:, 2:3]
    fwd = np.sum((transfer(H, p1) - p2) ** 2, axis=1)
    bwd = np.sum((transfer(np.linalg.inv(H), p2) - p1) ** 2, axis=1)
    return 0.5 * (fwd + bwd)


# ---------------------------------------------------------------- robust model fitting

def estimate_homography(p1, p2, thresh_px):
    H, inl = cv2.findHomography(p1, p2, cv2.USAC_MAGSAC, thresh_px, maxIters=10000, confidence=0.999)
    # A (near-)singular H maps the image onto a line or point: degenerate, not a real plane
    if H is None or np.linalg.cond(H) > 1e12:
        return None, np.zeros(len(p1), bool)
    return H, inl.ravel().astype(bool)


def estimate_essential(x1n, x2n, thresh_norm):
    E, inl = cv2.findEssentialMat(x1n, x2n, focal=1.0, pp=(0.0, 0.0), method=cv2.USAC_MAGSAC,
                                  prob=0.999, threshold=thresh_norm, maxIters=10000)
    if E is None or E.shape != (3, 3):   # several solutions get stacked as 3k x 3; keep the best one
        if E is None:
            return None, np.zeros(len(x1n), bool)
        E = E[:3]
    return E, inl.ravel().astype(bool)


def gric(err_sq, sigma, model):
    """Torr's Geometric Robust Information Criterion (lower is better).

    Each correspondence is a point in R^4 (r=4). A homography constrains it to a
    2-dimensional manifold (d=2) with 8 parameters; an essential matrix to a
    3-dimensional manifold (d=3) with 5 parameters. Residuals are capped so outliers
    cost a fixed amount instead of dominating.
    """
    r = 4
    d, k = {"H": (2, 8), "E": (3, 5)}[model]
    n = len(err_sq)
    lam1, lam2, lam3 = np.log(r), np.log(r * n), 2.0
    rho = np.minimum(err_sq / sigma ** 2, lam3 * (r - d))
    return float(np.sum(rho) + lam1 * d * n + lam2 * k)


# ---------------------------------------------------------------- pose recovery

def triangulate(R, t, x1n, x2n):
    """Triangulate normalized correspondences; returns Nx3 points in camera-1 coordinates."""
    P1 = np.hstack([np.eye(3), np.zeros((3, 1))])
    P2 = np.hstack([R, t.reshape(3, 1)])
    X = cv2.triangulatePoints(P1, P2, x1n.T, x2n.T)
    return (X[:3] / X[3]).T


def cheirality_count(R, t, x1n, x2n):
    """Number of points that end up in front of both cameras."""
    X1 = triangulate(R, t, x1n, x2n)
    X2 = X1 @ R.T + t
    return int(np.sum((X1[:, 2] > 0) & (X2[:, 2] > 0)))


AMBIGUITY_RATIO = 1.5   # Sampson errors closer than this give no evidence either way


def pose_from_homography(H, K1, K2, p1, p2, inliers):
    """Decompose H into (R, t, n) candidates and keep the physically valid one.

    Decomposition gives up to 4 solutions; removing those that put points behind a camera
    leaves two, and for a perfectly planar scene two views cannot tell them apart (a known
    two-fold ambiguity). They are separated by, in order:
      1. points in front of both cameras after triangulation,
      2. Sampson error over all matches -- off-plane points fit only the true pose,
         used only when it clearly prefers one candidate,
      3. otherwise a prior: the plane faces both cameras (plane normal close to the
         viewing axis in both views), true when looking at an object's surface.
    """
    Hn = np.linalg.inv(K2) @ H @ K1
    _, Rs, ts, normals = cv2.decomposeHomographyMat(Hn, np.eye(3))
    x1n, x2n = to_normalized(p1[inliers], K1), to_normalized(p2[inliers], K2)

    candidates = list(range(len(Rs)))
    visible = cv2.filterHomographyDecompByVisibleRefpoints(
        Rs, normals, x1n.reshape(-1, 1, 2).astype(np.float32), x2n.reshape(-1, 1, 2).astype(np.float32))
    if visible is not None and len(visible) > 0:
        candidates = [int(i) for i in np.ravel(visible)]

    def evidence(i):
        R, t = Rs[i], ts[i].ravel()
        if np.linalg.norm(t) < 1e-9:      # pure rotation: no translation to judge by
            return 0, np.inf
        t = t / np.linalg.norm(t)
        median_sampson = np.median(sampson_sq(fundamental_from_pose(R, t, K1, K2), p1, p2))
        return cheirality_count(R, t, x1n, x2n), median_sampson

    def faces_cameras(i):
        n = normals[i].ravel()
        return abs(n[2]) + abs((Rs[i] @ n)[2])

    ev = {i: evidence(i) for i in candidates}
    most_in_front = max(c for c, _ in ev.values())
    finalists = sorted((i for i in candidates if ev[i][0] == most_in_front), key=lambda i: ev[i][1])
    best = finalists[0]
    if len(finalists) > 1:
        e_best, e_next = ev[finalists[0]][1], ev[finalists[1]][1]
        if not (e_next > AMBIGUITY_RATIO * e_best):
            best = max(finalists, key=faces_cameras)
    R, t = Rs[best], ts[best].ravel()
    norm = np.linalg.norm(t)
    return R, (t / norm if norm > 1e-9 else t), normals[best].ravel()


TWIN_MATCH_DEG = 10.0   # the E pose "is" a homography candidate if their rotations differ less
TWIN_FIT_RATIO = 3.0     # replacement's median Sampson error may be at most this times the E pose's
                         # (chosen on the tuning split from 1.1-inf; off -> on: +1.9 mean AUC@10 on test)


def planar_twin(R, t, H, K1, K2, p1, p2, inliers):
    """For a (near-)planar scene the essential matrix is not unique: both physically valid
    decompositions of the scene plane's homography fit every planar point, and E-estimation
    can return either (seen live on a book: 3 deg instead of the true 28 deg). If the E pose
    coincides with one homography candidate, compare it with the other ("twin") using the same
    evidence as pose_from_homography: Sampson error over all matches when it clearly prefers
    one, else the prior that the plane faces both cameras. Returns (R, t) of the twin if it
    should replace the E pose, else None (also when the E pose matches no candidate: then the
    scene is not planar enough for the ambiguity to exist)."""
    if H is None:
        return None
    Hn = np.linalg.inv(K2) @ H @ K1
    _, Rs, ts, normals = cv2.decomposeHomographyMat(Hn, np.eye(3))
    x1n, x2n = to_normalized(p1[inliers], K1), to_normalized(p2[inliers], K2)
    visible = cv2.filterHomographyDecompByVisibleRefpoints(
        Rs, normals, x1n.reshape(-1, 1, 2).astype(np.float32), x2n.reshape(-1, 1, 2).astype(np.float32))
    cands = [int(i) for i in np.ravel(visible)] if visible is not None and len(visible) else list(range(len(Rs)))

    def rot_diff(Ra, Rb):
        return np.degrees(np.arccos(np.clip((np.trace(Ra.T @ Rb) - 1) / 2, -1, 1)))

    def sampson(Ri, ti):
        n = np.linalg.norm(ti)
        return np.inf if n < 1e-9 else float(np.median(sampson_sq(fundamental_from_pose(Ri, ti / n, K1, K2), p1, p2)))

    def faces(i):
        n = normals[i].ravel()
        return abs(n[2]) + abs((Rs[i] @ n)[2])

    same = min(range(len(Rs)), key=lambda i: rot_diff(Rs[i], R))
    if rot_diff(Rs[same], R) > TWIN_MATCH_DEG:
        return None
    s_pose = sampson(R, t)

    def fits(i):
        # on a truly 3D object a pose derived from one plane cannot explain the off-plane
        # matches: keep E unless the replacement fits all matches nearly as well
        return sampson(Rs[i], ts[i].ravel()) <= TWIN_FIT_RATIO * s_pose

    if same not in cands:
        # the E pose is a decomposition the plane rules out (scene plane behind a camera for
        # the matched points): replace it by the best physically valid one
        best = min(cands, key=lambda i: sampson(Rs[i], ts[i].ravel()))
        if rot_diff(Rs[best], R) <= 2.0 or not fits(best):
            return None
        tt = ts[best].ravel()
        return Rs[best], tt / np.linalg.norm(tt)
    twins = [i for i in cands if rot_diff(Rs[i], Rs[same]) > 2.0]
    if not twins:
        return None
    twin = min(twins, key=lambda i: sampson(Rs[i], ts[i].ravel()))
    # compare the two homography candidates with each other: the E pose itself was fitted to
    # these matches and always fits them a little better than either decomposed pose
    s_e, s_t = sampson(Rs[same], ts[same].ravel()), sampson(Rs[twin], ts[twin].ravel())
    if not fits(twin):
        return None
    if s_e > AMBIGUITY_RATIO * s_t or (not s_t > AMBIGUITY_RATIO * s_e and faces(twin) > faces(same)):
        tt = ts[twin].ravel()
        return Rs[twin], tt / np.linalg.norm(tt)
    return None


def pose_from_essential(E, x1n, x2n, inliers):
    mask = inliers.astype(np.uint8).reshape(-1, 1).copy()
    _, R, t, mask = cv2.recoverPose(E, x1n, x2n, focal=1.0, pp=(0.0, 0.0), mask=mask)
    return R, t.ravel(), mask.ravel().astype(bool)


def reprojection_rms(R, t, K1, K2, p1, p2):
    """Triangulate the correspondences with the estimated pose and reproject them into both
    images; RMS of the pixel errors over points in front of both cameras."""
    x1n, x2n = to_normalized(p1, K1), to_normalized(p2, K2)
    X1 = triangulate(R, t, x1n, x2n)
    X2 = X1 @ R.T + t
    ok = (X1[:, 2] > 0) & (X2[:, 2] > 0)
    if ok.sum() == 0:
        return float("nan")
    u1 = X1[ok] @ K1.T
    u2 = X2[ok] @ K2.T
    e1 = np.sum((u1[:, :2] / u1[:, 2:3] - p1[ok]) ** 2, axis=1)
    e2 = np.sum((u2[:, :2] / u2[:, 2:3] - p2[ok]) ** 2, axis=1)
    return float(np.sqrt(np.mean(np.concatenate([e1, e2]))))
