#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
python scripts/pz_ctl.py stop-clients
sleep 100
PZ_GIVEUP=0 PZ_STATUS="benchmark fight-v1 charge:1.8:0" python scripts/benchmark.py --backend rendered --episodes 30 --note "low-population world, hutch removed, one bat, give-up off, invariants on, floor swings aimed at the floor" charge:1.8:0 > logs/lowpop_ref.out 2>&1
python scripts/pz_ctl.py stop-clients
echo STUDYDONE >> logs/lowpop_ref.out
