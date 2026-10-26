#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
python scripts/record_episode.py --task rendezvous --policy models/rendezvous.pt --zombies 0 --backend mixed --time-scale 1 --out docs/media/rendezvous_trained_real_client.gif --seed 3
python scripts/pz_ctl.py stop-clients
echo ALLDONE
