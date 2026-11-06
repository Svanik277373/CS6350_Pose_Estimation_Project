# Results: loftr_ref

Config: `{"matcher": "loftr", "crop": true, "cascade": null, "shape": false, "model": "auto", "max_side": 800, "min_side": 0, "gric_sigma": "fixed", "masks": true, "refine": true, "datasets": ["tum", "objectron", "co3d", "mvimgnet"], "cached": true, "seconds_from": "results/_pretwin/loftr_ref/pairs.csv", "planar_twin": true, "per_bin": {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 9% | 50.8 | 66.4 | 76.5 | 0.55 | 1.67 | 1759 | 0.36 | 10.04 |
| objectron | 270 | 5% | 51.2 | 64.9 | 74.8 | 0.85 | 1.50 | 1474 | 0.76 | 10.75 |
| co3d | 300 | 12% | 23.1 | 31.8 | 41.8 | 3.60 | 7.86 | 232 | 0.52 | 8.14 |
| mvimgnet | 300 | 13% | 14.5 | 24.2 | 33.9 | 5.92 | 11.68 | 356 | 0.56 | 11.37 |

### Per dataset, test split only (pairs never used for tuning)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 142 | 8% | 51.7 | 67.1 | 76.8 | 0.55 | 1.61 | 2002 | 0.36 | 10.08 |
| objectron | 189 | 6% | 50.9 | 65.2 | 74.6 | 0.85 | 1.50 | 1492 | 0.75 | 10.79 |
| co3d | 210 | 10% | 24.1 | 33.1 | 43.1 | 3.18 | 7.92 | 242 | 0.53 | 8.78 |
| mvimgnet | 210 | 13% | 13.9 | 24.4 | 35.1 | 5.89 | 9.94 | 380 | 0.56 | 11.50 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 20% | 40.8 | 55.0 | 64.6 | 0.72 | 2.17 | 983 | 0.31 | 10.71 |
| flat_near | 60 | 27% | 46.9 | 57.6 | 63.6 | 0.55 | 1.34 | 1337 | 0.30 | 10.11 |
| struct_far | 40 | 0% | 69.5 | 83.1 | 91.7 | 0.43 | 1.07 | 2821 | 0.30 | 11.56 |
| struct_near | 60 | 0% | 48.8 | 70.0 | 84.2 | 0.63 | 2.37 | 2048 | 0.39 | 10.90 |
| checkerboard | 40 | 0% | 50.1 | 66.8 | 78.4 | 0.69 | 1.94 | 1280 | 0.45 | 6.81 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 4% | 50.0 | 68.1 | 80.5 | 0.51 | 1.86 | 2298 | 0.31 | 10.35 |
| 15-30 | 80 | 4% | 60.6 | 74.4 | 82.9 | 0.55 | 1.49 | 1792 | 0.39 | 9.77 |
| 30-60 | 40 | 32% | 35.4 | 47.8 | 55.1 | 0.72 | 2.31 | 1138 | 0.45 | 9.84 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 7% | 52.5 | 67.1 | 76.0 | 0.88 | 1.49 | 1553 | 0.72 | 10.02 |
| laptop | 90 | 9% | 27.9 | 42.2 | 56.7 | 1.91 | 3.78 | 496 | 0.86 | 11.30 |
| cereal_box | 90 | 0% | 74.1 | 85.9 | 92.5 | 0.48 | 0.88 | 2044 | 0.67 | 10.92 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 0% | 54.2 | 70.1 | 81.6 | 0.47 | 1.76 | 2048 | 0.66 | 11.11 |
| 15-30 | 90 | 1% | 54.0 | 68.5 | 79.0 | 0.95 | 1.56 | 1437 | 0.80 | 10.76 |
| 30-60 | 90 | 14% | 46.5 | 56.9 | 64.5 | 1.17 | 1.13 | 1008 | 0.91 | 10.37 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 18% | 3.1 | 7.7 | 16.7 | 9.26 | 26.17 | 134 | 0.51 | 4.03 |
| handbag | 150 | 5% | 43.3 | 56.3 | 67.3 | 1.10 | 1.96 | 716 | 0.54 | 12.26 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 26.8 | 37.4 | 50.7 | 1.63 | 7.64 | 446 | 0.49 | 8.49 |
| 15-30 | 100 | 6% | 29.3 | 38.5 | 48.1 | 4.91 | 6.34 | 242 | 0.54 | 8.16 |
| 30-60 | 100 | 29% | 14.0 | 20.5 | 27.6 | 12.51 | 11.99 | 100 | 0.56 | 7.79 |

### mvimgnet: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| key | 150 | 23% | 5.8 | 10.9 | 18.2 | 12.24 | 37.00 | 229 | 0.54 | 8.58 |
| watch | 150 | 3% | 23.5 | 37.7 | 49.9 | 3.80 | 4.95 | 740 | 0.58 | 14.15 |

### mvimgnet: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 2% | 23.4 | 37.8 | 52.1 | 1.99 | 5.83 | 1023 | 0.52 | 12.26 |
| 15-30 | 100 | 4% | 18.9 | 31.2 | 42.2 | 8.31 | 9.00 | 366 | 0.58 | 11.29 |
| 30-60 | 100 | 34% | 2.0 | 4.4 | 8.3 | 42.85 | 53.40 | 115 | 0.60 | 10.55 |
