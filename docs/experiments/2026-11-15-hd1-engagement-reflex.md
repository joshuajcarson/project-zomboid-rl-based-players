# H-D1 Division of labour: an engagement reflex takes fighting away from the planner
- Date / time: 2026-11-15, pre-registered ~13:10 CT
- Milestone: H-D1 (division of labour: real-time skill vs planner), design in `docs/planner-learning.md`
- Question: does the planner do better when a real-time reflex handles engagement (a zombie within 3 tiles: fight, or flee below 35 hp, exactly the rule planner's engagement branch) and the planner only decides the rest (needs, looting, bandaging, moving when nothing is close)?
- Background:
  - HB-F: the planner wins on needs (0.17 vs 0.33) but dies more than the rule planner (0.19 vs 0.08).
  - H-L1: lessons that pushed the planner into fight/flee timing made it die more (0.35 vs 0.18).
  - Both point to engagement as the planner's weak spot: about 3 s latency, decisions made for a state that has already changed.
- Hypothesis: llmR dies less and ends with more hp than llm, while keeping the planner's needs advantage.

## Pre-registered (fixed before running; never edited afterwards)
- Arms: `llm` (plain planner, as HB-F) and `llmR` (same planner; while the nearest zombie is <= 3 tiles the reflex runs each game step: fight, or flee below 35 hp; planner answers that arrive during the reflex are dropped). `--reflex 3`.
- Scenario: the fixed scenario as HB-F / H-L1 (`hybrid_run.py --fixes`, same supplies, box, hunger and thirst 0.6, 2 zombies on the 8-14 ring, 120 s episodes, Sonnet).
- Sessions: two of 110 minutes on fresh servers, seeds 71 and 73 (`hd1_s1.jsonl`, `hd1_s2.jsonl`), arms interleaved `llm,llmR`. Target >= 30 episodes per arm pooled; if short, a third session (seed 79) runs for the sample target alone.
- Watchdog on each session: `--arms llm,llmR --hunger 0.6 --thirst 0.6 --supplies --supplies-at 10753,9407`.
- Analysis: `python scripts/hl_analyze.py --a llm --b llmR hd1_s1.jsonl hd1_s2.jsonl` (end hp with deaths as 0, deaths, needs of survivors, wasted loots); the share of reflex steps per episode is reported.
- SUCCESS if llmR - llm end hp z >= 2 AND llmR needs <= llm needs + 0.10. (The script's alternative wasted-loot route does not apply here; only the hp route counts.)
- FAILURE if llmR - llm end hp z <= -1 OR llmR needs > llm needs + 0.15.
- INCONCLUSIVE otherwise.
- Stopping rule: each session runs its 110 minutes; stop early only on a scenario watchdog alert (start state, stray, immobile, step-1, stall, idle), a crash or a stall; a stopped session is rerun from scratch.
- Exploratory only: llmR next to the HB-F rule-planner numbers (different sessions, not evidence).

## Run log

## Result (filled at batch end, 2026-11-15 16:45 CT)
- Data: `results/experiments-2026-11-15/hd1_s1.jsonl` (seed 71, 12:53-14:43), `hd1_s2.jsonl` (seed 73, 14:44-16:35). Watchdog clean on both, 0 step-1 deaths.
- Numbers (pooled, `hl_analyze.py --a llm --b llmR`):

| Arm | n | died | end hp | needs | wasted loots / ep |
|---|---|---|---|---|---|
| llm | 39 | 0.26 | 59.3 (se 6.4) | 0.200 (se 0.043) | 0.28 |
| llmR (reflex) | 38 | 0.08 | 70.7 (se 4.7) | 0.197 (se 0.034) | 0.34 |

  llmR - llm: end hp +11.4 (z 1.44), deaths -0.18 (z -2.12), needs -0.003, wasted loots +0.06. Per session: s1 hp +12.5, deaths -0.16; s2 hp +10.0, deaths -0.19 (same direction in both). The reflex ran in 33 of 39 llmR episodes, about 14 game steps per episode.
- Verdict: **INCONCLUSIVE** on the pre-registered primary (end hp z 1.44 < 2; no failure condition holds). The death rate drops from 0.26 to 0.08 (z -2.1, a secondary measure here) and needs are unchanged.
- Exploratory (other sessions, not evidence): llmR's death rate 0.08 matches the rule planner's in HB-F (0.08), with needs 0.20 vs the rule planner's 0.33.
- Division of labour: handing engagement to a real-time reflex removed most of the planner's excess deaths without touching its needs advantage. This is the first direct evidence for the layered design (a reflex for fighting, the planner for needs and looting).
- MILESTONE IMPACT: modify. Under the acceptance rule an inconclusive test gets more sessions, never new thresholds: H-D1b pre-registers two confirmation sessions (seeds 79, 83), pooled with these two, same criteria, final.
