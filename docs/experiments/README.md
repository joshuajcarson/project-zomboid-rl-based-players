# Experiment cards

One card per experiment (batch). The card is the unit the 8:00 AM milestone review reads: it must hold enough to decide whether a milestone in `docs/milestones.md` should be added, removed or modified. Write the top half BEFORE launching (pre-registration) and the bottom half at batch end. A card with an empty required field is a review failure.

File naming: `docs/experiments/YYYY-MM-DD-<short-name>.md` (one file per batch; several cards may share a retro file when reconstructed from the journal).

## Template

```
# <ID> <short title>
- Date / time: 
- Milestone: <ID and title from docs/milestones.md>
- Question: <one sentence; what would we do differently depending on the answer?>
- Hypothesis:

## Pre-registered (fixed before running; never edited afterwards)
- Design: arms, episodes per arm (real episodes after dropping aborted resets), sessions, field/protocol, seed, env knobs (PZ_*), commit hash
- SUCCESS if: <numbers>
- FAILURE if: <numbers>
- INCONCLUSIVE if: <numbers>
- Stopping rule and invariants that must hold:

## Result (filled at batch end)
- Data: <path under results/> and the command that reproduces the numbers
- Numbers: n, mean +- se, difference and z for each metric
- Verdict: SUCCESS | FAILURE | INCONCLUSIVE (against the criteria above)
- Unexpected learnings:
- Validity notes: crashes, invariant failures, design flaws, anything that weakens the claim
- MILESTONE IMPACT: none | add <what> | remove <what> | modify <what and why>
- Follow-ups / next experiment:
```

## Rules the review enforces
1. Every experiment named in `docs/journal.md` since the last review has a card (reconstructed cards are allowed but must say RECONSTRUCTED and list what is unknown).
2. Every card has every required field, a data path that exists, and a verdict phrased against its own pre-registered criteria.
3. A milestone's status or acceptance test only changes through a card's MILESTONE IMPACT line (the review applies it and logs it in the daily log of `docs/milestones.md`).
4. Flawed or invalidated experiments stay in the index with their flaw stated; they are never deleted.
