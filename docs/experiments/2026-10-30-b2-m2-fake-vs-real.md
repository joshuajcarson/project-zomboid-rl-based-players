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

## Result (filled at batch end, 2026-10-30 16:10 CT)
- Data: `results/experiments-2026-10-30/b2_m2_fake_s1.jsonl`, `b2_m2_fake_s2.jsonl` (40 real episodes each, no aborted resets); `python scripts/compare_arms.py <file>`.
- Numbers (fake, charge:1.8:0, fight-v4, 4x clock):
  - S1: kills 1.02 (se 0.12), damage 20.4 (se 2.1); kills per episode 0:11, 1:17, 2:12; mean steps 36.5.
  - S2: kills 1.02 (se 0.06), damage 24.3 (se 2.2); kills per episode 0:1, 1:38, 3:1; mean steps 44.6.
  - Pooled n=80: kills 1.02 (95% CI 0.89-1.16), damage 22.3 (19.3-25.4).
  - Gap fake - real (real = Batch 1 pooled 1.36 / 39.2): kills -0.34 (se 0.12, z -2.8), damage -16.9 (se 3.9, z -4.4).
- Verdict: **INCONCLUSIVE** against the pre-registered criteria (SUCCESS needed |kills gap| <= 0.3 and |damage gap| <= 10; FAILURE needed |kills gap| > 0.5 or |damage gap| > 20: the gaps, 0.34 and 16.9, fall between). Statistically the gaps are real (z -2.8 and -4.4), so the fake is NOT equivalent to the real client; the card's own rule says to state the gap and run a calibration batch anyway.
- Unexpected learnings:
  1. My prediction was wrong in direction: the fake kills LESS than the real client (1.02 vs 1.36), not more (2.0 in the 10-26 refit), and does about half the damage. Taken with the 10-26 numbers (fight-v1 arena, 2.0 kills / 18.9 dmg) this is either a regression since then or a protocol effect (field, sandbox, code changes).
  2. The fake's outcomes are structurally degenerate: 55 of 80 episodes kill exactly one zombie and then run all 45 steps with the other alive (S2: 38 of 40; S1: 17 of 40, plus 11 stalls with zero kills). The cumulative combat stats show the fake character swings ~40 times per episode and lands ~40-45% of swings, so it IS hitting something. Hypothesis (untested): the server only removes a zombie on a lethal hit from that zombie's OWNER client (see the comment in `pzrl/env.py` step), so a zombie owned by the server or another client absorbs hits without dying; the 'ownership settle' waits in reset point at the same area.
  3. The two fake sessions differ sharply in structure (S1 mixed, S2 nearly deterministic) with similar damage: sessions on the fake are not exchangeable, which is a validity problem for any fake-vs-real comparison until the artifact is understood.
  4. The cleanup.py fix worked: the Batch 2 wrapper survived its own cleanup call and ran both sessions unattended (11 minutes per session including boot).
- Validity notes: both sessions ran to completion, no invariant failures logged for the fake, no early stops. The arm/world controls (noon, corpse clearing) do not apply to the fake run.
- MILESTONE IMPACT: add M2a (find and fix the fake's one-kill artifact before calibrating anything: acceptance = in a 20-episode fake session at least 40% of episodes kill both zombies and fewer than 30% run the full 45 steps with a zombie alive, with a mechanism shown in a logged trace); M2 stays not started until M2a passes and is then re-run against the real baseline (it would otherwise calibrate noise).
- Follow-ups / next experiment: Batch 3 = M2a diagnosis: ownership hypothesis test on the fake with logged zombie ids, owners and positions per swing.
