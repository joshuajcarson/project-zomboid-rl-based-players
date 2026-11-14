# HA Hybrid planner Stage A: plumbing on the real client
- Date / time: 2026-11-14, pre-registered ~08:45 CT
- Milestone: new track H (hybrid planner: a language model picks high-level skills over scripted / learned low-level skills), stage A; supersedes the M3 learned-fighter route if it works (decision 2026-11-14 with the user)
- Question: can a `claude -p` planner (Claude Sonnet, structured JSON, no tools) drive the real client through a skill menu reliably and fast enough, and do the new skills (eat, drink, bandage, loot) actually change the game state?
- Hypothesis: yes: a one-off test gave 5.1 s per Sonnet decision and 4.0 s per Haiku decision with schema-valid output; the new Lua skills compiled in game (bot reload OK on build 42.22.2).

## Pre-registered (fixed before running; never edited afterwards)
- Design: `scripts/hybrid_run.py --minutes 30 --model sonnet --out results/experiments-2026-11-14/a_plumbing.jsonl` on the real client, build 42.22.2; spawn box 10730,9380 .. 10810,9440 (Muldraugh residential area next to the old arena; containers expected); 2 zombies on an 8-14 tile ring per episode; 120 game-second episodes; character set to hunger 0.6 and thirst 0.6 at each episode start (`setstats`); skills: fight (scripted charge), flee, wait, eat, drink, bandage, loot (container from the survey list). The planner runs in a background thread while the current skill continues. Every decision is logged with latency, validity, the state it saw, and for one-shot skills the effect measured by a survey before and after.
- SUCCESS if ALL hold: (1) >= 95% of planner calls return a valid skill; (2) median decision latency <= 15 s; (3) the run completes its 30 minutes without a crash of the harness, client or server; (4) every one-shot skill that the planner chooses at least twice shows its intended effect at least once (eat: food -1 or hunger down; drink: thirst down or water -1; loot: food + water + bandages up; bandage: bleeding down). A skill never chosen is recorded as UNTESTED, not as a failure.
- FAILURE if ANY: valid decisions < 80%; median latency > 30 s; the harness cannot complete a 30-minute run after one fix attempt; a skill chosen >= 3 times never shows its effect.
- INCONCLUSIVE otherwise.
- Stopping rule: run the full 30 minutes; stop early only for an invalid run (crash, dead client loop, server down).
- Invariants: one bat, in arena region; the planner must never call movement during a one-shot timed action (enforced by the harness).

## Result (filled at batch end)
- Data: `results/experiments-2026-11-14/a_plumbing.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
