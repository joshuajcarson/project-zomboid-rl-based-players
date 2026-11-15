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

## Result (filled at batch end)
- Data: `results/experiments-2026-11-14/hbfix.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- MILESTONE IMPACT: (pending)
