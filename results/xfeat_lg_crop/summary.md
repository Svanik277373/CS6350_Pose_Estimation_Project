# Results: xfeat_lg_crop

Config: `{"matcher": "xfeat_lg", "crop": true, "model": "auto", "max_side": 800, "masks": true, "datasets": ["tum", "objectron", "co3d"], "per_bin": {"tum": 20, "objectron": 3, "co3d": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 1% | 48.8 | 64.9 | 75.9 | 0.71 | 1.92 | 913 | 0.50 | 0.59 |
| objectron | 270 | 9% | 37.0 | 49.3 | 58.7 | 1.43 | 2.47 | 584 | 1.04 | 0.42 |
| co3d | 300 | 16% | 17.9 | 28.2 | 39.0 | 3.80 | 8.03 | 192 | 0.59 | 0.30 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 10% | 27.6 | 40.3 | 47.6 | 1.86 | 5.04 | 796 | 0.54 | 0.66 |
| flat_near | 60 | 2% | 56.5 | 69.8 | 76.5 | 0.85 | 1.52 | 1090 | 0.47 | 0.62 |
| struct_far | 40 | 0% | 67.5 | 82.4 | 91.3 | 0.39 | 1.26 | 1062 | 0.48 | 0.60 |
| struct_near | 60 | 0% | 48.0 | 69.3 | 83.8 | 0.71 | 2.09 | 828 | 0.52 | 0.53 |
| checkerboard | 40 | 0% | 34.3 | 49.7 | 63.9 | 0.76 | 3.96 | 696 | 0.56 | 0.56 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 2% | 40.3 | 56.7 | 69.2 | 0.70 | 2.85 | 1002 | 0.50 | 0.60 |
| 15-30 | 80 | 0% | 58.3 | 75.0 | 85.4 | 0.61 | 1.65 | 904 | 0.50 | 0.57 |
| 30-60 | 40 | 3% | 53.0 | 67.4 | 74.9 | 0.88 | 1.71 | 733 | 0.50 | 0.60 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 10% | 38.3 | 51.3 | 61.0 | 1.44 | 2.39 | 588 | 1.08 | 0.42 |
| laptop | 90 | 16% | 15.9 | 28.5 | 41.0 | 3.81 | 7.53 | 324 | 1.04 | 0.40 |
| cereal_box | 90 | 1% | 57.9 | 68.9 | 74.9 | 0.66 | 1.38 | 748 | 0.98 | 0.46 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 1% | 41.3 | 55.5 | 66.7 | 0.71 | 2.54 | 674 | 0.98 | 0.43 |
| 15-30 | 90 | 8% | 38.1 | 50.6 | 59.5 | 1.57 | 2.31 | 598 | 1.03 | 0.43 |
| 30-60 | 90 | 18% | 32.7 | 42.9 | 50.7 | 2.12 | 2.31 | 479 | 1.11 | 0.41 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 25% | 2.2 | 6.8 | 15.9 | 8.39 | 21.64 | 82 | 0.56 | 0.18 |
| handbag | 150 | 7% | 34.0 | 49.9 | 62.3 | 1.76 | 2.92 | 456 | 0.63 | 0.41 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 20.8 | 32.6 | 45.5 | 2.71 | 9.55 | 332 | 0.56 | 0.30 |
| 15-30 | 100 | 9% | 21.5 | 34.1 | 45.5 | 4.59 | 5.82 | 222 | 0.58 | 0.29 |
| 30-60 | 100 | 40% | 12.4 | 18.6 | 26.8 | 10.30 | 8.94 | 52 | 0.63 | 0.30 |
