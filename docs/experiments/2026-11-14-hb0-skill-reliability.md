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

## Result (filled at batch end)
- Data: `results/experiments-2026-11-14/b0_reliability.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
