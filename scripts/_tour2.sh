#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
until grep -q STUDYDONE logs/v3_flee.out 2>/dev/null; do sleep 30; done
python scripts/pz_ctl.py stop-clients
sleep 100
python scripts/find_open_field.py 5377,10114 4010,11767 3950,11747 4070,11787 3990,11707 3990,11827 3910,11747 4110,11767 3850,11767 4010,11967 4010,11567 > logs/tour2.out 2>&1
python scripts/pz_ctl.py stop-clients
