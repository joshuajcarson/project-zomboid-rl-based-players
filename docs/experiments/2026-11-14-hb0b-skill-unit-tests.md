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

## Result (filled at batch end, 2026-11-14 10:05 CT)
- Data: `results/experiments-2026-11-14/b0b_skill_tests.jsonl` (15 trials, 09:58-10:03).
- Numbers: eat 0/5, drink 0/5, loot 0/5. Eat: `EAT Apple recipe=false ok=true` every trial (the game's eatItem was called without error) but the action queue was empty after 2 s and food stayed 9. Drink: `DRINK none` every trial (survey: water 0). Loot: the log shows the plain loot path (`queued=0` on containers without food), not the 'any' test mode.
- Verdict: **FAILURE** against the pre-registered criteria (every skill <= 1 of 5).
- Diagnosis (largely test design, one real finding): (1) loot 'any' never ran: the server relays only two bot arguments, so the third (`any`) was dropped; (2) drink never ran: the persistent character has no water left (the starter water was used up in earlier runs); (3) REAL: eating a client-side given item (`giveitem Base.Apple`) does not start the eat action even through the game's own entry point: client-only items are probably rejected by the server-checked action (H-A's successful eats used starter or looted food the server knows).
- Unexpected learnings: characters persist across runs (inventory state is not reset), so skill tests need a known server-side inventory; bot commands carry at most two arguments through the server relay.
- Validity notes: valid run of a flawed test design for loot and drink; the eat result is informative.
- MILESTONE IMPACT: none to acceptance; H-B0 stays the gate. Next: interactive debugging of each skill on the live client (not a batch), then one pre-registered verification batch.
- Follow-ups / next experiment: give items server-side or loot them from the world; relay 3 bot arguments (or encode 'any' in argument b); verify drink with a real water source.

## Interactive debugging after the batch (12:55-13:08 CT, not pre-registered; live client, no zombies)
- Server bot relay now passes a third argument; `loot|1|35|any` walked 18 tiles and moved items (carried items 24 -> 25).
- Root cause of 'eat none' / no effect: the persistent character's 8 food items were all ROTTEN (eat skips rotten food, the survey counted it): the survey now counts edible food only.
- New server command `seed|user|type|n|r` puts items into the container nearest the player ON THE SERVER: they appear on the client (shelf: food 3, water 2, bandages 2).
- With seeded, server-known items: `loot|1|35` queued 7 transfers, done in ~24 s (food 3, water 2, bandages 2 carried); `eat` (game's eatItem) ate an Apple: food 3 -> 2, hunger 0.60 -> 0.44; `drink` (game's onDrinkFluid) emptied a WaterBottle. Bandage still untested (no bleeding).
- Conclusion: the skills work when the items are real, edible and server-known; H-B0's low effect rates came from rotten / client-only food and loots of containers without supplies. Exception noise from probing non-bag items with getInventory removed (instanceof check).
