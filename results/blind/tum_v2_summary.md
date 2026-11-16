# Blind evaluation on tum (20 test pairs, MASt3R pose)

| version | AUC@5 / @10 / @20 | median rot err (deg) | median t-dir err (deg) | failed |
|---|---|---|---|---|
| A benchmark (dataset K, dataset region) | 59.4 / 76.4 / 85.7 | 0.55 | 1.72 | 0% |
| B estimated focal, dataset region | 51.6 / 71.7 / 83.3 | 0.73 | 2.03 | 0% |

| D estimated focal + automatic region, no name | 38.6 / 58.3 / 74.2 | 0.74 | 3.32 | 5% |

D used the whole images on 11 of 20 pairs (no separate object).
Focal estimate (MASt3R, pair-averaged) vs dataset focal: median error -4.4%, median |error| 4.4%, range -25.2% .. +5.1%.
Object found in both images: 0 of 20 pairs.

Per sequence (median pose error, deg):

| object | pairs | f error | A | B | C | D |
|---|---|---|---|---|---|---|
| checkerboard | 4 | -1.3% | 3.12 | 3.48 | inf | 8.77 |
| flat_far | 4 | -6.7% | 2.42 | 5.01 | inf | 5.01 |
| flat_near | 4 | -4.4% | 0.74 | 1.42 | inf | 1.42 |
| struct_far | 4 | -3.9% | 0.58 | 0.79 | inf | 1.76 |
| struct_near | 4 | -4.2% | 3.80 | 2.52 | inf | 2.52 |
