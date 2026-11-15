# HB-F Planner vs rules vs idle on the fixed scenario
- Date / time: 2026-11-15, pre-registered ~02:45 CT
- Milestone: track H, H-B2 (first step: does the H-B result hold once thirst, drink and looting really matter?)
- Question: on the validated fixed scenario (`hybrid_run.py --fixes`: thirst holds, the character starts with nothing, supplies only in the seeded shelf, skills reliable), is the Sonnet planner still non-inferior to the rule planner and better than idle?
- Hypothesis: same as H-B: llm non-inferior to rule on deaths and needs; both beat idle on end health.

## Pre-registered (fixed before running; never edited afterwards)
- Design: arms `llm,rule,idle` interleaved by episode; `scripts/hybrid_run.py --fixes --minutes 110 --model sonnet --arms llm,rule,idle --supplies Base.Apple:3,Base.WaterBottle:2,Base.Bandage:2 --supplies-at 10753,9407 --box 10740 9385 10770 9400 --seed S --out results/experiments-2026-11-15/hbf_sN.jsonl`. Two sessions on fresh servers: seed 41, then 43. Hunger and thirst 0.6, 2 zombies on the 8-14 ring, 120 s episodes. Target >= 30 episodes per arm pooled; if the two sessions fall short, a third session (seed 47) runs because of the sample target alone, decided before looking at pooled results.
- Watchdog on every session: `--arms llm,rule,idle --hunger 0.6 --thirst 0.6 --supplies --supplies-at 10753,9407`, no known deviations.
- Metrics per episode: died, end hp (deaths count as 0), needs = end hunger + thirst of survivors (lower is better; thirst now counts). Analysis: `scripts/hb_analyze.py` pooled.
- SUCCESS if: (llm death rate <= rule + 0.10) AND (llm needs <= rule needs + 0.10) AND (llm end hp > idle end hp with z >= 2).
- FAILURE if: (llm death rate > rule + 0.25) OR (llm end hp < rule end hp - 20) OR (llm vs idle end hp z < 1).
- INCONCLUSIVE otherwise.
- Stopping rule: each session runs its 110 minutes; stop early only on a scenario watchdog alert (start state, stray, immobile, step-1, stall, idle), a crash, or a stall. Any such stop invalidates that session, which is rerun from scratch.

## Run log
- Session 1 (seed 41, 02:35-04:25): 36 scored episodes; watchdog clean; 0 step-1 deaths.
- Session 2 (seed 43, 04:25-06:15): 35 scored episodes; watchdog clean; 0 step-1 deaths.
- Two-session pool: n 24/24/23, under the >= 30 per arm target, so session 3 (seed 47) runs as pre-registered.

## Result (filled at batch end)
- Data: `results/experiments-2026-11-15/hbf_s1.jsonl`, `hbf_s2.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- MILESTONE IMPACT: (pending)
