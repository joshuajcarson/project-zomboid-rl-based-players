# B2 M2 fidelity: the scripted fighter on the fake backend vs the measured real baseline
- Date / time: 2026-10-30, started ~15:55 CT
- Milestone: M2 (fake-vs-real fidelity for the solo fight)
- Question: how far is the fake-client fight from the real client for the same scripted policy and protocol? The answer decides whether the fake must be re-calibrated before any policy is trained on it (M3).
- Hypothesis: the fake is too easy: kills about 2.0 and damage about 19 (the 10-26 refit numbers), against the measured real baseline of 1.36 kills and 39.2 damage.

## Pre-registered (fixed before running; never edited afterwards)
- Real target (Batch 1, pooled n=69, `docs/experiments/2026-10-30-b1-m1-confirmation.md`): kills 1.36 (95% CI 1.17-1.56), damage 39.2 (32.3-46.2).
- Design: two independent sessions (full cleanup and fresh server between them), each 40 episodes requested of `charge:1.8:0` on the FAKE backend (backend fake, clock 4x as the lab sets it), fight-v4 dirt field (5377,10114), 2 zombies on a 5-8 ring, 45 steps max, end-when-clear, seeds 7 and 11. Real episodes = steps >= 5. Runner `scripts/_b2_m2.sh`. Note: the arm/world controls (noon, corpse clearing) exist only for the rendered client and are not applied here; the fake run is on whatever the server world is.
- SUCCESS if: pooled fake mean kills within 0.3 of 1.36 (1.06-1.66) AND pooled mean damage within 10 of 39.2 (29.2-49.2). Then the fake is usable for M3 as is.
- FAILURE if: pooled fake mean kills differ from 1.36 by more than 0.5 (outside 0.86-1.86) OR mean damage differs from 39.2 by more than 20 (outside 19.2-59.2). Then the fake must be re-calibrated (a new batch) before M3.
- INCONCLUSIVE if: neither (grey zone); then a third session or a statement of the gap with its interval and a calibration batch anyway.
- Stopping rule: all requested episodes per session; stop early only for an invalid run (server crash, fake clients not connecting, invariant failure other than death). No stopping on apparent effects. Report the gap as (fake - real) for kills and damage with intervals (both sources of uncertainty).
- Invariants: fake clients connected, one scripted agent, episodes end by clear or 45 steps.

## Result (filled at batch end)
- Data: `results/experiments-2026-10-30/b2_m2_fake_s1.jsonl`, `b2_m2_fake_s2.jsonl`.
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
