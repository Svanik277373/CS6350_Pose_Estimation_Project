# MASt3R: gain on data it was trained on (CO3D) vs unseen data

AUC@10 (%), test split. 'best other' = best of the other matchers on that dataset.

| dataset | in MASt3R training? | MASt3R | best other | gain |
|---|---|---|---|---|
| tum | no | 76.8 | 68.9 | +7.9 |
| objectron | no | 81.5 | 65.2 | +16.3 |
| co3d | yes (CO3Dv2) | 67.8 | 33.1 | +34.7 |
| mvimgnet | no | 65.9 | 33.5 | +32.4 |

A much larger gain on CO3D than on the unseen sets would point to memorisation; similar gains mean the advantage is general (dense matching, learned 3D priors).
