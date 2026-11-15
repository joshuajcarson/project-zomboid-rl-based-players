# HBfix4 Scenario fixes validated (rerun: mobility probe redraws fenced-in spawns)
- Date / time: 2026-11-15 ~01:42 CT
- Milestone: track H, H-B2 preparation
- Question: same as HBfix to HBfix3.
- Change from HBfix3: mobility probe under `--fixes` (after each reset, walk toward the shelf for 3 game s; redraw the spawn, up to 3 times, if the character moved < 1 tile; logged as `probe_fail` rows). The watchdog has the `immobile` check and the once-per-failing-use skill_health.

## Pre-registered (fixed before running; never edited afterwards)
- Design: HBfix3's command with `--seed 29 --out results/experiments-2026-11-15/hbfix4.jsonl`, 45 minutes, arms llm,rule, same watchdog flags.
- SUCCESS / FAILURE / INCONCLUSIVE: HBfix's criteria unchanged. The immobile check counts as a scenario alert (FAILURE), like stray and start-state.
- Stopping rule: 45 minutes; stop early only on a start-state, stray, immobile, step-1, stall or idle alert, a crash, or a stall.

## Run log

## Result (filled at batch end, 2026-11-15 01:45 CT)
- Data: `results/experiments-2026-11-15/hbfix4.jsonl` (01:30-01:37, 2 episodes, stopped early by the stopping rule on an immobile alert at 01:36).
- Numbers: 0 probe redraws. Episode 1 (llm): a loot at the shelf ran 20 s and was interrupted by a zombie (the character died). Episode 2 (rule): the shelf showed 3/2/2 supplies, but the rule planner looted natural counters in the other building instead: 7 loots, 0 gained, mostly ending in 2 s.
- Verdict: **FAILURE** (a scenario alert fired, as pre-registered). Not a test of the skills: the run lasted 2 episodes.
- Cause: the HBfix3 change that remembers failed containers for the whole session blacklisted the seeded shelf after one interrupted loot. Both planners then avoided the shelf for the rest of the session and chased unreachable counters.
- Fix:
  - With `--fixes`, only quick failures (the loot ends within 3 s with nothing taken: no path, or nothing queued) are remembered for the session.
  - Any other failed loot is remembered for that episode only.
  - The seeded container is never blacklisted for the session.
- Unexpected learnings: the counters in the other building can be walked to (the character got there), but every loot there ends in 2 s with nothing taken. Those items are probably not transferable this way; not investigated (natural world containers are out of scope for this scenario).
- MILESTONE IMPACT: none (HBfix5 next, same criteria).
