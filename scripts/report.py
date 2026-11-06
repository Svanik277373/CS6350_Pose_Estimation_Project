"""Phase 10: the final results table and overview figure, built from every run's pairs.csv.

    venv\\Scripts\\python.exe scripts\\report.py

Test split only (pairs never used for tuning), object only (matches restricted to the
object's region; the "with surroundings" comparison lives in results/experiments/masks.md).
Methods whose results are missing are skipped, so this can run at any time.
Writes results/overview.md and results/overview.png; README.md quotes these numbers.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.pipeline.metrics import pose_auc  # noqa: E402

RES = ROOT / "results"
DATASETS = ["tum", "objectron", "co3d", "mvimgnet"]
NAMES = {"tum": "TUM", "objectron": "Objectron", "co3d": "CO3D", "mvimgnet": "MVImgNet"}
COLORS = {"tum": "#2a78d6", "objectron": "#eb6834", "co3d": "#1baf7a", "mvimgnet": "#8a5cd1"}  # as evaluate.py
TEXT, MUTED, GRID, SURFACE = "#1f1f1e", "#6b6a63", "#e4e3dc", "#ffffff"
# label -> (results folder(s), kind)
METHODS = {
    "SIFT": ("sift_ref", "classical"),
    "XFeat": ("xfeat_ref", "learned sparse"),
    "XFeat+LightGlue": ("xfeat_lg_ref", "learned sparse"),
    "ALIKED+LightGlue": ("aliked_lg_ref", "learned sparse"),
    "DISK+LightGlue": ("disk_lg_ref", "learned sparse"),
    "LoFTR": ("loftr_ref", "learned dense"),
    "shape (mask outline)": ("shape_ref", "silhouette"),
    "MASt3R": (["mast3r_crop", "mast3r_mvimgnet"], "3D foundation model"),
    "cascade: fast": (["cascade_fast_ref", "cascade_fast_mvimgnet"], "preset"),
    "cascade: accurate": (["cascade_accurate_ref", "cascade_accurate_mvimgnet"], "preset"),
    "cascade: confident": ("confidence/pairs_budget_8s.csv", "preset"),   # simulated = run time, see confidence.py
}


def load(folders):
    folders = [folders] if isinstance(folders, str) else folders
    paths = [RES / f if f.endswith(".csv") else RES / f / "pairs.csv" for f in folders]
    parts = [pd.read_csv(p) for p in paths if p.exists()]
    if not parts:
        return None
    d = pd.concat(parts).drop_duplicates("pair")
    return d[d.split == "test"]


def main():
    rows = []
    for label, (folders, kind) in METHODS.items():
        d = load(folders)
        if d is None:
            continue
        row = dict(method=label, kind=kind)
        for ds in DATASETS:
            s = d[d.dataset == ds]
            if len(s):
                auc = pose_auc(s.pose_err_deg.to_numpy())
                row |= {f"{ds}_auc5": auc[5], f"{ds}_auc10": auc[10], f"{ds}_auc20": auc[20], f"{ds}_n": len(s)}
        have = [ds for ds in DATASETS if f"{ds}_auc10" in row]
        row["complete"] = len(have) == len(DATASETS)
        row["mean_auc10"] = np.mean([row[f"{ds}_auc10"] for ds in have])
        ok = d[d.ok.astype(bool)]
        row["failed_pct"] = 100 * (1 - d.ok.astype(bool).mean())
        row["median_rot"] = ok.rot_err_deg.median()
        row["median_t"] = ok.t_err_deg.median()
        row["median_reproj"] = ok.reproj_rms_px.median()
        row["s_per_pair"] = d.seconds.median()
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(RES / "overview.csv", index=False)

    def cell(r, key):
        v = r.get(key, np.nan)
        return "-" if pd.isna(v) else f"{v:.1f}"

    lines = ["# Overview: relative pose of the object, test split", "",
             "AUC@10 (%): area under the share-of-pairs-solved curve up to 10 deg of pose error "
             "(max of rotation and translation-direction error); failed pairs count as infinite error. "
             "Object only (matches restricted to the object's region). Medians over solved pairs, all datasets. "
             "Seconds = median wall time per pair on this laptop's CPU (runs were timed under different loads; "
             "see experiments/timing.md for a fair comparison).", "",
             "| method | kind | " + " | ".join(NAMES[d] for d in DATASETS)
             + " | mean | failed | median rot (deg) | median t-dir (deg) | median reproj (px) | s/pair |",
             "|---|---|" + "---|" * (len(DATASETS) + 6)]
    for _, r in df.iterrows():
        mean = cell(r, "mean_auc10") + ("" if r.complete else "*")
        lines.append(f"| {r.method} | {r.kind} | " + " | ".join(cell(r, f"{d}_auc10") for d in DATASETS)
                     + f" | {mean} | {r.failed_pct:.0f}% | {r.median_rot:.2f} | {r.median_t:.2f} | "
                       f"{r.median_reproj:.2f} | {r.s_per_pair:.1f} |")
    lines += ["", "\\* mean over the datasets this method was run on.", "",
              "## AUC@5 / @10 / @20 per dataset", "", "| method | " + " | ".join(NAMES[d] for d in DATASETS) + " |",
              "|---|" + "---|" * len(DATASETS)]
    for _, r in df.iterrows():
        lines.append(f"| {r.method} | " + " | ".join(
            "-" if pd.isna(r.get(f"{d}_auc10", np.nan)) else
            f"{r[f'{d}_auc5']:.1f} / {r[f'{d}_auc10']:.1f} / {r[f'{d}_auc20']:.1f}" for d in DATASETS) + " |")
    n = {d: int(df[f"{d}_n"].max()) for d in DATASETS if f"{d}_n" in df}
    lines += ["", "Test pairs: " + ", ".join(f"{NAMES[d]} {v}" for d, v in n.items()) + "."]
    (RES / "overview.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    figure(df)


def figure(df):
    """Grouped horizontal bars: one group per method, one bar per dataset (AUC@10)."""
    plt.rcParams.update({"font.size": 9, "text.color": TEXT, "axes.labelcolor": MUTED,
                         "xtick.color": MUTED, "ytick.color": TEXT})
    df = df.iloc[::-1].reset_index(drop=True)          # first method on top
    present = [d for d in DATASETS if f"{d}_auc10" in df]
    h = 0.8 / len(present)
    fig, ax = plt.subplots(figsize=(7.5, 0.55 * len(df) + 1.2))
    for k, ds in enumerate(present):
        y = np.arange(len(df)) + (len(present) - 1 - k - (len(present) - 1) / 2) * h
        vals = df[f"{ds}_auc10"].to_numpy(float)
        ok = np.isfinite(vals)
        ax.barh(y[ok], vals[ok], height=h, color=COLORS[ds], edgecolor=SURFACE, linewidth=1.5, label=NAMES[ds])
    for i, r in df.iterrows():                          # direct label: the mean, at the group's right
        ax.text(101, i, f"mean {r.mean_auc10:.1f}" + ("" if r.complete else "*"), va="center", fontsize=8,
                color=MUTED)
    ax.set_yticks(range(len(df)), df.method)
    ax.set_xlim(0, 100)
    ax.set_xlabel("AUC@10 (%), test split, object only")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="y", length=0)
    ax.legend(frameon=False, ncol=len(present), loc="lower center", bbox_to_anchor=(0.45, 1.0))
    fig.tight_layout()
    fig.savefig(RES / "overview.png", dpi=150, facecolor=SURFACE)


if __name__ == "__main__":
    main()
