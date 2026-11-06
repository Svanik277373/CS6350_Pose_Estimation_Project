# Cascade design: chosen on the tuning split, scored on the test split

268056 designs searched on 339 tuning pairs; scored on 751 test pairs. AUC@10 in %, failures count as infinite error.

| design (budget) | tune mean AUC@10 | test tum | test objectron | test co3d | test mvimgnet | test mean | test s/pair |
|---|---|---|---|---|---|---|---|
| xfeat_lg(>=30) -> sift(>=15) -> shape -> best (<= 0.5 s) | 49.3 | 67.8 | 60.9 | 35.5 | 28.3 | 48.1 | 1.56 |
| xfeat_lg(>=120) -> shape -> xfeat(>=80) -> aliked_lg(>=30) -> best (<= 1 s) | 52.3 | 68.7 | 62.5 | 39.8 | 29.2 | 50.1 | 2.00 |
| xfeat_lg(>=200) -> shape -> sift(>=50) -> loftr(>=120) -> best (<= 2 s) | 52.7 | 68.1 | 63.0 | 38.6 | 30.2 | 50.0 | 2.90 |
| disk_lg(>=200) -> shape -> xfeat_lg(>=200) -> loftr(>=120) -> best (no limit) | 54.0 | 69.6 | 63.3 | 41.1 | 30.9 | 51.2 | 5.83 |

Single methods on the same test pairs:

| method | test tum | test objectron | test co3d | test mvimgnet | test mean | test s/pair |
|---|---|---|---|---|---|---|
| sift | 65.8 | 50.7 | 18.1 | 8.5 | 35.8 | 0.25 |
| xfeat | 54.3 | 57.7 | 22.3 | 17.8 | 38.0 | 0.30 |
| xfeat_lg | 67.2 | 58.2 | 32.0 | 28.3 | 46.4 | 1.49 |
| aliked_lg | 64.7 | 57.8 | 32.1 | 33.5 | 47.0 | 2.36 |
| disk_lg | 68.9 | 59.5 | 28.1 | 21.0 | 44.3 | 4.29 |
| loftr | 67.1 | 65.2 | 33.1 | 24.4 | 47.5 | 5.25 |
| shape | 0.0 | 14.9 | 8.6 | 0.0 | 5.9 | 0.53 |

Per object, test split (AUC@10):

| design | flat_far | flat_near | struct_far | struct_near | checkerboard | book | laptop | cereal_box | cellphone | handbag | key | watch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cascade <= 0.5 s | 41.3 | 80.6 | 81.3 | 64.5 | 58.8 | 63.0 | 34.7 | 86.0 | 16.4 | 54.9 | 16.6 | 40.4 |
| cascade <= 1 s | 44.1 | 77.6 | 81.3 | 64.5 | 65.0 | 62.3 | 40.2 | 86.0 | 22.7 | 57.5 | 17.9 | 40.9 |
| cascade <= 2 s | 41.3 | 80.6 | 81.3 | 64.5 | 60.1 | 61.8 | 42.0 | 86.0 | 20.9 | 56.8 | 16.6 | 44.3 |
| cascade no limit | 49.8 | 79.4 | 82.1 | 58.7 | 70.0 | 62.3 | 43.9 | 84.7 | 21.3 | 61.3 | 16.7 | 45.6 |
| aliked_lg alone | 55.5 | 60.7 | 82.0 | 60.6 | 61.9 | 60.4 | 32.4 | 81.8 | 8.0 | 56.5 | 21.8 | 45.6 |
| loftr alone | 46.6 | 56.5 | 82.3 | 67.9 | 73.0 | 69.5 | 40.0 | 86.8 | 10.3 | 56.4 | 10.9 | 38.4 |

Which stage answered (test split, cascade <= 1 s):

- xfeat_lg: 526 pairs (70%)
- shape: 92 pairs (12%)
- best-so-far: 67 pairs (9%)
- aliked_lg: 44 pairs (6%)
- fail: 12 pairs (2%)
- xfeat: 10 pairs (1%)
