"""Object region, version 2: region.py's steps split into analyse / decide / finish, so the
decision rule can be changed without recomputing SAM and the matches.

    a = analyse(img1, img2)            # SAM 2.1 segments, XFeat+LightGlue matches, motion + change scores
    obj, mode, why = decide(a, rule)   # which segment is the object (or the whole images)
    m1, m2, note, mode = finish(a, obj, mode, why)

decide(a, ORIGINAL) reproduces region.find_regions exactly (no name given). The change in
version 2: in static scenes the change rule (region no longer lines up after the background's
motion is undone) fired on tiny segments -- a few hundred pixels of a poster or a checkerboard,
where parallax and blur alone break the local homography -- and the pose was then computed on
that patch. RULE_V2 lets the change rule alone declare an object only for segments of at least
`change_min_area` of the image and with a similarity gap of at least `change_gap`; smaller or
weaker ones count only if the motion rule (matches) agrees. The values are chosen on the tuning
split (scripts/region_tune.py), never on test pairs.

region.py is left unchanged (benchmark and earlier results come from it).
"""
import json
from pathlib import Path

import cv2
import numpy as np

from . import region as R

ORIGINAL = dict(change_min_area=0.0, change_gap=R.CHANGE_GAP)
# chosen on the tuning split by scripts/pick_rule.py (results/region_tune/chosen.json)
_CHOSEN = Path(__file__).resolve().parents[2] / "results" / "region_tune" / "chosen.json"
RULE_V2 = (json.loads(_CHOSEN.read_text())["rule"] if _CHOSEN.exists()
           else dict(change_min_area=0.02, change_gap=R.CHANGE_GAP))


def analyse(img1, img2):
    """Everything region.find_regions computes before its decision (no detector)."""
    a = dict(img1=img1, img2=img2, cands=[], bg_out=None, planar_drop=set())
    segs1 = R._sam_segments(img1)
    cands = R._candidates(segs1, R.MIN_AREA_ANY)
    a["cands"] = cands
    if not cands:
        return a
    from .match import match
    p1, p2, scale = match(img1, img2, None, None, matcher="xfeat_lg", max_side=800)
    i1, i2 = R._pixels(p1, img1.shape), R._pixels(p2, img2.shape)
    inside = np.zeros(len(p1), bool)
    for c in cands:
        c["sel"] = c["mask"][i1[:, 1], i1[:, 0]]
        inside |= c["sel"]
    background = ~inside
    thresh = 2.0 / min(scale, 1.0)
    a.update(p1=p1, p2=p2, i1=i1, i2=i2, background=background)
    for c in cands:
        c["motion"] = False
    if background.sum() >= 15:
        F, inl = cv2.findFundamentalMat(p1[background], p2[background], cv2.USAC_MAGSAC, thresh, 0.999, 10000)
        if F is not None and F.shape == (3, 3):
            bg_out = 1.0 - inl.ravel().astype(bool).mean()
            a["bg_out"] = bg_out
            outlier = R.G_sampson(F, p1, p2) > thresh ** 2
            for c in cands:
                n = int(c["sel"].sum())
                c["n"] = n
                c["out"] = float(outlier[c["sel"]].mean()) if n else 0.0
                c["motion"] = (n >= R.MIN_MATCHES and c["out"] - bg_out >= R.MOVED_GAP
                               and c["area"] >= R.MIN_AREA_MOVED)
            H, inl_H = cv2.findHomography(p1[background], p2[background], cv2.USAC_MAGSAC, thresh,
                                          maxIters=10000, confidence=0.999)
            planar_bg = H is not None and inl_H.ravel().mean() >= R.PLANAR_SHARE * (1.0 - bg_out)
            if any(c["motion"] for c in cands) and planar_bg:
                F_all, _ = cv2.findFundamentalMat(p1, p2, cv2.USAC_MAGSAC, thresh, 0.999, 10000)
                if F_all is not None and F_all.shape == (3, 3):
                    out_all = R.G_sampson(F_all, p1, p2) > thresh ** 2
                    for c in cands:
                        if c["motion"] and not out_all[c["sel"]].mean() >= R.MOVED_GAP:
                            c["motion"] = False
        for c in sorted(cands, key=lambda c: -c["score"])[:R.MAX_CHANGE_CANDS]:
            cs = R.change_score(img1, img2, c["mask"], p1, p2, background, thresh)
            if cs is None:
                continue
            c["ncc"], c["ring"] = cs
            c["static"] = cs[1] >= R.RING_MIN and cs[1] - cs[0] < R.CHANGE_GAP
    return a


def decide(a, rule):
    """(obj1 candidate or None, mode, why) under `rule`; mirrors region.find_regions."""
    cands = a["cands"]
    if not cands:
        return None, "none", "no separate object in image 1: whole images used"
    moved = [c for c in cands if c.get("motion")]
    changed = [c for c in cands if "ncc" in c and c["ring"] >= R.RING_MIN
               and c["ring"] - c["ncc"] >= rule["change_gap"]
               and (c["area"] >= rule["change_min_area"] or c.get("motion"))]
    if moved or changed:
        pool = {id(c): c for c in moved + changed}.values()
        obj1 = max(pool, key=lambda c: c["area"])
        parts = []
        if any(c is obj1 for c in changed):
            parts.append(f"it no longer lines up after the background's motion is undone "
                         f"(similarity {obj1['ncc']:.2f} vs {obj1['ring']:.2f} around it)")
        if any(c is obj1 for c in moved):
            parts.append(f"{100 * obj1['out']:.0f}% of its {obj1['n']} matches do not follow the background, "
                         f"vs {100 * a['bg_out']:.0f}% elsewhere")
        return obj1, "moved", "moved differently from the background: " + "; ".join(parts)
    judged = [c for c in cands if c.get("n", 0) >= R.MIN_MATCHES or c.get("static")]
    unjudged = [c for c in cands if c.get("n", 0) < R.MIN_MATCHES and not c.get("static")
                and c["area"] >= R.MIN_AREA_UNJUDGED]
    static_area = max((c["area"] for c in judged), default=0.0)
    if unjudged and unjudged[0]["area"] > static_area:
        return unjudged[0], "unconfirmed", "chosen by size and position; too few matches on it to confirm by motion"
    if judged:
        return None, "scene", ("everything moved together (static scene, moving camera): whole images used "
                               "-- the result is the camera's motion relative to the scene")
    if unjudged:
        return unjudged[0], "unconfirmed", "chosen by size and position; too few matches on it to confirm by motion"
    return None, "none", "no separate object found: whole images used"


_seg2 = {}


def finish(a, obj1, mode, why):
    """Masks for both images from the decision (the image-2 SAM segments are computed once)."""
    if obj1 is None:
        return None, None, why, mode
    img2 = a["img2"]
    key = id(img2)
    if key not in _seg2:
        _seg2.clear()
        _seg2[key] = R._sam_segments(img2)
    real = R._sam_segments
    R._sam_segments = lambda img: _seg2[key] if img is img2 else real(img)
    try:
        from_obj = obj1["mask"][a["i1"][:, 1], a["i1"][:, 0]]
        obj2, how = R._counterpart(obj1, img2, a["i2"], from_obj)
    finally:
        R._sam_segments = real
    if obj2 is None:
        return None, None, f"{how}: whole images used", "none"
    return (R._clean(obj1["mask"]), R._clean(obj2["mask"]),
            f"object found by SAM 2.1 ({100 * obj1['area']:.1f}% / {100 * obj2['area']:.1f}% of the image): "
            f"{why}; {how}", mode)


def find_regions(img1, img2, rule=RULE_V2):
    """Drop-in for region.find_regions (no name): (mask1, mask2, note, mode)."""
    a = analyse(img1, img2)
    return finish(a, *decide(a, rule))
