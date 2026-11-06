# Results: cascade_fast

Config: `{"matcher": "sift", "crop": false, "cascade": "fast", "shape": false, "model": "auto", "max_side": 800, "masks": true, "datasets": ["tum", "objectron", "co3d"], "per_bin": {"tum": 20, "objectron": 3, "co3d": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 0% | 46.8 | 64.9 | 77.7 | 0.78 | 2.10 | 440 | 0.46 | 0.83 |
| objectron | 270 | 2% | 41.9 | 57.9 | 69.4 | 1.39 | 2.21 | 380 | 0.74 | 1.16 |
| co3d | 300 | 2% | 16.4 | 32.0 | 48.8 | 3.75 | 6.74 | 214 | 0.65 | 1.04 |

### Per dataset, test split only (pairs never used for tuning)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 142 | 0% | 43.9 | 62.1 | 75.4 | 0.86 | 2.31 | 468 | 0.49 | 0.94 |
| objectron | 189 | 3% | 39.7 | 54.5 | 65.6 | 1.47 | 2.31 | 375 | 0.82 | 1.26 |
| co3d | 210 | 2% | 16.9 | 32.9 | 49.8 | 3.70 | 6.36 | 226 | 0.65 | 1.11 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 0% | 30.8 | 46.0 | 55.5 | 1.53 | 4.67 | 355 | 0.53 | 1.50 |
| flat_near | 60 | 0% | 69.8 | 83.3 | 90.0 | 0.66 | 1.06 | 351 | 0.25 | 0.79 |
| struct_far | 40 | 0% | 45.1 | 68.6 | 83.0 | 1.02 | 2.23 | 447 | 0.41 | 0.24 |
| struct_near | 60 | 0% | 42.9 | 64.6 | 80.9 | 0.77 | 2.46 | 371 | 0.50 | 0.74 |
| checkerboard | 40 | 0% | 32.3 | 47.7 | 62.9 | 0.76 | 4.23 | 630 | 0.56 | 1.28 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 35.1 | 53.2 | 68.0 | 0.86 | 3.29 | 441 | 0.46 | 0.82 |
| 15-30 | 80 | 0% | 55.3 | 73.5 | 85.2 | 0.68 | 1.81 | 458 | 0.49 | 0.79 |
| 30-60 | 40 | 0% | 61.7 | 79.1 | 88.3 | 0.77 | 1.21 | 320 | 0.41 | 0.94 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 0% | 40.3 | 57.8 | 71.8 | 1.53 | 2.65 | 344 | 0.83 | 1.15 |
| laptop | 90 | 6% | 27.4 | 44.0 | 56.2 | 2.11 | 4.30 | 254 | 0.98 | 1.77 |
| cereal_box | 90 | 0% | 59.1 | 72.8 | 81.0 | 0.88 | 1.35 | 552 | 0.51 | 0.56 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 1% | 42.5 | 60.6 | 74.4 | 0.79 | 2.43 | 491 | 0.49 | 0.84 |
| 15-30 | 90 | 1% | 47.1 | 63.3 | 74.3 | 1.35 | 2.01 | 342 | 0.76 | 1.12 |
| 30-60 | 90 | 3% | 37.2 | 50.9 | 60.4 | 2.11 | 2.61 | 333 | 1.05 | 1.52 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 2% | 7.0 | 20.1 | 37.6 | 4.90 | 10.53 | 126 | 0.71 | 1.00 |
| handbag | 150 | 2% | 26.2 | 44.2 | 60.2 | 2.71 | 3.68 | 378 | 0.62 | 1.09 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 18.4 | 32.4 | 49.6 | 2.44 | 9.11 | 296 | 0.56 | 0.81 |
| 15-30 | 100 | 0% | 19.1 | 37.0 | 56.0 | 3.55 | 5.59 | 207 | 0.66 | 0.90 |
| 30-60 | 100 | 6% | 12.8 | 27.5 | 41.7 | 7.12 | 7.72 | 136 | 0.75 | 1.41 |
