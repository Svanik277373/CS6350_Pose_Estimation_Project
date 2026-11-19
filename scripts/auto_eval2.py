"""Re-score scripts/auto_eval.py's test pairs with region version 2 (src/pipeline/region2.py),
keeping every method's R so the two-method agreement check can be evaluated.

    venv\\Scripts\\python.exe scripts\\auto_eval2.py

Same pairs, same estimated focal length (read from results/auto_eval/pairs.csv), same three
methods; the region is decided with region2.RULE_V2 (chosen on the tuning split). The reference
row (dataset K and region) is copied from pairs.csv. Adds per pair the angle between the
mast3r and accurate rotations ("agreement"). Writes results/auto_eval/pairs_v2.csv. New file only.
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import auto_eval as AE  # noqa: E402  (pairs, methods, scoring, match memo)
import auto_run  # noqa: E402
from src.pipeline import region2, rotation_error_deg  # noqa: E402
from src.pipeline.focal import K_from_focal  # noqa: E402


def main():
    old = pd.read_csv(ROOT / "results" / "auto_eval" / "pairs.csv")
    rng = np.random.default_rng(0)
    cells = AE.main_pairs(1, rng) | AE.tiny_pairs(2, rng) | AE.large_pairs(2, rng)
    order = AE.round_robin(cells)
    out = ROOT / "results" / "auto_eval" / "pairs_v2.csv"
    print(f"rule {region2.RULE_V2}; {len(order)} pairs", flush=True)
    rows_all, changed = [], 0
    for n, ((group, obj, abin), pair) in enumerate(order, 1):
        prev = old[old.pair == pair.name]
        if prev.empty:
            print("missing in pairs.csv:", pair.name)
            continue
        t0 = time.perf_counter()
        AE._memo.clear()
        img1, img2, _, _ = pair.load()
        a = region2.analyse(img1, img2)
        o_obj, o_mode, _ = region2.decide(a, region2.ORIGINAL)
        v_obj, v_mode, v_why = region2.decide(a, region2.RULE_V2)
        same = (o_obj is v_obj) and o_mode == v_mode
        changed += not same
        m1, m2, note, mode = region2.finish(a, v_obj, v_mode, v_why)
        base = prev[prev.method == "mast3r"].iloc[0].to_dict()   # carries est_f (the reference row does not)
        K1, K2 = K_from_focal(base["est_f"], img1.shape), K_from_focal(base["est_f"], img2.shape)
        box_masks = m1 is not None and (auto_run.is_box(m1) or auto_run.is_box(m2))
        fsrc = str(base.get("focal_source", "estimated by MASt3R"))
        keep = {k: base[k] for k in ["pair", "dataset", "object", "group", "bin", "angle_deg", "shape", "true_f",
                                     "est_f", "f_err_pct", "focal_source", "t_focal"]}
        keep |= dict(region_mode=mode, region_note=note[:120], cover1=np.nan if m1 is None else float(m1.mean()),
                     region_changed=not same, region_mode_v1=o_mode)
        rows = [prev[prev.method == "true_K_mask"].iloc[0].to_dict() | dict(region_changed=not same)]
        Rs = {}
        for method in AE.METHODS:
            AE._reused[0] = 0.0
            tm = time.perf_counter()
            res, mode_m = AE.run_method(method, img1, img2, K1, K2, m1, m2, mode)
            Rs[method] = res.R if res.ok else None
            rows.append(keep | dict(method=method, reproj=res.reproj_rms_px, inliers=res.n_inliers,
                                    matches=res.n_matches, model=res.model,
                                    seconds=time.perf_counter() - tm + AE._reused[0], final_mode=mode_m,
                                    reason=(res.reason or "")[:80],
                                    verdict=auto_run.verdict(res, fsrc, method, box_masks, mode_m)[:100],
                                    R=" ".join(f"{v:.6f}" for v in res.R.ravel()) if res.ok else "")
                        | AE.score(res, pair))
        agree = (rotation_error_deg(Rs["mast3r"], Rs["accurate"])
                 if Rs["mast3r"] is not None and Rs["accurate"] is not None else np.inf)
        for r in rows:
            r["agree_mast3r_accurate"] = agree
        rows_all += rows
        pd.DataFrame(rows_all).to_csv(out, index=False)
        e_old = prev[prev.method == "mast3r"].err.iloc[0]
        e_new = [r for r in rows if r["method"] == "mast3r"][0]["err"]
        print(f"[{n}/{len(order)}] {pair.name:40s} {o_mode:11s} -> {mode:11s} mast3r err {e_old:7.2f} -> {e_new:7.2f}"
              f"  agree {agree:6.2f}  ({time.perf_counter() - t0:.0f} s)", flush=True)
    print(f"done: region changed on {changed} of {len(order)} pairs", flush=True)


if __name__ == "__main__":
    main()
