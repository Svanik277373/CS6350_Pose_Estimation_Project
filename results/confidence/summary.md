# Confidence-gated cascade: chosen on the tuning split, scored on the test split

4368 designs searched on 339 tuning pairs; scored on 751 test pairs.
Confidence = P(pose error < 10 deg) from a gradient-boosted classifier (out-of-fold on tune). AUC@10 in %, failures count as infinite error.

| design (budget) | tune mean | test tum | test objectron | test co3d | test mvimgnet | test mean | test s/pair |
|---|---|---|---|---|---|---|---|
| xfeat_lg -> aliked_lg -> shape (conf >= 0.35) -> most confident (<= 1 s) | 51.1 | 68.3 | 63.5 | 39.1 | 30.6 | 50.4 | 2.19 |
| shape -> xfeat_lg -> disk_lg (conf >= 0.9) -> most confident (<= 3 s) | 51.8 | 69.4 | 63.5 | 39.9 | 27.2 | 50.0 | 4.06 |
| xfeat_lg -> sift -> shape (conf >= 0.45) -> mast3r (<= 8 s) | 62.4 | 70.5 | 77.2 | 57.4 | 51.1 | 64.0 | 7.82 |
| shape (conf >= 0.95) -> mast3r (no limit) | 69.6 | 76.8 | 81.5 | 67.8 | 65.9 | 73.0 | 22.61 |

Single methods on the same test pairs:

| method | tum | objectron | co3d | mvimgnet | mean | s/pair |
|---|---|---|---|---|---|---|
| sift | 65.8 | 50.7 | 18.1 | 8.5 | 35.8 | 0.25 |
| xfeat_lg | 67.2 | 58.2 | 32.0 | 28.3 | 46.4 | 1.49 |
| aliked_lg | 64.7 | 57.8 | 32.1 | 33.5 | 47.0 | 2.36 |
| disk_lg | 68.9 | 59.5 | 28.1 | 21.0 | 44.3 | 4.29 |
| loftr | 67.1 | 65.2 | 33.1 | 24.4 | 47.5 | 5.25 |
| shape | 0.0 | 14.9 | 8.6 | 0.0 | 5.9 | 0.53 |
| mast3r | 76.8 | 81.5 | 67.8 | 65.9 | 73.0 | 22.08 |

Per object, test split (AUC@10):

| design | flat_far | flat_near | struct_far | struct_near | checkerboard | book | laptop | cereal_box | cellphone | handbag | key | watch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| <= 1 s | 41.3 | 77.6 | 81.3 | 64.5 | 64.3 | 63.9 | 41.6 | 86.0 | 21.7 | 57.0 | 19.1 | 42.5 |
| <= 3 s | 41.7 | 77.7 | 81.3 | 63.5 | 70.7 | 62.7 | 42.4 | 86.4 | 24.0 | 56.3 | 16.5 | 38.3 |
| <= 8 s | 66.5 | 80.6 | 81.3 | 61.8 | 62.8 | 80.1 | 65.0 | 87.5 | 43.7 | 71.5 | 45.0 | 57.6 |
| no limit | 76.1 | 88.7 | 84.5 | 64.8 | 72.3 | 83.3 | 76.7 | 85.8 | 56.9 | 79.2 | 57.0 | 75.1 |
| aliked_lg alone | 55.5 | 60.7 | 82.0 | 60.6 | 61.9 | 60.4 | 32.4 | 81.8 | 8.0 | 56.5 | 21.8 | 45.6 |
| mast3r alone | 76.1 | 88.7 | 84.5 | 64.8 | 72.3 | 83.3 | 76.7 | 85.8 | 56.9 | 79.2 | 57.0 | 75.1 |

Accepted-but-wrong poses (> 20 deg off), test split:

- <= 1 s: 145 of 751 (19%); answered by xfeat_lg 582, aliked_lg 71, shape 69, fail 29
- <= 3 s: 158 of 751 (21%); answered by xfeat_lg 504, disk_lg 137, shape 80, fail 30
- <= 8 s: 55 of 751 (7%); answered by xfeat_lg 486, mast3r 195, shape 54, sift 13, fail 3
- no limit: 18 of 751 (2%); answered by mast3r 748, fail 3
