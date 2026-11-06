# Metric scale: length of the translation (test split, metric datasets)

ratio = estimated |t| / true |t|. 'median error' = typical factor off, as a percentage.

| method | dataset | pairs | median error | within 10% | within 25% | within 2x |
|---|---|---|---|---|---|---|
| MASt3R depth (raw) | tum | 30 | 66.6% | 20% | 33% | 90% |
| MASt3R depth (focal-corrected) | tum | 30 | 52.2% | 27% | 37% | 97% |
| size prior (mask outline) | objectron | 189 | 27.8% | 26% | 40% | 69% |
| size prior (matched points) | objectron | 189 | 17.9% | 20% | 59% | 76% |
| MASt3R depth (raw) | objectron | 30 | 198.3% | 0% | 0% | 10% |
| MASt3R depth (focal-corrected) | objectron | 30 | 217.5% | 0% | 0% | 7% |

Size prior per object (Objectron). Median ratio > 1: scale too large (extent measured too short).

| method | object | pairs | median ratio | median error | within 10% | within 25% |
|---|---|---|---|---|---|---|
| size prior (mask outline) | book | 63 | 0.78 | 29.0% | 25% | 43% |
| size prior (mask outline) | cereal_box | 63 | 0.92 | 9.1% | 51% | 75% |
| size prior (mask outline) | laptop | 63 | 0.43 | 153.4% | 2% | 3% |
| size prior (matched points) | book | 63 | 1.07 | 19.6% | 32% | 67% |
| size prior (matched points) | cereal_box | 63 | 1.17 | 17.8% | 13% | 70% |
| size prior (matched points) | laptop | 63 | 1.04 | 17.2% | 16% | 40% |

Objectron's masks are the projected 3D box, not the object's silhouette: for an open laptop the box hull is much larger than the laptop, so the outline method measures too long an extent. With true silhouettes (CO3D, MVImgNet, a phone held up to a webcam) the outline would not have this bias; run.py uses the matched points.
