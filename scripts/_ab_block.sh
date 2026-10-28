#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
python scripts/pz_ctl.py stop-clients
sleep 100
PZ_STATUS="A/B fence check ON, fight-v2" python scripts/benchmark.py --backend rendered --protocol fight-v2 --episodes 30 --setup lowpop-floor-v2 --note "A: fence check on, floor aim, one bat, low pop" charge:1.8:0 > logs/ab_block_A.out 2>&1
PZ_NOBLOCK=1 PZ_STATUS="A/B fence check OFF, fight-v2" python scripts/benchmark.py --backend rendered --protocol fight-v2 --episodes 30 --setup lowpop-floor-v2 --note "B: fence check OFF, floor aim, one bat, low pop" charge:1.8:0 > logs/ab_block_B.out 2>&1
python scripts/pz_ctl.py stop-clients
echo STUDYDONE >> logs/ab_block_B.out
