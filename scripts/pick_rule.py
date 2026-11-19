"""Pick region2's rule from the tuning run (results/region_tune) and write chosen.json.

Best AUC@10 on the tuning pairs; among rules within 0.5 points of the best, prefer one that still
finds the hand-moved object in every project photo, then the mildest change (smallest min area,
then smallest gap). Test pairs play no part.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from region_tune import GRID  # noqa: E402
from src.pipeline.metrics import pose_auc  # noqa: E402

OUT = ROOT / "results" / "region_tune"
d = pd.read_csv(OUT / "pairs.csv")
auc = [pose_auc(d[f"err_{i}"].to_numpy())[10] for i in range(len(GRID))]
photos_ok = [True] * len(GRID)
for line in (OUT / "summary.md").read_text(encoding="utf-8").splitlines():
    if line.startswith(("| coin", "| key", "| wallet")):
        cells = [c.strip() for c in line.strip("|").split("|")][1:]
        for i, c in enumerate(cells[:len(GRID)]):
            photos_ok[i] &= c.startswith("moved")
best = max(auc)
near = [i for i in range(len(GRID)) if auc[i] >= best - 0.5]
pref = [i for i in near if photos_ok[i]] or near
i = min(pref, key=lambda k: (GRID[k]["change_min_area"], GRID[k]["change_gap"]))
info = dict(rule=GRID[i], auc10_tune=auc[i], auc10_original=auc[0], photos_still_found=photos_ok[i],
            table=[dict(rule=GRID[k], auc10=round(auc[k], 2), photos_ok=photos_ok[k]) for k in range(len(GRID))])
(OUT / "chosen.json").write_text(json.dumps(info, indent=2))
print("chosen", GRID[i], f"AUC@10 tune {auc[i]:.1f} (original {auc[0]:.1f}), photos still found: {photos_ok[i]}")
