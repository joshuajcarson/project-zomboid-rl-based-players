# HB0f Hybrid planner: reliability rerun with supplies in a known reachable container
- Date / time: 2026-11-14, pre-registered ~14:50 CT
- Milestone: track H, prerequisite of H-B (same question as H-B0 / HB0c-e)
- Question: when the seeded supplies sit in a container the character can reach (metal shelves at 10753,9407, reached in the 13:05 interactive test), does loot reach its effect when applicable?
- Hypothesis: loot >= 70% when applicable; eat and bandage stay ~100%.

## Pre-registered (fixed before running; never edited afterwards)
- Design: as HB0e (30 min, Sonnet, supplies Base.Apple:3, Base.WaterBottle:2, Base.Bandage:2 at each episode start, loot by coordinates, failed-container memory, 2 zombies on an 8-14 ring) except: supplies seeded with server `seedat` into the container at 10753,9407, and the spawn box is 10740,9385 .. 10770,9400 (so the shelf is within ~25 tiles). `scripts/hybrid_run.py --minutes 30 --model sonnet --supplies Base.Apple:3,Base.WaterBottle:2,Base.Bandage:2 --supplies-at 10753,9407 --box 10740 9385 10770 9400 --out results/experiments-2026-11-14/b0f_reliability.jsonl`.
- Criteria: IDENTICAL to H-B0 / HB0c-e (applicable definitions; SUCCESS: each of eat, drink, loot with >= 5 applicable uses >= 70% effect, >= 95% valid, median latency <= 15 s, no crash; FAILURE: any of them with >= 5 applicable uses below 40%, valid < 80%, or a crash prevents the run; INCONCLUSIVE otherwise).
- Stopping rule: full 30 minutes; stop early only for an invalid run.

## Result (filled at batch end, 2026-11-14 15:14 CT)
- Data: `results/experiments-2026-11-14/b0f_reliability.jsonl` (14:42-15:12).
- Numbers: 208 decisions, 13 episodes (4 deaths); 100% valid, median 2.55 s. Skills: fight 103, eat 36, wait 33, flee 20, loot 10, bandage 6. Effect when applicable: eat 35/36 (97%), loot 10/10 (100%), bandage 4/4 (100%), drink 0 applicable (never chosen: apples keep thirst low). Loot waits 12-31 s (walk + transfers to the known shelf).
- Verdict: **SUCCESS** against the pre-registered criteria (eat and loot >= 70% with >= 5 applicable uses; drink had < 5 applicable uses and is reported, not judged; 100% valid; 2.55 s median; no crash).
- Unexpected learnings: 1. with reachable supplies the planner looted far less (10) and ate far more (36): it got what it needed in one trip; 2. drink remains untested in planner runs (scenario never makes thirst matter); 3. the whole H-B0 chain (HB0 -> HB0f) traced loot failures to: rotten/client-only items, renumbering, unsuitable containers, and unreachable containers whose failed path drops the action queue.
- MILESTONE IMPACT: H-B0 gate PASSED; H-B (planner vs rule planner vs idle on survival) is next. Caveat to carry: drink untested; supplies placed in a known reachable container.
