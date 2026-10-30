#!/bin/bash
# Batch 1 (M1 confirmation): two independent sessions of the plain charge fighter on the clean field (noon, corpses cleared every episode).
cd /c/bench/project-zomboid-rl-based-players
for S in 1 2; do
  python scripts/cleanup.py
  SEED=$([ "$S" = 1 ] && echo 7 || echo 11)
  PZ_ARM_FIXED=A PZ_ARM_HOUR=12 PZ_PROTOCOL=fight-v4 PZ_STATUS="batch1 M1 confirm session $S: charge:1.8:0, noon, corpses cleared" PZ_SEED=$SEED \
    python scripts/rendered_fight_lab.py 40 45 charge:1.8:0 rendered > .scratch/hl/b1s$S.out 2>&1
  grep '^{"ep"' .scratch/hl/b1s$S.out > results/experiments-2026-10-30/b1_m1_s$S.jsonl
  echo "SESSION $S DONE $(date +%T)" >> .scratch/hl/b1.status
done
python scripts/cleanup.py
echo B1DONE >> .scratch/hl/b1.status
