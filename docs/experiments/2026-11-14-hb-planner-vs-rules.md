# HB Hybrid planner vs rule planner vs idle on a short survival scenario
- Date / time: 2026-11-14, pre-registered ~15:25 CT
- Milestone: track H, H-B (does a language-model planner match a hand-written rule planner over the same skills?)
- Question: in a short survival scenario (hungry and thirsty, supplies in a reachable shelf, 2 zombies), is the Sonnet planner non-inferior to a rule planner using the same skills, and are both better than doing nothing?
- Hypothesis: llm is non-inferior to rule on deaths and needs; both clearly beat idle on end health.

## Pre-registered (fixed before running; never edited afterwards)
- Design: arms interleaved by episode in one session, `--arms llm,rule,idle` (llm = Sonnet via claude -p; rule = `hybrid.rule_decide` priority planner, one decision per game second; idle = always wait); scenario as HB0f (spawn box 10740,9385 .. 10770,9400; supplies Base.Apple:3, Base.WaterBottle:2, Base.Bandage:2 seeded with `seedat` into the shelf at 10753,9407 at each episode start; server-side hunger/thirst 0.6; 2 zombies on an 8-14 ring; 120 game-second episodes). Two sessions of 110 minutes each (fresh server between), target >= 15 episodes per arm per session, >= 30 per arm pooled. `scripts/hybrid_run.py --minutes 110 --model sonnet --arms llm,rule,idle --supplies Base.Apple:3,Base.WaterBottle:2,Base.Bandage:2 --supplies-at 10753,9407 --box 10740 9385 10770 9400 --out results/experiments-2026-11-14/hb_s<N>.jsonl` (seed 7 then 11).
- Metrics per episode: died (1/0), end hp, end hunger + thirst ('needs', lower is better), supplies carried at the end (food + water + bandages). Pooled over both sessions.
- SUCCESS if: (llm death rate <= rule death rate + 0.10) AND (llm mean needs <= rule mean needs + 0.10) AND (llm mean end hp > idle mean end hp with z >= 2).
- FAILURE if: (llm death rate > rule death rate + 0.25) OR (llm mean end hp < rule mean end hp - 20) OR (llm mean end hp vs idle z < 1).
- INCONCLUSIVE otherwise.
- Stopping rule: each session runs its 110 minutes; stop early only for an invalid run (crash, client loop, skills broken). A usage-window pause between sessions is allowed (resume with session 2).

## Run log (not part of the pre-registration)
- Session 1 run 1 (15:14-15:30) INVALID, stopped under the stopping rule: the rule arm never advanced game time (instant decisions looped back to deciding without an env.step; episode 2 sat at step 3 after 452 decisions). Fix: rule and idle arms take one game step per decision; the llm arm is unchanged. Data kept as `hb_s1_run1_INVALID.jsonl`, excluded. Design and criteria unchanged.
- Session 1 run 2 (started 15:30): all three arms complete 120-step episodes. Deviation found in the first episodes: the server `stats` command sets hunger (0.6) but NOT thirst (it reads 0.0 at episode start in every arm). It affects all arms equally, so the run continues unchanged; the needs metric is in effect hunger only. Both sessions keep the same setup so they can be pooled; the thirst handler gets fixed after H-B.

## Result (filled at batch end)
- Data: `results/experiments-2026-11-14/hb_s1.jsonl`, `hb_s2.jsonl`
- Numbers: (pending)
- Verdict: (pending)
