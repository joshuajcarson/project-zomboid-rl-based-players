# HB0d Hybrid planner: reliability rerun with loot by coordinates
- Date / time: 2026-11-14, pre-registered ~13:42 CT
- Milestone: track H, prerequisite of H-B (same question as H-B0 / H-B0c)
- Question: with loot sent as the coordinates of the container the planner chose (new client command `lootat|x|y`; HB0c's 'container N' was renumbered by distance while the planner thought), do eat / drink / loot reach their effect when applicable?
- Hypothesis: loot rises from 17% to >= 70%; eat and bandage stay near 100%.

## Pre-registered (fixed before running; never edited afterwards)
- Design: identical to HB0c (supplies Base.Apple:3, Base.WaterBottle:2, Base.Bandage:2 seeded server-side at each episode start; 30 minutes; Sonnet) except loot is dispatched as `lootat|x|y` with the chosen container's coordinates from the survey the planner saw. `scripts/hybrid_run.py --minutes 30 --model sonnet --supplies Base.Apple:3,Base.WaterBottle:2,Base.Bandage:2 --out results/experiments-2026-11-14/b0d_reliability.jsonl`.
- Criteria: IDENTICAL to H-B0 / HB0c (applicable definitions; SUCCESS: each of eat, drink, loot with >= 5 applicable uses has an effect rate >= 70%, plus >= 95% valid, median latency <= 15 s, no crash; FAILURE: any of them with >= 5 applicable uses below 40%, or valid < 80%, or a crash prevents the run; INCONCLUSIVE otherwise).
- Stopping rule: full 30 minutes; stop early only for an invalid run.

## Result (filled at batch end, 2026-11-14 14:10 CT)
- Data: `results/experiments-2026-11-14/b0d_reliability.jsonl` (13:38-14:08).
- Numbers: 197 decisions, 12 episodes (6 deaths); 100% valid, median 2.53 s. Skills: fight 107, loot 45, wait 26, eat 12, flee 5, bandage 2. Effect when applicable: eat 12/12 (100%), bandage 1/2, loot 6/45 (13%), drink 0 applicable.
- Verdict: **FAILURE** against the pre-registered criteria (loot < 40% with >= 5 applicable uses). Loot by coordinates did NOT fix it: the numbering mismatch was not the main cause.
- Diagnosis (not pre-registered): 34 of 45 loots ended after 2 s with an empty action queue (transfers rejected at once); one metal shelf at 10804,9406 was tried 17 times: seeded supplies accumulated there across episodes (client shows 14 queued items) but its transfers are rejected (unreachable / different room or floor). All 6 successes were reachable containers (crate 5 tiles, bin 6.4, barbecue 1.6, first shelf at 18 tiles after 27 s). Seeding puts items into the container nearest the spawn, including fireplaces, barbecues and dressers, some of which cannot be looted this way.
- Unexpected learnings: 1. the planner keeps choosing the container that shows the most supplies even after repeated 'no change' outcomes for it (the outcome line does not say WHICH container failed); 2. seeded supplies accumulate in unreachable containers across episodes; 3. eat stays at 100%.
- MILESTONE IMPACT: none to acceptance; next HB0e: (a) seed only into storage containers on the player's floor that the player can path to (allowlist: crate, shelves, counter, fridge, cabinet, wardrobe, dresser, desk, sidetable) and clear old seeded items; (b) the harness remembers containers whose loot failed this episode and marks them in the state ('loot here failed'); (c) loot logs walkAdj's result and the queue right after queueing.
