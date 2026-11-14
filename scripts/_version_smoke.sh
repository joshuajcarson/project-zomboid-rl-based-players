#!/bin/bash
# Behavioural smoke test after a game update: fake backend fights, then the real client fights (same server).
cd /c/bench/project-zomboid-rl-based-players
python scripts/cleanup.py
PZ_PROTOCOL=fight-v4 PZ_SEED=7 python scripts/rendered_fight_lab.py 6 45 charge:1.8:0 fake > .scratch/hl/vsmoke_fake.out 2>&1
echo "FAKE DONE $(date +%T) episodes=$(grep -c '^{"ep"' .scratch/hl/vsmoke_fake.out)" >> .scratch/hl/vsmoke.status
python scripts/cleanup.py --keep-server
PZ_ARM_FIXED=A PZ_ARM_HOUR=12 PZ_PROTOCOL=fight-v4 PZ_SEED=7 python scripts/rendered_fight_lab.py 4 45 charge:1.8:0 rendered > .scratch/hl/vsmoke_real.out 2>&1
echo "REAL DONE $(date +%T) episodes=$(grep -c '^{"ep"' .scratch/hl/vsmoke_real.out)" >> .scratch/hl/vsmoke.status
echo VSMOKEDONE >> .scratch/hl/vsmoke.status
