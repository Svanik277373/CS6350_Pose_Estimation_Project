"""Figures for the reports (report/final, report/ieee) drawn from saved results.

    venv\\Scripts\\python.exe report\\final\\make_figures.py

Every figure is drawn on a canvas close to the width at which it is printed (7.2 in for a full-width
figure, 3.5 in for a column), so text stays at 7-10 pt on paper. Text is dark, not grey, for printing.

pipeline.png   the two-image pipeline
dataprep.png   offline preparation of the four datasets
datasets.png   one test pair per dataset with its true rotation
viewpoint.png  AUC@10 per viewpoint regime and method (results/auto_eval/pairs_v2.csv)
cdf.png        cumulative pose-error curves per method
euler_struct_near_gap20.png  roll/pitch/yaw along a TUM sequence (results/euler_track/*.csv)
methods.jpg    one example per method where it wins (results/cases/method_runs.json + methods.json)
"""
import json
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
INK, BODY = "#111418", "#1f2430"
FILL, EDGE = "#e3eef8", "#2f6f9f"
FILL2, EDGE2 = "#fbe8d3", "#b5651d"
FILL3, EDGE3 = "#dff1e2", "#2e7d4f"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.titlesize": 9,
                     "axes.labelsize": 8.5, "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 7.5})


def box(ax, x, y, w, h, title, lines, fc, ec, tsize=8.5, bsize=7.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=0.06", fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h - 0.07, title, ha="center", va="top", fontsize=tsize, fontweight="bold", color=INK)
    ax.text(x + w / 2, y + h - 0.30, "\n".join(lines), ha="center", va="top", fontsize=bsize, color=BODY,
            linespacing=1.3)


def arrow(ax, p, q):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=10, lw=1.1, color=INK,
                                 shrinkA=0, shrinkB=0))


def canvas(w, h):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def pipeline():
    W, Hh = 7.2, 2.62
    fig, ax = canvas(W, Hh)
    w, h, gap = 1.24, 0.84, 0.2
    top = [("Input", ["two RGB images", "no K, no mask,", "no object name"], FILL3, EDGE3),
           ("Focal length", ["MASt3R point map", "+ Weiszfeld fit", "(70° FOV fallback)"], FILL2, EDGE2),
           ("Object region", ["SAM 2.1 segments", "motion rule (F)", "change rule (NCC)"], FILL2, EDGE2),
           ("ROI crop", ["mask box + 20%", "long side ≤ 800 px", "matches mapped back"], FILL2, EDGE2),
           ("Matching", ["MASt3R (default)", "or confident /", "accurate cascade"], FILL, EDGE)]
    bot = [("Robust fitting", ["MAGSAC++", "H: 4-point DLT", "E: 5-point Nistér"], FILL, EDGE),
           ("Model choice", ["GRIC score", "planar → H", "general 3D → E"], FILL, EDGE),
           ("Decomposition", ["cheirality test", "plane tie-break", "planar-twin check"], FILL, EDGE),
           ("Refinement", ["Levenberg–", "Marquardt on", "all inliers"], FILL, EDGE),
           ("Output", ["R, t direction", "reprojection RMS", "verdict"], FILL3, EDGE3)]
    x0 = (W - (5 * w + 4 * gap)) / 2
    xs = [x0 + i * (w + gap) for i in range(5)]
    yt, yb = 1.72, 0.40
    for x, (t, l, fc, ec) in zip(xs, top):
        box(ax, x, yt, w, h, t, l, fc, ec)
    for x, (t, l, fc, ec) in zip(xs, bot):
        box(ax, x, yb, w, h, t, l, fc, ec)
    for a, b in zip(xs[:-1], xs[1:]):
        arrow(ax, (a + w, yt + h / 2), (b, yt + h / 2))
        arrow(ax, (a + w, yb + h / 2), (b, yb + h / 2))
    ymid = (yt + yb + h) / 2
    xa, xb = xs[-1] + w / 2, xs[0] + w / 2
    ax.plot([xa, xa, xb], [yt, ymid, ymid], color=INK, lw=1.1)
    arrow(ax, (xb, ymid), (xb, yb + h))
    for x, fc, ec, lab in [(x0, FILL2, EDGE2, "front end: estimates what is not given (K, object region)"),
                           (x0 + 3.75, FILL, EDGE, "pose from the object's correspondences")]:
        ax.add_patch(FancyBboxPatch((x, 0.1), 0.16, 0.13, boxstyle="round,pad=0,rounding_size=0.02",
                                    fc=fc, ec=ec, lw=1))
        ax.text(x + 0.24, 0.165, lab, fontsize=7.5, va="center", color=INK)
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "pipeline.png", dpi=300, facecolor="white")
    plt.close(fig)


def dataprep():
    """Offline data preparation: each dataset to frames with K, an OpenCV pose and a mask, then test pairs."""
    W, Hh = 7.2, 3.6
    fig, ax = canvas(W, Hh)
    rows = [("TUM RGB-D", ["640×480 frames,", "mocap ~100 Hz"],
             ["pose interpolated at each RGB timestamp", "(linear position, slerp rotation),",
              "camera-to-world inverted; whole image used"]),
            ("Objectron", ["phone video (.MOV)", "+ ARKit annotation"],
             ["pairs chosen from annotated poses; only", "those frames decoded; portrait → landscape;",
              "ARKit → OpenCV axes; mask = hull of 3D box"]),
            ("CO3D", ["image sequence,", "PyTorch3D cameras"],
             ["only needed files fetched (HTTP range);", "NDC intrinsics → pixel K;",
              "axes flipped to OpenCV; dataset masks"]),
            ("MVImgNet", ["phone frames,", "COLMAP model"],
             ["only needed files fetched (HTTP range);", "radial distortion removed;",
              "alpha channel of cut-out = mask"])]
    h, gap, top = 0.80, 0.1, Hh - 0.08
    for i, (name, raw, steps) in enumerate(rows):
        y = top - (i + 1) * h - i * gap
        box(ax, 0.05, y, 1.35, h, name, raw, FILL3, EDGE3)
        box(ax, 1.65, y, 2.85, h, "Preprocessing", steps, FILL2, EDGE2)
        arrow(ax, (1.4, y + h / 2), (1.65, y + h / 2))
        arrow(ax, (4.5, y + h / 2), (4.85, Hh / 2))
    box(ax, 4.85, Hh / 2 - 0.62, 1.12, 1.24, "Common form", ["frames", "pixel K", "world-to-camera", "pose (OpenCV)",
                                                             "object mask"], FILL, EDGE)
    box(ax, 6.12, Hh / 2 - 0.62, 1.05, 1.24, "Test pairs", ["R_gt = R₂R₁ᵀ", "t_gt = t₂ − R_gt t₁", "stratified by",
                                                            "rotation;", "tune / test split"], FILL, EDGE, bsize=7)
    arrow(ax, (5.97, Hh / 2), (6.12, Hh / 2))
    fig.savefig(OUT / "dataprep.png", dpi=300, facecolor="white")
    plt.close(fig)


def datasets():
    from report_figures import pair_from_name
    pairs = [("TUM RGB-D (poster, planar)", "tum/flat_near/611-700"),
             ("Objectron (laptop, 3D)", "objectron/laptop/seq09/267-295"),
             ("CO3D (mobile phone)", "co3d/cellphone/seq08/62-96"),
             ("MVImgNet (watch, small)", "mvimgnet/watch/seq09/20-26")]
    fig, ax = plt.subplots(2, 4, figsize=(7.2, 3.3))
    for c, (label, name) in enumerate(pairs):
        p = pair_from_name(name)
        a, b, _, _ = p.load()
        for r, im in enumerate((a, b)):
            ax[r, c].imshow(im)
            ax[r, c].set_xticks([])
            ax[r, c].set_yticks([])
        ax[0, c].set_title(f"{label}\ntrue rotation {p.angle_deg:.1f}°", fontsize=8)
    ax[0, 0].set_ylabel("view 1", fontsize=8.5)
    ax[1, 0].set_ylabel("view 2", fontsize=8.5)
    fig.tight_layout(pad=0.3, h_pad=0.3, w_pad=0.3)
    fig.savefig(OUT / "datasets.png", dpi=300, facecolor="white")
    plt.close(fig)


COL = {"mast3r": "#2f6f9f", "confident": "#d08a2e", "accurate": "#6b7079", "true_K_mask": "#111418"}
LAB = {"mast3r": "MASt3R", "confident": "confident", "accurate": "accurate", "true_K_mask": "reference (true K + mask)"}


def viewpoint():
    from src.pipeline.metrics import pose_auc
    d = pd.read_csv(ROOT / "results" / "auto_eval" / "pairs_v2.csv")
    d["sel"] = np.where(d.group == "main", d.bin, np.where(d.group == "tiny", "<1", "60-90"))
    order = ["<1", "5-15", "15-30", "30-60", "60-90"]
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    x = np.arange(len(order))
    for k, m in enumerate(["mast3r", "confident", "accurate"]):
        v = [pose_auc(d[(d.sel == s) & (d.method == m)].err.to_numpy())[10] for s in order]
        ax.bar(x + (k - 1) * 0.26, v, 0.24, color=COL[m], label=LAB[m])
    ref = [pose_auc(d[(d.sel == s) & (d.method == "true_K_mask")].err.to_numpy())[10] for s in order]
    ax.scatter(x, ref, marker="_", s=160, linewidths=2, color=COL["true_K_mask"], zorder=3, label=LAB["true_K_mask"])
    ax.set_xticks(x, ["<1°", "5–15°", "15–30°", "30–60°", "60–90°"])
    ax.set_xlabel("viewpoint change")
    ax.set_ylabel("AUC@10 (%)")
    ax.set_ylim(0, 115)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(ncol=2, frameon=False, loc="upper center", columnspacing=0.8, handlelength=1.2)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "viewpoint.png", dpi=300, facecolor="white")
    plt.close(fig)


def cdf():
    d = pd.read_csv(ROOT / "results" / "auto_eval" / "pairs_v2.csv")
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    xs = np.linspace(0, 30, 301)
    for m in ["true_K_mask", "mast3r", "confident", "accurate"]:
        e = d[d.method == m].err.to_numpy()
        ax.plot(xs, [100 * np.mean(e <= v) for v in xs], color=COL[m], lw=1.8,
                ls="--" if m == "true_K_mask" else "-", label=LAB[m])
    ax.set_xlabel("pose error threshold (deg)")
    ax.set_ylabel("pairs with error below (%)")
    ax.set_ylim(0, 100)
    ax.set_xlim(0, 30)
    ax.grid(alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "cdf.png", dpi=300, facecolor="white")
    plt.close(fig)


def euler():
    d = pd.read_csv(ROOT / "results" / "euler_track" / "struct_near_gap20.csv")
    fig, axes = plt.subplots(3, 1, figsize=(5.0, 4.6), sharex=True)
    for ax, name in zip(axes, ["roll", "pitch", "yaw"]):
        ax.plot(range(len(d)), d[f"{name}_gt"], "-o", ms=2.5, lw=1.1, color="#1f5f9f", label="ground truth")
        ax.plot(range(len(d)), d[name], "-o", ms=2.5, lw=1.1, color="#e07b00", label="estimated (two images only)")
        ax.set_ylabel(f"{name} (deg)")
        ax.grid(alpha=0.3)
    axes[0].legend(loc="upper left", ncol=2, frameon=False)
    axes[0].set_ylim(top=axes[0].get_ylim()[1] + 3)
    axes[-1].set_xlabel("pair index (TUM structure sequence, 20-frame gap)")
    fig.tight_layout(pad=0.3, h_pad=0.4)
    fig.savefig(OUT / "euler_struct_near_gap20.png", dpi=300, facecolor="white")
    plt.close(fig)


def methods():
    """Rows = methods, columns = the four winning examples (transposed so every panel is wider)."""
    from report_figures import pair_from_name, side
    runs = json.loads((ROOT / "results" / "cases" / "method_runs.json").read_text())
    rows = json.loads((ROOT / "results" / "cases" / "methods.json").read_text())
    meths = [("SIFT", "sift"), ("XFeat+LightGlue", "xfeat_lg"), ("LoFTR", "loftr"), ("MASt3R", "mast3r"),
             ("accurate", "accurate"), ("confident", "confident")]
    names = dict((k, t) for t, k in meths)
    fig, ax = plt.subplots(len(meths), len(rows), figsize=(7.2, 8.6), squeeze=False)
    for j, row in enumerate(rows):
        k, name = row["winner"], row["pair"]
        r = runs[name]
        pair = pair_from_name(name)
        img1, img2, _, _ = pair.load()
        im, off = side(img1, img2)
        short = name.replace("mvimgnet/", "").replace("objectron/", "").replace("tum/", "")
        ax[0, j].set_title(f"{names[k]} wins\n{short}, {r['angle']:.0f}°", fontsize=8, pad=4)
        for i, (title, key) in enumerate(meths):
            a, res = ax[i, j], r[key]
            a.imshow(im)
            a.set_xticks([])
            a.set_yticks([])
            for u, w in zip(res["p1"][::2], res["p2"][::2]):
                a.plot([u[0], w[0] + off], [u[1], w[1]], "-", lw=0.6,
                       color="#1a9e3a" if res["rot"] < 5 else "#d62728", alpha=0.9)
            win = key == k
            for s in a.spines.values():
                s.set_edgecolor("#1a9e3a" if win else "#bbbbbb")
                s.set_linewidth(3 if win else 0.6)
            txt = (f"rot {res['rot']:.1f}°, t {res['tra']:.1f}°, {res['inliers']} inl." if res["ok"] else "failed")
            a.set_xlabel(txt, fontsize=7.5, labelpad=2, fontweight="bold" if win else "normal")
            if j == 0:
                a.set_ylabel(title, fontsize=8.5)
    fig.tight_layout(pad=0.3, h_pad=0.5, w_pad=0.4)
    fig.savefig(str(OUT / "methods.jpg"), dpi=300, facecolor="white", pil_kwargs={"quality": 90})
    plt.close(fig)


def methods_slide():
    """Landscape version for the slides: rows = the four winning examples, columns = the six methods."""
    from report_figures import pair_from_name, side
    runs = json.loads((ROOT / "results" / "cases" / "method_runs.json").read_text())
    rows = json.loads((ROOT / "results" / "cases" / "methods.json").read_text())
    meths = [("SIFT", "sift"), ("XFeat+LG", "xfeat_lg"), ("LoFTR", "loftr"), ("MASt3R", "mast3r"),
             ("accurate", "accurate"), ("confident", "confident")]
    why = {"mast3r": "MASt3R wins\nweak texture", "confident": "confident wins\nvia MASt3R",
           "accurate": "accurate wins\noutline stage", "loftr": "LoFTR wins\ncheckerboard"}
    fig, ax = plt.subplots(len(rows), len(meths), figsize=(6.4, 3.55), squeeze=False)
    for i, row in enumerate(rows):
        k, name = row["winner"], row["pair"]
        r = runs[name]
        img1, img2, _, _ = pair_from_name(name).load()
        im, off = side(img1, img2)
        for j, (title, key) in enumerate(meths):
            a, res = ax[i, j], r[key]
            a.imshow(im, aspect="auto")
            a.set_xticks([])
            a.set_yticks([])
            for u, w in zip(res["p1"][::3], res["p2"][::3]):
                a.plot([u[0], w[0] + off], [u[1], w[1]], "-", lw=0.5,
                       color="#1a9e3a" if res["rot"] < 5 else "#d62728", alpha=0.9)
            win = key == k
            for s in a.spines.values():
                s.set_edgecolor("#1a9e3a" if win else "#bbbbbb")
                s.set_linewidth(2.5 if win else 0.5)
            a.set_xlabel(f"rot {res['rot']:.1f}°" if res["ok"] else "failed", fontsize=7, labelpad=1,
                         fontweight="bold" if win else "normal")
            if i == 0:
                a.set_title(title, fontsize=8, pad=3)
            if j == 0:
                a.set_ylabel(why[k], fontsize=7)
    fig.tight_layout(pad=0.2, h_pad=0.3, w_pad=0.25)
    fig.savefig(str(OUT / "methods_slide.jpg"), dpi=300, facecolor="white", pil_kwargs={"quality": 90})
    plt.close(fig)


def focal_sens():
    """Mean over the four datasets of AUC@10 when only the focal length is perturbed (same matches)."""
    from src.pipeline.metrics import pose_auc
    d = pd.read_csv(ROOT / "results" / "sensitivity" / "sensitivity.csv")
    d = d[d.kind == "focal"]
    fig, ax = plt.subplots(figsize=(3.5, 2.3))
    for m, lab, col in [("xfeat_lg", "XFeat+LightGlue", "#2f6f9f"), ("aliked_lg", "ALIKED+LightGlue", "#e07b00")]:
        g = d[d.matcher == m]
        xs = sorted(g.error_pct.unique())
        ys = [np.mean([pose_auc(g[(g.error_pct == e) & (g.dataset == ds)].pose_err_deg.to_numpy())[10]
                       for ds in g.dataset.unique()]) for e in xs]
        ax.plot(xs, ys, "-o", ms=3.5, lw=1.6, color=col, label=lab)
        print(m, [round(y, 1) for y in ys])
    ax.set_xlabel("focal-length error (%)")
    ax.set_ylabel("mean AUC@10 (%)")
    ax.grid(alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="lower center")
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "focal_sens.png", dpi=300, facecolor="white")
    plt.close(fig)


def cascades():
    W, Hh = 3.5, 2.55
    fig, ax = canvas(W, Hh)
    rows = [("fast", [("XFeat+LG", "≥ 30 inl."), ("SIFT", "≥ 15 inl."), ("outline", "")], None),
            ("accurate", [("XFeat+LG", "≥ 200 inl."), ("outline", ""), ("SIFT", "≥ 50 inl."), ("LoFTR", "≥ 120 inl.")], None),
            ("confident", [("XFeat+LG", ""), ("SIFT", ""), ("outline", ""), ("MASt3R", "")], 3)]
    w, h, gap, x0 = 0.58, 0.42, 0.12, 0.68
    for r, (name, stages, special) in enumerate(rows):
        y = Hh - 0.12 - (r + 1) * h - r * 0.32
        ax.text(0.02, y + h / 2, name, fontsize=8.5, fontweight="bold", va="center", color=INK)
        for k, (a, b) in enumerate(stages):
            x = x0 + k * (w + gap)
            fc, ec = (FILL2, EDGE2) if special == k else (FILL, EDGE)
            ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.05", fc=fc, ec=ec, lw=1))
            ax.text(x + w / 2, y + h / 2 + (0.07 if b else 0), a, ha="center", va="center", fontsize=7.5, color=INK)
            if b:
                ax.text(x + w / 2, y + h / 2 - 0.1, b, ha="center", va="center", fontsize=7, color=INK)
            if k:
                arrow(ax, (x - gap, y + h / 2), (x, y + h / 2))
    ax.text(0.02, 0.04, "Each arrow: the stage failed its test. confident accepts a stage when the\n"
            "learned P(error < 10°) ≥ 0.45; otherwise it falls through to MASt3R.",
            fontsize=6.8, color=INK, va="bottom")
    fig.savefig(OUT / "cascades.png", dpi=300, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    todo = sys.argv[1:] or ["dataprep", "pipeline", "viewpoint", "cdf", "datasets", "euler", "methods"]
    for f in todo:
        globals()[f]()
        print("written", f, flush=True)
