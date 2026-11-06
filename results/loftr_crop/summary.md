# Results: loftr_crop

Config: `{"matcher": "loftr", "crop": true, "model": "auto", "max_side": 800, "masks": true, "datasets": ["tum", "objectron", "co3d"], "per_bin": {"tum": 20, "objectron": 3, "co3d": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 9% | 44.0 | 61.4 | 73.9 | 0.70 | 2.08 | 1759 | 0.38 | 4.94 |
| objectron | 270 | 5% | 43.6 | 59.2 | 70.2 | 1.12 | 1.97 | 1474 | 0.82 | 6.21 |
| co3d | 300 | 12% | 17.7 | 27.8 | 38.4 | 4.82 | 9.57 | 232 | 0.56 | 4.92 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 20% | 37.1 | 51.0 | 60.1 | 0.79 | 2.51 | 983 | 0.30 | 3.32 |
| flat_near | 60 | 27% | 43.4 | 55.4 | 62.6 | 0.62 | 1.50 | 1337 | 0.30 | 4.54 |
| struct_far | 40 | 0% | 57.6 | 76.9 | 88.6 | 0.57 | 1.76 | 2821 | 0.33 | 5.73 |
| struct_near | 60 | 0% | 41.2 | 62.3 | 80.0 | 0.80 | 2.70 | 2048 | 0.41 | 5.32 |
| checkerboard | 40 | 0% | 43.1 | 62.6 | 77.2 | 0.83 | 2.89 | 1280 | 0.50 | 5.02 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 4% | 44.7 | 64.5 | 78.4 | 0.62 | 2.26 | 2298 | 0.32 | 4.76 |
| 15-30 | 80 | 4% | 53.0 | 69.9 | 80.9 | 0.69 | 1.83 | 1792 | 0.42 | 5.21 |
| 30-60 | 40 | 32% | 26.5 | 38.6 | 50.4 | 1.40 | 3.29 | 1138 | 0.49 | 4.88 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 7% | 43.6 | 59.4 | 69.7 | 1.07 | 2.01 | 1553 | 0.77 | 6.95 |
| laptop | 90 | 9% | 23.3 | 38.8 | 53.6 | 2.07 | 4.76 | 496 | 0.92 | 5.97 |
| cereal_box | 90 | 0% | 65.1 | 80.2 | 88.3 | 0.63 | 1.18 | 2044 | 0.72 | 5.72 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 0% | 45.4 | 63.7 | 76.7 | 0.62 | 2.28 | 2048 | 0.68 | 6.44 |
| 15-30 | 90 | 1% | 47.3 | 63.3 | 75.3 | 1.14 | 1.99 | 1437 | 0.83 | 6.21 |
| 30-60 | 90 | 14% | 39.2 | 51.4 | 59.5 | 1.55 | 1.67 | 1008 | 0.94 | 6.00 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 18% | 2.3 | 6.0 | 14.2 | 11.37 | 27.96 | 134 | 0.55 | 2.33 |
| handbag | 150 | 5% | 33.4 | 49.8 | 63.0 | 1.76 | 2.70 | 716 | 0.59 | 7.51 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 20.8 | 32.4 | 46.4 | 2.28 | 9.49 | 446 | 0.53 | 5.09 |
| 15-30 | 100 | 6% | 23.1 | 34.0 | 44.0 | 5.29 | 6.29 | 242 | 0.57 | 4.84 |
| 30-60 | 100 | 29% | 10.1 | 17.8 | 25.9 | 13.02 | 14.76 | 100 | 0.60 | 4.83 |
