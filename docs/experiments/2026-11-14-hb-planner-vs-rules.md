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
- Session 1 run 2 (15:30-17:21, 48 episodes) INVALID (found at the session-1 check, before session 2 produced data): every episode that follows a real death is recorded as dead at step 1 with hp 100 (11 of 48 episodes). The previous episode ends at death_hp, the zombie finishes the character during the next reset after the revive check, and the reset carried on. Because arms rotate llm, rule, idle, the arm after idle (llm) absorbed 7 of these. Raw scoring gave FAILURE, but that is the artifact, not the planner. Data kept as `hb_s1_run2_INVALID.jsonl`. Fix in `pzrl/env.py` reset: a check_alive failure revives and redoes the reset (max 3). `hb_analyze.py` now counts step-1 deaths as an invariant (must be 0). Session 2's first launch was stopped before any episode (`hb_s2_run1_INVALID.jsonl`, empty). Both sessions rerun from scratch, seeds 7 and 11, design and criteria unchanged.
- Session 1 run 3 (17:23-19:13) valid (0 step-1 deaths). Session 2 started 19:14; the run watchdog (`scripts/watchdog.py`) was attached at 20:40 with known deviations `thirst` and `supplies`. Replaying it over all runs found the supplies deviation: the survey lists only the 8 nearest containers, so spawns at the west edge of the box (x 10740-10745) do not see the seeded shelf (session 1: 2 episodes, session 2 so far: 5, spread over all arms). Not a validity failure (all arms equally; the planners re-survey each decision), recorded as a scenario limitation.

## Result (filled at batch end)
- Data: `results/experiments-2026-11-14/hb_s1.jsonl`, `hb_s2.jsonl`
- Numbers: (pending)
- Verdict: (pending)
