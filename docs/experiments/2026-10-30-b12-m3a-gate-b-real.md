# B12 M3a gate B: the behaviour-cloned fighter vs the scripted fighter on the REAL client
- Date / time: 2026-10-30, started ~19:05 CT
- Milestone: M3a (imitation gate), gate B (real client)
- Question: is `models/fight_bc3.pt` (sha1 prefix e624cb83a0) non-inferior to `charge:1.8:0` on the real graphical client, interleaved in the same sessions?
- Hypothesis: yes: gate A showed a near copy of the scripted policy on the fake (kills 1.57 vs 1.67, damage 37.1 vs 37.1); the observation format is the same on the real client. Risk: real observations (distances, zombie slots) may differ from the fake's training data and the checkpoint was trained on 2026-10-26 data.

## Pre-registered (fixed before running; never edited afterwards)
- Design: two independent sessions (full cleanup and fresh server between them), each 64 episodes requested interleaved by episode between `models/fight_bc3.pt` (greedy) and `charge:1.8:0` (32 each), REAL rendered client at 1x, fight-v4 dirt field, every episode noon with corpses cleared (`PZ_ARM_FIXED=A`, `PZ_ARM_HOUR=12`), seeds 7 and 11. Runner `scripts/_b12_m3a.sh`; `compare_arms.py --by policy` per session and pooled. Real episodes = steps >= 5; pooled need >= 55 per arm.
- SUCCESS (M3a acceptance on the real client) if: pooled learned mean kills >= pooled scripted mean kills - 0.2 AND pooled learned mean damage <= pooled scripted mean damage + 8, AND neither session alone has learned kills < scripted - 0.5 or learned damage > scripted + 15.
- FAILURE if: pooled learned kills < scripted - 0.5 OR pooled learned damage > scripted + 15, OR either session alone is outside those bounds.
- INCONCLUSIVE if: neither (e.g., pooled kills difference between -0.5 and -0.2, or damage difference between +8 and +15): then a third session before deciding.
- Stopping rule: all requested episodes per session; stop early only for an invalid run (client dropout loop, a run stalled with a dead character for > 15 minutes, server crash, invariant failure other than death-at-reset). No stopping on apparent effects.
- Known design wrinkle (stated in advance): the arm alternates by episode index, and a death makes the next episode an aborted 1-step reset, so the arm that dies more loses fewer real episodes than the other arm's slot and also gets the first real episode after each client relaunch; the effect is small but real. Report real-episode counts per arm and the death share per arm.
- Also report: kills/damage/deaths/stuck per arm per session, the real baseline for context (kills 1.36 / damage 39.2, Batch 1), and any action-choice differences if cheap.

## STATUS: PAUSED at the user's request (2026-10-30 20:31 CT), session 2 incomplete: NO VERDICT YET
- Session 1 (seed 7) complete: 64 episodes, 57 real (28 scripted, 29 BC), data `results/experiments-2026-10-30/b12_m3a_real_s1.jsonl`. Interim reading (not a verdict): scripted kills 1.32 / damage 38.0 (3 deaths), BC kills 1.48 / damage 32.9 (4 deaths); differences not significant (kills z 0.83, damage z -0.69).
- Session 2 (seed 11) was interrupted after 16 of 64 episodes because the user needed the PC; the partial lines are kept in `b12_m3a_real_s2_PARTIAL_interrupted.jsonl` and must NOT be pooled with a restarted session 2.
- RESUME PLAN: restart session 2 from scratch (full cleanup, fresh server, same design and seed 11, 64 episodes) with `scripts/_b12_m3a.sh` edited to run only session 2 (`for S in 2`), then evaluate the pooled pre-registered criteria above. The interruption is not an "invalid run" verdict: the pre-registered criteria are unchanged. The env must NOT be edited before session 2 starts (session 1 ran the current code), so the M0 logging changes wait until this batch is finished.

## Result (filled at batch end)
- Data: `results/experiments-2026-10-30/b12_m3a_real_s1.jsonl`, `b12_m3a_real_s2.jsonl` (session 2 pending)
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending; so far: the reset head start, see docs/milestones.md M0 addition and the journal entry of 20:30)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
