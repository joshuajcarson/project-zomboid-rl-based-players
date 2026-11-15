# HBfix5 Scenario fixes validated (rerun: failure memory scoped)
- Date / time: 2026-11-15 ~01:47 CT
- Milestone: track H, H-B2 preparation
- Question: same as HBfix to HBfix4.
- Change from HBfix4: with `--fixes`, a failed loot is remembered for the session only when it ended within 3 s with nothing taken, and never for the seeded container; other failures are remembered for the episode.

## Pre-registered (fixed before running; never edited afterwards)
- Design: HBfix4's command with `--seed 31 --out results/experiments-2026-11-15/hbfix5.jsonl`, 45 minutes, arms llm,rule, same watchdog flags.
- SUCCESS / FAILURE / INCONCLUSIVE: HBfix's criteria unchanged; immobile, stray and start-state alerts are scenario alerts (FAILURE).
- Stopping rule: 45 minutes; stop early only on a start-state, stray, immobile, step-1, stall or idle alert, a crash, or a stall.

## Run log

## Result (filled at batch end, 2026-11-15 01:52 CT)
- Data: `results/experiments-2026-11-15/hbfix5.jsonl` (01:38-01:48, stopped early by the stopping rule on an immobile alert at 01:47, episode 3).
- Verdict: **FAILURE** (a scenario alert fired, as pre-registered).
- Cause: the planner walked to the next building (about 30 tiles) and looted 5 different natural counters in a row, each ending in 2 s with nothing taken. Per-container memory cannot stop this when there are 7 such containers. These containers are not part of the scenario: they can be walked to, but they are never looted.
- Fix (scenario definition): with `--fixes`, both planners see only containers within 12 tiles of the seeded container ("the supplies are in this building"). The rows log the filtered list, so the watchdog's stray check therefore only covers that radius, and the clearnear radius (45) still covers the old seeds.
- MILESTONE IMPACT: none (HBfix6 next, same criteria).
