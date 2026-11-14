# HB0d Hybrid planner: reliability rerun with loot by coordinates
- Date / time: 2026-11-14, pre-registered ~13:42 CT
- Milestone: track H, prerequisite of H-B (same question as H-B0 / H-B0c)
- Question: with loot sent as the coordinates of the container the planner chose (new client command `lootat|x|y`; HB0c's 'container N' was renumbered by distance while the planner thought), do eat / drink / loot reach their effect when applicable?
- Hypothesis: loot rises from 17% to >= 70%; eat and bandage stay near 100%.

## Pre-registered (fixed before running; never edited afterwards)
- Design: identical to HB0c (supplies Base.Apple:3, Base.WaterBottle:2, Base.Bandage:2 seeded server-side at each episode start; 30 minutes; Sonnet) except loot is dispatched as `lootat|x|y` with the chosen container's coordinates from the survey the planner saw. `scripts/hybrid_run.py --minutes 30 --model sonnet --supplies Base.Apple:3,Base.WaterBottle:2,Base.Bandage:2 --out results/experiments-2026-11-14/b0d_reliability.jsonl`.
- Criteria: IDENTICAL to H-B0 / HB0c (applicable definitions; SUCCESS: each of eat, drink, loot with >= 5 applicable uses has an effect rate >= 70%, plus >= 95% valid, median latency <= 15 s, no crash; FAILURE: any of them with >= 5 applicable uses below 40%, or valid < 80%, or a crash prevents the run; INCONCLUSIVE otherwise).
- Stopping rule: full 30 minutes; stop early only for an invalid run.

## Result (filled at batch end)
- Data: `results/experiments-2026-11-14/b0d_reliability.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
