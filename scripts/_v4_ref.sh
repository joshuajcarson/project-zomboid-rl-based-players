#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
python scripts/pz_ctl.py stop-clients
sleep 20
PZ_STATUS="fight-v4 dirt field: charge:1.8:35 vs charge:1.8:0" python scripts/benchmark.py --backend rendered --protocol fight-v4 --episodes 30 --setup field5377-v4 --note "dirt field 5377,10114" charge:1.8:35 charge:1.8:0 > logs/v4_ref.out 2>&1
python scripts/pz_ctl.py stop-clients
echo STUDYDONE >> logs/v4_ref.out
