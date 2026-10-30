#!/bin/bash
# Batch 2 (M2 fidelity): the scripted fighter on the FAKE backend, two independent sessions.
cd /c/bench/project-zomboid-rl-based-players
for S in 1 2; do
  python scripts/cleanup.py
  SEED=$([ "$S" = 1 ] && echo 7 || echo 11)
  PZ_PROTOCOL=fight-v4 PZ_STATUS="batch2 M2 fake session $S" PZ_SEED=$SEED python scripts/rendered_fight_lab.py 40 45 charge:1.8:0 fake > .scratch/hl/b2s$S.out 2>&1
  grep '^{"ep"' .scratch/hl/b2s$S.out > results/experiments-2026-10-30/b2_m2_fake_s$S.jsonl
  echo "SESSION $S DONE $(date +%T)" >> .scratch/hl/b2.status
done
python scripts/cleanup.py
echo B2DONE >> .scratch/hl/b2.status
