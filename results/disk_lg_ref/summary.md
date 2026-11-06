# Results: disk_lg_ref

Config: `{"matcher": "disk_lg", "crop": true, "cascade": null, "shape": false, "model": "auto", "max_side": 800, "min_side": 0, "gric_sigma": "fixed", "masks": true, "refine": true, "datasets": ["tum", "objectron", "co3d", "mvimgnet"], "cached": true, "seconds_from": "results/_pretwin/disk_lg_ref/pairs.csv", "planar_twin": true, "per_bin": {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 4% | 53.8 | 69.9 | 80.9 | 0.59 | 1.73 | 1013 | 0.43 | 10.40 |
| objectron | 270 | 14% | 48.3 | 61.0 | 68.4 | 0.80 | 1.33 | 632 | 0.79 | 9.75 |
| co3d | 300 | 33% | 22.1 | 29.2 | 35.4 | 2.48 | 4.38 | 67 | 0.52 | 5.89 |
| mvimgnet | 300 | 28% | 8.1 | 15.9 | 24.6 | 8.04 | 15.01 | 154 | 0.56 | 7.80 |

### Per dataset, test split only (pairs never used for tuning)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 142 | 4% | 52.5 | 68.9 | 80.0 | 0.57 | 1.76 | 996 | 0.43 | 10.36 |
| objectron | 189 | 16% | 46.8 | 59.5 | 66.9 | 0.78 | 1.30 | 722 | 0.78 | 9.81 |
| co3d | 210 | 33% | 21.2 | 28.1 | 34.2 | 2.51 | 5.56 | 69 | 0.53 | 6.33 |
| mvimgnet | 210 | 24% | 10.9 | 21.0 | 31.2 | 5.67 | 9.97 | 242 | 0.56 | 8.22 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 15% | 44.5 | 54.7 | 62.8 | 0.64 | 2.35 | 820 | 0.33 | 8.97 |
| flat_near | 60 | 8% | 59.2 | 74.1 | 82.0 | 0.65 | 1.50 | 1109 | 0.42 | 10.62 |
| struct_far | 40 | 0% | 68.7 | 82.8 | 91.5 | 0.39 | 1.24 | 1375 | 0.36 | 11.08 |
| struct_near | 60 | 0% | 47.6 | 66.2 | 80.6 | 0.72 | 2.10 | 907 | 0.47 | 10.06 |
| checkerboard | 40 | 0% | 48.7 | 67.3 | 81.0 | 0.70 | 2.17 | 582 | 0.50 | 10.62 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 3% | 49.7 | 66.2 | 79.4 | 0.55 | 1.92 | 1150 | 0.39 | 10.53 |
| 15-30 | 80 | 3% | 58.2 | 74.5 | 84.1 | 0.55 | 1.64 | 1013 | 0.43 | 10.50 |
| 30-60 | 40 | 7% | 57.2 | 72.0 | 79.7 | 0.90 | 1.57 | 850 | 0.45 | 9.89 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 7% | 49.9 | 64.4 | 74.1 | 0.91 | 1.33 | 550 | 0.79 | 9.02 |
| laptop | 90 | 36% | 23.4 | 34.4 | 40.9 | 1.60 | 3.15 | 182 | 0.87 | 9.96 |
| cereal_box | 90 | 1% | 72.6 | 84.7 | 91.2 | 0.52 | 0.95 | 868 | 0.75 | 10.27 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 6% | 50.0 | 64.8 | 73.4 | 0.49 | 1.65 | 844 | 0.68 | 9.87 |
| 15-30 | 90 | 13% | 50.8 | 64.0 | 71.9 | 0.95 | 1.26 | 624 | 0.76 | 9.77 |
| 30-60 | 90 | 24% | 45.3 | 55.0 | 60.8 | 1.19 | 1.03 | 534 | 0.93 | 9.62 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 53% | 2.2 | 4.7 | 8.6 | 11.51 | 31.81 | 22 | 0.47 | 3.00 |
| handbag | 150 | 13% | 42.2 | 54.0 | 62.6 | 1.17 | 1.45 | 498 | 0.55 | 8.78 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 12% | 23.7 | 33.6 | 42.8 | 2.22 | 6.79 | 188 | 0.47 | 5.95 |
| 15-30 | 100 | 26% | 27.6 | 34.3 | 40.0 | 2.64 | 3.26 | 74 | 0.53 | 6.00 |
| 30-60 | 100 | 60% | 15.7 | 20.5 | 24.4 | 3.26 | 1.95 | 22 | 0.59 | 5.71 |

### mvimgnet: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| key | 150 | 31% | 5.0 | 11.9 | 20.6 | 10.55 | 17.58 | 131 | 0.54 | 6.12 |
| watch | 150 | 25% | 11.5 | 20.2 | 28.8 | 6.13 | 9.41 | 176 | 0.59 | 9.48 |

### mvimgnet: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 9% | 12.6 | 23.7 | 36.2 | 3.65 | 9.32 | 324 | 0.54 | 8.28 |
| 15-30 | 100 | 18% | 10.4 | 19.8 | 30.2 | 11.70 | 10.27 | 208 | 0.57 | 7.81 |
| 30-60 | 100 | 58% | 2.2 | 5.0 | 8.1 | 33.48 | 60.84 | 35 | 0.60 | 7.32 |
