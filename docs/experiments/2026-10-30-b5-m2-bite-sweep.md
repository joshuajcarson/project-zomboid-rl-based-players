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

## Result (filled at batch end)
- Data: `results/experiments-2026-10-30/b5_m2_bite_sweep.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
