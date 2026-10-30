# B10 M3 gate A: PPO fighter trained on the calibrated fake vs the scripted fighter (on the fake)
- Date / time: 2026-10-30, started ~18:25 CT
- Milestone: M3 (learned solo fighter): first gate, on the fake only; real-client validation is gate B (a later batch)
- Question: can the repo's own PPO (`pzrl/train.py`, shared-policy, torch only; stable-baselines3 is NOT needed and was not installed) learn a fighter on the calibrated fake that is not worse than `charge:1.8:0` on the same fake?
- Hypothesis: the fight is simple (walk to the nearest zombie, swing within ~1.8 tiles), so a small MLP can reach scripted level within ~300 training episodes; if not, the budget or the observation (zombie distance resolution, swing cooldown) is the limit.

## Pre-registered (fixed before running; never edited afterwards)
- Training: `python -m pzrl.train --task fight --agents 1 --iters 40 --episodes 8 --steps 45 --zombies 2 --ring 5 8 --box 5362 10099 5392 10129 --time-scale 4 --end-when-clear --eval-episodes 0 --trend-check 20 --trend-min-gain 0.2 --out models/fight_cal1` (320 training episodes on the calibrated fake fight profile: bite 2.25 / hit scale 0.6, force-kill on; defaults lr 3e-4, gamma 0.97, hidden 64; reward = survival terms + 1.0 per kill + 1.5 per damage dealt). The EVALUATED checkpoint is the final one (`models/fight_cal1.pt`), not the best by any metric.
- Pre-registered learning-trend stop (your rule: stop failing runs early): at iteration 20 the mean training kills of iterations 16-20 must exceed the mean of iterations 1-5 by >= 0.2; otherwise the run stops, `models/fight_cal1.stopped` is written and the batch verdict is FAILURE (no learning trend), with no evaluation.
- Evaluation (only if training completes): ONE fresh fake session, 120 episodes interleaved by episode between `models/fight_cal1.pt` (greedy) and `charge:1.8:0` (60 each), fight-v4, seed 7, 4x clock, same calibrated profile, `compare_arms.py --by policy`.
- SUCCESS (gate A passed) if: learned kills >= scripted kills - 0.2 AND learned damage <= scripted damage + 8 (non-inferiority, the M3 acceptance form), on >= 55 real episodes per arm.
- FAILURE if: the trend stop triggers, OR learned kills < scripted kills - 0.5, OR learned damage > scripted damage + 15.
- INCONCLUSIVE if: neither (between the success and failure bounds).
- Stopping rule: training runs its 40 iterations unless the trend stop triggers; evaluation runs all 120 episodes; stop early otherwise only for an invalid run (server crash, fake client not connecting).
- Also report: the learning curve (kills, damage, deaths per iteration; `results/experiments-2026-10-30/b10_m3_train_curve.jsonl`), the action distribution if cheap, and the learned-vs-scripted difference with z.

## Result (filled at batch end)
- Data: `results/experiments-2026-10-30/b10_m3_train_curve.jsonl`, `b10_m3_eval.jsonl`; checkpoint `models/fight_cal1.pt`.
- Numbers: (pending)
- Verdict: (pending)
- Unexpected learnings: (pending)
- Validity notes: (pending)
- MILESTONE IMPACT: (pending)
- Follow-ups / next experiment: (pending)
