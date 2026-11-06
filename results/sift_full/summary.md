# Results: sift_full

Config: `{"matcher": "sift", "crop": false, "cascade": null, "shape": false, "model": "auto", "max_side": 800, "min_side": 0, "gric_sigma": "fixed", "masks": false, "refine": true, "datasets": ["tum", "objectron", "co3d", "mvimgnet"], "cached": false, "seconds_from": null, "planar_twin": true, "per_bin": {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 3% | 52.1 | 67.3 | 78.0 | 0.65 | 1.59 | 218 | 0.27 | 0.87 |
| objectron | 270 | 13% | 50.1 | 62.4 | 71.0 | 0.65 | 1.27 | 260 | 0.58 | 1.06 |
| co3d | 300 | 28% | 37.4 | 46.6 | 53.3 | 0.71 | 1.54 | 97 | 0.46 | 0.76 |
| mvimgnet | 300 | 22% | 44.6 | 51.4 | 56.6 | 0.48 | 1.00 | 114 | 0.67 | 1.00 |

### Per dataset, test split only (pairs never used for tuning)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 142 | 4% | 50.3 | 65.8 | 77.0 | 0.66 | 1.61 | 178 | 0.27 | 0.82 |
| objectron | 189 | 12% | 51.2 | 63.4 | 71.9 | 0.64 | 1.22 | 229 | 0.56 | 1.00 |
| co3d | 210 | 26% | 36.5 | 45.8 | 53.0 | 0.72 | 1.72 | 92 | 0.44 | 0.75 |
| mvimgnet | 210 | 25% | 38.8 | 44.8 | 49.6 | 0.67 | 1.12 | 101 | 0.66 | 1.06 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 10% | 45.6 | 57.7 | 63.8 | 0.64 | 2.12 | 98 | 0.27 | 1.64 |
| flat_near | 60 | 0% | 74.4 | 87.0 | 93.5 | 0.59 | 1.08 | 246 | 0.24 | 1.30 |
| struct_far | 40 | 0% | 65.4 | 80.7 | 89.1 | 0.41 | 1.39 | 447 | 0.28 | 0.34 |
| struct_near | 60 | 2% | 41.7 | 61.6 | 78.4 | 0.77 | 2.40 | 180 | 0.33 | 0.62 |
| checkerboard | 40 | 7% | 28.4 | 41.1 | 52.5 | 1.48 | 5.05 | 131 | 0.30 | 0.74 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 2% | 46.7 | 63.2 | 75.2 | 0.63 | 2.08 | 263 | 0.27 | 0.97 |
| 15-30 | 80 | 5% | 56.1 | 69.2 | 78.4 | 0.60 | 1.43 | 227 | 0.28 | 0.68 |
| 30-60 | 40 | 0% | 60.0 | 75.1 | 86.1 | 0.73 | 1.32 | 180 | 0.26 | 1.00 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 9% | 53.5 | 67.4 | 77.7 | 0.69 | 1.15 | 247 | 0.60 | 1.02 |
| laptop | 90 | 30% | 31.4 | 42.7 | 50.7 | 0.99 | 2.48 | 84 | 0.62 | 0.88 |
| cereal_box | 90 | 0% | 66.5 | 78.1 | 85.4 | 0.51 | 0.99 | 505 | 0.53 | 1.29 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 3% | 57.9 | 71.4 | 80.2 | 0.31 | 1.14 | 508 | 0.52 | 1.00 |
| 15-30 | 90 | 14% | 54.4 | 66.2 | 73.5 | 0.79 | 1.15 | 260 | 0.62 | 1.18 |
| 30-60 | 90 | 21% | 39.1 | 50.6 | 60.2 | 1.31 | 1.60 | 140 | 0.69 | 1.02 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 37% | 24.4 | 33.0 | 39.9 | 0.96 | 3.70 | 72 | 0.48 | 0.78 |
| handbag | 150 | 18% | 50.9 | 60.4 | 67.0 | 0.47 | 1.06 | 122 | 0.44 | 0.73 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 5% | 52.0 | 65.2 | 74.6 | 0.39 | 1.54 | 244 | 0.47 | 0.97 |
| 15-30 | 100 | 20% | 45.5 | 55.2 | 61.7 | 0.68 | 1.19 | 102 | 0.45 | 0.75 |
| 30-60 | 100 | 58% | 15.7 | 20.2 | 24.4 | 2.28 | 3.69 | 36 | 0.45 | 0.56 |

### mvimgnet: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| key | 150 | 23% | 38.7 | 45.7 | 51.4 | 0.60 | 1.38 | 110 | 0.72 | 1.06 |
| watch | 150 | 21% | 50.8 | 57.4 | 62.0 | 0.42 | 0.88 | 132 | 0.60 | 0.95 |

### mvimgnet: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 5% | 56.3 | 64.1 | 70.2 | 0.19 | 1.00 | 264 | 0.50 | 1.30 |
| 15-30 | 100 | 17% | 52.5 | 58.9 | 63.2 | 0.45 | 0.81 | 183 | 0.62 | 1.16 |
| 30-60 | 100 | 43% | 25.8 | 32.1 | 37.0 | 2.71 | 1.68 | 67 | 0.86 | 0.54 |
