# Homography (planar) vs essential matrix (3D) vs GRIC choice

Same matches, only the geometric model changes. AUC@10 (%), test split.

## aliked_lg

| model | flat_far | flat_near | struct_far | struct_near | checkerboard | book | laptop | cereal_box | cellphone | handbag | key | watch | all |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H | 55.5 | 62.9 | 82.3 | 52.6 | 28.9 | 54.9 | 31.1 | 79.1 | 5.8 | 26.1 | 3.0 | 5.6 | 29.9 |
| E | 18.6 | 56.4 | 82.0 | 63.0 | 60.4 | 61.6 | 33.4 | 80.6 | 8.0 | 56.8 | 21.8 | 45.6 | 44.3 |
| GRIC | 55.5 | 60.7 | 82.0 | 60.6 | 61.9 | 60.4 | 32.4 | 81.8 | 8.0 | 56.5 | 21.8 | 45.6 | 44.9 |

GRIC chose H for 16.5% of the pairs it solved.

## xfeat_lg

| model | flat_far | flat_near | struct_far | struct_near | checkerboard | book | laptop | cereal_box | cellphone | handbag | key | watch | all |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H | 52.1 | 84.2 | 68.3 | 61.5 | 27.1 | 53.8 | 31.9 | 79.8 | 8.1 | 20.0 | 4.1 | 9.1 | 30.5 |
| E | 41.3 | 77.3 | 81.3 | 64.5 | 58.8 | 62.4 | 27.3 | 86.0 | 9.7 | 54.8 | 16.6 | 40.4 | 44.0 |
| GRIC | 41.3 | 77.6 | 81.3 | 64.5 | 58.8 | 62.4 | 27.3 | 86.0 | 9.7 | 54.8 | 16.6 | 40.4 | 44.0 |

GRIC chose H for 0.9% of the pairs it solved.

