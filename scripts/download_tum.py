"""Download the TUM RGB-D fr3 sequences used for evaluation into data/tum/<short name>/."""
import shutil
import tarfile
import time
from pathlib import Path

import requests
from tqdm import tqdm

BASE_URL = "https://cvg.cit.tum.de/rgbd/dataset/freiburg3/rgbd_dataset_freiburg3_{}.tgz"
ROOT = Path(__file__).resolve().parents[1] / "data" / "tum"

# short folder name -> official TUM sequence name
SEQUENCES = {
    "flat_far": "nostructure_texture_far",
    "flat_near": "nostructure_texture_near_withloop",
    "struct_far": "structure_texture_far",
    "struct_near": "structure_texture_near",
    "checkerboard": "checkerboard_large",
}


def download(url: str, dest: Path, retries: int = 20) -> None:
    """Download with resume: a partial file is continued with an HTTP Range request."""
    total = int(requests.head(url, timeout=60, allow_redirects=True).headers["content-length"])
    for attempt in range(retries):
        done = dest.stat().st_size if dest.exists() else 0
        if done >= total:
            return
        try:
            headers = {"Range": f"bytes={done}-"}
            with requests.get(url, stream=True, timeout=60, headers=headers) as r:
                r.raise_for_status()
                with open(dest, "ab") as f, tqdm(total=total, initial=done, unit="B", unit_scale=True, desc=dest.name) as bar:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        f.write(chunk)
                        bar.update(len(chunk))
        except requests.exceptions.RequestException as e:
            print(f"[retry {attempt + 1}] {dest.name}: {e}")
            time.sleep(5 * (attempt + 1))
    if dest.stat().st_size < total:
        raise RuntimeError(f"could not finish {dest.name} after {retries} retries")


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    for short, official in SEQUENCES.items():
        out_dir = ROOT / short
        if (out_dir / "groundtruth.txt").exists():
            print(f"[skip] {short} already present")
            continue

        archive = ROOT / f"{short}.tgz"
        download(BASE_URL.format(official), archive)

        # Archives contain a single top-level folder named after the official sequence
        with tarfile.open(archive) as tar:
            tar.extractall(ROOT, filter="data")
        shutil.move(str(ROOT / f"rgbd_dataset_freiburg3_{official}"), str(out_dir))
        archive.unlink()

        # Depth is not used: the problem statement takes RGB images only
        shutil.rmtree(out_dir / "depth", ignore_errors=True)
        (out_dir / "depth.txt").unlink(missing_ok=True)
        print(f"[done] {short}")


if __name__ == "__main__":
    main()
