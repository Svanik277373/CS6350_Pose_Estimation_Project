# Region rule tuning (tuning split, MASt3R pose, dataset K)

31 pairs, 1 per object x viewpoint bin.

| change_min_area | change_gap | AUC@10 | moved decisions | pairs > 20 deg |
|---|---|---|---|---|
| 0.0 | 0.3 | 65.8 | 22 | 3 |
| 0.005 | 0.3 | 69.9 | 20 | 1 |
| 0.01 | 0.3 | 72.6 | 18 | 1 |
| 0.015 | 0.3 | 72.6 | 18 | 1 |
| 0.02 | 0.3 | 75.5 | 17 | 0 |
| 0.03 | 0.3 | 75.5 | 14 | 0 |
| 0.05 | 0.3 | 75.5 | 13 | 0 |
| 0.0 | 0.4 | 70.4 | 17 | 2 |
| 0.005 | 0.4 | 74.5 | 15 | 0 |
| 0.01 | 0.4 | 77.1 | 13 | 0 |
| 0.015 | 0.4 | 77.1 | 13 | 0 |
| 0.02 | 0.4 | 77.1 | 13 | 0 |
| 0.03 | 0.4 | 77.1 | 11 | 0 |
| 0.05 | 0.4 | 77.1 | 10 | 0 |
| 0.0 | 0.5 | 73.5 | 15 | 2 |
| 0.005 | 0.5 | 77.6 | 13 | 0 |
| 0.01 | 0.5 | 77.6 | 12 | 0 |
| 0.015 | 0.5 | 77.6 | 12 | 0 |
| 0.02 | 0.5 | 77.6 | 12 | 0 |
| 0.03 | 0.5 | 77.6 | 10 | 0 |
| 0.05 | 0.5 | 77.6 | 9 | 0 |

Moved-object photos (no ground truth): decision per rule

| photo | 0.0/0.3 | 0.005/0.3 | 0.01/0.3 | 0.015/0.3 | 0.02/0.3 | 0.03/0.3 | 0.05/0.3 | 0.0/0.4 | 0.005/0.4 | 0.01/0.4 | 0.015/0.4 | 0.02/0.4 | 0.03/0.4 | 0.05/0.4 | 0.0/0.5 | 0.005/0.5 | 0.01/0.5 | 0.015/0.5 | 0.02/0.5 | 0.03/0.5 | 0.05/0.5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| coin | moved 2.7% | moved 2.7% | moved 2.7% | moved 2.7% | moved 2.7% | unconfirmed 2.7% | unconfirmed 2.7% | moved 2.7% | moved 2.7% | moved 2.7% | moved 2.7% | moved 2.7% | unconfirmed 2.7% | unconfirmed 2.7% | moved 2.7% | moved 2.7% | moved 2.7% | moved 2.7% | moved 2.7% | unconfirmed 2.7% | unconfirmed 2.7% |
| key | moved 1.6% | moved 1.6% | moved 1.6% | moved 1.6% | scene | scene | scene | scene | scene | scene | scene | scene | scene | scene | scene | scene | scene | scene | scene | scene | scene |
| wallet | moved 8.5% | moved 8.5% | moved 8.5% | moved 8.5% | moved 8.5% | moved 8.5% | moved 8.5% | moved 8.5% | moved 8.5% | moved 8.5% | moved 8.5% | moved 8.5% | moved 8.5% | moved 8.5% | moved 0.4% | unconfirmed 8.5% | unconfirmed 8.5% | unconfirmed 8.5% | unconfirmed 8.5% | unconfirmed 8.5% | unconfirmed 8.5% |
