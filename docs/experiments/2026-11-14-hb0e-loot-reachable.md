# HB0e Hybrid planner: reliability rerun with storage-only seeding and failed-container memory
- Date / time: 2026-11-14, pre-registered ~14:20 CT
- Milestone: track H, prerequisite of H-B (same question as H-B0 / HB0c / HB0d)
- Question: with supplies seeded only into storage containers (crate, shelves, counter, fridge, wardrobe, dresser, desk, sidetable, boxes; no fireplaces, barbecues, bins, stoves) and the planner told which containers' loot failed this episode, does loot reach its effect when applicable?
- Hypothesis: loot >= 70% when applicable; eat stays near 100%.

## Pre-registered (fixed before running; never edited afterwards)
- Design: identical to HB0d (30 min, Sonnet, supplies Base.Apple:3, Base.WaterBottle:2, Base.Bandage:2 seeded server-side at each episode start, loot by coordinates) plus: server `seed` restricted to storage container types; the harness keeps a per-episode set of containers whose `lootat` brought nothing and marks them '[looting here failed this episode]' in the planner's container list; `lootat` logs the walk result and queue length. `scripts/hybrid_run.py --minutes 30 --model sonnet --supplies Base.Apple:3,Base.WaterBottle:2,Base.Bandage:2 --out results/experiments-2026-11-14/b0e_reliability.jsonl`.
- Criteria: IDENTICAL to H-B0 / HB0c / HB0d (applicable definitions; SUCCESS: each of eat, drink, loot with >= 5 applicable uses >= 70% effect, >= 95% valid, median latency <= 15 s, no crash; FAILURE: any of them with >= 5 applicable uses below 40%, valid < 80%, or a crash prevents the run; INCONCLUSIVE otherwise).
- Stopping rule: full 30 minutes; stop early only for an invalid run.

## Result (filled at batch end)
- Data: `results/experiments-2026-11-14/b0e_reliability.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
