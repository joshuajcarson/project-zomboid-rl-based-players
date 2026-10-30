# B7 M2 calibration: two-knob sweep (bite damage x swing hit scale) on the fake
- Date / time: 2026-10-30, started ~17:05 CT
- Milestone: M2 (fake-vs-real fidelity for the solo fight)
- Question: can a (bite damage, swing hit scale) pair make the fake match the real baseline on kills AND damage? Batch 6 showed bite alone cannot: at 6.0 kills stay too high (1.75 vs 1.36) while damage is already slightly high (48.0 vs 39.2).
- Hypothesis: lowering the swing hit chance (longer fights, more deaths and timeouts) lowers kills, so a smaller bite scale (3.0-4.5) with hit scale 0.5-0.7 reaches both targets.

## Pre-registered (fixed before running; never edited afterwards)
- Real target (Batch 1 pooled n=69): kills 1.36, damage 39.2; M2 bands: kills 1.06-1.66, damage 29.2-49.2.
- Design: ONE fake session, 120 episodes of `charge:1.8:0` requested, fight-v4 field, seed 13, 4x clock, force-kill fix on. Six arms alternating by episode, `PZ_FAKE_ARMS` = bite/hit-scale: 3.0/0.7, 3.0/0.5, 4.5/0.7, 4.5/0.5, 3.0/0.35, 4.5/0.35 (20 episodes each; hit scale multiplies the calibrated swing hit chance, 1.0 = unchanged; at 1 tile it takes the hit rate from 0.46 to 0.32 (0.7), 0.23 (0.5), 0.16 (0.35)). Analysis `python scripts/compare_arms.py <file> --by fake_arm`.
- Candidate rule (fixed now): the candidate is the arm minimising D = ((kills - 1.36)/0.3)^2 + ((damage - 39.2)/10)^2 over arm means.
- SUCCESS (a candidate exists) if: the candidate has BOTH means inside the M2 bands. This only NOMINATES the candidate: six arms make a chance pass likely, so M2 is accepted only after a confirmation batch on fresh sessions (>= 60 episodes, two sessions) under the M2 test.
- FAILURE if: no arm is inside both bands AND the best arm's D >= 2.25 (a distance of 1.5 standardised units: the two knobs cannot reach the target in this range).
- INCONCLUSIVE if: no arm is inside both bands but the best D < 2.25 (a near miss: extend the range or the sample).
- Stopping rule: run all 120 episodes; stop early only for an invalid run (server crash, fake client not connecting). No stopping on apparent effects.
- Also report: death share (damage >= 80), stuck share, median damage and kills distribution per arm vs the real (deaths 16% pooled, stalls ~21% in S2).

## Result (filled at batch end, 2026-10-30 17:15 CT)
- Data: `results/experiments-2026-10-30/b7_m2_two_knob.jsonl` (120 episodes, 20 per arm, all real); `python scripts/compare_arms.py <file> --by fake_arm`.
- Numbers (fake, force-kill on, charge:1.8:0; real target kills 1.36 / damage 39.2 / deaths 16%):
  | bite/hit | kills (se) | damage (se) | median dmg | deaths >= 80 | stuck | kills band | damage band | D |
  |---|---|---|---|---|---|---|---|---|
  | 3.0/0.7 | 1.35 (0.20) | 56.1 (6.1) | 57.6 | 6 | 2 | yes | no | 2.87 |
  | 4.5/0.7 | 0.90 (0.23) | 64.9 (7.1) | 83.4 | 10 | 0 | no | no | 8.96 |
  | 3.0/0.5 | 0.50 (0.17) | 77.3 (6.3) | 90.9 | 16 | 3 | no | no | 22.71 |
  | 4.5/0.5 | 0.45 (0.17) | 78.7 (6.0) | 91.7 | 16 | 1 | no | no | 24.82 |
  | 3.0/0.35 | 0.40 (0.17) | 81.2 (5.5) | 90.2 | 16 | 1 | no | no | 27.87 |
  | 4.5/0.35 | 0.20 (0.09) | 77.2 (5.4) | 89.1 | 14 | 3 | no | no | 29.36 |
- Verdict: **FAILURE** against the pre-registered rule (no arm inside both bands and the best arm's D = 2.87 >= 2.25; candidate would have been 3.0/0.7). The swept range cannot reach the target.
- Unexpected learnings:
  1. The swing hit scale is a very steep knob: from 0.7 to 0.5 kills fall 1.35 -> 0.50 and damage rises 56 -> 77 (death share 30% -> 80%); at 0.5 and below the fake becomes a massacre, nothing like the real client (deaths 16%). Kills are controlled by the hit rate; damage by hit rate and bite together.
  2. Arm 3.0/0.7 is a near miss in a specific direction: kills right on target (1.35) with damage 17 too high (56.1 vs 39.2). Damage falls with bite, which my range did not cover below 3.0 at hit 0.7: the unexplored region is bite 1.5-2.5 with hit 0.6-0.8.
  3. Death shares 80% for 4 arms mean the fake's bite damage is lethal once fights last long: real fights stay bounded (deaths 16%, median damage 22-30), i.e. real zombies contribute damage in bursts (grabs, bites) that this uniform per-second rule does not reproduce.
- Validity notes: single session (seed 13), 20 per arm, all episodes real, no early stops, force-kill fix active (stuck 0-3 per arm).
- MILESTONE IMPACT: none to acceptance; M2 next step restated: sweep a lower bite range around hit scale 0.6-0.8 (Batch 8), then confirm a candidate on fresh sessions.
- Follow-ups / next experiment: Batch 8 = bite {1.5, 2.25} x hit {0.6, 0.7, 0.8}.
