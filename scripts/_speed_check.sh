#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
python scripts/measure_speed.py fake 4
python scripts/pz_ctl.py stop-clients; sleep 4
python scripts/measure_speed.py mixed 1
python scripts/pz_ctl.py stop-clients
echo ALLDONE
