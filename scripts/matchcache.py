"""Matched points saved per (matcher, pair), so geometry experiments don't re-run the networks.

    from matchcache import cached_matches
    p1, p2, scale = cached_matches("aliked_lg", pair, crop=True)

Matching depends only on the images and masks, not on K, so experiments that change the
geometry (perturbed intrinsics, forced H/E, ...) can re-use the same matches. Files live in
data/cache/matches/<matcher>[_crop]/<pair>.npz (not in git; deleted = recomputed).
"""
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.pipeline.match import match  # noqa: E402

CACHE = ROOT / "data" / "cache" / "matches"


def cached_matches(matcher, pair, crop=True, max_side=800, images=None):
    """(p1, p2, scale) for a Pair; images = pair.load() output if already loaded."""
    return cached_matches_timed(matcher, pair, crop, max_side, images)[:3]


def cached_matches_timed(matcher, pair, crop=True, max_side=800, images=None):
    """(p1, p2, scale, seconds the matching took); seconds is NaN for entries cached before
    timing was stored (scripts/evaluate.py then takes the time from the earlier run)."""
    path = CACHE / f"{matcher}{'_crop' if crop else ''}" / (pair.name.replace("/", "__") + ".npz")
    if path.exists():
        z = np.load(path)
        return z["p1"], z["p2"], float(z["scale"]), float(z["seconds"]) if "seconds" in z else float("nan")
    img1, img2, m1, m2 = images if images is not None else pair.load()
    start = time.perf_counter()
    p1, p2, scale = match(img1, img2, m1, m2, matcher=matcher, max_side=max_side, crop=crop)
    seconds = time.perf_counter() - start
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, p1=p1, p2=p2, scale=scale, seconds=seconds)
    return p1, p2, scale, seconds
