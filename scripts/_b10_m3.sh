#!/bin/bash
# Batch 10 (M3 gate A): train PPO on the calibrated fake fight, then evaluate interleaved against the scripted fighter on the fake.
cd /c/bench/project-zomboid-rl-based-players
rm -f models/fight_cal1.jsonl models/fight_cal1.stopped models/fight_cal1.pt
python scripts/cleanup.py
python -m pzrl.train --task fight --agents 1 --iters 40 --episodes 8 --steps 45 --zombies 2 --ring 5 8 --box 5362 10099 5392 10129 --time-scale 4 --end-when-clear --eval-episodes 0 --trend-check 20 --trend-min-gain 0.2 --out models/fight_cal1 > .scratch/hl/b10_train.out 2>&1
echo "TRAIN DONE $(date +%T)" >> .scratch/hl/b10.status
cp models/fight_cal1.jsonl results/experiments-2026-10-30/b10_m3_train_curve.jsonl
if [ -f models/fight_cal1.stopped ]; then
  echo "STOPPED EARLY (no learning trend)" >> .scratch/hl/b10.status
  python scripts/cleanup.py
  echo B10DONE >> .scratch/hl/b10.status
  exit 0
fi
python scripts/cleanup.py
PZ_PROTOCOL=fight-v4 PZ_STATUS="batch10 gate A eval" PZ_SEED=7 python scripts/rendered_fight_lab.py 120 45 models/fight_cal1.pt,charge:1.8:0 fake > .scratch/hl/b10_eval.out 2>&1
grep '^{"ep"' .scratch/hl/b10_eval.out > results/experiments-2026-10-30/b10_m3_eval.jsonl
echo "EVAL DONE $(date +%T)" >> .scratch/hl/b10.status
python scripts/cleanup.py
echo B10DONE >> .scratch/hl/b10.status
