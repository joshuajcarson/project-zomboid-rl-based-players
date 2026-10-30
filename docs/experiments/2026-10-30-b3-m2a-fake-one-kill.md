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

## Result (filled at batch end, 2026-10-30 16:20 CT)
- Data: `results/experiments-2026-10-30/b3_m2a_fake_trace.jsonl` (20 episodes, all with a `ztrace`).
- Numbers: 18 of 20 episodes were stuck (>= 1 kill, a zombie alive at step 45); 1 zero-kill stall; 1 clean 2-kill episode.
  - Hypothesis A test: the surviving zombie had >= 3 lethal hits in 14 of 18 stuck episodes (78%, criterion 70%); zombies that did die had <= 2 lethal hits in 18 of 18 (100%, criterion 80%).
  - Alternative B test: surviving zombie with <= 2 swings and > 3 tiles away: 0 of 18. Surviving zombies took 25-41 swings, their closest swing distance was 0.3-1.8 tiles and they ended 0.3-1.8 tiles from the character.
  - Sample trace: killed zombie {swings 4, lethal 1}; surviving zombie {swings 34, lethal 5, enddist 1.3}.
- Verdict: **SUPPORTED (A)** against the pre-registered criteria: the env believes the surviving zombie dead (repeated lethal hits, 2-5 per episode) but the server never removes it; the zombies that die do so on the first lethal hit. Alternative B is rejected.
- Unexpected learnings:
  1. The artifact is not occasional: 90% of fake episodes are stuck (18 of 20), so the fake's kill count is capped near 1 and its 'kills 1.02' says nothing about combat realism.
  2. The stuck zombie stands next to the character and gets ~35 swings: the fake character is fighting a zombie it can never kill, which also inflates fake damage exposure (the synthetic bite keeps applying), so the fake's damage numbers (22.3) are not a clean measure either.
  3. Why the server ignores the lethal hit is NOT shown (the ownership explanation is consistent but untested: both zombies are adjacent and swung at, yet only the first dies). The fix does not need the mechanism: removing the zombie server-side is enough for the fake, whose damage model is synthetic anyway.
  4. The 10-26 refit's 2.0 kills in the old arena suggests the problem depends on spawn geometry, sandbox or code changes since; not investigated.
- Validity notes: instrumentation worked in all 20 episodes; single session (seed 7), 18 stuck episodes (>= 8 required); no early stops.
- MILESTONE IMPACT: M2a stays in progress: next batch tests a fix (after the second lethal hit on a zombie that is still alive, remove it server-side); acceptance in the milestone table unchanged (>= 40% two-kill episodes and < 30% stuck over a 20-episode fake session).
- Follow-ups / next experiment: Batch 4 = M2a fix validation.
