# HBfix2 Scenario fixes validated (rerun with per-episode stray-seed clearing)
- Date / time: 2026-11-14 ~23:58 CT
- Milestone: track H, H-B2 preparation
- Question: same as HBfix: does every episode start in the configured state, and do drink, eat and loot work for both planners with nothing carried?
- Change from HBfix: `--fixes` now also runs `clearnear|10753|9407|45|types` each episode (removes the seeded types from every other container within 45 squares; leftover seeds come back on every server boot). The watchdog also gets `--supplies-at 10753,9407` (stray_supplies) and the new skill_health check.

## Pre-registered (fixed before running; never edited afterwards)
- Design: HBfix's command with `--seed 19 --out results/experiments-2026-11-14/hbfix2.jsonl`, 45 minutes, arms llm,rule. Watchdog: `--arms llm,rule --hunger 0.6 --thirst 0.6 --supplies --supplies-at 10753,9407`, no known deviations.
- SUCCESS / FAILURE / INCONCLUSIVE: HBfix's criteria unchanged. SUCCESS needs no watchdog alert (now including stray_supplies; skill_health alerts are judged through criterion 3, not 1), drink >= 5 uses at >= 70%, eat and loot each >= 70% with >= 5 uses. FAILURE: a watchdog alert other than planner_health or skill_health, or drink, eat or loot below 50% with >= 5 uses. INCONCLUSIVE otherwise.
- Stopping rule: 45 minutes; stop early only on a start-state, stray, step-1, stall or idle alert, a crash, or a stall.

## Run log

## Result (filled at batch end)
- Data: `results/experiments-2026-11-14/hbfix2.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- MILESTONE IMPACT: (pending)
