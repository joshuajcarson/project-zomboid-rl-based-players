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

## Result (filled at batch end, 2026-11-15 08:15 CT)
- Data: `results/experiments-2026-11-15/hbf_s1.jsonl` (seed 41), `hbf_s2.jsonl` (seed 43), `hbf_s3.jsonl` (seed 47, run for the sample target). All three sessions: watchdog clean, 0 step-1 deaths.
- Numbers (pooled over 3 sessions):

| Arm | n | died | end hp | needs (hunger + thirst) | wasted loots / ep |
|---|---|---|---|---|---|
| llm | 37 | 0.19 (se 0.07) | 63.3 (se 6.3) | 0.166 (se 0.014) | 0.19 |
| rule | 36 | 0.08 (se 0.05) | 75.6 (se 4.9) | 0.328 (se 0.028) | 0.06 |
| idle | 35 | 0.80 (se 0.07) | 18.2 (se 6.5) | 1.224 | 0 |

  llm - rule: died +0.11, needs -0.161, end hp -12.2 (z -1.54). llm - idle: end hp +45.2 (z 5.01).
- Verdict: **INCONCLUSIVE**. The death-rate condition for SUCCESS (llm <= rule + 0.10) misses by 0.01; no FAILURE condition holds (deaths +0.11 < +0.25, hp -12.2 > -20, vs idle z 5.0).
- Reading:
  - On the fixed scenario the planner keeps needs at half the rule planner's level (0.17 vs 0.33) and is far better than doing nothing.
  - It dies more (19% vs 8%) and ends with about 12 hp less: a fighting and disengaging weakness, not a needs weakness.
  - Same pattern as H-B (needs 0.20 vs 0.30, deaths 0.22 vs 0.21), but with drink and thirst counting, the needs gap is larger and the death gap shows.
- Division of labour: the needs advantage comes from planner judgement (eating and drinking at the right moments, looting once). The death gap comes from when the planner chooses fight or flee, which a dedicated engagement skill or lessons should fix (H-L1, H-D1).
- MILESTONE IMPACT: modify. H-F is INCONCLUSIVE (no more sessions planned: the comparison moves to H-L1, which targets exactly this gap). The death and hp gap becomes H-L1's primary target and H-D1's motivation.
- Unexpected learnings (RECONSTRUCTED 2026-11-16 from the Reading above): with drink and thirst counting, the planner's needs advantage doubled (0.17 vs 0.33), while the death gap (0.19 vs 0.08) appeared; the gap is in engagement, not needs.
- Validity notes (RECONSTRUCTED): watchdog clean in all 3 sessions, 0 step-1 deaths; arms interleaved per session; n 37/36/35 pooled over 3 sessions (the third was added for the sample target, pre-registered). The death condition missed by 0.01, so the INCONCLUSIVE is a close call.
- Follow-ups: H-L1 (lessons) then H-D1 (engagement reflex); see their cards.
