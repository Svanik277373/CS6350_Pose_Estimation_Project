# Results: shape_ref

Config: `{"matcher": "xfeat", "crop": false, "cascade": null, "shape": true, "model": "auto", "max_side": 800, "min_side": 0, "gric_sigma": "fixed", "masks": true, "refine": true, "datasets": ["tum", "objectron", "co3d", "mvimgnet"], "per_bin": {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 100% | 0.0 | 0.0 | 0.0 | - | - | 0 | - | 0.00 |
| objectron | 270 | 36% | 10.0 | 15.2 | 23.4 | 5.43 | 14.68 | 224 | 10.39 | 1.05 |
| co3d | 300 | 59% | 2.9 | 8.5 | 15.5 | 5.14 | 11.62 | 0 | 2.92 | 0.31 |
| mvimgnet | 300 | 100% | 0.0 | 0.0 | 0.0 | 109.67 | 86.39 | 0 | 11.07 | 0.48 |

### Per dataset, test split only (pairs never used for tuning)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 142 | 100% | 0.0 | 0.0 | 0.0 | - | - | 0 | - | 0.00 |
| objectron | 189 | 34% | 10.4 | 14.9 | 22.8 | 5.82 | 15.61 | 223 | 11.94 | 1.20 |
| co3d | 210 | 58% | 2.9 | 8.6 | 16.0 | 5.20 | 11.74 | 0 | 2.97 | 0.30 |
| mvimgnet | 210 | 100% | 0.0 | 0.0 | 0.0 | - | - | 0 | - | 0.52 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 100% | 0.0 | 0.0 | 0.0 | - | - | 0 | - | 0.00 |
| flat_near | 60 | 100% | 0.0 | 0.0 | 0.0 | - | - | 0 | - | 0.00 |
| struct_far | 40 | 100% | 0.0 | 0.0 | 0.0 | - | - | 0 | - | 0.00 |
| struct_near | 60 | 100% | 0.0 | 0.0 | 0.0 | - | - | 0 | - | 0.00 |
| checkerboard | 40 | 100% | 0.0 | 0.0 | 0.0 | - | - | 0 | - | 0.00 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 100% | 0.0 | 0.0 | 0.0 | - | - | 0 | - | 0.00 |
| 15-30 | 80 | 100% | 0.0 | 0.0 | 0.0 | - | - | 0 | - | 0.00 |
| 30-60 | 40 | 100% | 0.0 | 0.0 | 0.0 | - | - | 0 | - | 0.00 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 23% | 9.1 | 17.9 | 31.0 | 4.66 | 13.15 | 318 | 8.59 | 0.93 |
| laptop | 90 | 64% | 13.9 | 15.9 | 17.4 | 1.27 | 3.13 | 0 | 4.57 | 0.43 |
| cereal_box | 90 | 20% | 7.9 | 12.4 | 22.7 | 5.95 | 18.61 | 712 | 12.99 | 1.81 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 33% | 10.3 | 15.5 | 23.1 | 3.95 | 17.11 | 405 | 5.49 | 1.09 |
| 15-30 | 90 | 40% | 9.9 | 14.4 | 21.7 | 7.47 | 15.92 | 158 | 12.09 | 1.00 |
| 30-60 | 90 | 34% | 10.9 | 16.6 | 26.3 | 10.11 | 10.75 | 164 | 16.96 | 1.07 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 29% | 5.8 | 16.8 | 29.8 | 4.38 | 9.12 | 96 | 2.47 | 0.29 |
| handbag | 150 | 88% | 0.0 | 0.4 | 1.4 | 11.58 | 39.50 | 0 | 9.23 | 0.33 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 56% | 2.9 | 7.2 | 13.3 | 5.20 | 19.31 | 0 | 2.47 | 0.32 |
| 15-30 | 100 | 56% | 3.5 | 8.6 | 16.8 | 4.93 | 11.79 | 0 | 2.99 | 0.31 |
| 30-60 | 100 | 64% | 3.2 | 10.5 | 17.4 | 5.57 | 6.49 | 0 | 3.34 | 0.30 |

### mvimgnet: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| key | 150 | 100% | 0.0 | 0.0 | 0.0 | - | - | 0 | - | 0.38 |
| watch | 150 | 99% | 0.0 | 0.0 | 0.0 | 109.67 | 86.39 | 0 | 11.07 | 0.58 |

### mvimgnet: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 100% | 0.0 | 0.0 | 0.0 | - | - | 0 | - | 0.47 |
| 15-30 | 100 | 99% | 0.0 | 0.0 | 0.0 | 109.67 | 86.39 | 0 | 11.07 | 0.49 |
| 30-60 | 100 | 100% | 0.0 | 0.0 | 0.0 | - | - | 0 | - | 0.48 |
