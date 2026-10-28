#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
sleep 100
python scripts/benchmark.py --backend rendered --episodes 30 --note "matched reference, retry on dropout, client-side bat giveitem" charge:1.8:0:3:0 > logs/fresh_ref.out 2>&1
python scripts/pz_ctl.py stop-clients
echo STUDYDONE >> logs/fresh_ref.out
