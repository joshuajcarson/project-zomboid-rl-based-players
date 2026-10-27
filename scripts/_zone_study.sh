#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
PZ_HEAD_SIGN=0 python scripts/rendered_fight_lab.py 14 45 charge:1.8:0 rendered > logs/zone.out 2>&1
cp $(ls -t .pzclient/Logs/*DebugLog* | head -1) logs/zone.debuglog
cp .pzdata/Logs/*DebugLog-server.txt logs/zone.server.log 2>/dev/null
echo ZONEDONE
