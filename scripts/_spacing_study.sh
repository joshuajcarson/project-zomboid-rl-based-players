#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
python scripts/pz_ctl.py stop-clients
sleep 100
python scripts/benchmark.py --backend rendered --episodes 30 --note "min_dist 0.8 step back (spacing), centre aim" charge:1.8:0:3:0.8 > logs/spacing_study.out 2>&1
python scripts/pz_ctl.py stop-clients
echo STUDYDONE >> logs/spacing_study.out
