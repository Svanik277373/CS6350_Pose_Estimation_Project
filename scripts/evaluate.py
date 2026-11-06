"""Evaluation harness: run one pipeline configuration on every dataset and save the results.

    venv\\Scripts\\python.exe scripts\\evaluate.py --name sift_auto --matcher sift

Pairs are sampled with a fixed seed, so every configuration is scored on exactly the same
pairs. Failed pairs are kept: in the AUC they count as infinite error, and every table
reports the failure rate, so a method can't look good by skipping hard pairs.

Writes results/<name>/:
    pairs.csv     one row per pair (errors, matches, inliers, chosen model, time, ...)
    summary.md    tables per dataset, per object and per viewpoint-change bin
    curves.png    share of pairs solved vs pose error, per dataset
    objects.png   share of pairs solved within 10 deg, per object
"""
import argparse
import cv2
import csv
import json
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from tqdm import tqdm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.loaders import LOADERS, split_of  # noqa: E402
from src.loaders.common import ANGLE_BINS  # noqa: E402
from src.pipeline import ALL_PRESETS, CONFIDENT, PoseResult, estimate_pose, pose_from_matches, estimate_pose_cascade, estimate_pose_confident, estimate_pose_shape, rotation_error_deg, translation_angle_deg  # noqa: E402
from src.pipeline.match import MATCHERS  # noqa: E402
from src.pipeline.metrics import pose_auc  # noqa: E402
from awake import keep_awake  # noqa: E402
from matchcache import cached_matches_timed  # noqa: E402

# pairs per viewpoint bin per sequence; chosen so each dataset gives roughly 250-300 pairs
PER_BIN = {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}
SEED = 0

# Validated categorical palette, fixed order (dataviz reference palette, light mode)
COLORS = {"tum": "#2a78d6", "objectron": "#eb6834", "co3d": "#1baf7a", "mvimgnet": "#8a5cd1"}
INK, INK_2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def object_of(dataset, sequence):
    return sequence if dataset == "tum" else sequence.split("/")[0]


def bin_of(angle):
    for lo, hi in ANGLE_BINS:
        if lo <= angle < hi:
            return f"{lo}-{hi}"
    return "other"


FIELDS = ["dataset", "object", "pair", "split", "angle_deg", "angle_bin", "ok", "refined", "reason",
          "matches", "inliers", "model", "rot_err_deg", "t_err_deg", "pose_err_deg", "reproj_rms_px", "seconds",
          # the estimate itself (rotation vector, unit t) and model scores: inputs for the
          # confidence model and for agreement between methods (scripts/confidence.py)
          "gric_H", "gric_E", "rx", "ry", "rz", "tx", "ty", "tz"]
TEXT_FIELDS = {"dataset", "object", "pair", "split", "angle_bin", "reason", "model"}


def _read_partial(path):
    """Rows already computed by an interrupted run (partial.csv), with their types restored."""
    if not path.exists():
        return []
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k, v in r.items():
            if k in ("ok", "refined"):
                r[k] = v == "True"
            elif k not in TEXT_FIELDS:
                r[k] = float(v) if v not in ("", "nan") else float("nan")
    return rows


def run(args, out):
    """Evaluate every pair. Each result is appended to out/partial.csv as soon as it is computed,
    so an interrupted run (sleep, crash, closed terminal) resumes where it stopped."""
    partial = out / "partial.csv"
    rows = _read_partial(partial)
    done = {r["pair"] for r in rows}
    if done:
        print(f"resuming: {len(done)} pairs already done")
    new_file = not partial.exists()
    header = FIELDS
    if not new_file:   # resume with the columns the file was started with
        with open(partial, newline="") as g:
            header = next(csv.reader(g), FIELDS)
    f = open(partial, "a", newline="")
    writer = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
    if new_file:
        writer.writeheader()
    old_seconds = {}
    if args.seconds_from:
        with open(args.seconds_from, newline="") as g:
            old_seconds = {r["pair"]: float(r["seconds"]) for r in csv.DictReader(g)}
    for name in args.datasets:
        pairs = LOADERS[name].load_pairs(per_bin=PER_BIN[name], seed=SEED)
        for pair in tqdm(pairs, desc=name):
            if pair.name in done:
                continue
            img1, img2, m1, m2 = pair.load()
            try:
                if args.cascade in CONFIDENT:   # confidence-gated cascade (src/pipeline/cascade.py)
                    res = estimate_pose_confident(img1, img2, pair.frame1.K, pair.frame2.K, m1, m2,
                                                  preset=args.cascade, max_side=args.max_side, refine=args.refine)
                elif args.cascade:   # several methods in order (src/pipeline/cascade.py)
                    res = estimate_pose_cascade(img1, img2, pair.frame1.K, pair.frame2.K, m1, m2,
                                                preset=args.cascade, max_side=args.max_side, refine=args.refine)
                elif args.shape:   # pose from the object outline; the matcher only breaks its symmetry
                    res = estimate_pose_shape(img1, img2, pair.frame1.K, pair.frame2.K, m1, m2,
                                              matcher=args.matcher, max_side=args.max_side)
                elif args.cached:   # same matches as before (scripts/matchcache.py), geometry re-run
                    p1, p2, scale, match_s = cached_matches_timed(args.matcher, pair, crop=True,
                                                                  max_side=args.max_side, images=(img1, img2, m1, m2))
                    t0 = time.perf_counter()   # geometry only: match_s already holds the matching time
                    res = pose_from_matches(p1, p2, scale, pair.frame1.K, pair.frame2.K, model=args.model,
                                            refine=args.refine, gric_sigma=args.gric_sigma,
                                            planar_twin=args.planar_twin)
                    if np.isnan(match_s):   # cached before timing was stored: time of the earlier run
                        res.seconds = old_seconds.get(pair.name, np.nan)
                    else:
                        res.seconds = match_s + (time.perf_counter() - t0)
                else:
                    res = estimate_pose(img1, img2, pair.frame1.K, pair.frame2.K,
                                        m1 if args.masks else None, m2 if args.masks else None,
                                        matcher=args.matcher, max_side=args.max_side, model=args.model,
                                        crop=args.crop, refine=args.refine,
                                        min_side=args.min_side, gric_sigma=args.gric_sigma,
                                        planar_twin=args.planar_twin)
            except Exception as e:  # one bad pair must not stop the run; it counts as a failure
                res = PoseResult(False, reason=f"error: {type(e).__name__}: {e}")
            rot = rotation_error_deg(res.R, pair.R_gt) if res.ok else np.inf
            tra = translation_angle_deg(res.t, pair.t_gt) if res.ok else np.inf
            # Pose error = worse of the two; if the true translation is ~0 only rotation counts
            pose = rot if np.isnan(tra) else max(rot, tra)
            row = dict(
                dataset=name, object=object_of(name, pair.sequence), pair=pair.name, split=split_of(pair.name),
                angle_deg=round(pair.angle_deg, 2), angle_bin=bin_of(pair.angle_deg),
                ok=res.ok, refined=res.refined, reason=res.reason, matches=res.n_matches, inliers=res.n_inliers,
                model=res.model, rot_err_deg=rot, t_err_deg=tra, pose_err_deg=pose,
                reproj_rms_px=res.reproj_rms_px, seconds=round(res.seconds, 3),
                gric_H=res.gric_H, gric_E=res.gric_E,
            )
            rvec = cv2.Rodrigues(np.asarray(res.R, float))[0].ravel() if res.ok else [np.nan] * 3
            tvec = np.asarray(res.t, float).ravel() if res.ok else [np.nan] * 3
            row |= dict(zip(["rx", "ry", "rz"], map(float, rvec))) | dict(zip(["tx", "ty", "tz"], map(float, tvec)))
            rows.append(row)
            writer.writerow(row)
            f.flush()
    f.close()
    return rows


def summarise(rows):
    """One summary line for a group of pair rows."""
    pose = np.array([r["pose_err_deg"] for r in rows], float)
    ok = np.array([r["ok"] for r in rows])
    rot = np.array([r["rot_err_deg"] for r in rows if r["ok"]], float)
    tra = np.array([r["t_err_deg"] for r in rows if r["ok"]], float)
    auc = pose_auc(pose)
    return dict(
        pairs=len(rows), failed=f"{100 * (1 - ok.mean()):.0f}%",
        auc5=f"{auc[5]:.1f}", auc10=f"{auc[10]:.1f}", auc20=f"{auc[20]:.1f}",
        med_rot=f"{np.median(rot):.2f}" if len(rot) else "-",
        med_t=f"{np.nanmedian(tra):.2f}" if len(tra) and not np.all(np.isnan(tra)) else "-",
        med_matches=f"{np.median([r['matches'] for r in rows]):.0f}",
        med_reproj=f"{np.nanmedian([r['reproj_rms_px'] for r in rows if r['ok']]):.2f}" if len(rot) else "-",
        sec=f"{np.mean([r['seconds'] for r in rows]):.2f}",
    )


HEADER = ["group", "pairs", "failed", "AUC@5", "AUC@10", "AUC@20",
          "median rot err (deg)", "median t-dir err (deg)", "median matches", "median reproj (px)", "s/pair"]
KEYS = ["pairs", "failed", "auc5", "auc10", "auc20", "med_rot", "med_t", "med_matches", "med_reproj", "sec"]


def table(title, groups):
    lines = [f"### {title}", "", "| " + " | ".join(HEADER) + " |", "|" + "---|" * len(HEADER)]
    for label, rows in groups:
        s = summarise(rows)
        lines.append(f"| {label} | " + " | ".join(str(s[k]) for k in KEYS) + " |")
    return "\n".join(lines) + "\n"


def write_summary(rows, out, config):
    datasets = list(dict.fromkeys(r["dataset"] for r in rows))
    parts = [f"# Results: {out.name}", "", f"Config: `{json.dumps(config)}`", "",
             "AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error "
             "(max of rotation and translation-direction error), in %. Failed pairs count as "
             "infinite error. Medians are over successful pairs only.", ""]
    parts.append(table("Per dataset", [(d, [r for r in rows if r["dataset"] == d]) for d in datasets]))
    parts.append(table("Per dataset, test split only (pairs never used for tuning)",
                       [(d, [r for r in rows if r["dataset"] == d and r["split"] == "test"]) for d in datasets]))
    for d in datasets:
        sub = [r for r in rows if r["dataset"] == d]
        objects = list(dict.fromkeys(r["object"] for r in sub))
        parts.append(table(f"{d}: per object", [(o, [r for r in sub if r["object"] == o]) for o in objects]))
        bins = [f"{lo}-{hi}" for lo, hi in ANGLE_BINS]
        parts.append(table(f"{d}: per viewpoint change (deg)",
                           [(b, [r for r in sub if r["angle_bin"] == b]) for b in bins
                            if any(r["angle_bin"] == b for r in sub)]))
    (out / "summary.md").write_text("\n".join(parts), encoding="utf-8")


def style(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_2, labelsize=9)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def plot_curves(rows, out, title):
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=150, facecolor=SURFACE)
    style(ax)
    xs = np.linspace(0, 20, 401)
    for d in dict.fromkeys(r["dataset"] for r in rows):
        err = np.array([r["pose_err_deg"] for r in rows if r["dataset"] == d], float)
        ys = [100 * np.mean(err <= x) for x in xs]
        ax.plot(xs, ys, color=COLORS[d], linewidth=2, label=d)
        ax.annotate(f"{d}  {ys[-1]:.0f}%", (xs[-1], ys[-1]), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=9, color=INK)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 100)
    ax.set_xlabel("pose error threshold (deg)", color=INK_2, fontsize=9)
    ax.set_ylabel("pairs solved within threshold (%)", color=INK_2, fontsize=9)
    ax.set_title(title, color=INK, fontsize=11, loc="left")
    ax.legend(frameon=False, fontsize=9, loc="lower right", bbox_to_anchor=(0.88, 0.02))
    fig.tight_layout()
    fig.savefig(out / "curves.png", facecolor=SURFACE)
    plt.close(fig)


def plot_objects(rows, out, title):
    groups = list(dict.fromkeys((r["dataset"], r["object"]) for r in rows))
    vals = [100 * np.mean([r["pose_err_deg"] <= 10 for r in rows if (r["dataset"], r["object"]) == g])
            for g in groups]
    fig, ax = plt.subplots(figsize=(7, 0.42 * len(groups) + 1.2), dpi=150, facecolor=SURFACE)
    style(ax)
    ax.grid(True, axis="x", color=GRID, linewidth=0.8)
    ax.grid(False, axis="y")
    y = np.arange(len(groups))[::-1]
    ax.barh(y, vals, height=0.6, color=[COLORS[d] for d, _ in groups], edgecolor=SURFACE, linewidth=2)
    for yi, v in zip(y, vals):
        ax.text(v + 1, yi, f"{v:.0f}%", va="center", fontsize=8, color=INK)
    ax.set_yticks(y, [f"{o}  ({d})" for d, o in groups], fontsize=9, color=INK)
    ax.set_xlim(0, 105)
    ax.set_xlabel("pairs solved within 10 deg (%)", color=INK_2, fontsize=9)
    ax.set_title(title, color=INK, fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(out / "objects.png", facecolor=SURFACE)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="results folder name, e.g. sift_auto")
    ap.add_argument("--matcher", default="sift", choices=MATCHERS)
    ap.add_argument("--crop", action="store_true", help="match on a crop around the object mask")
    ap.add_argument("--cascade", choices=ALL_PRESETS, help="run a cascade preset instead of one matcher")
    ap.add_argument("--shape", action="store_true", help="pose from the object outline (rectangles)")
    ap.add_argument("--model", default="auto", choices=["auto", "H", "E"])
    ap.add_argument("--max-side", type=int, default=800)
    ap.add_argument("--min-side", type=int, default=0, help="enlarge object crops smaller than this (px)")
    ap.add_argument("--gric-sigma", default="fixed", choices=["fixed", "robust"])
    ap.add_argument("--no-masks", dest="masks", action="store_false")
    ap.add_argument("--no-refine", dest="refine", action="store_false", help="skip non-linear pose refinement")
    ap.add_argument("--datasets", nargs="+", default=list(LOADERS))
    ap.add_argument("--cached", action="store_true",
                    help="object-only matcher runs: re-use / store matches in data/cache/matches (implies --crop)")
    ap.add_argument("--seconds-from", help="pairs.csv whose per-pair seconds stand in for matches cached without timing")
    ap.add_argument("--no-planar-twin", dest="planar_twin", action="store_false",
                    help="E path without the planar twin check (src/pipeline/geometry.py planar_twin)")
    args = ap.parse_args()
    keep_awake()   # long runs: don't let the laptop sleep mid-run

    out = ROOT / "results" / args.name
    out.mkdir(parents=True, exist_ok=True)
    config = {k: v for k, v in vars(args).items() if k != "name"} | {"per_bin": PER_BIN, "seed": SEED}

    rows = run(args, out)
    with open(out / "pairs.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    (out / "partial.csv").unlink()   # the run is complete; pairs.csv now holds everything
    write_summary(rows, out, config)
    plot_curves(rows, out, f"Relative pose accuracy: {args.name}")
    plot_objects(rows, out, f"Pairs solved within 10 deg, by object: {args.name}")
    print((out / "summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
