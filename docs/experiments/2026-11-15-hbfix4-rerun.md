# HBfix4 Scenario fixes validated (rerun: mobility probe redraws fenced-in spawns)
- Date / time: 2026-11-15 ~01:42 CT
- Milestone: track H, H-B2 preparation
- Question: same as HBfix to HBfix3.
- Change from HBfix3: mobility probe under `--fixes` (after each reset, walk toward the shelf for 3 game s; redraw the spawn, up to 3 times, if the character moved < 1 tile; logged as `probe_fail` rows). The watchdog has the `immobile` check and the once-per-failing-use skill_health.

## Pre-registered (fixed before running; never edited afterwards)
- Design: HBfix3's command with `--seed 29 --out results/experiments-2026-11-15/hbfix4.jsonl`, 45 minutes, arms llm,rule, same watchdog flags.
- SUCCESS / FAILURE / INCONCLUSIVE: HBfix's criteria unchanged. The immobile check counts as a scenario alert (FAILURE), like stray and start-state.
- Stopping rule: 45 minutes; stop early only on a start-state, stray, immobile, step-1, stall or idle alert, a crash, or a stall.

## Run log

## Result (filled at batch end)
- Data: `results/experiments-2026-11-15/hbfix4.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- MILESTONE IMPACT: (pending)
