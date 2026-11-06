# Results: mast3r_crop

Config: `{"matcher": "mast3r", "crop": true, "cascade": null, "shape": false, "model": "auto", "max_side": 800, "min_side": 0, "gric_sigma": "fixed", "masks": true, "refine": true, "datasets": ["tum", "objectron", "co3d", "mvimgnet"], "cached": true, "seconds_from": null, "planar_twin": true, "per_bin": {"tum": 20, "objectron": 3, "co3d": 5, "mvimgnet": 5}, "seed": 0}`

AUC = area under the share-of-pairs-solved curve up to 5/10/20 deg of pose error (max of rotation and translation-direction error), in %. Failed pairs count as infinite error. Medians are over successful pairs only.

### Per dataset

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 220 | 0% | 60.8 | 77.4 | 87.5 | 0.54 | 1.49 | 2090 | 0.20 | 42.36 |
| objectron | 270 | 0% | 65.1 | 80.4 | 89.4 | 0.62 | 1.24 | 1140 | 0.54 | 34.81 |
| co3d | 300 | 0% | 46.3 | 66.4 | 80.6 | 1.34 | 1.74 | 848 | 0.26 | 48.14 |
| mvimgnet | 300 | 2% | 41.9 | 63.1 | 77.3 | 1.86 | 1.95 | 947 | 0.29 | 47.97 |

### Per dataset, test split only (pairs never used for tuning)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| tum | 142 | 0% | 60.2 | 76.8 | 86.9 | 0.55 | 1.55 | 2109 | 0.20 | 42.80 |
| objectron | 189 | 0% | 66.3 | 81.5 | 90.2 | 0.60 | 1.23 | 1131 | 0.54 | 35.57 |
| co3d | 210 | 0% | 47.4 | 67.8 | 82.2 | 1.33 | 1.56 | 898 | 0.26 | 52.01 |
| mvimgnet | 210 | 1% | 44.1 | 65.9 | 79.8 | 1.86 | 1.79 | 939 | 0.28 | 44.28 |

### tum: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| flat_far | 20 | 0% | 57.4 | 75.8 | 85.4 | 0.65 | 2.11 | 1212 | 0.21 | 73.42 |
| flat_near | 60 | 0% | 75.7 | 87.8 | 93.9 | 0.55 | 1.11 | 1964 | 0.19 | 43.54 |
| struct_far | 40 | 0% | 71.8 | 85.2 | 92.6 | 0.42 | 1.15 | 2386 | 0.20 | 30.54 |
| struct_near | 60 | 0% | 49.9 | 70.7 | 83.8 | 0.64 | 2.18 | 2212 | 0.20 | 35.38 |
| checkerboard | 40 | 0% | 49.9 | 68.2 | 81.5 | 0.58 | 2.10 | 2009 | 0.24 | 47.35 |

### tum: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 54.9 | 73.5 | 85.6 | 0.53 | 1.88 | 2046 | 0.20 | 49.16 |
| 15-30 | 80 | 0% | 67.3 | 81.7 | 90.0 | 0.50 | 1.42 | 2204 | 0.20 | 35.40 |
| 30-60 | 40 | 0% | 65.1 | 79.9 | 88.9 | 0.74 | 1.28 | 1916 | 0.19 | 39.28 |

### objectron: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| book | 90 | 0% | 66.0 | 81.8 | 90.7 | 0.61 | 1.02 | 1084 | 0.54 | 32.49 |
| laptop | 90 | 1% | 57.5 | 75.3 | 86.4 | 0.84 | 1.56 | 1034 | 0.63 | 34.89 |
| cereal_box | 90 | 0% | 72.9 | 85.1 | 91.9 | 0.55 | 0.96 | 1260 | 0.51 | 37.07 |

### objectron: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 90 | 0% | 58.9 | 76.0 | 87.6 | 0.42 | 1.64 | 1174 | 0.52 | 32.90 |
| 15-30 | 90 | 0% | 70.1 | 84.3 | 92.0 | 0.65 | 1.22 | 1140 | 0.53 | 35.17 |
| 30-60 | 90 | 1% | 67.5 | 81.9 | 89.3 | 0.93 | 0.98 | 1088 | 0.59 | 36.38 |

### co3d: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| cellphone | 150 | 1% | 32.7 | 55.5 | 73.4 | 1.63 | 2.71 | 672 | 0.21 | 38.24 |
| handbag | 150 | 0% | 60.1 | 77.6 | 88.2 | 1.18 | 1.16 | 1062 | 0.34 | 58.03 |

### co3d: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 0% | 36.6 | 58.4 | 75.2 | 1.18 | 2.92 | 910 | 0.25 | 45.39 |
| 15-30 | 100 | 0% | 51.0 | 70.6 | 83.9 | 1.33 | 1.49 | 848 | 0.24 | 48.23 |
| 30-60 | 100 | 1% | 52.1 | 71.1 | 83.6 | 1.86 | 1.19 | 795 | 0.30 | 50.78 |

### mvimgnet: per object

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| key | 150 | 3% | 29.9 | 50.4 | 67.1 | 2.79 | 2.89 | 560 | 0.25 | 52.43 |
| watch | 150 | 0% | 54.2 | 76.0 | 87.6 | 1.40 | 1.41 | 1226 | 0.33 | 43.51 |

### mvimgnet: per viewpoint change (deg)

| group | pairs | failed | AUC@5 | AUC@10 | AUC@20 | median rot err (deg) | median t-dir err (deg) | median matches | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-15 | 100 | 2% | 39.6 | 62.0 | 77.2 | 1.38 | 2.59 | 1048 | 0.24 | 46.61 |
| 15-30 | 100 | 3% | 46.1 | 67.0 | 79.2 | 1.97 | 1.79 | 932 | 0.28 | 47.33 |
| 30-60 | 100 | 0% | 40.9 | 61.0 | 76.3 | 2.64 | 1.61 | 870 | 0.38 | 49.97 |
