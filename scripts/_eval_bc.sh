#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
python scripts/rendered_fight_lab.py 12 45 models/fight_bc.pt rendered > logs/eval_bc_real.out 2>&1
python scripts/pz_ctl.py stop-clients; sleep 45
python scripts/rendered_fight_lab.py 12 45 models/fight_bc.pt fake > logs/eval_bc_fake.out 2>&1
python scripts/pz_ctl.py stop-clients
echo EVALDONE
