# Results: shape_other

Config: `{"matcher": "xfeat", "crop": false, "shape": true, "model": "auto", "max_side": 800, "masks": true, "datasets": ["tum", "objectron"], "per_bin": {"tum": 20, "objectron": 3, "co3d": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 100% | 0.0 | 0.0 | 0.0 | - | - | 0 | - | 0.00 |
| objectron | 270 | 36% | 10.0 | 15.2 | 23.4 | 5.43 | 14.68 | 224 | 10.39 | 0.73 |

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
| book | 90 | 23% | 9.1 | 17.9 | 31.0 | 4.66 | 13.15 | 318 | 8.59 | 0.89 |
| laptop | 90 | 64% | 13.9 | 15.9 | 17.4 | 1.27 | 3.13 | 0 | 4.57 | 0.39 |
| cereal_box | 90 | 20% | 7.9 | 12.4 | 22.7 | 5.95 | 18.61 | 712 | 12.99 | 0.91 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 33% | 10.3 | 15.5 | 23.1 | 3.95 | 17.11 | 405 | 5.49 | 0.77 |
| 15-30 | 90 | 40% | 9.9 | 14.4 | 21.7 | 7.47 | 15.92 | 158 | 12.09 | 0.70 |
| 30-60 | 90 | 34% | 10.9 | 16.6 | 26.3 | 10.11 | 10.75 | 164 | 16.96 | 0.72 |
