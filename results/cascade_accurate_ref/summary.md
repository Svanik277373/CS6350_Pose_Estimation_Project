# Results: cascade_accurate_ref

Config: `{"matcher": "sift", "crop": false, "cascade": "accurate", "shape": false, "model": "auto", "max_side": 800, "min_side": 0, "gric_sigma": "fixed", "masks": true, "refine": true, "datasets": ["tum", "objectron", "co3d", "mvimgnet"], "cached": false, "seconds_from": null, "planar_twin": true, "per_bin": {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 0% | 53.0 | 70.1 | 81.8 | 0.68 | 1.66 | 912 | 0.50 | 1.07 |
| objectron | 270 | 1% | 51.8 | 65.7 | 74.9 | 0.89 | 1.55 | 588 | 1.06 | 1.47 |
| co3d | 300 | 3% | 22.6 | 36.9 | 51.5 | 3.13 | 6.00 | 233 | 0.68 | 1.74 |
| mvimgnet | 300 | 6% | 17.8 | 30.4 | 42.2 | 4.70 | 7.86 | 336 | 0.59 | 4.18 |

### Per dataset, test split only (pairs never used for tuning)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 142 | 0% | 50.3 | 68.1 | 80.7 | 0.71 | 1.84 | 900 | 0.50 | 1.10 |
| objectron | 189 | 2% | 49.0 | 63.0 | 72.8 | 0.94 | 1.76 | 694 | 1.03 | 1.61 |
| co3d | 210 | 3% | 24.2 | 38.6 | 53.1 | 2.94 | 5.68 | 242 | 0.68 | 1.87 |
| mvimgnet | 210 | 5% | 17.2 | 30.2 | 43.1 | 4.87 | 7.76 | 364 | 0.59 | 3.90 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 0% | 32.3 | 46.7 | 57.8 | 1.18 | 3.73 | 796 | 0.53 | 2.27 |
| flat_near | 60 | 0% | 66.7 | 83.0 | 91.5 | 0.75 | 1.15 | 1090 | 0.46 | 1.12 |
| struct_far | 40 | 0% | 67.3 | 82.2 | 91.2 | 0.40 | 1.19 | 1062 | 0.48 | 1.00 |
| struct_near | 60 | 0% | 48.7 | 69.5 | 83.9 | 0.71 | 2.03 | 828 | 0.51 | 0.83 |
| checkerboard | 40 | 0% | 39.0 | 54.7 | 69.4 | 0.75 | 2.54 | 686 | 0.54 | 0.86 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 41.9 | 60.5 | 74.6 | 0.70 | 2.50 | 991 | 0.50 | 1.23 |
| 15-30 | 80 | 0% | 61.3 | 77.7 | 87.8 | 0.56 | 1.59 | 904 | 0.49 | 0.90 |
| 30-60 | 40 | 0% | 66.2 | 80.8 | 89.1 | 0.86 | 1.17 | 733 | 0.50 | 1.01 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 0% | 47.7 | 62.1 | 72.9 | 1.19 | 1.69 | 588 | 1.16 | 0.88 |
| laptop | 90 | 4% | 35.4 | 50.0 | 60.6 | 1.52 | 3.01 | 334 | 1.03 | 2.76 |
| cereal_box | 90 | 0% | 73.3 | 85.5 | 92.2 | 0.57 | 1.06 | 748 | 0.98 | 0.78 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 0% | 52.7 | 68.9 | 81.0 | 0.51 | 1.87 | 680 | 0.98 | 1.27 |
| 15-30 | 90 | 0% | 56.4 | 70.2 | 78.7 | 1.06 | 1.43 | 598 | 1.04 | 1.24 |
| 30-60 | 90 | 4% | 47.2 | 58.7 | 66.0 | 1.36 | 1.36 | 479 | 1.13 | 1.91 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 3% | 6.2 | 19.0 | 36.1 | 4.96 | 11.46 | 132 | 1.07 | 1.11 |
| handbag | 150 | 3% | 39.2 | 55.0 | 67.1 | 1.54 | 2.28 | 460 | 0.63 | 2.37 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 24.8 | 39.5 | 55.3 | 1.89 | 6.20 | 394 | 0.62 | 1.14 |
| 15-30 | 100 | 1% | 27.3 | 42.5 | 58.2 | 3.09 | 4.01 | 266 | 0.70 | 1.26 |
| 30-60 | 100 | 9% | 16.6 | 29.5 | 41.8 | 7.11 | 6.52 | 118 | 0.69 | 2.82 |

### mvimgnet: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| key | 150 | 12% | 8.1 | 16.9 | 27.8 | 10.44 | 17.61 | 268 | 0.56 | 3.73 |
| watch | 150 | 1% | 27.8 | 44.2 | 56.9 | 3.02 | 3.58 | 419 | 0.62 | 4.63 |

### mvimgnet: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 2% | 21.7 | 38.8 | 53.8 | 2.50 | 5.64 | 428 | 0.56 | 1.93 |
| 15-30 | 100 | 2% | 25.8 | 40.7 | 54.0 | 4.06 | 4.30 | 352 | 0.59 | 4.12 |
| 30-60 | 100 | 15% | 6.8 | 12.6 | 19.8 | 29.39 | 36.71 | 132 | 0.63 | 6.49 |
