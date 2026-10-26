#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
python scripts/eval_transfer.py models/rendezvous_safe.pt 6 mixed rendezvous_safe 2
python scripts/pz_ctl.py stop-clients
sleep 5
python scripts/eval_transfer.py models/rendezvous_safe.pt 6 fake rendezvous_safe 2
python scripts/pz_ctl.py stop-clients
echo ALLDONE
