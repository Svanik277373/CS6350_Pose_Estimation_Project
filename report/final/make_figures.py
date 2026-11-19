"""Figures for the final report (report/final/main.tex) drawn from saved results.

    venv\\Scripts\\python.exe report\\final\\make_figures.py

pipeline.png   the two-image pipeline
datasets.png   one test pair per dataset with its true rotation
viewpoint.png  AUC@10 per viewpoint regime and method (results/auto_eval/pairs_v2.csv)
cdf.png        cumulative pose-error curves per method
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
OUT = HERE / "figures"
INK, MUTED = "#1f2430", "#5b6170"
FILL, EDGE = "#e3eef8", "#2f6f9f"
FILL2, EDGE2 = "#fbe8d3", "#b5651d"
FILL3, EDGE3 = "#dff1e2", "#2e7d4f"
plt.rcParams.update({"font.family": "DejaVu Sans"})


def box(ax, x, y, w, h, title, lines, fc, ec):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.10", fc=fc, ec=ec, lw=1.5))
    ax.text(x + w / 2, y + h - 0.18, title, ha="center", va="top", fontsize=10, fontweight="bold", color=INK)
    ax.text(x + w / 2, y + h - 0.55, "\n".join(lines), ha="center", va="top", fontsize=8, color=MUTED, linespacing=1.35)


def arrow(ax, p, q, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=13, lw=1.4, color=INK,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2))


def pipeline():
    fig, ax = plt.subplots(figsize=(16, 4.6))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    w, h = 2.35, 1.35
    top = [("Input", ["two RGB images", "no K, no mask,", "no object name"], FILL3, EDGE3),
           ("Focal length", ["MASt3R point map", "+ Weiszfeld fit", "(70° FOV fallback)"], FILL2, EDGE2),
           ("Object region", ["SAM 2.1 segments", "motion rule (F, MAGSAC++)", "change rule (warp + NCC)"], FILL2, EDGE2),
           ("ROI crop", ["mask box + 20% margin", "long side ≤ 800 px", "matches mapped back"], FILL2, EDGE2)]
    bot = [("Matching", ["MASt3R (default)", "or confident /", "accurate cascade"], FILL, EDGE),
           ("Robust fitting", ["MAGSAC++", "homography H (4-pt)", "essential E (5-pt)"], FILL, EDGE),
           ("Model choice", ["GRIC:", "planar (H) or", "general 3D (E)"], FILL, EDGE),
           ("Decomposition", ["cheirality test", "plane tie-break", "planar-twin check"], FILL, EDGE),
           ("Refinement", ["Levenberg–Marquardt", "on all inliers,", "inlier re-selection"], FILL, EDGE),
           ("Output", ["R, t direction", "reprojection RMS (px)", "verdict"], FILL3, EDGE3)]
    yt, yb = 2.85, 0.55
    xs_t = [0.3 + i * 2.75 for i in range(len(top))]
    for x, (t, l, fc, ec) in zip(xs_t, top):
        box(ax, x, yt, w, h, t, l, fc, ec)
    for a, b in zip(xs_t[:-1], xs_t[1:]):
        arrow(ax, (a + w, yt + h / 2), (b, yt + h / 2))
    xs_b = [0.3 + i * 2.6 for i in range(len(bot))]
    wb = 2.25
    for x, (t, l, fc, ec) in zip(xs_b, bot):
        box(ax, x, yb, wb, h, t, l, fc, ec)
    for a, b in zip(xs_b[:-1], xs_b[1:]):
        arrow(ax, (a + wb, yb + h / 2), (b, yb + h / 2))
    ymid = (yt + yb + h) / 2
    xa, xb = xs_t[-1] + w / 2, xs_b[0] + wb / 2
    ax.plot([xa, xa, xb], [yt, ymid, ymid], color=INK, lw=1.4)
    arrow(ax, (xb, ymid), (xb, yb + h))
    ax.text(xs_t[-1] + w + 0.25, yt + h / 2, "Front end: quantities\nthat are not given\nare estimated", fontsize=9,
            color=EDGE2, style="italic", va="center")
    ax.text(xs_b[-1] + wb, yb - 0.22, "Pose estimation from the object's matches", fontsize=9, color=EDGE,
            style="italic", ha="right")
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "pipeline.png", dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def datasets():
    from report_figures import pair_from_name
    pairs = [("TUM RGB-D (poster, planar)", "tum/flat_near/611-700"),
             ("Objectron (laptop, 3D)", "objectron/laptop/seq09/267-295"),
             ("CO3D (mobile phone)", "co3d/cellphone/seq08/62-96"),
             ("MVImgNet (watch, small)", "mvimgnet/watch/seq09/20-26")]
    fig, ax = plt.subplots(2, 4, figsize=(16, 6.4))
    for c, (label, name) in enumerate(pairs):
        p = pair_from_name(name)
        a, b, _, _ = p.load()
        for r, im in enumerate((a, b)):
            ax[r, c].imshow(im)
            ax[r, c].axis("off")
        ax[0, c].set_title(f"{label}\ntrue rotation {p.angle_deg:.1f}°", fontsize=10)
    ax[0, 0].text(-0.08, 0.5, "view 1", transform=ax[0, 0].transAxes, rotation=90, va="center", fontsize=10)
    ax[1, 0].text(-0.08, 0.5, "view 2", transform=ax[1, 0].transAxes, rotation=90, va="center", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "datasets.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


COL = {"mast3r": "#2f6f9f", "confident": "#d08a2e", "accurate": "#8a8f98", "true_K_mask": "#1f2430"}
LAB = {"mast3r": "MASt3R", "confident": "confident", "accurate": "accurate", "true_K_mask": "reference (true K + mask)"}


def viewpoint():
    from src.pipeline.metrics import pose_auc
    d = pd.read_csv(ROOT / "results" / "auto_eval" / "pairs_v2.csv")
    d["sel"] = np.where(d.group == "main", d.bin, np.where(d.group == "tiny", "<1", "60-90"))
    order = ["<1", "5-15", "15-30", "30-60", "60-90"]
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    x = np.arange(len(order))
    for k, m in enumerate(["mast3r", "confident", "accurate"]):
        v = [pose_auc(d[(d.sel == s) & (d.method == m)].err.to_numpy())[10] for s in order]
        ax.bar(x + (k - 1) * 0.26, v, 0.24, color=COL[m], label=LAB[m])
    ref = [pose_auc(d[(d.sel == s) & (d.method == "true_K_mask")].err.to_numpy())[10] for s in order]
    ax.scatter(x, ref, marker="_", s=500, color=COL["true_K_mask"], zorder=3, label=LAB["true_K_mask"])
    ax.set_xticks(x, ["< 1°\n(consecutive)", "5–15°", "15–30°", "30–60°", "60–90°"])
    ax.set_ylabel("AUC@10 (%)")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=8, ncol=2, frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "viewpoint.png", dpi=200, facecolor="white")
    plt.close(fig)


def cdf():
    d = pd.read_csv(ROOT / "results" / "auto_eval" / "pairs_v2.csv")
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    xs = np.linspace(0, 30, 301)
    for m in ["true_K_mask", "mast3r", "confident", "accurate"]:
        e = d[d.method == m].err.to_numpy()
        ax.plot(xs, [100 * np.mean(e <= v) for v in xs], color=COL[m], lw=2,
                ls="--" if m == "true_K_mask" else "-", label=LAB[m])
    ax.set_xlabel("pose error threshold (deg)")
    ax.set_ylabel("pairs with error below (%)")
    ax.set_ylim(0, 100)
    ax.set_xlim(0, 30)
    ax.grid(alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=8, frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "cdf.png", dpi=200, facecolor="white")
    plt.close(fig)


def dataprep():
    """Offline data preparation: each dataset to frames with K, an OpenCV pose and a mask, then test pairs."""
    fig, ax = plt.subplots(figsize=(16, 6.4))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    rows = [("TUM RGB-D", "640×480 frames,\nmocap ~100 Hz",
             ["pose interpolated at each RGB timestamp:", "linear position, slerp rotation",
              "camera-to-world inverted; whole image = region"]),
            ("Objectron", "phone video (.MOV)\n+ ARKit annotation",
             ["pairs chosen from annotated poses first", "video decoded once, chosen frames only",
              "portrait → landscape; ARKit axes → OpenCV", "mask = hull of projected 3D box"]),
            ("CO3D", "image sequence,\nPyTorch3D cameras",
             ["only needed files fetched (HTTP range)", "NDC intrinsics → pixel K",
              "axes flipped to OpenCV; dataset masks"]),
            ("MVImgNet", "phone frames,\nCOLMAP model",
             ["only needed files fetched (HTTP range)", "radial distortion removed",
              "alpha channel of cut-out = mask"])]
    h, gap = 1.42, 0.12
    for i, (name, raw, steps) in enumerate(rows):
        y = 6.4 - 0.2 - (i + 1) * h - i * gap
        box(ax, 0.2, y, 2.6, h, name, raw.split("\n"), FILL3, EDGE3)
        box(ax, 3.4, y, 5.0, h, "Preprocessing", steps, FILL2, EDGE2)
        arrow(ax, (2.8, y + h / 2), (3.4, y + h / 2))
        arrow(ax, (8.4, y + h / 2), (9.2, 3.2))
    box(ax, 9.2, 2.25, 3.0, 1.9, "Common form", ["frames", "pixel intrinsics K", "world-to-camera pose", "(OpenCV axes)", "object mask"], FILL, EDGE)
    box(ax, 12.8, 2.25, 3.0, 1.9, "Test pairs", ["R_gt = R₂R₁ᵀ", "t_gt = t₂ − R_gt t₁", "stratified by rotation", "tune / test split"], FILL, EDGE)
    arrow(ax, (12.2, 3.2), (12.8, 3.2))
    fig.savefig(OUT / "dataprep.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    dataprep()
    pipeline()
    viewpoint()
    cdf()
    datasets()
    print("written to", OUT)
