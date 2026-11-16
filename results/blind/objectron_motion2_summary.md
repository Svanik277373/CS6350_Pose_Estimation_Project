# Blind evaluation on objectron (15 test pairs, MASt3R pose)

| version | AUC@5 / @10 / @20 | median rot err (deg) | median t-dir err (deg) | failed |
|---|---|---|---|---|
| A benchmark (dataset K, dataset region) | 71.0 / 84.8 / 92.4 | 0.72 | 0.99 | 0% |
| B estimated focal, dataset region | 67.3 / 80.3 / 91.0 | 1.11 | 1.09 | 0% |

| D estimated focal + automatic region, no name | 62.5 / 80.4 / 90.2 | 0.73 | 1.18 | 0% |

D used the whole images on 12 of 15 pairs (no separate object).
Focal estimate (MASt3R, pair-averaged) vs dataset focal: median error -1.3%, median |error| 3.2%, range -15.7% .. +4.2%.
Object found in both images: 0 of 15 pairs.

Per sequence (median pose error, deg):

| object | pairs | f error | A | B | C | D |
|---|---|---|---|---|---|---|
| book | 5 | -4.1% | 0.99 | 1.56 | inf | 1.35 |
| cereal_box | 5 | -1.4% | 1.11 | 1.18 | inf | 1.01 |
| laptop | 5 | +2.3% | 1.30 | 1.21 | inf | 1.59 |
