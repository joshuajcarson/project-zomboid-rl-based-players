#!/bin/bash
# Batch 6 (M2 confirmation): the scripted fighter on the fake backend at bite 6.0, two independent sessions.
cd /c/bench/project-zomboid-rl-based-players
for S in 1 2; do
  python scripts/cleanup.py
  SEED=$([ "$S" = 1 ] && echo 7 || echo 11)
  PZ_FAKE_ARMS=2.25:0.6 PZ_PROTOCOL=fight-v4 PZ_STATUS="batch9 M2 confirm session $S" PZ_SEED=$SEED python scripts/rendered_fight_lab.py 40 45 charge:1.8:0 fake > .scratch/hl/b9s$S.out 2>&1
  grep '^{"ep"' .scratch/hl/b9s$S.out > results/experiments-2026-10-30/b9_m2_fake_s$S.jsonl
  echo "SESSION $S DONE $(date +%T)" >> .scratch/hl/b9.status
done
python scripts/cleanup.py
echo B9DONE >> .scratch/hl/b9.status
