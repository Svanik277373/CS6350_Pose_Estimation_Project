# Results: shape_xfeat

Config: `{"matcher": "xfeat", "crop": false, "shape": true, "model": "auto", "max_side": 800, "masks": true, "datasets": ["co3d"], "per_bin": {"tum": 20, "objectron": 3, "co3d": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| co3d | 300 | 59% | 2.9 | 8.5 | 15.5 | 5.14 | 11.62 | 0 | 2.92 | 0.53 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 29% | 5.8 | 16.8 | 29.8 | 4.38 | 9.12 | 96 | 2.47 | 0.46 |
| handbag | 150 | 88% | 0.0 | 0.4 | 1.4 | 11.58 | 39.50 | 0 | 9.23 | 0.60 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 56% | 2.9 | 7.2 | 13.3 | 5.20 | 19.31 | 0 | 2.47 | 0.56 |
| 15-30 | 100 | 56% | 3.5 | 8.6 | 16.8 | 4.93 | 11.79 | 0 | 2.99 | 0.52 |
| 30-60 | 100 | 64% | 3.2 | 10.5 | 17.4 | 5.57 | 6.49 | 0 | 3.34 | 0.51 |
