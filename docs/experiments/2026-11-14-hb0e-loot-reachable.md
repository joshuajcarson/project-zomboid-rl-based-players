# HB0e Hybrid planner: reliability rerun with storage-only seeding and failed-container memory
- Date / time: 2026-11-14, pre-registered ~14:20 CT
- Milestone: track H, prerequisite of H-B (same question as H-B0 / HB0c / HB0d)
- Question: with supplies seeded only into storage containers (crate, shelves, counter, fridge, wardrobe, dresser, desk, sidetable, boxes; no fireplaces, barbecues, bins, stoves) and the planner told which containers' loot failed this episode, does loot reach its effect when applicable?
- Hypothesis: loot >= 70% when applicable; eat stays near 100%.

## Pre-registered (fixed before running; never edited afterwards)
- Design: identical to HB0d (30 min, Sonnet, supplies Base.Apple:3, Base.WaterBottle:2, Base.Bandage:2 seeded server-side at each episode start, loot by coordinates) plus: server `seed` restricted to storage container types; the harness keeps a per-episode set of containers whose `lootat` brought nothing and marks them '[looting here failed this episode]' in the planner's container list; `lootat` logs the walk result and queue length. `scripts/hybrid_run.py --minutes 30 --model sonnet --supplies Base.Apple:3,Base.WaterBottle:2,Base.Bandage:2 --out results/experiments-2026-11-14/b0e_reliability.jsonl`.
- Criteria: IDENTICAL to H-B0 / HB0c / HB0d (applicable definitions; SUCCESS: each of eat, drink, loot with >= 5 applicable uses >= 70% effect, >= 95% valid, median latency <= 15 s, no crash; FAILURE: any of them with >= 5 applicable uses below 40%, valid < 80%, or a crash prevents the run; INCONCLUSIVE otherwise).
- Stopping rule: full 30 minutes; stop early only for an invalid run.

## Result (filled at batch end, 2026-11-14 14:42 CT)
- Data: `results/experiments-2026-11-14/b0e_reliability.jsonl` (14:10-14:40).
- Numbers: 181 decisions, 14 episodes (7 deaths); 100% valid, median 2.67 s. Skills: fight 79, loot 38, wait 31, eat 19, flee 9, bandage 5. Effect when applicable: eat 19/19 (100%), bandage 5/5 (100%), loot 11/36 (31%, HB0d 13%), drink 0 applicable.
- Verdict: **FAILURE** against the pre-registered criteria (loot < 40% with >= 5 applicable uses).
- Diagnosis (not pre-registered; from the new loot log): two shelves (10781,9411: 8 attempts; 10804,9406: 7) received the seeded supplies and each attempt queued 15-36 actions (walk accepted) yet the queue was empty 2 s later (20 of 38 loots waited 2 s): a failed path (shelf behind walls or a locked door) makes the game drop the whole queue. The failed-container memory limited repeats to about one per episode (memory is per episode). 'Nearest storage container to the spawn' is often unreachable.
- Unexpected learnings: 1. eat and bandage are solved (100% across two runs); 2. drink is never chosen because apples quench thirst (drink untested in a planner run); 3. queue_now in the loot log is a good reachability symptom.
- MILESTONE IMPACT: none to acceptance; next HB0f: seed into a fixed container proven reachable (metal shelves at 10753,9407, reached in the 13:05 interactive test) and a spawn box near it, so loot is tested on reachable supplies; keep the criteria.
