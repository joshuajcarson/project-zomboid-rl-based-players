#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
python scripts/pz_ctl.py stop-clients
sleep 100
PZ_STATUS="fight-v3 open field, charge:1.8:35 (flee below 35 hp)" python scripts/benchmark.py --backend rendered --protocol fight-v3 --episodes 30 --setup field4010-v3 --note "open field, flee below 35 hp within 3 tiles" charge:1.8:35 > logs/v3_flee.out 2>&1
python scripts/pz_ctl.py stop-clients
echo STUDYDONE >> logs/v3_flee.out
