"""Draws the pipeline figure for the report and slides (report/figures/pipeline.png).

    venv\\Scripts\\python.exe report\\figures.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent / "figures"
INK, MUTED = "#1f2430", "#5b6170"
CORE, AUTO, OUTC = "#dcebf7", "#fbe8d3", "#dff1e2"
CORE_E, AUTO_E, OUT_E = "#2f6f9f", "#b5651d", "#2e7d4f"


def box(ax, x, y, w, h, title, lines, fc, ec):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.6))
    ax.text(x + w / 2, y + h - 0.22, title, ha="center", va="top", fontsize=10.5,
            fontweight="bold", color=INK)
    ax.text(x + w / 2, y + h - 0.62, "\n".join(lines), ha="center", va="top", fontsize=8.3,
            color=MUTED, linespacing=1.35)


def arrow(ax, p, q, color=INK, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=14, lw=1.5,
                                 color=color, linestyle=ls, shrinkA=2, shrinkB=2))


def pipeline():
    fig, ax = plt.subplots(figsize=(17, 6.2))
    ax.set_xlim(0, 17)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    w, h = 2.25, 1.95

    # --- automatic front end (only when K and the object region are unknown) ---
    ax.text(0.15, 6.05, "Automatic front end (photos with nothing known: auto_run.py)", fontsize=10,
            fontweight="bold", color=AUTO_E, va="top")
    box(ax, 0.15, 3.75, w, h, "Focal length",
        ["given K / --focal", "else EXIF (35 mm equiv.)", "else MASt3R point map", "  (Weiszfeld fit)",
         "else 70° FOV guess"], AUTO, AUTO_E)
    box(ax, 2.65, 3.75, w + 0.35, h, "Object region",
        ["SAM 2.1 segments (point grid)", "motion rule: outliers to the", "  background's F (MAGSAC)",
         "change rule: warp + NCC", "else whole image (flagged)"], AUTO, AUTO_E)

    # --- core pipeline ---
    ax.text(5.6, 3.25, "Core pipeline (run.py, used for every benchmark number)", fontsize=10,
            fontweight="bold", color=CORE_E, va="top")
    y = 0.75
    stages = [
        ("Inputs", ["two RGB images", "K (intrinsics)", "object masks / boxes"]),
        ("Crop + resize", ["mask box + 20% margin", "longest side ≤ 800 px", "(small objects keep detail)"]),
        ("Matching", ["SIFT | XFeat(+LG)", "ALIKED+LG | DISK+LG", "LoFTR | MASt3R | shape",
                      "or a cascade preset"]),
        ("Robust fit", ["MAGSAC++", "homography H (planar)", "essential E (3D)",
                        "GRIC picks H or E"]),
        ("Decompose", ["(R, t) candidates", "cheirality check", "planar-twin check"]),
        ("Refine", ["Levenberg–Marquardt", "Sampson (E) or", "transfer error (H)"]),
    ]
    xs = [0.15 + i * 2.4 for i in range(len(stages))]
    for x, (t, lines) in zip(xs, stages):
        box(ax, x, y, 2.15, h, t, lines, CORE, CORE_E)
    for a, b in zip(xs[:-1], xs[1:]):
        arrow(ax, (a + 2.15, y + h / 2), (b, y + h / 2))

    # output
    ox = xs[-1] + 2.4
    box(ax, ox, y, 17 - ox - 0.1, h, "Output",
        ["R, rotation angle", "t direction", "RMS reprojection", "error (px)", "|t| if size known"],
        OUTC, OUT_E)
    arrow(ax, (xs[-1] + 2.15, y + h / 2), (ox, y + h / 2))

    # auto -> core
    arrow(ax, (0.15 + w / 2, 3.75), (0.15 + 2.15 * 0.45, y + h), AUTO_E, ls="--")
    arrow(ax, (2.65 + (w + 0.35) / 2, 3.75), (0.15 + 2.15 * 0.8, y + h), AUTO_E, ls="--")
    ax.text(3.45, 3.3, "fills in K and masks", fontsize=8.3, color=AUTO_E, style="italic")

    # cascade note
    ax.text(xs[2] + 1.075, 0.42, "cascade: try methods in order, stop at the first pose with\n"
            "enough inliers (fast / accurate) or high learned confidence (confident)",
            ha="center", va="top", fontsize=8, color=MUTED, style="italic")

    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "pipeline.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def cascades():
    """Small figure: what the three presets try, in order."""
    fig, ax = plt.subplots(figsize=(12, 3.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3.6)
    ax.axis("off")
    rows = [("fast", ["XFeat+LG\n≥ 30 inliers", "SIFT\n≥ 15 inliers", "shape\n(outline)"]),
            ("accurate", ["XFeat+LG\n≥ 200 inliers", "shape\n(outline)", "SIFT\n≥ 50 inliers",
                          "LoFTR\n≥ 120 inliers"]),
            ("confident", ["XFeat+LG", "SIFT", "shape", "MASt3R"])]
    for r, (name, steps) in enumerate(rows):
        yy = 2.65 - r * 1.15
        ax.text(0.1, yy + 0.35, name, fontsize=12, fontweight="bold", color=INK, va="center")
        for i, s in enumerate(steps):
            x = 1.8 + i * 2.5
            last = name == "confident" and i == 3
            ax.add_patch(FancyBboxPatch((x, yy), 1.9, 0.7, boxstyle="round,pad=0.02,rounding_size=0.1",
                                        fc=AUTO if last else CORE, ec=AUTO_E if last else CORE_E, lw=1.4))
            ax.text(x + 0.95, yy + 0.35, s, ha="center", va="center", fontsize=9, color=INK)
            if i:
                arrow(ax, (x - 0.6, yy + 0.35), (x, yy + 0.35))
                ax.text(x - 0.3, yy + 0.5, "fail", ha="center", fontsize=7, color=MUTED)
        if name == "confident":
            ax.text(1.8 + 3 * 2.5 + 2.05, yy + 0.35,
                    "move on unless the learned\nconfidence ≥ 0.45 (P(err < 10°))",
                    fontsize=8.3, color=MUTED, va="center")
    fig.savefig(OUT / "cascades.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    pipeline()
    cascades()
    print("written to", OUT)
