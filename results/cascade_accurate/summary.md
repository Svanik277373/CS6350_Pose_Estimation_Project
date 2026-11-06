# Results: cascade_accurate

Config: `{"matcher": "sift", "crop": false, "cascade": "accurate", "shape": false, "model": "auto", "max_side": 800, "masks": true, "datasets": ["tum", "objectron", "co3d"], "per_bin": {"tum": 20, "objectron": 3, "co3d": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 0% | 53.6 | 71.1 | 82.9 | 0.64 | 1.82 | 410 | 0.33 | 4.51 |
| objectron | 270 | 4% | 46.7 | 61.1 | 70.6 | 1.01 | 1.80 | 374 | 0.65 | 4.81 |
| co3d | 300 | 7% | 24.0 | 37.1 | 50.4 | 2.93 | 5.62 | 154 | 0.59 | 4.65 |

### Per dataset, test split only (pairs never used for tuning)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 142 | 0% | 51.8 | 69.2 | 81.2 | 0.65 | 2.01 | 427 | 0.35 | 5.00 |
| objectron | 189 | 5% | 43.7 | 57.8 | 67.0 | 1.11 | 1.86 | 362 | 0.64 | 4.96 |
| co3d | 210 | 8% | 23.4 | 36.9 | 50.1 | 2.85 | 5.60 | 156 | 0.58 | 5.01 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 0% | 39.4 | 49.7 | 57.7 | 0.93 | 2.54 | 398 | 0.31 | 5.96 |
| flat_near | 60 | 0% | 64.8 | 81.7 | 90.8 | 0.66 | 1.31 | 407 | 0.27 | 3.59 |
| struct_far | 40 | 0% | 68.4 | 82.8 | 91.5 | 0.44 | 1.20 | 415 | 0.24 | 2.48 |
| struct_near | 60 | 0% | 46.3 | 66.6 | 81.7 | 0.69 | 2.20 | 322 | 0.40 | 4.72 |
| checkerboard | 40 | 0% | 44.4 | 64.3 | 79.5 | 0.77 | 2.27 | 480 | 0.51 | 6.89 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 47.4 | 65.4 | 78.2 | 0.62 | 2.21 | 387 | 0.30 | 4.14 |
| 15-30 | 80 | 0% | 57.7 | 75.6 | 86.9 | 0.59 | 1.85 | 445 | 0.33 | 4.52 |
| 30-60 | 40 | 0% | 63.0 | 78.6 | 88.1 | 0.77 | 1.35 | 332 | 0.37 | 5.40 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 0% | 41.2 | 58.3 | 70.1 | 1.24 | 2.25 | 344 | 0.76 | 4.30 |
| laptop | 90 | 12% | 34.9 | 47.8 | 56.9 | 1.73 | 2.64 | 258 | 0.71 | 6.96 |
| cereal_box | 90 | 0% | 65.0 | 78.4 | 85.8 | 0.72 | 1.18 | 478 | 0.62 | 3.18 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 3% | 46.5 | 63.6 | 75.5 | 0.62 | 2.07 | 428 | 0.56 | 4.38 |
| 15-30 | 90 | 2% | 51.9 | 66.4 | 75.9 | 1.04 | 1.73 | 380 | 0.63 | 4.72 |
| 30-60 | 90 | 7% | 42.7 | 54.3 | 61.4 | 1.72 | 1.79 | 321 | 0.91 | 5.34 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 9% | 7.2 | 19.2 | 34.4 | 4.96 | 10.92 | 93 | 1.07 | 3.50 |
| handbag | 150 | 6% | 41.1 | 55.3 | 66.7 | 1.19 | 2.09 | 306 | 0.54 | 5.80 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 24.2 | 37.3 | 51.9 | 1.66 | 6.70 | 239 | 0.51 | 4.08 |
| 15-30 | 100 | 1% | 29.7 | 42.7 | 56.3 | 2.85 | 4.21 | 158 | 0.62 | 4.64 |
| 30-60 | 100 | 21% | 19.1 | 32.3 | 43.9 | 5.07 | 4.78 | 90 | 0.75 | 5.23 |
