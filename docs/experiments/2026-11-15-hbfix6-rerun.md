# HBfix6 Scenario fixes validated (rerun: planners see only the supplies building)
- Date / time: 2026-11-15 ~01:54 CT
- Milestone: track H, H-B2 preparation
- Question: same as HBfix to HBfix5.
- Change from HBfix5: with `--fixes`, both planners see only containers within 12 tiles of the seeded container.

## Pre-registered (fixed before running; never edited afterwards)
- Design: HBfix5's command with `--seed 37 --out results/experiments-2026-11-15/hbfix6.jsonl`, 45 minutes, arms llm,rule, same watchdog flags.
- SUCCESS / FAILURE / INCONCLUSIVE: HBfix's criteria unchanged; immobile, stray and start-state alerts are scenario alerts (FAILURE).
- Stopping rule: 45 minutes; stop early only on a start-state, stray, immobile, step-1, stall or idle alert, a crash, or a stall.

## Run log

## Result (filled at batch end)
- Data: `results/experiments-2026-11-15/hbfix6.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- MILESTONE IMPACT: (pending)
