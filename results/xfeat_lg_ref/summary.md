# Results: xfeat_lg_ref

Config: `{"matcher": "xfeat_lg", "crop": true, "cascade": null, "shape": false, "model": "auto", "max_side": 800, "min_side": 0, "gric_sigma": "fixed", "masks": true, "refine": true, "datasets": ["tum", "objectron", "co3d", "mvimgnet"], "cached": true, "seconds_from": "results/_pretwin/xfeat_lg_ref/pairs.csv", "planar_twin": true, "per_bin": {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 1% | 52.3 | 69.1 | 80.4 | 0.68 | 1.67 | 913 | 0.50 | 0.92 |
| objectron | 270 | 7% | 47.3 | 60.7 | 70.2 | 1.02 | 1.58 | 584 | 1.03 | 0.48 |
| co3d | 300 | 16% | 20.3 | 30.3 | 41.0 | 3.53 | 7.35 | 192 | 0.58 | 2.66 |
| mvimgnet | 300 | 10% | 15.4 | 27.2 | 38.3 | 5.10 | 9.18 | 282 | 0.59 | 0.47 |

### Per dataset, test split only (pairs never used for tuning)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 142 | 1% | 49.7 | 67.2 | 79.2 | 0.71 | 1.84 | 904 | 0.50 | 0.92 |
| objectron | 189 | 9% | 44.9 | 58.2 | 67.9 | 1.02 | 1.79 | 694 | 1.03 | 0.50 |
| co3d | 210 | 13% | 21.5 | 32.0 | 42.7 | 3.53 | 7.35 | 204 | 0.59 | 3.69 |
| mvimgnet | 210 | 8% | 16.1 | 28.3 | 40.3 | 4.94 | 8.21 | 305 | 0.59 | 0.56 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 10% | 32.3 | 46.7 | 55.9 | 1.04 | 3.44 | 796 | 0.53 | 0.99 |
| flat_near | 60 | 2% | 64.1 | 80.1 | 88.4 | 0.75 | 1.17 | 1090 | 0.46 | 1.16 |
| struct_far | 40 | 0% | 67.3 | 82.2 | 91.2 | 0.40 | 1.19 | 1062 | 0.48 | 1.04 |
| struct_near | 60 | 0% | 48.7 | 69.5 | 83.9 | 0.71 | 2.03 | 828 | 0.51 | 0.76 |
| checkerboard | 40 | 0% | 39.0 | 53.8 | 67.0 | 0.75 | 2.54 | 696 | 0.55 | 0.66 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 2% | 41.9 | 60.2 | 73.5 | 0.69 | 2.46 | 1002 | 0.50 | 1.00 |
| 15-30 | 80 | 0% | 61.3 | 77.7 | 87.8 | 0.56 | 1.59 | 904 | 0.49 | 0.86 |
| 30-60 | 40 | 3% | 62.3 | 76.3 | 84.4 | 0.88 | 1.18 | 733 | 0.50 | 0.84 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 9% | 48.5 | 63.4 | 73.8 | 1.02 | 1.48 | 588 | 1.08 | 0.48 |
| laptop | 90 | 12% | 21.0 | 33.8 | 45.2 | 2.69 | 6.79 | 324 | 1.02 | 0.44 |
| cereal_box | 90 | 1% | 73.3 | 85.5 | 92.2 | 0.57 | 1.06 | 748 | 0.98 | 0.53 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 1% | 47.0 | 62.2 | 73.3 | 0.63 | 2.04 | 674 | 0.98 | 0.50 |
| 15-30 | 90 | 4% | 51.6 | 65.6 | 74.7 | 1.18 | 1.48 | 598 | 1.02 | 0.48 |
| 30-60 | 90 | 17% | 44.1 | 55.2 | 63.2 | 1.24 | 1.16 | 479 | 1.08 | 0.46 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 25% | 2.5 | 7.6 | 17.4 | 8.31 | 19.84 | 82 | 0.54 | 0.20 |
| handbag | 150 | 7% | 38.5 | 53.4 | 64.9 | 1.41 | 2.29 | 456 | 0.63 | 5.12 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 23.1 | 35.9 | 50.0 | 2.74 | 7.01 | 332 | 0.55 | 0.34 |
| 15-30 | 100 | 8% | 24.7 | 36.1 | 46.8 | 4.50 | 4.64 | 222 | 0.58 | 0.33 |
| 30-60 | 100 | 40% | 14.1 | 19.9 | 27.2 | 9.33 | 9.24 | 52 | 0.60 | 7.32 |

### mvimgnet: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| key | 150 | 13% | 6.5 | 14.6 | 25.3 | 12.02 | 18.98 | 206 | 0.56 | 0.26 |
| watch | 150 | 7% | 24.7 | 40.1 | 51.6 | 3.40 | 3.78 | 344 | 0.62 | 0.68 |

### mvimgnet: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 3% | 19.6 | 33.9 | 47.1 | 2.87 | 7.11 | 394 | 0.57 | 0.47 |
| 15-30 | 100 | 2% | 20.8 | 36.4 | 50.5 | 4.88 | 5.72 | 298 | 0.60 | 0.46 |
| 30-60 | 100 | 24% | 6.9 | 12.2 | 18.3 | 28.86 | 26.22 | 110 | 0.62 | 0.47 |
