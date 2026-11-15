# Run watchdog: checks and the incidents behind them

`scripts/watchdog.py` reads a long run's JSONL while it grows and prints `ALERT` lines (each problem once). Attach it to every long run under a Monitor that streams only `ALERT` lines; an alert that is not a listed known deviation means the run is invalid under the stopping rule: stop it, record it on the card, fix, restart.

    python scripts/watchdog.py <run.jsonl> --arms llm,rule,idle --hunger 0.6 --thirst 0.6 --supplies --known thirst,supplies
    python scripts/watchdog.py --selftest            # must print "watchdog selftest ok" after any change

**Rule: whenever a run turns out invalid in a way the watchdog did not catch, add a check (one function in CHECKS plus a selftest case) and a row below.** Known deviations passed with `--known` go on the experiment card.

| Check | Catches | Incident that added it |
|---|---|---|
| step1_death | a death during the reset charged to the next episode (dead at step <= 1) | H-B s1 run 2, 2026-11-14: 11 of 48 episodes, 7 charged to the llm arm; found only at the end of a 110-minute session |
| stall | decisions repeating at one game step (the loop never steps the game) | H-B s1 run 1, 2026-11-14: rule arm sat at step 3 for 452 decisions |
| short_episode | an episode ending alive before its length (loop broke out early) | preventive (same family as stall) |
| start_state | first survey's hunger/thirst differ from the configured start; no container with supplies visible | H-B, 2026-11-14: the server `stats` command sets hunger but not thirst (known deviation `thirst` until fixed); supplies: the survey lists only the 8 nearest containers, so spawns at the west edge (x 10740-10745) do not see the seeded shelf (7 of 61 episodes, all arms; known deviation `supplies` for H-B). The stat check looks at the first 3 surveys: in 3 of 61 H-B episodes the first survey ran before the server's hunger change reached the client (one decision on stale stats; harness fix later: wait for the stat to show before the first decision) |
| arm_rotation | arms not alternating in the configured order | preventive (interleaving is the validity basis) |
| planner_health | planner valid rate < 95% or median latency > 15 s over the last 20 decisions | H-A gate bounds |
| idle (loop) | the file stops growing for --idle-minutes | stuck runs (2026-10-29 "Still dead" hang, 2026-11-14 client hangs) |

Replaying today's runs: run 1 alerts at the stall (episode 2), run 2 at the first step-1 death (episode 6, about 15 minutes in), the valid runs only on the two known deviations.
