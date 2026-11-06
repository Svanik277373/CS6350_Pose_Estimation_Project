# Results: aliked_lg_full

Config: `{"matcher": "aliked_lg", "crop": false, "cascade": null, "shape": false, "model": "auto", "max_side": 800, "min_side": 0, "gric_sigma": "fixed", "masks": false, "refine": true, "datasets": ["tum", "objectron", "co3d", "mvimgnet"], "cached": false, "seconds_from": null, "planar_twin": true, "per_bin": {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 7% | 49.8 | 66.6 | 78.0 | 0.59 | 1.74 | 262 | 0.30 | 6.43 |
| objectron | 270 | 4% | 63.5 | 75.6 | 83.4 | 0.47 | 1.05 | 523 | 0.84 | 8.18 |
| co3d | 300 | 7% | 62.8 | 72.5 | 79.2 | 0.43 | 0.81 | 346 | 0.57 | 4.38 |
| mvimgnet | 300 | 7% | 67.3 | 76.7 | 82.6 | 0.33 | 0.66 | 224 | 0.84 | 3.67 |

### Per dataset, test split only (pairs never used for tuning)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 142 | 8% | 47.6 | 64.7 | 76.5 | 0.62 | 1.80 | 229 | 0.29 | 6.46 |
| objectron | 189 | 4% | 65.1 | 77.1 | 84.7 | 0.47 | 1.05 | 507 | 0.83 | 8.22 |
| co3d | 210 | 8% | 61.1 | 72.0 | 79.2 | 0.46 | 0.91 | 328 | 0.58 | 3.96 |
| mvimgnet | 210 | 7% | 65.7 | 74.9 | 81.1 | 0.34 | 0.75 | 206 | 0.84 | 3.51 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 20% | 45.2 | 59.6 | 67.3 | 0.60 | 1.66 | 138 | 0.27 | 7.59 |
| flat_near | 60 | 18% | 50.2 | 64.7 | 72.4 | 0.67 | 1.54 | 332 | 0.27 | 6.95 |
| struct_far | 40 | 0% | 68.8 | 83.0 | 91.5 | 0.41 | 1.25 | 415 | 0.24 | 6.20 |
| struct_near | 60 | 0% | 46.3 | 66.7 | 80.8 | 0.69 | 2.38 | 238 | 0.34 | 5.73 |
| checkerboard | 40 | 0% | 42.4 | 60.6 | 76.5 | 0.57 | 2.52 | 178 | 0.40 | 6.38 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 4% | 47.7 | 64.8 | 78.3 | 0.54 | 1.85 | 299 | 0.27 | 6.72 |
| 15-30 | 80 | 3% | 57.8 | 75.6 | 85.8 | 0.62 | 1.59 | 262 | 0.33 | 6.24 |
| 30-60 | 40 | 22% | 41.5 | 55.3 | 63.4 | 0.77 | 1.76 | 192 | 0.35 | 6.10 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 1% | 69.2 | 82.1 | 89.8 | 0.43 | 0.87 | 548 | 0.84 | 8.73 |
| laptop | 90 | 10% | 44.4 | 58.0 | 68.5 | 1.00 | 1.59 | 320 | 0.95 | 7.68 |
| cereal_box | 90 | 0% | 78.0 | 87.3 | 92.6 | 0.41 | 0.79 | 581 | 0.75 | 8.11 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 1% | 63.6 | 76.1 | 84.9 | 0.27 | 1.16 | 652 | 0.71 | 7.89 |
| 15-30 | 90 | 2% | 70.4 | 81.7 | 88.6 | 0.47 | 0.95 | 524 | 0.84 | 8.19 |
| 30-60 | 90 | 8% | 57.6 | 69.8 | 77.5 | 0.87 | 1.09 | 398 | 0.95 | 8.44 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 7% | 56.5 | 66.9 | 74.4 | 0.57 | 0.96 | 282 | 0.58 | 5.04 |
| handbag | 150 | 7% | 69.4 | 78.4 | 84.3 | 0.39 | 0.66 | 404 | 0.57 | 3.72 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 76.1 | 85.6 | 91.5 | 0.23 | 0.68 | 558 | 0.48 | 4.68 |
| 15-30 | 100 | 0% | 74.8 | 84.8 | 91.4 | 0.39 | 0.59 | 400 | 0.57 | 4.36 |
| 30-60 | 100 | 22% | 38.3 | 47.9 | 55.5 | 1.71 | 1.68 | 142 | 0.68 | 4.10 |

### mvimgnet: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| key | 150 | 7% | 63.5 | 73.3 | 79.7 | 0.40 | 0.79 | 206 | 0.82 | 3.67 |
| watch | 150 | 7% | 71.4 | 80.5 | 85.8 | 0.25 | 0.58 | 250 | 0.86 | 3.67 |

### mvimgnet: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 1% | 70.9 | 82.3 | 88.9 | 0.21 | 0.82 | 358 | 0.66 | 3.93 |
| 15-30 | 100 | 1% | 78.9 | 86.3 | 91.5 | 0.30 | 0.51 | 278 | 0.84 | 3.67 |
| 30-60 | 100 | 20% | 52.8 | 62.2 | 68.4 | 0.69 | 0.77 | 122 | 1.05 | 3.42 |
