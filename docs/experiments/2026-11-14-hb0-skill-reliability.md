# HB0 Hybrid planner: skill reliability fix (wait for the action queue, outcome feedback)
- Date / time: 2026-11-14, pre-registered ~09:10 CT
- Milestone: track H, prerequisite of H-B (survival comparison)
- Question: with one-shot skills that wait until the client's timed-action queue is empty (caps: eat 20, drink 15, bandage 15, loot 35 game s) and the last skill's outcome fed back to the planner, do eat / drink / loot achieve their effect when they can (when the item or supplies exist)?
- Hypothesis: yes, effect rates rise from 21-44% (H-A) to >= 70% when applicable; futile repeated loots drop.

## Pre-registered (fixed before running; never edited afterwards)
- Design: identical to H-A run 2 (real client, build 42.22.2, Sonnet via claude -p, spawn box 10730,9380 .. 10810,9440, 2 zombies on an 8-14 ring, 120 game-second episodes, server-side hunger/thirst 0.6 at episode start, survey radius 30) except: new client command `busy` and `hybrid.run_one_shot` (poll the queue each game second until empty or the cap), and the state text gains `Last skill: <outcome>`. 30 minutes: `scripts/hybrid_run.py --minutes 30 --model sonnet --out results/experiments-2026-11-14/b0_reliability.jsonl`.
- Applicable use: eat with food > 0 before; drink with water > 0 before; loot of a listed container whose survey showed food + water + bandages > 0; bandage with bleeding > 0 and bandages > 0. Effect: eat food -1 or hunger down; drink water -1 or thirst down; loot supplies up; bandage bleeding down (survey right after the skill ends).
- SUCCESS if: for each of eat, drink, loot with >= 5 applicable uses the effect rate is >= 70%; AND >= 95% valid decisions, median latency <= 15 s, no harness/client/server crash in 30 minutes.
- FAILURE if: any of eat, drink, loot with >= 5 applicable uses has an effect rate < 40%, OR valid < 80%, OR a crash prevents the 30-minute run.
- INCONCLUSIVE otherwise (including a skill with fewer than 5 applicable uses: reported, not judged).
- Also report: futile loots (container with no supplies) H-A vs HB0 share, waited durations, deaths per episode.
- Stopping rule: full 30 minutes; stop early only for an invalid run.

## Result (filled at batch end, 2026-11-14 09:30 CT)
- Data: `results/experiments-2026-11-14/b0_reliability.jsonl` (08:53-09:24).
- Numbers: 292 decisions in 12 episodes (4 deaths); 100% valid; latency median 2.69 s. Skills: fight 227, loot 32, eat 28, drink 2, flee 2, wait 1. Applicable uses and effect: eat 3 of 28 (11%), loot 3 of 31 (10%; 1 futile loot), drink 2 of 2 (too few to judge), bandage none. Median wait of one-shot skills 2.0 game s. H-A comparison (same analysis): eat 7/16 (44%), drink 3/14 (21%).
- Verdict: **FAILURE** against the pre-registered criteria (eat and loot each had >= 5 applicable uses with an effect rate below 40%).
- Diagnosis (client log, not part of the pre-registration): the client's `busy` check works (BUSY n=1-3 for 10+ s after a loot), but (a) EAT never enters the action queue: BUSY n=0 right after `eat` in 62 checks, so the eat action is rejected at once; the food sits in the backpack and `ISInventoryPaneContextMenu.transferIfNeeded` evidently does not run or does not exist under that name in 42.22, so the eat skill ends after 2 s with no effect (worse than H-A's fixed 8 s wait, which caught some eats after a loot had put food in the main inventory); (b) LOOT is queued (walk + transfer) but rarely completes before the 35 s cap: walking into the building to the container (luautils.walkAdj) or zombie interruptions stall it.
- Unexpected learnings: 1. With outcome feedback the planner fought far more (227 of 292 decisions) and looted less (32 vs 38): it saw 'no change' outcomes and stopped repeating futile actions, but it also had fewer successful non-fight actions available. 2. The busy check is a good diagnostic: it separates 'action never queued' (n=0 at once) from 'action queued but stuck' (n>0 until the cap). 3. Skill bugs, not the planner, are the bottleneck: the planner stayed 100% valid at ~2.7 s.
- Validity notes: valid run; the failure is in the skill layer, so the planner question (H-B) is untouched.
- MILESTONE IMPACT: modify H-B prerequisites: add H-B0b (each one-shot skill verified in isolation on the real client with a step-by-step log: eat from the backpack, drink, loot a container inside a building, bandage a wound) before any planner comparison.
- Follow-ups / next experiment: H-B0b skill unit tests in game (explicit transfer action to the main inventory before eating/drinking, walk-then-transfer for loot with a door/path check, bandage on an induced wound).
