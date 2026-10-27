#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
sleep 30
for h in 1 -1 0; do
  PZ_HEAD_SIGN=$h python scripts/rendered_fight_lab.py 10 45 charge:1.8:0 rendered > logs/head_$h.out 2>&1
  cp $(ls -t .pzclient/Logs/*DebugLog* | head -1) logs/head_$h.debuglog 2>/dev/null
  sleep 30
done
echo HEADDONE
