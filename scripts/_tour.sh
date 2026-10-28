#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
sleep 100
python scripts/find_open_field.py 10770,9410 4010,11767 10800,9300 > logs/find_open_field.out 2>&1
python scripts/pz_ctl.py stop-clients
