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

- ADDENDUM, written 2026-10-30 14:06 CT while session 1 was still running (no session finished, no result seen): the acceptance rule in `docs/milestones.md` ("pooled over sessions") also applies as a SECOND reading. If the per-session criteria above come out INCONCLUSIVE, the pooled data of S1+S2 (>= 60 real episodes) decide: SUCCESS if pooled mean kills >= 1.6 and pooled mean damage <= 25; FAILURE if pooled mean kills < 1.4 or pooled mean damage > 32; otherwise still INCONCLUSIVE and a third session follows. The thresholds are unchanged.

## Result (filled at batch end, 2026-10-30 15:45 CT)
- Data: `results/experiments-2026-10-30/b1_m1_s1.jsonl`, `b1_m1_s2.jsonl`; reproduce with `python scripts/compare_arms.py <file>` (per session) and the pooled numbers below with the 95% intervals from the per-episode lines.
- Numbers (real episodes = steps >= 5):
  - S1 (seed 7): n=31 (9 aborted resets after deaths), kills 1.52 (95% CI 1.22-1.82), damage 39.8 (27.9-51.7), 8 deaths (damage >= 80). Kills per episode: 0:7, 1:1, 2:23. Median damage 22.0.
  - S2 (seed 11): n=38 (2 aborted), kills 1.24 (0.99-1.49), damage 38.8 (30.6-47.0), 3 deaths, 8 stalled episodes (45 steps, both zombies alive). Kills per episode: 0:8, 1:13, 2:17. Median damage 30.2.
  - Pooled n=69: kills 1.36 (95% CI 1.17-1.56), damage 39.2 (32.3-46.2). S1 vs S2 damage difference 1.0 (se 7.4, z 0.14): the sessions agree.
- Verdict: **FAILURE** against the pre-registered criteria (SUCCESS needed kills >= 1.6 and damage <= 25 in BOTH sessions: neither session qualifies; FAILURE was triggered by S1 damage 39.8 > 32 and S2 kills 1.24 < 1.4 and damage 38.8 > 32). The pooled reading in the addendum agrees (pooled kills 1.36 < 1.4, damage 39.2 > 32). M1's acceptance test as written is NOT met.
- Unexpected learnings:
  1. The plain charge fighter on the cleared noon field is worse than every earlier estimate (25.7 n=27, 24.5 n=17, 31.4/32.7 n=20 each): earlier favourable blocks looked better than the truth (regression to the mean); the M1 bar (1.6 / 25) was set from optimistic data. The robust estimate is ~1.4 kills and ~39 damage.
  2. Two different failure modes: deaths (S1: 8 of 31 episodes with >= 80 damage) and stalls (S2: 8 of 38 episodes ended at step 45 with both zombies alive and little damage). They differ between sessions although mean damage matches, so the means hide a bimodal outcome (median damage 22 to 30).
  3. `scripts/cleanup.py` killed the batch wrapper at its own start-of-session-2 cleanup; the client stood idle for ~12 minutes (user noticed). Fixed (protects its ancestor chain, ignores tool shells); session 2 was restarted manually at 15:02.
  4. Post-hoc nulls (exploratory): damage does not track the number of zombies loaded near the field (r = -0.03, n=160); first halves of sessions are not significantly worse than second halves (pooled z 1.27).
- Validity notes: both sessions valid (noon 12.04, daylight 0.87, 0 corpses in every episode; only death-at-reset invariant failures plus the known in-arena check right after a death relaunch). S2 started 12 minutes later than planned (see learning 3), on a fresh server. S1 launch reported a spurious tool failure (same cleanup bug) but ran normally.
- MILESTONE IMPACT: modify M1 (record the FAILED test; M1 becomes "scripted baseline characterised": kills 1.36, damage 39.2, pooled n=69); modify M3 (target relative to the measured baseline, non-inferiority first); modify M2 (the fake must match the REAL baseline 1.36 / 39.2: the fake's 2.0 / 18.9 is far too easy); add M1b (two failure modes: reduce stalls and deaths in the scripted fighter, optional, only if M3 needs a better teacher).
- Follow-ups / next experiment: Batch 2 = M2 fidelity: the same scripted fighter on the fake backend vs the real baseline above.
