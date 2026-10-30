# B1 M1 confirmation: plain charge fighter on the clean field
- Date / time: 2026-10-30, started 13:59 CT (the first draft of this card said ~14:30; wrong)
- Milestone: M1 (scripted solo fighter baseline on the real client)
- Question: does `charge:1.8:0` meet the M1 bar (kills >= 1.6 of 2, damage <= 25) on the clean field in two independent sessions? If yes M1 is done and M2 (fake-vs-real fidelity) starts; if not, M1 needs a different acceptance test or scripted work.
- Hypothesis: yes; recent clean-field data (1.82 kills / 24.5 dmg, n=17; 1.74 / 25.7, n=27; 1.30 / 31.4 and 1.35 / 32.7, n=20 each) average about 1.55 kills / 28 dmg, so this is genuinely uncertain and the true value may sit just outside the bar.

## Pre-registered (fixed before running; never edited afterwards)
- Design: two independent sessions (full cleanup and fresh server boot between them), each 40 episodes requested of `charge:1.8:0`, rendered 1x, fight-v4 dirt field (5377,10114; spawn box 5362,10099 .. 5392,10129), 2 zombies on a 5-8 ring, 45 steps max, end-when-clear, god mode between episodes, every episode `PZ_ARM_FIXED=A` (client clock and server clock noon, corpses cleared within 35 tiles), seeds 7 (S1) and 11 (S2). Real episodes = episodes with steps >= 5 (1-step resets after deaths are dropped); the target is >= 30 real episodes per session. Runner: `scripts/_b1_m1.sh`; commit hash = the commit that holds this card.
- SUCCESS if: in BOTH sessions (>= 30 real episodes each) mean kills >= 1.6 AND mean damage <= 25, and no invariant failure other than death-at-reset (repaired by relaunch).
- FAILURE if: in EITHER session mean kills < 1.4 OR mean damage > 32 (clearly outside the bar given se ~0.1 kills and ~5 damage).
- INCONCLUSIVE if: neither of the above (a session has a metric between the success and failure bounds, or a session has < 30 real episodes). Then run a third session, or restate M1 as a confidence-bound test, before declaring anything.
- Stopping rule: each session runs all requested episodes. Stop early ONLY for an invalid run (client dropout loop, server crash, invariant failure that is not a death). No stopping on apparent effects. Also report pooled n and mean +- se over both sessions.
- Invariants that must hold: one bat, in arena; `check_alive` failures are expected after deaths.

- ADDENDUM, written 2026-10-30 14:10 CT while session 1 was still running (no session finished, no result seen): the acceptance rule in `docs/milestones.md` ("pooled over sessions") also applies as a SECOND reading. If the per-session criteria above come out INCONCLUSIVE, the pooled data of S1+S2 (>= 60 real episodes) decide: SUCCESS if pooled mean kills >= 1.6 and pooled mean damage <= 25; FAILURE if pooled mean kills < 1.4 or pooled mean damage > 32; otherwise still INCONCLUSIVE and a third session follows. The thresholds are unchanged.

## Result (filled at batch end)
- Data: `results/experiments-2026-10-30/b1_m1_s1.jsonl`, `b1_m1_s2.jsonl`; reproduce with `python scripts/compare_arms.py <file> --by arm`.
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
