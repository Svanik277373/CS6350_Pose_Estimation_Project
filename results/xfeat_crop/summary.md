# Results: xfeat_crop

Config: `{"matcher": "xfeat", "crop": true, "model": "auto", "max_side": 800, "masks": true, "datasets": ["tum", "objectron", "co3d"], "per_bin": {"tum": 20, "objectron": 3, "co3d": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 1% | 26.6 | 46.0 | 63.9 | 1.22 | 4.21 | 884 | 0.55 | 0.19 |
| objectron | 270 | 5% | 32.1 | 48.9 | 61.2 | 1.91 | 3.19 | 574 | 1.11 | 0.24 |
| co3d | 300 | 9% | 7.3 | 16.5 | 28.8 | 7.60 | 15.33 | 236 | 0.60 | 0.19 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 0% | 9.9 | 17.0 | 30.7 | 9.78 | 16.37 | 759 | 0.57 | 0.29 |
| flat_near | 60 | 3% | 22.7 | 42.5 | 57.1 | 1.60 | 5.15 | 870 | 0.54 | 0.17 |
| struct_far | 40 | 0% | 47.6 | 70.4 | 85.1 | 0.77 | 2.37 | 1176 | 0.51 | 0.18 |
| struct_near | 60 | 0% | 29.5 | 51.3 | 72.9 | 1.22 | 4.06 | 849 | 0.56 | 0.18 |
| checkerboard | 40 | 0% | 20.0 | 38.1 | 59.6 | 0.99 | 6.48 | 694 | 0.58 | 0.20 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 22.8 | 41.6 | 61.4 | 1.10 | 5.67 | 1028 | 0.54 | 0.20 |
| 15-30 | 80 | 0% | 36.2 | 58.7 | 75.5 | 1.11 | 3.18 | 892 | 0.55 | 0.17 |
| 30-60 | 40 | 5% | 19.7 | 34.4 | 49.1 | 4.27 | 7.14 | 664 | 0.58 | 0.22 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 6% | 30.3 | 46.0 | 60.0 | 1.99 | 4.25 | 573 | 1.16 | 0.23 |
| laptop | 90 | 9% | 18.8 | 33.9 | 46.1 | 3.03 | 6.31 | 375 | 1.07 | 0.28 |
| cereal_box | 90 | 1% | 48.4 | 67.7 | 78.7 | 1.10 | 1.77 | 734 | 1.10 | 0.20 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 2% | 31.1 | 47.8 | 61.9 | 1.22 | 3.66 | 696 | 1.03 | 0.21 |
| 15-30 | 90 | 3% | 31.0 | 49.1 | 63.3 | 2.22 | 3.84 | 566 | 1.12 | 0.23 |
| 30-60 | 90 | 10% | 35.3 | 50.7 | 59.5 | 2.52 | 2.07 | 433 | 1.16 | 0.27 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 15% | 0.6 | 4.1 | 13.0 | 11.39 | 33.22 | 130 | 0.57 | 0.16 |
| handbag | 150 | 3% | 14.2 | 29.2 | 44.8 | 5.08 | 7.38 | 443 | 0.67 | 0.22 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 1% | 8.0 | 17.2 | 30.6 | 4.83 | 16.30 | 356 | 0.58 | 0.13 |
| 15-30 | 100 | 4% | 9.7 | 21.4 | 35.4 | 7.91 | 11.43 | 220 | 0.60 | 0.18 |
| 30-60 | 100 | 21% | 4.9 | 11.8 | 21.2 | 22.14 | 31.96 | 166 | 0.64 | 0.26 |
