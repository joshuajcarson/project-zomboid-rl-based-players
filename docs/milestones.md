# Milestones toward the long-term goal

**Long-term goal:** several agents (up to 4) cooperating to survive in Project Zomboid on one server, validated on the real graphical client. Solo-first is fine; the route does not matter as long as each step is validated on the real client.

**Last updated: 2026-10-30.** Update this file at least once per calendar day (first action of a day's session, and at the end of every batch when a status, evidence line or next experiment changed). Statuses: `done`, `in progress`, `not started`, `blocked`, `parked`. Every status needs an evidence pointer (journal section, results file or ledger row); a milestone is `done` only when its acceptance test passed in a session that meets the experiment rules in CLAUDE.md.

## Acceptance-test rule (decided 2026-10-30)
Numeric acceptance tests are judged on the POOLED real episodes of at least two independent sessions (pooled mean and 95% interval): success needs the pooled mean at or better than the target; failure if the pooled mean is clearly outside the pre-registered failure bound; anything between is INCONCLUSIVE and means more sessions, never moved thresholds. Reason: per-episode damage has sd ~27, so one 30-episode session cannot decide a threshold that sits at the current estimate (se ~5). M1 in this form: target kills >= 1.6 and damage <= 25; failure bound kills < 1.4 or damage > 32; planned n >= 60 pooled (Batch 1 = 2 sessions x 30+).

## Strategy (as of 2026-10-30)
The real client is the VALIDATOR, not the trainer: ~45 s per episode at 1x, 30+ episodes per arm for any claim, ~4 GB per client on a 15.8 GB machine (1-2 real clients). Learning at scale and 4-agent cooperation come from the fake-client backend (4-8x clock, several agents, combat already refit); the real client checks transfer with interleaved comparisons. Details: end of `docs/journal.md` ("strategic read").

## Milestones

| ID | Milestone | Acceptance test | Status | Evidence / next |
|---|---|---|---|---|
| M0 | Trustworthy infrastructure and measurement | Server + fake + rendered clients run unattended; per-reset invariants; one-command cleanup; interleaved A/B tooling; raw per-episode data kept in `results/` | in progress (mostly done) | invariants, `scripts/cleanup.py`, `scripts/compare_arms.py`, `results/experiments-2026-10-30/`. Open: corpse invariant at reset, `benchmark.py` reference reuse is now opt-in and `--interleave` exists (2026-10-30), ledger rows before 2026-10-30 are tagged `[unpaired]`; `cleanup.py` also kills the shell that launched a wrapper (fix after Batch 1) |
| M1 | Scripted solo fighter baseline on the real client | `charge:1.8:0` on the cleared fight-v4 field at noon, n >= 30 real episodes per session, in two independent sessions (fresh server each): mean kills >= 1.6 of 2 and mean damage <= 25 in BOTH, no invariant failures beyond repaired death relaunches (idle is a sanity reference only: 0 kills, ~90 dmg) | in progress (likely met, unconfirmed) | cleared arm 1.82 kills / 24.5 dmg (n=17), earlier block 1.74 / 25.7 (n=27); needs one clean confirming session at n >= 30 |
| M2 | Fake-vs-real fidelity for the solo fight | Scripted fighter on the fake and on the real client (same protocol, interleaved by session pairs, n >= 30 each): kills within 0.3 and damage within 10 of each other; transfer gap recorded in the ledger | not started | fake after combat refit: 2.0 kills / 18.9 dmg vs real ~1.7 / 26 (10-26, small n). Fake is slightly lenient: tune damage/hit model until equal within noise |
| M3 | Learned solo fighter | PPO trained on the calibrated fake; on the real client interleaved against the scripted fighter, n >= 30 per arm: kills >= 90% of scripted, damage <= scripted + 5 | not started | `pzrl/train.py` exists; imitation attempts (`models/fight_bc*.pt`) were never benchmarked in the ledger |
| M4 | Solo survival loop beyond fighting | One agent survives one full game day on the real client against ambient zombies (feeds itself, drinks, bandages, rests, avoids or fights) | not started | needs needs/wounds in observation (backlog item 6), eat/drink/bandage actions; wound types |
| M5 | Two cooperating agents, one real | Mixed backend (1 real + fakes) or 2 real clients: pair rendezvous + joint fight; per-agent damage with a partner is lower than solo (interleaved, n >= 30) | not started | rendezvous movement transfer already proven for 1 real + fakes (2026-10-26); 2 real clients depend on the memory experiment |
| M6 | Client memory budget for 2+ real clients | Real client at <= ~3 GB (heap/texture options) with unchanged fight results (interleaved, n >= 30), or a measured proof it cannot be done | not started | draw removal gave no saving (4.2 vs 3.8 GB); heap -Xmx 3072m, textures untested |
| M7 | Four cooperating agents (fakes) with real validation at two | 4-agent policy trained on fakes survives a scripted scenario; same policy with 2 real agents within noise of the fake result | not started | depends on M3, M5, M6 |
| M8 | Human-like play demo / recorder | Clip per day, human demo recorder, visible behaviour comparable to a player | not started | clips are local (git-ignored) |
| M9 | Optional speed-up: faster-than-1x real client | Real client at 2x with fight results equal to 1x within noise (interleaved, 60+ eps per arm, two sessions) | parked | 2x runs mechanically (2.00x game time, needs PZ_SETTLE=2); fidelity unproven (no clean paired test); 4x broken |

## Closed or deprioritised tracks (kept so nobody redoes them)
- Headless real client by removing the world draw: works (`norender=world`) but saves no CPU/RAM (client is a frame-limiter spin + ~4.2 GB either way); window goes "Not Responding"; closed.
- More scripted-fighter tuning (swing distance 1.8-2.6, retreat <35 hp): differences are within noise; only 1.3 and 3.0 swing distance are clearly worse. Re-test only inside an interleaved session if a learned policy needs it.
- Server-side NPCs (option B): parked, zombie AI does not run.

## Daily update log
- 2026-10-30 (evening): scheduled review added (task `pz-daily-milestone-review`, 8:00 AM Central daily); experiment cards required (docs/experiments/); M1 acceptance restated as absolute thresholds in two sessions; Batch 1 (M1 confirmation) started.
- 2026-10-30: file created; statuses taken from the journal (hour 1-3, drift hunt, strategic read).
