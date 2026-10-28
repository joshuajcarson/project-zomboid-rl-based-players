#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
python scripts/pz_ctl.py stop-clients
sleep 100
PZ_HEAD_SIGN=3 PZ_GIVEUP=0 python scripts/rendered_fight_lab.py 30 45 charge:1.8:0 rendered > logs/head3_study.out 2>&1
cp $(ls -t .pzclient/Logs/*/*DebugLog.txt | head -1) logs/head3_study.debuglog 2>/dev/null
echo STUDYDONE
