# HB0b Hybrid planner: in-game unit tests of the one-shot skills
- Date / time: 2026-11-14, pre-registered ~10:00 CT (5-hour usage guard temporarily 92%, user)
- Milestone: track H, prerequisite of H-B
- Question: after switching eat and drink to the game's own entry points (`ISInventoryPaneContextMenu.eatItem` / `onDrinkFluid`, which move the item to the main inventory and run the Build 42 opening recipe for sealed food) and testing loot on containers in isolation, do the skills work when nothing interferes?
- Hypothesis: eat and drink yes (H-B0's eat failure was the missing opening/transfer step); loot uncertain (walking into the building may fail).

## Pre-registered (fixed before running; never edited afterwards)
- Design: `scripts/skill_test.py --trials 5 --out results/experiments-2026-11-14/b0b_skill_tests.jsonl` on the real client (build 42.22.2), spawn box 10730,9380 .. 10810,9440, NO zombies spawned, each trial runs eat, drink, loot in that order with server-side hunger/thirst 0.5 first; eat gets a client-side `Base.Apple` before each trial (the first eat may use the starter chips); drink uses the starter water bottle; loot uses `loot|i|30|any` on container i = trial number (nearest first), at most 2 items. Wait for the action queue to empty (caps eat 25, drink 20, loot 40 game s).
- Success per trial: eat: food -1 or hunger down; drink: water -1 or thirst down; loot: carried item count up (client `invcount`).
- SUCCESS if: eat, drink and loot each succeed in >= 4 of 5 trials.
- FAILURE if: any of the three succeeds in <= 1 of 5 trials.
- INCONCLUSIVE otherwise.
- Stopping rule: all trials; stop early only for an invalid run (crash, client not reachable).

## Result (filled at batch end)
- Data: `results/experiments-2026-11-14/b0b_skill_tests.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
