"""Pick the report's example-case pairs from results/auto_eval/pairs_v2.csv (MASt3R rows) and print
them as report_figures.py arguments: one clean success per situation plus the worst failure."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
d = pd.read_csv(ROOT / "results" / "auto_eval" / "pairs_v2.csv")
m = d[d.method == "mast3r"].copy()
used, out = set(), []


def pick(label, sub, worst=False):
    sub = sub[~sub.pair.isin(used)].sort_values("err", ascending=not worst)
    if len(sub):
        used.add(sub.pair.iloc[0])
        out.append((label, sub.pair.iloc[0]))


main = m[m.group == "main"]
pick("planar", main[(main.dataset == "tum") & (main["shape"] == "planar") & (main.bin != "5-15")])
pick("3d", main[main.object.isin(["cereal_box", "handbag", "laptop"])])
pick("small", m[m.object.isin(["key", "watch"]) & (m.group == "main")])
pick("large", m[m.group == "large"])
pick("tiny", m[m.group == "tiny"])
pick("failure", main, worst=True)
print(" ".join(f"--case {lab} {p}" for lab, p in out))
