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

## Result (filled at batch end)
- Data: `results/experiments-2026-10-30/b8_m2_low_bite.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
