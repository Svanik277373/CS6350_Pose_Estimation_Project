# Results: sift_crop

Config: `{"matcher": "sift", "crop": true, "model": "auto", "max_side": 800, "masks": true, "datasets": ["tum", "objectron", "co3d"], "per_bin": {"tum": 20, "objectron": 3, "co3d": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 3% | 46.3 | 62.3 | 74.3 | 0.80 | 1.97 | 218 | 0.34 | 0.09 |
| objectron | 270 | 21% | 33.1 | 46.8 | 57.2 | 1.34 | 2.25 | 158 | 0.52 | 0.14 |
| co3d | 300 | 62% | 7.0 | 13.1 | 18.9 | 3.56 | 7.70 | 18 | 0.50 | 0.08 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 10% | 41.9 | 51.0 | 55.5 | 0.80 | 2.29 | 98 | 0.27 | 0.08 |
| flat_near | 60 | 0% | 73.2 | 86.6 | 93.3 | 0.61 | 1.04 | 246 | 0.24 | 0.10 |
| struct_far | 40 | 0% | 45.1 | 68.6 | 83.0 | 1.02 | 2.23 | 447 | 0.41 | 0.09 |
| struct_near | 60 | 2% | 36.3 | 55.6 | 74.9 | 0.91 | 3.14 | 180 | 0.40 | 0.09 |
| checkerboard | 40 | 10% | 28.6 | 38.7 | 48.1 | 2.05 | 5.19 | 131 | 0.38 | 0.10 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 3% | 39.4 | 56.7 | 69.4 | 0.81 | 2.48 | 263 | 0.36 | 0.09 |
| 15-30 | 80 | 5% | 51.4 | 65.8 | 76.6 | 0.82 | 1.65 | 227 | 0.34 | 0.09 |
| 30-60 | 40 | 0% | 56.1 | 71.6 | 84.2 | 0.79 | 1.30 | 180 | 0.28 | 0.10 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 23% | 30.3 | 46.0 | 58.3 | 1.25 | 2.43 | 158 | 0.58 | 0.13 |
| laptop | 90 | 40% | 17.9 | 29.9 | 39.6 | 1.81 | 3.48 | 48 | 0.53 | 0.14 |
| cereal_box | 90 | 1% | 52.2 | 65.3 | 74.6 | 1.04 | 1.54 | 404 | 0.51 | 0.15 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 12% | 37.7 | 54.0 | 66.6 | 0.72 | 2.43 | 340 | 0.42 | 0.14 |
| 15-30 | 90 | 20% | 37.9 | 52.8 | 62.7 | 1.44 | 2.09 | 163 | 0.57 | 0.14 |
| 30-60 | 90 | 32% | 24.8 | 34.4 | 43.3 | 2.11 | 2.64 | 96 | 0.71 | 0.14 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 84% | 1.0 | 1.8 | 2.9 | 6.22 | 49.91 | 11 | 0.49 | 0.05 |
| handbag | 150 | 39% | 13.1 | 24.6 | 35.1 | 2.73 | 5.32 | 51 | 0.51 | 0.12 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 37% | 11.8 | 20.0 | 28.9 | 2.17 | 8.93 | 40 | 0.48 | 0.08 |
| 15-30 | 100 | 65% | 7.0 | 15.1 | 21.7 | 3.41 | 4.59 | 18 | 0.54 | 0.08 |
| 30-60 | 100 | 83% | 3.0 | 5.2 | 7.0 | 14.88 | 14.35 | 10 | 0.57 | 0.08 |
