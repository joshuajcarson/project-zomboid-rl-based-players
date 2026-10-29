#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
python scripts/pz_ctl.py stop-clients
sleep 20
PZ_STATUS="fight-v4 swing-distance study: charge:1.3 / charge:2.2 (ref 1.8)" python scripts/benchmark.py --backend rendered --protocol fight-v4 --episodes 30 --setup field5377-v4 --note "swing-distance study, dirt field" charge:1.3:0 charge:2.2:0 > logs/v4_swing.out 2>&1
python scripts/cleanup.py --keep-server >> logs/v4_swing.out 2>&1
echo STUDYDONE >> logs/v4_swing.out
