# Results: cascade_fast_ref

Config: `{"matcher": "sift", "crop": false, "cascade": "fast", "shape": false, "model": "auto", "max_side": 800, "min_side": 0, "gric_sigma": "fixed", "masks": true, "refine": true, "datasets": ["tum", "objectron", "co3d", "mvimgnet"], "cached": false, "seconds_from": null, "planar_twin": true, "per_bin": {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 0% | 53.0 | 69.9 | 81.3 | 0.68 | 1.66 | 913 | 0.50 | 1.00 |
| objectron | 270 | 3% | 48.9 | 62.5 | 72.4 | 1.04 | 1.60 | 584 | 1.03 | 0.75 |
| co3d | 300 | 5% | 21.3 | 33.9 | 47.0 | 3.66 | 6.49 | 196 | 0.59 | 0.51 |
| mvimgnet | 300 | 9% | 15.4 | 27.2 | 38.3 | 5.16 | 9.35 | 282 | 0.59 | 0.58 |

### Per dataset, test split only (pairs never used for tuning)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 142 | 0% | 50.3 | 67.8 | 79.9 | 0.71 | 1.84 | 904 | 0.50 | 0.98 |
| objectron | 189 | 4% | 47.2 | 60.9 | 71.1 | 1.02 | 1.79 | 694 | 1.03 | 0.81 |
| co3d | 210 | 5% | 22.5 | 35.5 | 47.9 | 3.59 | 6.37 | 204 | 0.59 | 0.55 |
| mvimgnet | 210 | 8% | 16.1 | 28.3 | 40.3 | 4.94 | 8.21 | 305 | 0.59 | 0.63 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 0% | 32.3 | 46.7 | 55.9 | 1.18 | 3.73 | 796 | 0.53 | 1.11 |
| flat_near | 60 | 0% | 66.7 | 83.0 | 91.5 | 0.75 | 1.15 | 1090 | 0.46 | 1.11 |
| struct_far | 40 | 0% | 67.3 | 82.2 | 91.2 | 0.40 | 1.19 | 1062 | 0.48 | 1.07 |
| struct_near | 60 | 0% | 48.7 | 69.5 | 83.9 | 0.71 | 2.03 | 828 | 0.51 | 0.91 |
| checkerboard | 40 | 0% | 39.0 | 53.8 | 67.0 | 0.75 | 2.54 | 696 | 0.55 | 0.87 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 41.9 | 60.2 | 73.5 | 0.70 | 2.50 | 1002 | 0.50 | 1.06 |
| 15-30 | 80 | 0% | 61.3 | 77.7 | 87.8 | 0.56 | 1.59 | 904 | 0.49 | 0.94 |
| 30-60 | 40 | 0% | 66.2 | 80.8 | 89.1 | 0.88 | 1.17 | 733 | 0.50 | 1.00 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 0% | 48.5 | 63.8 | 75.0 | 1.16 | 1.69 | 588 | 1.11 | 0.81 |
| laptop | 90 | 8% | 25.9 | 39.0 | 50.6 | 2.53 | 5.39 | 324 | 1.01 | 0.73 |
| cereal_box | 90 | 1% | 73.3 | 85.5 | 92.2 | 0.57 | 1.06 | 748 | 0.98 | 0.70 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 1% | 48.0 | 63.2 | 74.4 | 0.60 | 1.97 | 674 | 0.98 | 0.68 |
| 15-30 | 90 | 1% | 53.5 | 67.6 | 77.0 | 1.17 | 1.46 | 598 | 1.02 | 0.73 |
| 30-60 | 90 | 7% | 46.1 | 57.7 | 66.5 | 1.39 | 1.25 | 479 | 1.09 | 0.83 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 4% | 4.5 | 14.7 | 29.1 | 5.77 | 16.44 | 106 | 0.56 | 0.39 |
| handbag | 150 | 7% | 38.5 | 53.5 | 65.3 | 1.43 | 2.28 | 456 | 0.63 | 0.63 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 23.1 | 36.4 | 50.7 | 2.61 | 6.69 | 332 | 0.55 | 0.44 |
| 15-30 | 100 | 2% | 25.4 | 38.2 | 50.9 | 3.79 | 4.64 | 222 | 0.60 | 0.48 |
| 30-60 | 100 | 14% | 16.4 | 28.1 | 40.4 | 7.12 | 7.55 | 97 | 0.65 | 0.62 |

### mvimgnet: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| key | 150 | 12% | 6.5 | 14.6 | 25.3 | 12.10 | 19.13 | 206 | 0.56 | 0.48 |
| watch | 150 | 6% | 24.7 | 40.1 | 51.7 | 3.40 | 3.81 | 344 | 0.62 | 0.68 |

### mvimgnet: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 2% | 19.6 | 33.9 | 47.2 | 2.88 | 7.39 | 394 | 0.57 | 0.52 |
| 15-30 | 100 | 2% | 20.8 | 36.4 | 50.5 | 4.88 | 5.72 | 298 | 0.60 | 0.52 |
| 30-60 | 100 | 23% | 6.9 | 12.2 | 18.3 | 29.36 | 26.80 | 110 | 0.63 | 0.72 |
