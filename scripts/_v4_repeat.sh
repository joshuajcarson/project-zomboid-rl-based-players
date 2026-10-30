#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
python scripts/pz_ctl.py stop-clients
sleep 20
PZ_STATUS="fight-v4 swing-distance repeat: 2.6, 3.0, 1.8" python scripts/benchmark.py --backend rendered --protocol fight-v4 --episodes 30 --setup field5377-v4-r2 --note "swing-distance repeat, dirt field" charge:2.6:0 charge:3.0:0 charge:1.8:0 > logs/v4_repeat.out 2>&1
python scripts/cleanup.py --keep-server >> logs/v4_repeat.out 2>&1
echo STUDYDONE >> logs/v4_repeat.out
