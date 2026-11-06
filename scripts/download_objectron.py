"""Download a fixed set of Objectron test-split videos into data/objectron/<category>/seqNN/."""
import csv
from pathlib import Path

import requests
from tqdm import tqdm

BASE_URL = "https://storage.googleapis.com/objectron"
ROOT = Path(__file__).resolve().parents[1] / "data" / "objectron"

CATEGORIES = ["book", "laptop", "cereal_box"]
PER_CATEGORY = 10


def fetch(url: str, dest: Path) -> None:
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    dest.write_bytes(r.content)


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest_rows = []

    for category in CATEGORIES:
        index = requests.get(f"{BASE_URL}/v1/index/{category}_annotations_test", timeout=60).text.split()
        # The index is in a fixed order, so taking the first N gives the same sequences every run
        chosen = index[:PER_CATEGORY]

        for i, seq_id in enumerate(tqdm(chosen, desc=category), start=1):
            out_dir = ROOT / category / f"seq{i:02d}"
            out_dir.mkdir(parents=True, exist_ok=True)
            if not (out_dir / "video.MOV").exists():
                fetch(f"{BASE_URL}/videos/{seq_id}/video.MOV", out_dir / "video.MOV")
            if not (out_dir / "annotation.pbdata").exists():
                fetch(f"{BASE_URL}/annotations/{seq_id}.pbdata", out_dir / "annotation.pbdata")
            if not (out_dir / "geometry.pbdata").exists():
                fetch(f"{BASE_URL}/videos/{seq_id}/geometry.pbdata", out_dir / "geometry.pbdata")
            manifest_rows.append([category, out_dir.name, seq_id])

    with open(ROOT / "manifest.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "folder", "objectron_id"])
        writer.writerows(manifest_rows)
    print(f"[done] {len(manifest_rows)} sequences, manifest at {ROOT / 'manifest.csv'}")


if __name__ == "__main__":
    main()
