#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
sleep 60
python scripts/rendered_fight_lab.py 2 45 idle rendered > logs/repro.out 2>&1
python scripts/pz_ctl.py stop-clients
echo REPRODONE >> logs/repro.out
