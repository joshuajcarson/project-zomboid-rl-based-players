# HB0f Hybrid planner: reliability rerun with supplies in a known reachable container
- Date / time: 2026-11-14, pre-registered ~14:50 CT
- Milestone: track H, prerequisite of H-B (same question as H-B0 / HB0c-e)
- Question: when the seeded supplies sit in a container the character can reach (metal shelves at 10753,9407, reached in the 13:05 interactive test), does loot reach its effect when applicable?
- Hypothesis: loot >= 70% when applicable; eat and bandage stay ~100%.

## Pre-registered (fixed before running; never edited afterwards)
- Design: as HB0e (30 min, Sonnet, supplies Base.Apple:3, Base.WaterBottle:2, Base.Bandage:2 at each episode start, loot by coordinates, failed-container memory, 2 zombies on an 8-14 ring) except: supplies seeded with server `seedat` into the container at 10753,9407, and the spawn box is 10740,9385 .. 10770,9400 (so the shelf is within ~25 tiles). `scripts/hybrid_run.py --minutes 30 --model sonnet --supplies Base.Apple:3,Base.WaterBottle:2,Base.Bandage:2 --supplies-at 10753,9407 --box 10740 9385 10770 9400 --out results/experiments-2026-11-14/b0f_reliability.jsonl`.
- Criteria: IDENTICAL to H-B0 / HB0c-e (applicable definitions; SUCCESS: each of eat, drink, loot with >= 5 applicable uses >= 70% effect, >= 95% valid, median latency <= 15 s, no crash; FAILURE: any of them with >= 5 applicable uses below 40%, valid < 80%, or a crash prevents the run; INCONCLUSIVE otherwise).
- Stopping rule: full 30 minutes; stop early only for an invalid run.

## Result (filled at batch end)
- Data: `results/experiments-2026-11-14/b0f_reliability.jsonl`
- Numbers: (pending)
- Verdict: (pending)
