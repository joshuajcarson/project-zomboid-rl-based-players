#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
sleep 100
PZ_GIVEUP=0 python scripts/benchmark.py --backend rendered --episodes 30 --note "zero-population world, hutch removed, give-up off" charge:1.8:0 > logs/zeropop_ref.out 2>&1
python scripts/pz_ctl.py stop-clients
echo STUDYDONE >> logs/zeropop_ref.out
