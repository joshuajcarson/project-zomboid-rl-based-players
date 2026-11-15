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

## Result (filled at batch end, 2026-11-15 02:40 CT)
- Data: `results/experiments-2026-11-15/hbfix6.jsonl` (01:48-02:33, 16 episodes: llm 8, rule 8; 2 deaths; planner 131/131 valid; 0 probe redraws).
- Numbers:
  - Watchdog: no alert (start state, stray, immobile, step-1, stall, skill health, planner health).
  - Skills: drink 13/13 (llm 7/7, rule 6/6), eat 32/32, bandage 8/8, loot 14/15 = 93% (llm 8/9, rule 6/6; the one miss was a dishwasher with a zombie close).
- Verdict: **SUCCESS** on all pre-registered criteria. The fixed scenario now starts in the stated state every episode, and all four one-shot skills are reliable for both planners.
- What it took (HBfix to HBfix6, 6 runs):
  - auto-drink off, carried supplies stripped, seeded types cleared every episode (including stray seeds that come back on every boot);
  - a wider survey; loot by container index on multi-container squares; a mobility probe for fenced-in spawns;
  - failure memory scoped to quick failures; planners shown only the supplies building.

  Each failure state became a watchdog check (`stray_supplies`, `skill_health`, `immobile`).
- Unexpected learnings: most of the failures came from the world, not the skills: persistent state, unsaved edits, fenced-in pockets, and loot-proof natural containers.
- MILESTONE IMPACT: modify. H-B2 can be built on the `--fixes` scenario. Its first experiment: re-run the H-B comparison (llm / rule / idle) on the fixed scenario, where thirst and drink now matter, before making the scenario harder.
