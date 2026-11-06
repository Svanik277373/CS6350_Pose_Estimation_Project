# Results: aliked_lg_ref

Config: `{"matcher": "aliked_lg", "crop": true, "cascade": null, "shape": false, "model": "auto", "max_side": 800, "min_side": 0, "gric_sigma": "fixed", "masks": true, "refine": true, "datasets": ["tum", "objectron", "co3d", "mvimgnet"], "cached": true, "seconds_from": "results/_pretwin/aliked_lg_ref/pairs.csv", "planar_twin": true, "per_bin": {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 7% | 49.8 | 66.6 | 78.0 | 0.59 | 1.74 | 262 | 0.30 | 1.42 |
| objectron | 270 | 13% | 44.6 | 57.8 | 67.2 | 0.96 | 1.66 | 340 | 0.62 | 4.23 |
| co3d | 300 | 34% | 22.7 | 31.7 | 39.9 | 2.03 | 3.38 | 56 | 0.47 | 1.39 |
| mvimgnet | 300 | 15% | 15.9 | 28.5 | 40.3 | 4.41 | 6.74 | 90 | 0.53 | 2.06 |

### Per dataset, test split only (pairs never used for tuning)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 142 | 8% | 47.6 | 64.7 | 76.5 | 0.62 | 1.80 | 229 | 0.29 | 1.39 |
| objectron | 189 | 15% | 44.2 | 57.8 | 67.1 | 0.94 | 1.62 | 332 | 0.61 | 4.39 |
| co3d | 210 | 34% | 22.6 | 32.1 | 39.9 | 1.82 | 3.78 | 52 | 0.47 | 1.34 |
| mvimgnet | 210 | 12% | 19.0 | 33.5 | 46.6 | 3.97 | 4.85 | 110 | 0.52 | 2.21 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 20% | 45.2 | 59.6 | 67.3 | 0.60 | 1.66 | 138 | 0.27 | 1.63 |
| flat_near | 60 | 18% | 50.2 | 64.7 | 72.4 | 0.67 | 1.54 | 332 | 0.27 | 1.44 |
| struct_far | 40 | 0% | 68.8 | 83.0 | 91.5 | 0.41 | 1.25 | 415 | 0.24 | 1.18 |
| struct_near | 60 | 0% | 46.3 | 66.7 | 80.8 | 0.69 | 2.38 | 238 | 0.34 | 1.03 |
| checkerboard | 40 | 0% | 42.4 | 60.6 | 76.5 | 0.57 | 2.52 | 178 | 0.40 | 2.10 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 4% | 47.7 | 64.8 | 78.3 | 0.54 | 1.85 | 299 | 0.27 | 1.35 |
| 15-30 | 80 | 3% | 57.8 | 75.6 | 85.8 | 0.62 | 1.59 | 262 | 0.33 | 1.61 |
| 30-60 | 40 | 22% | 41.5 | 55.3 | 63.4 | 0.77 | 1.76 | 192 | 0.35 | 1.20 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 6% | 42.7 | 58.4 | 70.6 | 1.07 | 2.07 | 314 | 0.66 | 3.12 |
| laptop | 90 | 33% | 23.5 | 34.4 | 42.8 | 1.82 | 2.86 | 164 | 0.61 | 3.43 |
| cereal_box | 90 | 0% | 68.5 | 81.5 | 89.1 | 0.60 | 1.06 | 464 | 0.60 | 6.15 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 9% | 43.9 | 58.8 | 69.7 | 0.58 | 2.12 | 414 | 0.51 | 4.27 |
| 15-30 | 90 | 12% | 47.6 | 59.3 | 68.4 | 1.10 | 1.56 | 350 | 0.61 | 4.53 |
| 30-60 | 90 | 18% | 43.3 | 56.3 | 64.5 | 1.47 | 1.60 | 311 | 0.84 | 3.91 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 57% | 2.9 | 6.4 | 12.5 | 5.57 | 16.97 | 20 | 0.42 | 1.24 |
| handbag | 150 | 11% | 42.9 | 57.3 | 67.5 | 1.08 | 1.88 | 210 | 0.51 | 1.53 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 15% | 24.6 | 34.8 | 45.0 | 1.68 | 6.79 | 94 | 0.44 | 1.38 |
| 15-30 | 100 | 32% | 28.4 | 38.5 | 47.8 | 1.39 | 2.72 | 68 | 0.47 | 1.46 |
| 30-60 | 100 | 56% | 16.2 | 22.5 | 27.5 | 3.16 | 2.40 | 22 | 0.53 | 1.32 |

### mvimgnet: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| key | 150 | 19% | 8.8 | 16.3 | 26.1 | 9.68 | 14.09 | 76 | 0.50 | 1.40 |
| watch | 150 | 11% | 23.3 | 41.1 | 54.9 | 2.93 | 3.30 | 116 | 0.55 | 2.72 |

### mvimgnet: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 2% | 19.2 | 34.7 | 48.3 | 2.59 | 7.07 | 132 | 0.50 | 2.06 |
| 15-30 | 100 | 10% | 19.5 | 33.5 | 46.8 | 4.95 | 5.01 | 98 | 0.55 | 2.08 |
| 30-60 | 100 | 34% | 9.9 | 18.3 | 26.7 | 10.84 | 7.06 | 52 | 0.57 | 2.05 |
