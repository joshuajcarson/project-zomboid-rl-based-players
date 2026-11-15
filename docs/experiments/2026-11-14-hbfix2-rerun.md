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

## Result (filled at batch end, 2026-11-15 00:45 CT)
- Data: `results/experiments-2026-11-14/hbfix2.jsonl` (23:52-00:38, 18 episodes: llm 9, rule 9; 0 deaths; planner 134/134 valid).
- Numbers:
  - Watchdog: no alert, including stray_supplies and skill_health.
  - Skills: drink 17/17 (llm 9/9, rule 8/8), eat 38/38, bandage 6/7, loot 19/28 = 68% (llm 10/19, rule 9/9).
- Verdict: **INCONCLUSIVE** (loot 68% is under the 70% success bar and over the 50% failure bar; every other criterion is met).
- What the loot numbers hide:
  - Every loot at the seeded shelf worked: llm 9/9, rule 9/9.
  - All 9 failures are the planner gathering extra supplies (already carrying food, water and bandages) from natural world containers:
    - 10780,9419: a counter 29 tiles away in another building; 2 items queued, the path failed. Tried in 4 different episodes, because failure memory was per episode.
    - 10782,9418-9419 and 10783,9419: these squares hold more than one container. The survey lists each container, but `lootat` took the first container on the square, which held nothing (queued 0).
- Unexpected learnings:
  1. Clearing stray seeds every episode works: none seen in any episode.
  2. The planner over-gathers: it keeps looting when already supplied, which costs time and exposes it.
  3. Multi-container squares break loot by coordinates.
- Fix: the survey reports `ci` (the container's index on its square), and `lootat|x|y|ci` loots that container. With `--fixes`, failed containers are remembered for the whole session (the world is fixed); the planner sees "[looting here failed earlier]".
- MILESTONE IMPACT: none (HBfix3 reruns with the fix and the same criteria).
