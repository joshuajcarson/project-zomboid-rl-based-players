# HBfix Scenario fixes validated: thirst, supplies visibility, no carried supplies, drink skill
- Date / time: 2026-11-14, pre-registered ~23:35 CT
- Milestone: track H, H-B2 preparation (a harder scenario needs a scenario whose start state is what we say it is)
- Question: with `hybrid_run.py --fixes`, does every episode start in the configured state, and do drink, eat and loot work for both planners now that the character starts with nothing?
- Background: H-B ran with three known deviations (thirst undone by the game's auto-drink, the survey listing only 8 containers, supplies piling up on the shelf and in the inventory). They are fixed and were checked interactively on a dev server at 23:20: auto-drink off keeps thirst at 0.60; `clearat` empties the seeded types from a container; `strip` empties the carried supplies; the survey lists the 8 nearest plus further containers with supplies (max 12). Leftover seeds from HB0c-e at 10779,9411 / 10781,9411 / 10804,9406 / 10775,9421 were cleared once (63 items).

## Pre-registered (fixed before running; never edited afterwards)
- Design: `scripts/hybrid_run.py --fixes --minutes 45 --model sonnet --arms llm,rule --supplies Base.Apple:3,Base.WaterBottle:2,Base.Bandage:2 --supplies-at 10753,9407 --box 10740 9385 10770 9400 --seed 17 --out results/experiments-2026-11-14/hbfix.jsonl`, hunger and thirst 0.6, 2 zombies, 120 s episodes. Watchdog attached with NO known deviations: `--hunger 0.6 --thirst 0.6 --supplies`.
- SUCCESS if all of: (1) the watchdog raises no alert for the whole run (thirst and hunger reach 0.6 within the first 3 surveys, a container with supplies is visible at the start of every episode, no step-1 deaths or stalls); (2) drink has >= 5 applicable uses (both arms together) with >= 70% effective (thirst falls or a water item is used); (3) eat and loot are each >= 70% effective over their applicable uses (>= 5 each).
- FAILURE if: any watchdog alert other than a planner-health alert, OR drink, eat or loot below 50% with >= 5 uses.
- INCONCLUSIVE otherwise (e.g. fewer than 5 uses of a skill).
- Stopping rule: 45 minutes; stop early only on a watchdog alert, crash or stall (an alert also decides FAILURE for criterion 1).
- Not a comparison between arms: both arms only generate skill uses.

## Run log
- Correction: the times above are off by half an hour; the card was committed and the run launched at 23:05 CT (dev checks ~22:50).

## Result (filled at batch end, 2026-11-14 23:55 CT)
- Data: `results/experiments-2026-11-14/hbfix.jsonl` (23:05-23:50, 17 episodes: llm 9, rule 8; 1 death; planner 122/122 valid).
- Numbers:
  - Criterion 1: the watchdog raised no alert during the run. Thirst and hunger were at 0.6, supplies were visible, no step-1 deaths, no stalls.
  - Skills (applicable uses, both arms): drink 11/11 (llm 4/4, rule 7/7), eat 23/23, bandage 2/3, loot 12/67 = 18% (llm 5/60, rule 7/7).
- Verdict: **FAILURE** (loot below 50% with >= 5 uses). The fixes themselves worked: thirst held (the first planner runs where drink was used, 11/11) and the start state matched.
- Cause of the loot failures:
  1. The leftover seeds cleared by hand at 22:50 came back on the next server boot, because world edits are not saved when the server stops. The fireplace 10779,9411 (6/4/4), the shelves 10781,9411 (12/8/8) and the sidetable 10775,9421 reappeared, and the planner chased those large piles 39 times, all failed: paths across buildings fail and drop the action queue.
  2. In episode 1 the planner then retried the reachable shelf 14 times; every attempt ended in 2 s with nothing queued.

  The rule planner loots only the first container showing supplies (the shelf), 7/7.
- Unexpected learnings:
  1. Server-side world edits made through the bridge do not persist across boots unless the world is saved. Scenario hygiene has to run every episode: new server `clearnear|x|y|r|types`, called by `--fixes`.
  2. The planner prefers big piles far away over a small nearby one even after failures, a planner-quality issue for H-B2 (show distance and reachability, or remember failures across episodes).
  3. Two watchdog checks added: `stray_supplies` and `skill_health`. Replayed on this run, they alert in episode 1.
- MILESTONE IMPACT: none (H-B2 preparation continues; HBfix2 reruns with clearnear and the same criteria).
