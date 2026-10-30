# B8 M2 calibration: low-bite sweep (bite 1.5-2.25 x hit scale 0.6-0.8)
- Date / time: 2026-10-30, started ~17:20 CT
- Milestone: M2 (fake-vs-real fidelity for the solo fight)
- Question: does a lower bite scale at a hit scale near 0.7 bring damage down to the real 39.2 while keeping kills near 1.36 (Batch 7's near miss was bite 3.0 / hit 0.7: kills 1.35, damage 56.1)?
- Hypothesis: yes, in the region bite ~2.0-2.25 with hit 0.7 (damage falls roughly linearly in bite; kills depend mostly on the hit scale).

## Pre-registered (fixed before running; never edited afterwards)
- Real target (Batch 1 pooled n=69): kills 1.36, damage 39.2; M2 bands: kills 1.06-1.66, damage 29.2-49.2.
- Design: ONE fake session, 120 episodes of `charge:1.8:0` requested, fight-v4, seed 17, 4x clock, force-kill on. Six arms alternating by episode, `PZ_FAKE_ARMS` = bite/hit: 1.5/0.6, 1.5/0.7, 1.5/0.8, 2.25/0.6, 2.25/0.7, 2.25/0.8 (20 each). Analysis `compare_arms.py --by fake_arm`.
- Candidate rule (same as Batch 7): the arm minimising D = ((kills - 1.36)/0.3)^2 + ((damage - 39.2)/10)^2.
- SUCCESS (candidate exists) if: the candidate has BOTH means inside the M2 bands. Only nominates a candidate: M2 is accepted after a confirmation batch (>= 60 episodes, two fresh sessions).
- FAILURE if: no arm is inside both bands AND the best D >= 2.25.
- INCONCLUSIVE if: no arm inside both bands but best D < 2.25.
- Stopping rule: run all 120 episodes; stop early only for an invalid run. No stopping on apparent effects.
- Also report death share, stuck share, median damage per arm vs the real.

## Result (filled at batch end, 2026-10-30 17:40 CT)
- Data: `results/experiments-2026-10-30/b8_m2_low_bite.jsonl` (120 episodes, 20 per arm, all real).
- Numbers (fake, force-kill on, charge:1.8:0; real target kills 1.36 / damage 39.2):
  | bite/hit | kills (se) | damage (se) | median dmg | deaths >= 80 | stuck | kills band | damage band | D |
  |---|---|---|---|---|---|---|---|---|
  | 1.5/0.6 | 1.55 (0.11) | 23.6 (3.8) | 26.9 | 0 | 9 | yes | no | 2.85 |
  | 1.5/0.7 | 1.70 (0.11) | 21.7 (3.1) | 22.5 | 0 | 6 | no | no | 4.34 |
  | 1.5/0.8 | 2.00 (0.00) | 12.9 (2.0) | 11.0 | 0 | 0 | no | no | 11.45 |
  | 2.25/0.6 | 1.65 (0.11) | 41.0 (5.3) | 48.3 | 0 | 7 | yes (edge) | yes | 0.97 |
  | 2.25/0.7 | 1.95 (0.05) | 26.8 (4.5) | 23.4 | 0 | 1 | no | no | 5.41 |
  | 2.25/0.8 | 2.00 (0.00) | 22.8 (3.1) | 20.8 | 0 | 0 | no | no | 7.23 |
- Verdict: **SUCCESS** against the pre-registered rule: the candidate arm 2.25/0.6 has both means inside the M2 bands (kills 1.65, damage 41.0; D = 0.97). It only nominates a candidate; M2 is accepted after the confirmation batch.
- Unexpected learnings:
  1. Kills fall with the hit scale mainly through STUCK episodes (low hit chance means the 45 steps run out before the second zombie dies: 9, 6 and 7 stuck of 20 in the 0.6 arms), not through deaths: deaths are 0 in all six arms. The real client loses kills to both deaths (16%) and stalls (21% in S2); the candidate reproduces stalls but never deaths. So the match is on means only; the shape differs (no deaths, no bimodal very-bad fights).
  2. Damage depends strongly on bite at hit 0.6 (23.6 at bite 1.5, 41.0 at 2.25) but is weak or non-monotone at hit 0.7-0.8 (21.7 vs 26.8; 12.9 vs 22.8): the surface is noisy at n=20 per arm.
  3. Selection caveat repeats: kills 1.65 sits at the band edge (1.66) with se 0.11, as with Batch 5's pass that did not survive confirmation.
- Validity notes: single session (seed 17), 20 per arm, no early stops, force-kill fix active (stuck arises from low hit chance, not the artifact: 0-1 stuck in the 0.8 arms).
- MILESTONE IMPACT: none to acceptance; M2 next step: confirm 2.25/0.6 on fresh sessions (Batch 9), noting the shape difference (no deaths) in the milestone as a known residual.
- Follow-ups / next experiment: Batch 9 = M2 confirmation at bite 2.25 / hit 0.6, two sessions.
