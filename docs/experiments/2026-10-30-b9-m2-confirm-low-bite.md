# B9 M2 confirmation: fake at bite 2.25 / hit scale 0.6 vs the real baseline
- Date / time: 2026-10-30, started ~17:45 CT
- Milestone: M2 (fake-vs-real fidelity for the solo fight)
- Question: does the Batch 8 candidate (bite 2.25, hit scale 0.6) match the real baseline within the M2 bands over two fresh sessions?
- Hypothesis: damage yes; kills near the upper band edge (Batch 8: 1.65 at n=20, se 0.11); Batch 5's pass at the edge did not confirm.

## Pre-registered (fixed before running; never edited afterwards)
- Real target (Batch 1 pooled n=69): kills 1.36 (95% CI 1.17-1.56), damage 39.2 (32.3-46.2).
- Design: two independent sessions (full cleanup and fresh server between them), each 40 episodes of `charge:1.8:0` on the fake backend at 4x clock, fight-v4, force-kill on, `PZ_FAKE_ARMS=2.25:0.6`, seeds 7 and 11; pooled real episodes >= 60. Runner `scripts/_b9_m2.sh`.
- SUCCESS (M2 acceptance) if: pooled mean kills within 0.3 of 1.36 (1.06-1.66) AND pooled mean damage within 10 of 39.2 (29.2-49.2), AND neither session alone is outside the failure band (kills 0.86-1.86, damage 19.2-59.2).
- FAILURE if: pooled kills differ from 1.36 by more than 0.5 (outside 0.86-1.86) OR pooled damage by more than 20 (outside 19.2-59.2), OR either session alone is outside those bands.
- INCONCLUSIVE if: neither (grey zone, e.g. kills 1.67-1.86): then more sessions at this setting, or a finer sweep, decided in the next batch.
- Stopping rule: all requested episodes per session; stop early only for an invalid run. No stopping on apparent effects.
- Also report: death share (real 16% pooled), stuck share (real S2 21%), median damage per session; if SUCCESS, M2 is marked done WITH these shape differences written down as known residuals (the means match, the shape does not).

## Result (filled at batch end)
- Data: `results/experiments-2026-10-30/b9_m2_fake_s1.jsonl`, `b9_m2_fake_s2.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
