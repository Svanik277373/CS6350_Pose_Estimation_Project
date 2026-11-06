# Results: sift_ref

Config: `{"matcher": "sift", "crop": true, "cascade": null, "shape": false, "model": "auto", "max_side": 800, "min_side": 0, "gric_sigma": "fixed", "masks": true, "refine": true, "datasets": ["tum", "objectron", "co3d", "mvimgnet"], "cached": true, "seconds_from": "results/_pretwin/sift_ref/pairs.csv", "planar_twin": true, "per_bin": {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 3% | 52.1 | 67.3 | 78.0 | 0.65 | 1.59 | 218 | 0.27 | 0.29 |
| objectron | 270 | 21% | 38.1 | 52.3 | 62.6 | 1.06 | 1.82 | 158 | 0.49 | 0.65 |
| co3d | 300 | 61% | 10.8 | 16.6 | 21.2 | 1.74 | 4.52 | 18 | 0.44 | 0.25 |
| mvimgnet | 300 | 58% | 4.5 | 8.7 | 13.5 | 6.75 | 17.94 | 26 | 0.48 | 0.28 |

### Per dataset, test split only (pairs never used for tuning)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 142 | 4% | 50.3 | 65.8 | 77.0 | 0.66 | 1.61 | 178 | 0.27 | 0.24 |
| objectron | 189 | 24% | 37.9 | 50.7 | 60.5 | 0.97 | 1.78 | 140 | 0.50 | 0.61 |
| co3d | 210 | 59% | 12.1 | 18.1 | 22.7 | 1.64 | 4.37 | 20 | 0.48 | 0.25 |
| mvimgnet | 210 | 60% | 4.2 | 8.5 | 13.2 | 6.91 | 17.75 | 26 | 0.48 | 0.29 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 10% | 45.6 | 57.7 | 63.8 | 0.64 | 2.12 | 98 | 0.27 | 0.45 |
| flat_near | 60 | 0% | 74.4 | 87.0 | 93.5 | 0.59 | 1.08 | 246 | 0.24 | 0.42 |
| struct_far | 40 | 0% | 65.4 | 80.7 | 89.1 | 0.41 | 1.39 | 447 | 0.28 | 0.12 |
| struct_near | 60 | 2% | 41.7 | 61.6 | 78.4 | 0.77 | 2.40 | 180 | 0.33 | 0.23 |
| checkerboard | 40 | 7% | 28.4 | 41.1 | 52.5 | 1.48 | 5.05 | 131 | 0.30 | 0.25 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 2% | 46.7 | 63.2 | 75.2 | 0.63 | 2.08 | 263 | 0.27 | 0.29 |
| 15-30 | 80 | 5% | 56.1 | 69.2 | 78.4 | 0.60 | 1.43 | 227 | 0.28 | 0.24 |
| 30-60 | 40 | 0% | 60.0 | 75.1 | 86.1 | 0.73 | 1.32 | 180 | 0.26 | 0.36 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 23% | 34.9 | 51.5 | 62.9 | 0.86 | 1.93 | 158 | 0.54 | 0.54 |
| laptop | 90 | 40% | 18.9 | 30.8 | 40.1 | 1.89 | 3.79 | 48 | 0.47 | 0.59 |
| cereal_box | 90 | 1% | 61.6 | 75.6 | 85.6 | 0.76 | 1.19 | 404 | 0.47 | 0.82 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 12% | 41.8 | 58.7 | 70.7 | 0.57 | 1.93 | 340 | 0.40 | 0.80 |
| 15-30 | 90 | 20% | 42.3 | 55.7 | 65.2 | 1.11 | 1.80 | 163 | 0.53 | 0.67 |
| 30-60 | 90 | 32% | 31.2 | 43.5 | 52.8 | 1.71 | 1.78 | 96 | 0.61 | 0.49 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 84% | 1.1 | 2.5 | 3.5 | 4.02 | 42.71 | 11 | 0.38 | 0.13 |
| handbag | 150 | 39% | 20.8 | 30.9 | 39.3 | 1.46 | 3.85 | 51 | 0.47 | 0.37 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 37% | 15.6 | 24.4 | 32.3 | 1.75 | 5.09 | 40 | 0.43 | 0.30 |
| 15-30 | 100 | 64% | 12.4 | 19.3 | 24.1 | 1.55 | 3.72 | 18 | 0.49 | 0.23 |
| 30-60 | 100 | 83% | 5.1 | 7.0 | 8.0 | 8.35 | 8.53 | 10 | 0.49 | 0.22 |

### mvimgnet: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| key | 150 | 63% | 0.9 | 2.4 | 4.9 | 9.98 | 34.58 | 22 | 0.51 | 0.24 |
| watch | 150 | 53% | 8.3 | 15.4 | 22.5 | 3.58 | 6.69 | 34 | 0.47 | 0.32 |

### mvimgnet: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 21% | 9.1 | 16.7 | 25.9 | 4.68 | 17.94 | 58 | 0.47 | 0.30 |
| 15-30 | 100 | 60% | 3.9 | 8.5 | 13.4 | 13.09 | 13.43 | 25 | 0.49 | 0.29 |
| 30-60 | 100 | 94% | 1.3 | 1.6 | 1.8 | 62.61 | 58.28 | 14 | 0.51 | 0.26 |
