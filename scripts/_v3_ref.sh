#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
python scripts/pz_ctl.py stop-clients
sleep 100
PZ_STATUS="fight-v3 open field, charge:1.8:0" python scripts/benchmark.py --backend rendered --protocol fight-v3 --episodes 30 --setup field4010-v3 --note "open field 4010,11767, floor aim, one bat, low pop, invariants, end-when-clear" charge:1.8:0 > logs/v3_ref.out 2>&1
python scripts/pz_ctl.py stop-clients
echo STUDYDONE >> logs/v3_ref.out
