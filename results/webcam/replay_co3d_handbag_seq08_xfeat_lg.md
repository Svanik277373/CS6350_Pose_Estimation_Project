# Live tracker replay: co3d/handbag/seq08, xfeat_lg

39 frames after the reference (every 1th from 0); pose of each frame relative to the first, error vs ground truth.

Pose error = max(rotation error, translation-direction error). With almost no camera motion (first frames) the translation direction is undefined, so the rotation error is shown separately.

| ground-truth rotation | frames | AUC@10 | median pose error (deg) | median rotation error (deg) | within 10 deg | median ms |
|---|---|---|---|---|---|---|
| 0-5 deg | 7 | 13.0 | 21.19 | 0.55 | 29% | 730 |
| 5-15 deg | 4 | 22.2 | 9.59 | 0.93 | 50% | 649 |
| 15-30 deg | 9 | 79.4 | 2.04 | 0.57 | 100% | 590 |
| 30-60 deg | 15 | 50.3 | 4.06 | 4.06 | 67% | 632 |
| 60-180 deg | 4 | 0.0 | 79.12 | 66.75 | 0% | 704 |

Whole frame searched (object lost) on 0% of frames.
Video: replay_co3d_handbag_seq08_xfeat_lg.mp4
