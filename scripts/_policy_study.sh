#!/bin/bash
cd /c/bench/project-zomboid-rl-based-players
for spec in charge:1.8:0 charge:1.2:0 charge:1.8:35 charge:2.4:0; do
  name=$(echo $spec | tr ':.' '__')
  python scripts/rendered_fight_lab.py 12 45 $spec rendered > logs/study2_$name.out 2>&1
done
echo STUDYDONE
