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

## Result (filled at batch end)
- Data: `results/experiments-2026-10-30/b12_m3a_real_s1.jsonl`, `b12_m3a_real_s2.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
