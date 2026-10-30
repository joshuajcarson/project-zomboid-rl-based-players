# B3 M2a diagnosis: why do fake fights end with one zombie alive?
- Date / time: 2026-10-30, started ~16:30 CT
- Milestone: M2a (find and fix the fake fight artifact; prerequisite for M2)
- Question: in the fake backend, why do most episodes kill exactly one zombie and then idle to step 45 with the second zombie alive? The fix depends on the mechanism.
- Hypothesis A (lethal hits ignored): the env marks the second zombie dead in its own bookkeeping and sends a lethal hit through the fake client, but the server does not remove it (the server only removes a zombie on a lethal hit from its owner client); the env then forgets the zombie's tally and re-kills it on paper again and again.
- Alternative B (never engaged): the second zombie is not reachable or never approaches; the fake character swings at nothing useful or only at the first (dead) target area.

## Pre-registered (fixed before running; never edited afterwards)
- Design: ONE fake session, 20 episodes of `charge:1.8:0`, fight-v4 field, seed 7, 4x clock, instrumented env (`env.ztrace`: per zombie id swings aimed at it, lethal hits sent, closest swing distance, alive at the end, distance at the end; printed per episode as `ztrace`). Observation only: no behaviour changes. Runner: the lab directly. "Stuck episode" = an episode with >= 1 kill that ends (45 steps) with at least one zombie alive; "surviving zombie" = a zombie alive at the end of a stuck episode.
- SUPPORTED (A) if: in >= 70% of stuck episodes the surviving zombie received >= 3 lethal hits (the env believed it dead) AND the zombies that did die received <= 2 lethal hits in >= 80% of cases.
- SUPPORTED (B) if: in >= 70% of stuck episodes the surviving zombie received <= 2 swings AND ends > 3 tiles from the character.
- INCONCLUSIVE if: neither holds, or fewer than 8 stuck episodes occur (then extend to a second session); the observed pattern is recorded either way.
- FAILURE if: the trace is missing or unreadable (instrumentation bug); then fix the instrumentation and rerun.
- Stopping rule: run all 20 episodes; stop early only for an invalid run (server crash, fake client not connecting).

## Result (filled at batch end)
- Data: `results/experiments-2026-10-30/b3_m2a_fake_trace.jsonl`
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
