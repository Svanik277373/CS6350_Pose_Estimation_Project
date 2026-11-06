# Results: disk_lg_crop

Config: `{"matcher": "disk_lg", "crop": true, "model": "auto", "max_side": 800, "masks": true, "datasets": ["tum", "objectron", "co3d"], "per_bin": {"tum": 20, "objectron": 3, "co3d": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 4% | 51.8 | 68.4 | 79.8 | 0.62 | 1.84 | 1013 | 0.43 | 3.18 |
| objectron | 270 | 16% | 43.9 | 56.9 | 65.1 | 0.96 | 1.56 | 632 | 0.80 | 3.26 |
| co3d | 300 | 34% | 21.4 | 28.0 | 34.1 | 2.86 | 4.89 | 67 | 0.55 | 1.92 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 15% | 39.7 | 49.8 | 57.8 | 0.86 | 2.27 | 820 | 0.31 | 2.77 |
| flat_near | 60 | 10% | 58.2 | 72.4 | 79.5 | 0.66 | 1.39 | 1109 | 0.42 | 3.26 |
| struct_far | 40 | 0% | 68.7 | 82.9 | 91.5 | 0.39 | 1.22 | 1375 | 0.36 | 3.43 |
| struct_near | 60 | 0% | 46.5 | 66.0 | 81.8 | 0.75 | 2.16 | 907 | 0.47 | 3.27 |
| checkerboard | 40 | 0% | 43.7 | 63.9 | 79.4 | 0.78 | 2.23 | 582 | 0.51 | 2.88 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 3% | 47.8 | 64.9 | 77.7 | 0.59 | 1.97 | 1150 | 0.39 | 3.13 |
| 15-30 | 80 | 3% | 56.9 | 73.9 | 84.8 | 0.55 | 1.75 | 1013 | 0.43 | 3.26 |
| 30-60 | 40 | 10% | 53.6 | 68.1 | 76.7 | 0.94 | 1.64 | 850 | 0.45 | 3.15 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 8% | 45.5 | 60.0 | 69.6 | 1.07 | 1.78 | 550 | 0.80 | 3.13 |
| laptop | 90 | 38% | 20.6 | 32.5 | 40.9 | 1.72 | 3.25 | 182 | 0.88 | 3.35 |
| cereal_box | 90 | 1% | 66.7 | 78.9 | 85.5 | 0.61 | 1.10 | 868 | 0.75 | 3.30 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 7% | 47.7 | 61.9 | 71.2 | 0.53 | 1.82 | 844 | 0.68 | 3.24 |
| 15-30 | 90 | 16% | 45.8 | 60.7 | 70.2 | 1.07 | 1.47 | 624 | 0.77 | 3.26 |
| 30-60 | 90 | 24% | 39.4 | 49.0 | 54.5 | 1.53 | 1.27 | 534 | 0.94 | 3.27 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 53% | 2.0 | 3.4 | 7.2 | 12.77 | 44.72 | 22 | 0.52 | 1.01 |
| handbag | 150 | 15% | 41.1 | 52.9 | 61.3 | 1.15 | 1.60 | 498 | 0.56 | 2.83 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 15% | 23.9 | 32.9 | 41.2 | 2.43 | 6.81 | 188 | 0.51 | 1.90 |
| 15-30 | 100 | 27% | 26.5 | 32.6 | 38.2 | 2.70 | 3.17 | 74 | 0.57 | 1.96 |
| 30-60 | 100 | 60% | 14.8 | 19.4 | 23.8 | 3.90 | 2.94 | 22 | 0.58 | 1.91 |
