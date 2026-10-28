#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
python scripts/pz_ctl.py stop-clients
sleep 100
python scripts/benchmark.py --backend rendered --episodes 30 --note "matched reference, 30 episodes requested" charge:1.8:0 > logs/charge_ref.out 2>&1
python scripts/pz_ctl.py stop-clients
echo STUDYDONE >> logs/charge_ref.out
