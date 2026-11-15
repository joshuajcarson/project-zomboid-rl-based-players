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

## Result (filled at batch end)
- Data: `results/experiments-2026-11-14/hb_s3.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- MILESTONE IMPACT: (pending)
