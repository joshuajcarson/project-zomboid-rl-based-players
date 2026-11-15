# H-D1b Engagement reflex: confirmation sessions (pooled with H-D1)
- Date / time: 2026-11-15, pre-registered ~16:47 CT
- Milestone: H-D1
- Why: H-D1 came out INCONCLUSIVE on its primary metric (end hp +11.4, z 1.44) with deaths 0.26 -> 0.08 (z -2.1). The acceptance rule (CLAUDE.md) says an inconclusive test gets more sessions under the same criteria.
- Design: identical to `2026-11-15-hd1-engagement-reflex.md` (arms llm,llmR, --reflex 3, the fixed scenario, 110-minute sessions, the same watchdog), two more sessions on fresh servers with seeds 79 and 83 (`hd1_s3.jsonl`, `hd1_s4.jsonl`).

## Pre-registered (fixed before running; never edited afterwards)
- Analysis: `hl_analyze.py --a llm --b llmR hd1_s1.jsonl hd1_s2.jsonl hd1_s3.jsonl hd1_s4.jsonl` (all four sessions pooled).
- SUCCESS / FAILURE / INCONCLUSIVE: H-D1's criteria unchanged (SUCCESS: end hp z >= 2 and needs <= llm + 0.10; FAILURE: end hp z <= -1 or needs > llm + 0.15). The four-session verdict is final for H-D1.
- Also reported (not judged): deaths z on the four-session pool.
- Stopping rule: as H-D1; a stopped session is rerun from scratch.

## Run log

## Result (filled at batch end)
- Numbers: (pending)
- Verdict: (pending)
- MILESTONE IMPACT: (pending)
