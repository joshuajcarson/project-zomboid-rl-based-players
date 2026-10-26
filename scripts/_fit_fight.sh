#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
run() { # name hit hurt stagger_steps stagger_scale
  PZ_HIT_SCALE=$2 PZ_HURT_FACTOR=$3 PZ_STAGGER_STEPS=$4 PZ_STAGGER_SCALE=$5 python scripts/rendered_fight_lab.py 12 45 scripted fake > logs/fit_$1.out 2>&1
  python scripts/pz_ctl.py stop-clients; sleep 40
}
run K 0.8 1.0 3 0.45
echo FITDONE
