# Live tracker replay: mvimgnet/watch/seq08, xfeat_lg

30 frames after the reference (every 1th from 0); pose of each frame relative to the first, error vs ground truth.

Pose error = max(rotation error, translation-direction error). With almost no camera motion (first frames) the translation direction is undefined, so the rotation error is shown separately.

| ground-truth rotation | frames | AUC@10 | median pose error (deg) | median rotation error (deg) | within 10 deg | median ms |
|---|---|---|---|---|---|---|
| 0-5 deg | 1 | 93.6 | 1.29 | 0.22 | 100% | 2458 |
| 5-15 deg | 2 | 0.0 | 121.91 | 11.30 | 0% | 290 |
| 15-30 deg | 2 | 0.0 | 84.34 | 48.26 | 0% | 275 |
| 30-60 deg | 5 | 0.0 | inf | inf | 0% | 297 |
| 60-180 deg | 20 | 0.0 | inf | inf | 0% | 325 |

Whole frame searched (object lost) on 70% of frames.
Video: replay_mvimgnet_watch_seq08_xfeat_lg.mp4
