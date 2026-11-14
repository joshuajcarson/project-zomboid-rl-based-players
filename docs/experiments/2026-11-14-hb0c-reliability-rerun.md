# HB0c Hybrid planner: reliability rerun with server-seeded supplies
- Date / time: 2026-11-14, pre-registered ~13:10 CT
- Milestone: track H, prerequisite of H-B (same question as H-B0)
- Question: with the fixes found in H-B0b's interactive debugging (game entry points for eat/drink, edible-only food count, server-known items seeded into the nearest container at each episode start), do eat / drink / loot achieve their effect when applicable, in a full planner run with zombies?
- Hypothesis: yes: in isolation loot, eat and drink all worked once the items were real and server-known.

## Pre-registered (fixed before running; never edited afterwards)
- Design: as H-B0 (real client, build 42.22.2, Sonnet via claude -p, spawn box 10730,9380 .. 10810,9440, 2 zombies on an 8-14 ring, 120 game-second episodes, server-side hunger/thirst 0.6 at episode start, survey radius 30, wait-for-queue one-shot skills, last-skill outcome in the state) plus `--supplies Base.Apple:3,Base.WaterBottle:2,Base.Bandage:2` seeded server-side into the container nearest the player at each episode start. 30 minutes: `scripts/hybrid_run.py --minutes 30 --model sonnet --supplies Base.Apple:3,Base.WaterBottle:2,Base.Bandage:2 --out results/experiments-2026-11-14/b0c_reliability.jsonl`.
- Applicable / effect definitions and thresholds: IDENTICAL to H-B0 (applicable: eat with edible food > 0; drink with water > 0; loot of a listed container showing food + water + bandages > 0; bandage with bleeding > 0 and bandages > 0. SUCCESS: each of eat, drink, loot with >= 5 applicable uses has an effect rate >= 70%, plus >= 95% valid decisions, median latency <= 15 s, no crash. FAILURE: any of eat, drink, loot with >= 5 applicable uses below 40%, or valid < 80%, or a crash prevents the run. INCONCLUSIVE otherwise.)
- Stopping rule: full 30 minutes; stop early only for an invalid run.

## Result (filled at batch end)
- Data: `results/experiments-2026-11-14/b0c_reliability.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
