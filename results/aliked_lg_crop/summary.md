# Results: aliked_lg_crop

Config: `{"matcher": "aliked_lg", "crop": true, "model": "auto", "max_side": 800, "masks": true, "datasets": ["tum", "objectron", "co3d"], "per_bin": {"tum": 20, "objectron": 3, "co3d": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 7% | 48.7 | 65.4 | 77.2 | 0.61 | 1.81 | 262 | 0.30 | 1.00 |
| objectron | 270 | 14% | 41.4 | 55.0 | 64.5 | 1.08 | 1.82 | 340 | 0.63 | 1.47 |
| co3d | 300 | 36% | 20.0 | 29.9 | 38.3 | 2.36 | 3.88 | 56 | 0.50 | 0.94 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 20% | 42.5 | 58.0 | 66.5 | 0.66 | 2.03 | 138 | 0.27 | 0.96 |
| flat_near | 60 | 18% | 48.9 | 63.7 | 71.9 | 0.66 | 1.56 | 332 | 0.27 | 1.14 |
| struct_far | 40 | 0% | 68.4 | 82.8 | 91.5 | 0.44 | 1.20 | 415 | 0.24 | 1.03 |
| struct_near | 60 | 2% | 46.0 | 64.3 | 78.0 | 0.63 | 2.01 | 238 | 0.34 | 0.89 |
| checkerboard | 40 | 0% | 40.5 | 60.3 | 77.7 | 0.67 | 2.54 | 178 | 0.43 | 0.94 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 4% | 46.3 | 64.5 | 78.4 | 0.56 | 2.09 | 299 | 0.28 | 0.98 |
| 15-30 | 80 | 4% | 56.6 | 74.2 | 84.5 | 0.64 | 1.74 | 262 | 0.33 | 1.00 |
| 30-60 | 40 | 22% | 41.5 | 52.4 | 61.2 | 0.68 | 1.62 | 192 | 0.37 | 1.03 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 7% | 39.0 | 54.9 | 66.6 | 1.14 | 2.34 | 314 | 0.66 | 1.32 |
| laptop | 90 | 36% | 22.6 | 33.7 | 42.5 | 1.91 | 3.07 | 164 | 0.63 | 1.59 |
| cereal_box | 90 | 0% | 63.5 | 77.3 | 85.2 | 0.75 | 1.20 | 464 | 0.62 | 1.49 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 10% | 41.5 | 56.8 | 68.7 | 0.69 | 2.21 | 414 | 0.53 | 1.45 |
| 15-30 | 90 | 14% | 44.0 | 57.3 | 66.5 | 1.21 | 1.75 | 350 | 0.62 | 1.46 |
| 30-60 | 90 | 18% | 39.6 | 51.7 | 59.0 | 1.60 | 1.68 | 311 | 0.83 | 1.49 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 60% | 2.7 | 6.9 | 12.0 | 5.21 | 17.03 | 20 | 0.46 | 0.54 |
| handbag | 150 | 11% | 37.7 | 53.3 | 64.9 | 1.22 | 2.32 | 210 | 0.51 | 1.33 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 19% | 22.2 | 33.6 | 44.0 | 1.55 | 6.23 | 94 | 0.48 | 0.91 |
| 15-30 | 100 | 32% | 25.1 | 35.9 | 44.9 | 1.99 | 2.85 | 68 | 0.50 | 0.97 |
| 30-60 | 100 | 56% | 13.6 | 21.1 | 26.9 | 4.57 | 3.12 | 22 | 0.58 | 0.93 |
