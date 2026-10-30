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

## Result (filled at batch end, 2026-10-30 18:02 CT)
- Data: `results/experiments-2026-10-30/b9_m2_fake_s1.jsonl`, `b9_m2_fake_s2.jsonl` (40 real episodes each).
- Numbers (fake, bite 2.25 / hit 0.6, force-kill on, charge:1.8:0):
  - S1: kills 1.52 (se 0.09), damage 38.4 (se 4.6), median 33.5, 4 deaths, 14 stuck; kills {0: 2, 1: 15, 2: 23}.
  - S2: kills 1.65 (se 0.08), damage 40.6 (se 3.6), median 39.4, 1 death, 13 stuck; kills {1: 14, 2: 26}.
  - Pooled n=80: kills 1.59 (95% CI 1.47-1.71), damage 39.5 (33.8-45.2), median 36.3, 5 deaths (6%), 27 stuck (34%).
  - Gap fake - real (1.36 / 39.2): kills +0.23 (se 0.12, z 2.0), damage +0.3 (se 4.6, z 0.1).
- Verdict: **SUCCESS** against the pre-registered criteria: pooled kills 1.59 inside 1.06-1.66, pooled damage 39.5 inside 29.2-49.2, neither session alone outside the failure bands (S1 kills 1.52 / damage 38.4, S2 1.65 / 40.6). The M2 acceptance test (means within the bands) is met.
- Unexpected learnings / known residuals (the means match, the shape does not):
  1. Deaths: fake 6% (5 of 80) vs real 16% (11 of 69; S1 26%, S2 8%): the fake under-produces deaths.
  2. Stuck episodes (45 steps, a zombie alive): fake 34% vs real about 12% pooled (8 of 69; none in S1, 21% in S2): the fake over-produces stalls; its kills deficit comes from stalls where the real client's comes from deaths and stalls together.
  3. Median damage: fake 36.3 vs real 22.0 (S1) and 30.2 (S2): the fake's damage is concentrated near the mean while the real client's is bimodal (clean fights and bad ones).
  4. The kills gap (+0.23, z 2.0) is borderline significant even though it passes the band; Batch 5's pass at the band edge had not confirmed, this one did (kills 1.65 at n=20 in Batch 8, 1.59 at n=80 here).
  5. Wall clock for a 40-episode fake session was ~10 minutes including a fresh server boot: roughly 5-6 times more episodes per minute than the real client (a real 40-episode session took ~35 minutes).
- Validity notes: both sessions complete, force-kill fix active, seeds 7 and 11, no early stops.
- MILESTONE IMPACT: modify M2 -> done (acceptance met on means; residual shape differences recorded above and in docs/milestones.md); the calibrated profile (bite 2.25, hit 0.6) is now the default for the fake fight task (`PZ_FAKE_RAW=1` restores the raw fake); M3 (learned fighter) becomes the next milestone. Any claim about learned policies must be validated on the real client (M3's acceptance already requires it) because the fake's shape differs.
- Follow-ups / next experiment: Batch 10 = M3 first step: train PPO on the calibrated fake fight and evaluate it against the scripted fighter on the fake (interleaved), as the gate before any real-client validation.
