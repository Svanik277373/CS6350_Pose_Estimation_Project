# Run time on CPU (same pairs, one session)

24 random test pairs from all datasets; images already in memory; first call per method (model loading) excluded.

| method | median s/pair | mean s/pair |
|---|---|---|
| sift | 0.13 | 0.28 |
| xfeat | 0.26 | 0.34 |
| xfeat_lg | 0.56 | 0.61 |
| aliked_lg | 1.76 | 1.74 |
| disk_lg | 4.70 | 4.37 |
| loftr | 5.82 | 6.64 |
| mast3r | 23.66 | 23.56 |
| shape | 0.34 | 0.37 |
| cascade fast | 0.80 | 0.83 |
| cascade accurate | 1.14 | 3.03 |

CPU threads available: 22.
