# HBfix3 Scenario fixes validated (rerun: loot by container index, session-wide failure memory)
- Date / time: 2026-11-15 ~00:47 CT
- Milestone: track H, H-B2 preparation
- Question: same as HBfix / HBfix2.
- Change from HBfix2: survey reports each container's index on its square (`ci`); `lootat|x|y|ci` loots that container (several containers share some squares and the first was always taken). With `--fixes`, containers where looting failed stay marked for the whole session ("[looting here failed earlier]") for both planners.

## Pre-registered (fixed before running; never edited afterwards)
- Design: HBfix2's command with `--seed 23 --out results/experiments-2026-11-14/hbfix3.jsonl`, 45 minutes, arms llm,rule, same watchdog flags.
- SUCCESS / FAILURE / INCONCLUSIVE: HBfix's criteria unchanged (no watchdog alert other than planner_health/skill_health; drink >= 5 uses at >= 70%; eat and loot each >= 70% with >= 5 uses; FAILURE if any is < 50% or a scenario alert fires).
- Stopping rule: 45 minutes; stop early only on a start-state, stray, step-1, stall or idle alert, a crash, or a stall.

## Run log
- 00:53 watchdog skill_health alert (loot 2 of last 10). Not a stopping condition under this card (judged through criterion 3). Cause: in episode 5 the character never moved (position 10769,9390 for all 12 decisions, fights included), so 10 loots ended in 2 s. HBfix episode 1 had the same freeze (19 decisions at 10755,9397); the spawn square is not the cause (similar spawns worked). Added watchdog check `immobile` (5 loots in a row at one position ending within 3 s with nothing taken). The run continues to its 45 minutes; the cause is the next thing to investigate.

## Result (filled at batch end, 2026-11-15 01:40 CT)
- Data: `results/experiments-2026-11-14/hbfix3.jsonl` (00:40-01:27, 18 episodes; 4 deaths; planner 150/150 valid).
- Numbers:
  - Skills: drink 8/8, eat 19/19, bandage 4/5, loot 9/31 = 29% (llm 7/29, rule 2/2).
  - Watchdog: the immobile alert (added during the run) fired on episode 5. No start-state, stray or step-1 alerts.
- Verdict: **FAILURE** (loot below 50%; a scenario alert fired).
- Cause: in episode 5 the character could not move at all. Its position stayed at 10769,9390 for all 121 steps, through 19 loots and the fights. The zombies never reached it (hp stayed 100). The client log shows no fence climbing in that episode, while the episode before it had about 60 ClimbWall attempts. Most likely the spawn was a fenced-in pocket: the pathfinder found no route out and nothing could get in. HBfix episode 1 (10755,9397) was the same; spawns 1-3 tiles away from it worked fine, so a smaller box would not fix it. Excluding episode 5 (exploratory only, not the verdict): loot 9/12 = 75%, so the container-index fix worked.
- Unexpected learnings:
  1. The spawn box has unreachable pockets that freeze a whole episode, and they look like skill failures.
  2. The skill_health alert repeated every 50 rows; it now fires only when a new failing use arrives.
- Fix: a mobility probe under `--fixes`. After each reset, the character walks toward the shelf for 3 game seconds; if it moved less than 1 tile, the spawn is redrawn (up to 3 times) and the redraw is logged as `probe_fail`. Side effect: each episode starts with up to 3 s of walking toward the shelf, the same for both arms.
- MILESTONE IMPACT: none (HBfix4 next, same criteria).
