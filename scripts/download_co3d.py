"""Download a small CO3Dv2 subset into data/co3d/<category>/seqNN/.

Full categories are 90-140 GB, so instead of downloading whole zips this reads only the
needed files out of the remote zips with HTTP range requests. For each category it keeps
the PER_CATEGORY sequences with the best viewpoint quality score, and from each sequence
only the RGB images, object masks and per-frame cameras (no depth or point clouds).
"""
import csv
import gzip
import json
import struct
import time
import zipfile
import zlib
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from remotezip import RemoteIOError, RemoteZip
from tqdm import tqdm

LINKS_URL = "https://raw.githubusercontent.com/facebookresearch/co3d/main/co3d/links.json"
ROOT = Path(__file__).resolve().parents[1] / "data" / "co3d"

CATEGORIES = ["cellphone", "handbag"]
PER_CATEGORY = 10
MIN_FRAMES = 100  # a few CO3D sequences are only a handful of frames long
WORKERS = 2
RETRIES = 10


def with_retries(fn):
    """The CO3D server occasionally resets connections, so retry any remote read."""
    for attempt in range(RETRIES):
        try:
            return fn()
        except RemoteIOError:
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"giving up after {RETRIES} retries")


def read_jgz(zip_url: str, member: str):
    def read():
        with RemoteZip(zip_url) as z:
            return json.loads(gzip.decompress(z.read(member)))
    return with_retries(read)


def cached_jgz(zip_url: str, category: str, filename: str):
    """Annotation files are ~40 MB, so keep a local copy instead of refetching each run."""
    cache = ROOT / "cache" / f"{category}_{filename.replace('.jgz', '.json')}"
    if cache.exists():
        return json.loads(cache.read_text())
    data = read_jgz(zip_url, f"{category}/{filename}")
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(data))
    return data


def list_members(zip_url: str) -> dict:
    """Map member name -> ZipInfo (holds each file's byte offset and size inside the zip)."""
    def read():
        with RemoteZip(zip_url) as z:
            return {info.filename: info for info in z.infolist()}
    return with_retries(read)


def pick_sequences(seq_annotations: list, frames: list) -> list:
    frame_counts = Counter(f["sequence_name"] for f in frames)
    scored = [
        s for s in seq_annotations
        if s.get("viewpoint_quality_score") is not None and frame_counts[s["sequence_name"]] >= MIN_FRAMES
    ]
    scored.sort(key=lambda s: s["viewpoint_quality_score"], reverse=True)
    return [s["sequence_name"] for s in scored[:PER_CATEGORY]]


def fetch_range(url: str, start: int, end: int) -> bytes:
    """Fetch bytes [start, end] with one Range request, resuming after connection resets."""
    buf = bytearray()
    for attempt in range(RETRIES):
        try:
            headers = {"Range": f"bytes={start + len(buf)}-{end}"}
            with requests.get(url, headers=headers, stream=True, timeout=60) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=1 << 20):
                    buf.extend(chunk)
            if len(buf) == end - start + 1:
                return bytes(buf)
        except requests.exceptions.RequestException:
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"giving up on {url} [{start}-{end}] after {RETRIES} retries")


def extract_files(zip_url: str, jobs: list, infos: dict) -> None:
    """jobs: list of (member path in zip, destination path).

    Files of one sequence are stored next to each other in the zip, so instead of one
    request per file (which the server throttles) this downloads each sequence's whole
    byte span in a single request and unpacks the members from memory.
    """
    by_sequence = {}
    for member, dest in jobs:
        by_sequence.setdefault(member.split("/")[1], []).append((member, dest))

    def work(items):
        start = min(infos[m].header_offset for m, _ in items)
        # Local headers repeat the name and may carry an extra field, so pad the end generously
        end = max(infos[m].header_offset + infos[m].compress_size + 30 + len(m) + 1024 for m, _ in items)
        blob = fetch_range(zip_url, start, end)
        for member, dest in items:
            info = infos[member]
            off = info.header_offset - start
            name_len, extra_len = struct.unpack("<HH", blob[off + 26:off + 30])
            data_start = off + 30 + name_len + extra_len
            raw = blob[data_start:data_start + info.compress_size]
            if info.compress_type == zipfile.ZIP_DEFLATED:
                raw = zlib.decompress(raw, -15)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)

    with ThreadPoolExecutor(WORKERS) as pool:
        list(pool.map(work, by_sequence.values()))


def main() -> None:
    links = requests.get(LINKS_URL, timeout=60).json()["full"]
    manifest_path = ROOT / "manifest.csv"
    ROOT.mkdir(parents=True, exist_ok=True)

    # The selection is fixed by the first run and reused afterwards, so a resumed download
    # can never put one sequence's images next to another sequence's cameras
    pinned = {}
    if manifest_path.exists():
        with open(manifest_path, newline="") as f:
            for row in csv.DictReader(f):
                pinned.setdefault(row["category"], {})[row["co3d_sequence"]] = row["folder"]

    for category in CATEGORIES:
        chunk_urls = links[category]
        meta_url = chunk_urls[0]  # chunk 000 holds only the annotation files

        frames = cached_jgz(meta_url, category, "frame_annotations.jgz")
        if category in pinned:
            folder_of = pinned[category]
        else:
            seq_names = pick_sequences(cached_jgz(meta_url, category, "sequence_annotations.jgz"), frames)
            folder_of = {name: f"seq{i:02d}" for i, name in enumerate(seq_names, start=1)}
            write_manifest(manifest_path, pinned | {category: folder_of})
            pinned[category] = folder_of
        print(f"[{category}] sequences: {folder_of}")

        # Every image and mask we need, keyed by its path inside the zip
        missing = {}
        for name, folder in folder_of.items():
            seq_frames = [f for f in frames if f["sequence_name"] == name]
            out_dir = ROOT / category / folder
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "cameras.json").write_text(json.dumps(seq_frames, indent=1))
            for f in seq_frames:
                for kind in ("image", "mask"):
                    member = f[kind]["path"]
                    dest = out_dir / f"{kind}s" / Path(member).name
                    if not dest.exists():
                        missing[member] = dest

        if not missing:
            print(f"[{category}] already complete")
            continue

        # Scan chunks only until every missing file has been found, so finished chunks are not reopened
        for url in tqdm(chunk_urls[1:], desc=f"{category} chunks"):
            infos = list_members(url)
            jobs = [(m, missing.pop(m)) for m in infos if m in missing]
            if jobs:
                extract_files(url, jobs, infos)
            if not missing:
                break

    print(f"[done] {sum(len(v) for v in pinned.values())} sequences, manifest at {manifest_path}")


def write_manifest(path: Path, selection: dict) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "folder", "co3d_sequence"])
        for category, folder_of in selection.items():
            for name, folder in folder_of.items():
                writer.writerow([category, folder, name])


if __name__ == "__main__":
    main()
