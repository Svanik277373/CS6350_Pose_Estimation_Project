# Zhang calibration: TUM fr3 checkerboard

262 of 318 sampled frames show the full 9x7 board. Board tilt: median 11 deg, max 25 deg (nearly face-on).

TUM official: fx 535.4, fy 539.2, cx 320.1, cy 247.6, no distortion.

| variant | views | fx | fy | cx | cy | fx vs official | fx bootstrap std | corner RMS (px) |
|---|---|---|---|---|---|---|---|---|
| full model (k1 k2 p1 p2), 40 diverse views | 40 | 683.6 | 688.2 | 302.2 | 237.8 | +27.7% | 209.1 | 0.235 |
| full model (k1 k2 p1 p2), all views | 262 | 581.5 | 585.0 | 302.2 | 246.1 | +8.6% | 41.2 | 0.216 |
| no distortion, all views **(chosen)** | 262 | 547.7 | 551.6 | 313.0 | 256.8 | +2.3% | 31.0 | 0.218 |
| focal only (centre pp, fx=fy, no distortion), all views | 262 | 556.3 | 556.3 | 319.5 | 239.5 | +3.9% | 13.7 | 0.236 |
| focal only, 40 most tilted views | 40 | 565.4 | 565.4 | 319.5 | 239.5 | +5.6% | 16.2 | 0.182 |

Ambiguity check (views not used for calibration):

- K from 40 diverse views (fx 684, +27.7%): corner RMS 0.230 px
- TUM official K (fx 535): corner RMS 0.219 px
- Nearly equal: face-on views cannot tell a long focal length + far board from a short focal length + near board, so a low reprojection error alone does not prove a good K.

Board square size from calibration vs motion capture: 86.6 mm (median of 33670 view pairs; IQR 83.5-87.9 mm).
