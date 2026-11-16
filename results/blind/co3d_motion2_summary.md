# Blind evaluation on co3d (16 test pairs, MASt3R pose)

| version | AUC@5 / @10 / @20 | median rot err (deg) | median t-dir err (deg) | failed |
|---|---|---|---|---|
| A benchmark (dataset K, dataset region) | 50.6 / 67.9 / 80.1 | 1.40 | 1.42 | 0% |
| B estimated focal, dataset region | 40.8 / 61.0 / 77.7 | 1.61 | 2.34 | 0% |

| D estimated focal + automatic region, no name | 63.1 / 74.8 / 81.2 | 0.53 | 1.15 | 0% |

D used the whole images on 11 of 16 pairs (no separate object).
Focal estimate (MASt3R, pair-averaged) vs dataset focal: median error -0.9%, median |error| 3.0%, range -11.1% .. +9.5%.
Object found in both images: 0 of 16 pairs.

Per sequence (median pose error, deg):

| object | pairs | f error | A | B | C | D |
|---|---|---|---|---|---|---|
| cellphone | 8 | +2.4% | 3.66 | 4.49 | inf | 1.15 |
| handbag | 8 | -2.7% | 1.79 | 2.18 | inf | 1.62 |
