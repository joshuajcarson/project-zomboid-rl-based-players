# HBfix3 Scenario fixes validated (rerun: loot by container index, session-wide failure memory)
- Date / time: 2026-11-15 ~00:47 CT
- Milestone: track H, H-B2 preparation
- Question: same as HBfix / HBfix2.
- Change from HBfix2: survey reports each container's index on its square (`ci`); `lootat|x|y|ci` loots that container (several containers share some squares and the first was always taken). With `--fixes`, containers where looting failed stay marked for the whole session ("[looting here failed earlier]") for both planners.

## Pre-registered (fixed before running; never edited afterwards)
- Design: HBfix2's command with `--seed 23 --out results/experiments-2026-11-14/hbfix3.jsonl`, 45 minutes, arms llm,rule, same watchdog flags.
- SUCCESS / FAILURE / INCONCLUSIVE: HBfix's criteria unchanged (no watchdog alert other than planner_health/skill_health; drink >= 5 uses at >= 70%; eat and loot each >= 70% with >= 5 uses; FAILURE if any is < 50% or a scenario alert fires).
- Stopping rule: 45 minutes; stop early only on a start-state, stray, step-1, stall or idle alert, a crash, or a stall.

## Run log

## Result (filled at batch end)
- Data: `results/experiments-2026-11-14/hbfix3.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- MILESTONE IMPACT: (pending)
