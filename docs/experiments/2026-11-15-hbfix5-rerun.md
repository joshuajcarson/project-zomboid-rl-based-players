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

## Result (filled at batch end)
- Data: `results/experiments-2026-11-15/hbfix5.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- MILESTONE IMPACT: (pending)
