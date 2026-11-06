"""Download a few MVImgNet sequences of small objects (key, watch) without the full zips.

    set MVIMGNET_PASSWORD=<password from the MVImgNet form>
    venv\\Scripts\\python.exe scripts\\download_mvimgnet.py

MVImgNet (Yu et al., CVPR 2023) is distributed as one zip per category on SharePoint
(key: 11 GB, watch: 24 GB). Like download_co3d.py, this reads the zips' central directory
over HTTP range requests and fetches only the chosen sequences' files:
    images/NNN.jpg, images/NNN_bg_removed.png (object cut-out, alpha = mask),
    sparse/0/{cameras,images}.bin (COLMAP camera calibration and poses).

Sequences are chosen in sorted order among those whose COLMAP model registered every frame
(complete ground truth) and that have >= MIN_FRAMES frames; the choice is pinned in
data/mvimgnet/manifest.csv so reruns fetch the same sequences.
"""
import csv
import os
import struct
import sys
import time
from pathlib import Path

from remotezip import RemoteZip

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sharepoint import Share  # noqa: E402
from awake import keep_awake  # noqa: E402

ROOT = Path(__file__).resolve().parents[1] / "data" / "mvimgnet"
LINK = "https://cuhko365.sharepoint.com/:f:/s/GAP_Lab_MVImgNet/End5E56f5x1IgPiUZ8U5n0kBFedIKvizIy1xnW-yKMtr1w?e=1PUl1t"
CATEGORIES = {"key": 219, "watch": 222}      # folder name -> MVImgNet class id
PER_CATEGORY = 10
MIN_FRAMES = 25
RETRIES = 8


def registered_images(images_bin: bytes) -> int:
    """Number of frames in a COLMAP images.bin."""
    return struct.unpack("<Q", images_bin[:8])[0]


def retry(fn, *a):
    for attempt in range(RETRIES):
        try:
            return fn(*a)
        except Exception as e:  # network hiccups: SharePoint resets long sessions
            if attempt == RETRIES - 1:
                raise
            print(f"  retry after {type(e).__name__}")
            time.sleep(3 * (attempt + 1))


def open_zip(share, cid):
    item = next(i for i in share.list("MVImgNet_by_categories") if i["name"] == f"{cid}.zip")
    return RemoteZip(share.download_url(item))


def choose(zc, cid):
    seqs = sorted({n.split("/")[1] for n in zc.names if n.count("/") >= 2 and n.split("/")[1]})
    chosen = []
    for s in seqs:
        jpgs = [n for n in zc.names if n.startswith(f"{cid}/{s}/images/") and n.endswith(".jpg")]
        if len(jpgs) < MIN_FRAMES or f"{cid}/{s}/sparse/0/images.bin" not in zc.names:
            continue
        if registered_images(zc.read(f"{cid}/{s}/sparse/0/images.bin")) == len(jpgs):
            chosen.append(s)
            print(f"  {s}: {len(jpgs)} frames, all registered", flush=True)
        if len(chosen) == PER_CATEGORY:
            break
    return chosen


class Category:
    """One category zip, reopened with a fresh SharePoint session when the connection drops
    (download links carry a temporary token, and long runs hit network outages)."""

    def __init__(self, password, cid):
        self.password, self.cid, self.z = password, cid, None
        self.reopen()

    def reopen(self):
        if self.z is not None:
            try:
                self.z.close()
            except Exception:
                pass
        self.z = retry(open_zip, Share(LINK, self.password), self.cid)
        self.names = self.z.namelist()

    def read(self, name):
        for attempt in range(RETRIES):
            try:
                return self.z.read(name)
            except Exception as e:
                print(f"  {type(e).__name__} on {name}; reconnecting in {30 * (attempt + 1)} s", flush=True)
                time.sleep(30 * (attempt + 1))
                try:
                    self.reopen()
                except Exception as e2:
                    print(f"  reconnect failed: {type(e2).__name__}", flush=True)
        raise SystemExit(f"giving up on {name}; rerun to resume")


def write_manifest(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["category", "folder", "sequence", "class_id"])
        w.writeheader()
        w.writerows(rows)


def main():
    keep_awake()
    password = os.environ.get("MVIMGNET_PASSWORD")
    if not password:
        raise SystemExit("set MVIMGNET_PASSWORD (from the MVImgNet form)")
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest = ROOT / "manifest.csv"
    pinned = {}
    if manifest.exists():
        with open(manifest) as f:
            for row in csv.DictReader(f):
                pinned.setdefault(row["category"], []).append(row["sequence"])

    rows = []
    for cat, cid in CATEGORIES.items():
        print(f"{cat} ({cid}.zip)", flush=True)
        zc = Category(password, cid)
        seqs = pinned.get(cat) or choose(zc, cid)
        rows += [dict(category=cat, folder=f"seq{k:02d}", sequence=s, class_id=cid) for k, s in enumerate(seqs, 1)]
        write_manifest(manifest, rows)   # saved now, so a rerun after a failure fetches the same sequences
        for k, s in enumerate(seqs, 1):
            out = ROOT / cat / f"seq{k:02d}"
            want = [n for n in zc.names if n.startswith(f"{cid}/{s}/") and not n.endswith("/")
                    and ("/images/" in n or n.endswith(("cameras.bin", "images.bin")))]
            todo = [n for n in want if not (out / n.split(f"{s}/", 1)[1]).exists()]
            for n in todo:
                dest = out / n.split(f"{s}/", 1)[1]
                dest.parent.mkdir(parents=True, exist_ok=True)
                tmp = dest.with_suffix(dest.suffix + ".part")
                tmp.write_bytes(zc.read(n))
                tmp.replace(dest)          # only complete files get their final name
            print(f"  seq{k:02d} <- {s}: {len(want)} files ({len(todo)} new)", flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
