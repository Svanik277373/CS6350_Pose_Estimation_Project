# Overview: relative pose of the object, test split

AUC@10 (%): area under the share-of-pairs-solved curve up to 10 deg of pose error (max of rotation and translation-direction error); failed pairs count as infinite error. Object only (matches restricted to the object's region). Medians over solved pairs, all datasets. Seconds = median wall time per pair on this laptop's CPU (runs were timed under different loads; see experiments/timing.md for a fair comparison).

| method | kind | TUM | Objectron | CO3D | MVImgNet | mean | failed | median rot (deg) | median t-dir (deg) | median reproj (px) | s/pair |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SIFT | classical | 65.8 | 50.7 | 18.1 | 8.5 | 35.8 | 40% | 1.22 | 2.62 | 0.42 | 0.1 |
| XFeat | learned sparse | 54.3 | 57.7 | 22.3 | 17.8 | 38.0 | 5% | 2.72 | 6.74 | 0.61 | 0.3 |
| XFeat+LightGlue | learned sparse | 67.2 | 58.2 | 32.0 | 28.3 | 46.4 | 8% | 1.82 | 3.40 | 0.60 | 0.5 |
| ALIKED+LightGlue | learned sparse | 64.7 | 57.8 | 32.1 | 33.5 | 47.0 | 18% | 1.27 | 2.57 | 0.49 | 2.0 |
| DISK+LightGlue | learned sparse | 68.9 | 59.5 | 28.1 | 21.0 | 44.3 | 21% | 1.20 | 2.80 | 0.55 | 4.6 |
| LoFTR | learned dense | 67.1 | 65.2 | 33.1 | 24.4 | 47.5 | 9% | 1.41 | 3.12 | 0.55 | 5.4 |
| shape (mask outline) | silhouette | 0.0 | 14.9 | 8.6 | 0.0 | 5.9 | 72% | 5.47 | 14.68 | 5.61 | 0.3 |
| MASt3R | 3D foundation model | 76.8 | 81.5 | 67.8 | 65.9 | 73.0 | 0% | 0.90 | 1.49 | 0.29 | 20.2 |
| cascade: fast | preset | 67.8 | 60.9 | 35.5 | 28.3 | 48.1 | 4% | 1.86 | 3.61 | 0.61 | 0.7 |
| cascade: accurate | preset | 68.1 | 63.0 | 38.6 | 30.2 | 50.0 | 3% | 1.78 | 3.37 | 0.63 | 0.9 |
| cascade: confident | preset | 70.5 | 77.2 | 57.4 | 51.1 | 64.0 | 0% | 1.21 | 1.91 | 0.57 | 0.8 |

\* mean over the datasets this method was run on.

## AUC@5 / @10 / @20 per dataset

| method | TUM | Objectron | CO3D | MVImgNet |
|---|---|---|---|---|
| SIFT | 50.3 / 65.8 / 77.0 | 37.9 / 50.7 / 60.5 | 12.1 / 18.1 / 22.7 | 4.2 / 8.5 / 13.2 |
| XFeat | 36.6 / 54.3 / 69.9 | 43.3 / 57.7 / 67.9 | 13.5 / 22.3 / 33.4 | 9.5 / 17.8 / 28.5 |
| XFeat+LightGlue | 49.7 / 67.2 / 79.2 | 44.9 / 58.2 / 67.9 | 21.5 / 32.0 / 42.7 | 16.1 / 28.3 / 40.3 |
| ALIKED+LightGlue | 47.6 / 64.7 / 76.5 | 44.2 / 57.8 / 67.1 | 22.6 / 32.1 / 39.9 | 19.0 / 33.5 / 46.6 |
| DISK+LightGlue | 52.5 / 68.9 / 80.0 | 46.8 / 59.5 / 66.9 | 21.2 / 28.1 / 34.2 | 10.9 / 21.0 / 31.2 |
| LoFTR | 51.7 / 67.1 / 76.8 | 50.9 / 65.2 / 74.6 | 24.1 / 33.1 / 43.1 | 13.9 / 24.4 / 35.1 |
| shape (mask outline) | 0.0 / 0.0 / 0.0 | 10.4 / 14.9 / 22.8 | 2.9 / 8.6 / 16.0 | 0.0 / 0.0 / 0.0 |
| MASt3R | 60.2 / 76.8 / 86.9 | 66.3 / 81.5 / 90.2 | 47.4 / 67.8 / 82.2 | 44.1 / 65.9 / 79.8 |
| cascade: fast | 50.3 / 67.8 / 79.9 | 47.2 / 60.9 / 71.1 | 22.5 / 35.5 / 47.9 | 16.1 / 28.3 / 40.3 |
| cascade: accurate | 50.3 / 68.1 / 80.7 | 49.0 / 63.0 / 72.8 | 24.2 / 38.6 / 53.1 | 17.2 / 30.2 / 43.1 |
| cascade: confident | 52.3 / 70.5 / 83.3 | 61.6 / 77.2 / 87.5 | 38.1 / 57.4 / 72.2 | 31.7 / 51.1 / 66.5 |

Test pairs: TUM 142, Objectron 189, CO3D 210, MVImgNet 210.
