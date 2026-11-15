# HB3 H-B confirmation session (planner vs rules vs idle, session 3)
- Date / time: 2026-11-14, pre-registered ~21:12 CT (after H-B sessions 1-2; written before session 3 runs)
- Milestone: track H, H-B
- Question: does the H-B result (llm non-inferior to rule, better than idle) hold once the pooled sample reaches the pre-registered >= 30 episodes per arm?
- Why: H-B passed its criteria on 25/23/23 episodes; the pre-registered target was >= 30 per arm (the shortfall comes from revive time and was known before the pooled result). This session exists to reach the sample target, not because of the effect size.

## Pre-registered (fixed before running; never edited afterwards)
- Design: identical to H-B (`2026-11-14-hb-planner-vs-rules.md`): same command, scenario, arms `llm,rule,idle`, 110 minutes, seed 13, fresh server. Known deviations unchanged (thirst not set; 8-container survey) so the data pools. The watchdog is attached for the whole session (`--known thirst,supplies`).
- Analysis: `hb_analyze.py hb_s1.jsonl hb_s2.jsonl hb_s3.jsonl` (pooled over 3 sessions).
- SUCCESS / FAILURE / INCONCLUSIVE: the H-B criteria, unchanged, on the 3-session pool. This verdict is final for H-B whatever it shows; no fourth session for H-B unless the run is invalid.
- Stopping rule: 110 minutes; stop early only on a watchdog alert that is not a known deviation, a crash or a stall.

## Run log

## Result (filled at batch end, 2026-11-14 23:00 CT)
- Data: `results/experiments-2026-11-14/hb_s3.jsonl` (seed 13, 21:05-22:56, 35 episodes). Watchdog: no alerts beyond the known deviations; 0 step-1 deaths.
- Session 3 alone: llm/rule/idle n 12/11/11, died 0.33/0.18/0.73, end hp 57.3/68.0/27.3, needs 0.073/0.287/0.658 (alone it would be INCONCLUSIVE; single sessions are not the test).
- Pooled over 3 sessions (the pre-registered test):

| Arm | n | died | end hp | needs |
|---|---|---|---|---|
| llm (Sonnet) | 37 | 0.22 (se 0.07) | 64.7 (se 6.4) | 0.197 (se 0.044) |
| rule | 34 | 0.21 (se 0.07) | 62.9 (se 6.3) | 0.297 (se 0.017) |
| idle | 34 | 0.62 (se 0.08) | 33.3 (se 7.8) | 0.648 (se 0.012) |

  llm - rule: died +0.01, needs -0.100, hp +1.8 (z 0.20). llm - idle: hp +31.4 (z 3.13).
- Verdict: **SUCCESS** (death rate within rule + 0.10: +0.01; needs within rule + 0.10: -0.10, better; hp beats idle z 3.13 >= 2). The sample target (>= 30 per arm) is met. H-B is passed: the Sonnet planner is non-inferior to the hand-written rule planner over the same skills and clearly better than doing nothing.
- Planner this session: 170 decisions, 100% valid, median 2.9 s; loot 7/8 effective (much better than s1-s2's 16/59, likely because the shelf had more visible supplies; not tested).
- Unexpected learnings: the llm keeps hunger much lower than the rule planner in every session (pooled needs 0.20 vs 0.30) while dying as often; session-to-session swings of 20+ hp per arm show again why single sessions decide nothing.
- MILESTONE IMPACT: modify. H-B done. Next for track H: fix the scenario limits (thirst not set, 8-container survey cap, shelf accumulation), then a harder scenario where planning matters more than reflexes (supplies spread over several buildings, longer episodes); H-C (two agents cooperating) needs M6 (memory for two real clients).
