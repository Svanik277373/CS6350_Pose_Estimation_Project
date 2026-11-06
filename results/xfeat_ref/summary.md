# Results: xfeat_ref

Config: `{"matcher": "xfeat", "crop": true, "cascade": null, "shape": false, "model": "auto", "max_side": 800, "min_side": 0, "gric_sigma": "fixed", "masks": true, "refine": true, "datasets": ["tum", "objectron", "co3d", "mvimgnet"], "cached": true, "seconds_from": "results/_pretwin/xfeat_ref/pairs.csv", "planar_twin": true, "per_bin": {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 1% | 37.2 | 55.3 | 70.4 | 0.84 | 3.04 | 884 | 0.52 | 0.43 |
| objectron | 270 | 4% | 44.9 | 59.8 | 70.4 | 1.17 | 2.03 | 574 | 1.05 | 0.52 |
| co3d | 300 | 8% | 12.3 | 20.8 | 32.4 | 6.41 | 13.90 | 236 | 0.58 | 0.40 |
| mvimgnet | 300 | 7% | 9.5 | 18.5 | 29.4 | 8.46 | 18.34 | 300 | 0.60 | 0.50 |

### Per dataset, test split only (pairs never used for tuning)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 142 | 0% | 36.6 | 54.3 | 69.9 | 0.82 | 3.32 | 899 | 0.52 | 0.44 |
| objectron | 189 | 5% | 43.3 | 57.7 | 67.9 | 1.15 | 2.07 | 612 | 1.05 | 0.53 |
| co3d | 210 | 8% | 13.5 | 22.3 | 33.4 | 5.89 | 13.81 | 254 | 0.59 | 0.42 |
| mvimgnet | 210 | 4% | 9.5 | 17.8 | 28.5 | 9.44 | 20.63 | 318 | 0.60 | 0.51 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 0% | 24.9 | 34.9 | 49.7 | 2.48 | 11.23 | 759 | 0.56 | 0.70 |
| flat_near | 60 | 3% | 34.4 | 50.6 | 62.7 | 0.97 | 3.16 | 870 | 0.49 | 0.43 |
| struct_far | 40 | 0% | 62.4 | 78.3 | 89.2 | 0.41 | 1.65 | 1176 | 0.49 | 0.38 |
| struct_near | 60 | 0% | 35.4 | 57.6 | 77.6 | 0.87 | 3.36 | 849 | 0.54 | 0.39 |
| checkerboard | 40 | 0% | 29.5 | 50.1 | 66.8 | 0.86 | 4.63 | 694 | 0.55 | 0.39 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 35.5 | 53.7 | 71.0 | 0.75 | 3.59 | 1028 | 0.51 | 0.44 |
| 15-30 | 80 | 0% | 46.3 | 67.0 | 80.2 | 0.78 | 2.05 | 892 | 0.51 | 0.39 |
| 30-60 | 40 | 5% | 25.3 | 38.2 | 51.9 | 3.38 | 5.95 | 664 | 0.55 | 0.46 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 3% | 43.4 | 60.1 | 73.0 | 1.26 | 2.07 | 573 | 1.12 | 0.49 |
| laptop | 90 | 9% | 24.1 | 37.5 | 48.4 | 2.65 | 5.47 | 375 | 1.02 | 0.56 |
| cereal_box | 90 | 0% | 68.2 | 82.8 | 90.7 | 0.62 | 1.10 | 734 | 1.03 | 0.52 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 1% | 43.2 | 59.0 | 71.3 | 0.83 | 2.27 | 696 | 0.99 | 0.49 |
| 15-30 | 90 | 2% | 48.0 | 64.0 | 75.2 | 1.25 | 1.79 | 566 | 1.07 | 0.52 |
| 30-60 | 90 | 9% | 44.5 | 57.5 | 65.4 | 1.52 | 1.57 | 433 | 1.12 | 0.56 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 13% | 0.8 | 4.2 | 13.7 | 10.59 | 33.56 | 130 | 0.55 | 0.32 |
| handbag | 150 | 3% | 24.1 | 37.7 | 51.4 | 3.23 | 5.74 | 443 | 0.65 | 0.49 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 1% | 15.4 | 23.6 | 36.8 | 3.45 | 13.86 | 356 | 0.56 | 0.34 |
| 15-30 | 100 | 3% | 14.4 | 24.7 | 37.5 | 7.03 | 12.02 | 220 | 0.60 | 0.39 |
| 30-60 | 100 | 20% | 7.9 | 14.9 | 23.7 | 23.81 | 25.71 | 166 | 0.60 | 0.48 |

### mvimgnet: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| key | 150 | 9% | 2.7 | 7.2 | 16.2 | 14.88 | 36.19 | 242 | 0.58 | 0.46 |
| watch | 150 | 5% | 16.6 | 30.2 | 42.8 | 5.32 | 6.80 | 363 | 0.62 | 0.54 |

### mvimgnet: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 3% | 10.9 | 23.3 | 38.1 | 3.06 | 12.93 | 438 | 0.59 | 0.42 |
| 15-30 | 100 | 3% | 14.1 | 23.8 | 35.6 | 12.09 | 12.89 | 301 | 0.60 | 0.48 |
| 30-60 | 100 | 15% | 4.5 | 9.3 | 15.3 | 32.62 | 62.61 | 210 | 0.61 | 0.60 |
