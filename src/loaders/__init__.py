"""Dataset loaders: every dataset is turned into Pair objects in the OpenCV convention."""
from . import co3d, mvimgnet, objectron, tum
from .common import Frame, Pair

LOADERS = {"tum": tum, "objectron": objectron, "co3d": co3d, "mvimgnet": mvimgnet}

# Tuning / test split. Every threshold and design choice is made on "tune" pairs only;
# reported numbers come from "test" pairs.
#   Objectron, CO3D, MVImgNet: whole sequences held out (seq01-03 of each object tune, seq04-10 test).
#   TUM has one sequence per scene, so it is split in time: first 30% of each video tunes.
TUNE_SEQUENCES = {"seq01", "seq02", "seq03"}
TUNE_FRACTION = 0.3
_tum_lengths = {}


def split_of(pair_name: str) -> str:
    """'tune' or 'test' for a pair name such as co3d/cellphone/seq04/12-40 or tum/flat_far/347-420."""
    parts = pair_name.split("/")
    if parts[0] == "tum":
        seq = parts[1]
        if seq not in _tum_lengths:
            _tum_lengths[seq] = len(tum.load_frames(seq))
        first = int(parts[-1].split("-")[0])
        return "tune" if first < TUNE_FRACTION * _tum_lengths[seq] else "test"
    return "tune" if parts[2] in TUNE_SEQUENCES else "test"
