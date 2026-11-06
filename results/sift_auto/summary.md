# Results: sift_auto

Config: `{"matcher": "sift", "model": "auto", "max_side": 800, "masks": true, "datasets": ["tum", "objectron", "co3d"], "per_bin": {"tum": 20, "objectron": 3, "co3d": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 3% | 46.3 | 62.3 | 74.3 | 0.80 | 1.97 | 218 | 0.34 | 0.11 |
| objectron | 270 | 24% | 32.0 | 46.0 | 56.7 | 1.34 | 2.20 | 143 | 0.55 | 0.13 |
| co3d | 300 | 66% | 6.4 | 11.5 | 17.3 | 3.02 | 7.48 | 13 | 0.69 | 0.11 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 10% | 41.9 | 51.0 | 55.5 | 0.80 | 2.29 | 98 | 0.27 | 0.08 |
| flat_near | 60 | 0% | 73.2 | 86.6 | 93.3 | 0.61 | 1.04 | 246 | 0.24 | 0.12 |
| struct_far | 40 | 0% | 45.1 | 68.6 | 83.0 | 1.02 | 2.23 | 447 | 0.41 | 0.11 |
| struct_near | 60 | 2% | 36.3 | 55.6 | 74.9 | 0.91 | 3.14 | 180 | 0.40 | 0.10 |
| checkerboard | 40 | 10% | 28.6 | 38.7 | 48.1 | 2.05 | 5.19 | 131 | 0.38 | 0.11 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 3% | 39.4 | 56.7 | 69.4 | 0.81 | 2.48 | 263 | 0.36 | 0.10 |
| 15-30 | 80 | 5% | 51.4 | 65.8 | 76.6 | 0.82 | 1.65 | 227 | 0.34 | 0.11 |
| 30-60 | 40 | 0% | 56.1 | 71.6 | 84.2 | 0.79 | 1.30 | 180 | 0.28 | 0.12 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 26% | 29.2 | 44.1 | 55.6 | 1.32 | 2.45 | 146 | 0.60 | 0.13 |
| laptop | 90 | 44% | 15.4 | 26.6 | 35.9 | 1.95 | 3.58 | 40 | 0.57 | 0.12 |
| cereal_box | 90 | 3% | 52.3 | 68.2 | 79.4 | 0.98 | 1.34 | 355 | 0.52 | 0.14 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 14% | 35.0 | 51.1 | 62.5 | 0.98 | 2.58 | 286 | 0.46 | 0.13 |
| 15-30 | 90 | 23% | 34.2 | 48.9 | 60.1 | 1.33 | 2.07 | 152 | 0.61 | 0.13 |
| 30-60 | 90 | 36% | 27.8 | 38.8 | 48.3 | 2.04 | 1.75 | 96 | 0.71 | 0.13 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 89% | 1.1 | 1.9 | 3.3 | 5.47 | 17.56 | 6 | 0.65 | 0.11 |
| handbag | 150 | 43% | 11.9 | 21.4 | 31.6 | 2.51 | 6.83 | 40 | 0.71 | 0.11 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 51% | 10.3 | 17.8 | 27.0 | 1.95 | 7.37 | 30 | 0.65 | 0.11 |
| 15-30 | 100 | 65% | 7.0 | 13.4 | 19.6 | 3.45 | 5.53 | 13 | 0.64 | 0.11 |
| 30-60 | 100 | 82% | 2.4 | 4.3 | 6.3 | 15.30 | 18.61 | 7 | 0.92 | 0.11 |
