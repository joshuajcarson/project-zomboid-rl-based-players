#!/bin/bash
# Batch 12 (M3a gate B): BC checkpoint vs scripted fighter on the REAL client, interleaved, two independent sessions.
cd /c/bench/project-zomboid-rl-based-players
for S in 1 2; do
  python scripts/cleanup.py
  SEED=$([ "$S" = 1 ] && echo 7 || echo 11)
  PZ_ARM_FIXED=A PZ_ARM_HOUR=12 PZ_PROTOCOL=fight-v4 PZ_STATUS="batch12 M3a gate B session $S: bc3 vs scripted, noon, cleared" PZ_SEED=$SEED \
    python scripts/rendered_fight_lab.py 64 45 models/fight_bc3.pt,charge:1.8:0 rendered > .scratch/hl/b12s$S.out 2>&1
  grep '^{"ep"' .scratch/hl/b12s$S.out > results/experiments-2026-10-30/b12_m3a_real_s$S.jsonl
  echo "SESSION $S DONE $(date +%T)" >> .scratch/hl/b12.status
done
python scripts/cleanup.py
echo B12DONE >> .scratch/hl/b12.status
