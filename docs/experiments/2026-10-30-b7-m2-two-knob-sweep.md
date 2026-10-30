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

## Result (filled at batch end)
- Data: `results/experiments-2026-10-30/b7_m2_two_knob.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
