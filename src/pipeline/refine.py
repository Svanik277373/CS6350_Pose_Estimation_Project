"""Non-linear refinement of a relative pose on all its inliers (Levenberg-Marquardt).

RANSAC-style estimators (MAGSAC++) return a model computed from minimal samples plus a
local polish of the *algebraic* model. Here the pose itself is refined, minimising a
geometric pixel error over every inlier (Hartley & Zisserman, ch. 4 and 11):

  E model (general 3D): R (3 params) and the translation direction (2 params, on the unit
      sphere) minimise the Sampson distance, the first-order approximation of the
      reprojection error, without having to estimate every 3D point.
  H model (planar):     R, t/d and the plane normal n (8 params, as many as a homography)
      minimise the symmetric transfer error of the induced homography
      H = K2 (R + (t/d) n^T) K1^-1, so the result stays a rigid motion seen through a plane.

The refined pose is kept only if it lowers the median error (a safeguard: LM can wander
off when the inliers are few or nearly degenerate).
"""
import cv2
import numpy as np
from scipy.optimize import least_squares

from . import geometry as G


def _tangent_basis(v):
    """Two unit vectors orthogonal to v (to move v on the sphere with 2 parameters)."""
    a = np.array([1.0, 0, 0]) if abs(v[0]) < 0.9 else np.array([0, 1.0, 0])
    b1 = np.cross(v, a)
    b1 /= np.linalg.norm(b1)
    return np.stack([b1, np.cross(v, b1)], axis=1)


def _rotate(R0, w):
    return cv2.Rodrigues(np.asarray(w, float))[0] @ R0


def _sampson_signed(R, t, K1, K2, h1, h2):
    F = G.fundamental_from_pose(R, t, K1, K2)
    Fx1, Ftx2 = h1 @ F.T, h2 @ F
    num = np.sum(h2 * Fx1, axis=1)
    den = np.sqrt(Fx1[:, 0] ** 2 + Fx1[:, 1] ** 2 + Ftx2[:, 0] ** 2 + Ftx2[:, 1] ** 2)
    return num / np.maximum(den, 1e-12)


def refine_essential(R0, t0, K1, K2, p1, p2):
    """Refine (R, unit t) on inlier pixels p1, p2. Returns (R, t, improved?)."""
    if len(p1) < 8:
        return R0, t0, False
    h1 = np.hstack([p1, np.ones((len(p1), 1))])
    h2 = np.hstack([p2, np.ones((len(p2), 1))])
    t0 = t0 / np.linalg.norm(t0)
    B = _tangent_basis(t0)

    def unpack(x):
        t = t0 + B @ x[3:]
        return _rotate(R0, x[:3]), t / np.linalg.norm(t)

    def residuals(x):
        return _sampson_signed(*unpack(x), K1, K2, h1, h2)

    sol = least_squares(residuals, np.zeros(5), method="lm", x_scale=np.r_[np.full(3, 1e-2), np.full(2, 1e-2)])
    before = np.median(np.abs(residuals(np.zeros(5))))
    after = np.median(np.abs(sol.fun))
    if not np.all(np.isfinite(sol.x)) or after > before:
        return R0, t0, False
    R, t = unpack(sol.x)
    return R, t, True


def _plane_parameters(H, K1, K2, R, n):
    """t/d for a given (R, n) from the homography: solve s*Hn - (t/d) n^T = R (linear)."""
    Hn = np.linalg.inv(K2) @ H @ K1
    A = np.zeros((9, 4))
    A[:, 0] = Hn.ravel()
    for i in range(3):            # (t n^T)[i, j] = t_i n_j
        for j in range(3):
            A[3 * i + j, 1 + i] = -n[j]
    x, *_ = np.linalg.lstsq(A, R.ravel(), rcond=None)
    return x[1:]


def refine_homography(R0, n0, H, K1, K2, p1, p2):
    """Refine (R, unit t) for a planar object. Returns (R, t, improved?, t/d, n): the last two
    describe the refined plane, so the caller can rebuild its homography."""
    if len(p1) < 8:
        return R0, None, False, None, None
    n0 = n0 / np.linalg.norm(n0)
    td0 = _plane_parameters(H, K1, K2, R0, n0)
    if np.linalg.norm(td0) < 1e-9:
        return R0, None, False, None, None
    B = _tangent_basis(n0)

    def unpack(x):
        n = n0 + B @ x[6:]
        return _rotate(R0, x[:3]), x[3:6], n / np.linalg.norm(n)

    def residuals(x):
        R, td, n = unpack(x)
        Hx = K2 @ (R + np.outer(td, n)) @ np.linalg.inv(K1)
        return np.sqrt(G.homography_transfer_sq(Hx, p1, p2))

    x0 = np.r_[np.zeros(3), td0, np.zeros(2)]
    sol = least_squares(residuals, x0, method="lm")
    before = np.median(residuals(x0))
    after = np.median(sol.fun)
    if not np.all(np.isfinite(sol.x)) or after > before:
        return R0, None, False, None, None
    R, td, n = unpack(sol.x)
    return R, td / np.linalg.norm(td), True, td, n
