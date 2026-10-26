#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
run() { # name hit stagger_steps stagger_scale
  PZ_HIT_SCALE=$2 PZ_STAGGER_STEPS=$3 PZ_STAGGER_SCALE=$4 python scripts/rendered_fight_lab.py 12 45 scripted fake > logs/fit_$1.out 2>&1
  python scripts/pz_ctl.py stop-clients; sleep 40
}
run A 1.6 5 0.2
run B 2.2 6 0.15
echo FITDONE
