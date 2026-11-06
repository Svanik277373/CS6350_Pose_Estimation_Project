# Object only vs with surroundings (labelled comparison)

Object only = matches restricted to the object mask (the task). With surroundings = whole image.
The objects here are static in a static scene, so background matches follow the same camera motion.
AUC@10 (%), test split.

| method | input | tum | objectron | co3d | mvimgnet |
|---|---|---|---|---|---|
| ALIKED+LG | object only | 64.7 | 57.8 | 32.1 | 33.5 |
| ALIKED+LG | with surroundings | 64.7 | 77.1 | 72.0 | 74.9 |
| SIFT | object only | 65.8 | 50.7 | 18.1 | 8.5 |
| SIFT | with surroundings | 65.8 | 63.4 | 45.8 | 44.8 |
