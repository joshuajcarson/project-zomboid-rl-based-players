# B5 M2 calibration: bite-damage sweep on the fake
- Date / time: 2026-10-30, started ~16:35 CT
- Milestone: M2 (fake-vs-real fidelity for the solo fight)
- Question: can the fake's bite damage (the server-side rule `biteDamage`, hit points per adjacent zombie per game second; default 1.5) be scaled so that the scripted fighter's kills and damage match the real baseline (kills 1.36, damage 39.2)? Which value?
- Hypothesis: a bite scale of about 3-4.5 (2-3x the default) brings damage to ~39 and kills to ~1.4 (more damage means earlier deaths and fewer kills).

## Pre-registered (fixed before running; never edited afterwards)
- Design: ONE fake session, 80 episodes of `charge:1.8:0` requested, fight-v4 field, seed 7, 4x clock, force-kill fix ON (default since Batch 4). Arms alternate by episode (`PZ_BITE_ARMS=1.5,3.0,4.5,6.0`; episode i uses arm i mod 4): bite damage 1.5 (default), 3.0, 4.5, 6.0. Target >= 18 real episodes per arm (real = steps >= 5). Analysis: `python scripts/compare_arms.py <file> --by bite`.
- Real target (Batch 1 pooled n=69): kills 1.36, damage 39.2; M2 bands: kills 1.06-1.66, damage 29.2-49.2.
- SUCCESS if: at least one arm has BOTH mean kills inside 1.06-1.66 AND mean damage inside 29.2-49.2. (A calibration point exists; the confirming M2 batch of >= 60 episodes over >= 2 sessions follows.)
- FAILURE if: no arm reaches mean damage >= 29.2, OR every arm that reaches damage >= 29.2 has mean kills < 1.06 (the bite scale cannot match both metrics; another knob is needed).
- INCONCLUSIVE if: neither (for example, the best arm misses one band by under 0.15 on kills or 3 on damage, or the arm means are not monotone in bite scale so no value can be picked).
- Stopping rule: run all 80 episodes; stop early only for an invalid run (server crash, fake client not connecting).
- Also report: monotonicity of damage and kills in bite scale; share of deaths (damage >= 80) per arm vs real (S1 26%, S2 8%); shape (median vs mean).

## Result (filled at batch end, 2026-10-30 16:40 CT)
- Data: `results/experiments-2026-10-30/b5_m2_bite_sweep.jsonl` (80 episodes, 20 per arm, all real); `python scripts/compare_arms.py <file> --by bite`.
- Numbers (fake, force-kill fix on, charge:1.8:0; real target kills 1.36 / damage 39.2):
  | bite | kills (se) | damage (se) | median dmg | deaths >= 80 | stuck | in kills band | in damage band |
  |---|---|---|---|---|---|---|---|
  | 1.5 | 2.00 (0.00) | 11.6 (1.5) | 12.0 | 0 | 0 | no | no |
  | 3.0 | 1.85 (0.08) | 30.6 (2.9) | 29.5 | 0 | 3 | no | yes (just) |
  | 4.5 | 1.90 (0.10) | 41.9 (6.0) | 35.8 | 2 | 0 | no | yes |
  | 6.0 | 1.65 (0.13) | 40.8 (7.4) | 36.9 | 4 | 2 | yes (edge: 1.65 vs 1.66) | yes |
- Verdict: **SUCCESS** against the pre-registered criteria (one arm, bite 6.0, has both metrics in the M2 bands), marginal: its kills mean sits at the band edge with se 0.13, and its damage matches the real mean of 39.2 well (40.8).
- Unexpected learnings:
  1. Damage rises with the bite scale but saturates near 40 (4.5: 41.9, 6.0: 40.8): the character dies sooner (deaths 0 -> 2 -> 4 of 20), which ends episodes. Kills barely move until deaths appear (2.00, 1.85, 1.90, 1.65): fake kills are driven by deaths and stalls, not by hit points lost.
  2. At bite 6.0 the fake death share is 4 of 20 (20%), close to the real 11 of 69 (16%; S1 26%, S2 8%), and its damage median (36.9) is above the real medians (22-30): the fake's damage distribution is narrower (fewer very clean fights) than the real client's, which is bimodal.
  3. The knob matters far more for damage than for kills: a single scale cannot be tuned independently for both; the pass at 6.0 may be partly luck at the kills edge.
- Validity notes: single session (seed 7), 20 per arm; the kills result at 6.0 (1.65, se 0.13) cannot distinguish 1.5 from 1.8; no early stops, no stuck-artifact issue (stuck episodes only 3 and 2 in the 3.0 and 6.0 arms: the fix holds).
- MILESTONE IMPACT: modify M2 next step: confirm bite 6.0 on >= 60 episodes over two fresh fake sessions against the real baseline before calling the fake calibrated; keep the damage shape (bimodality) as a known remaining difference.
- Follow-ups / next experiment: Batch 6 = M2 confirmation at bite 6.0 (two sessions).
