"""In-game unit tests of the hybrid planner's one-shot skills on the real client (H-B0b).

    python scripts/skill_test.py --trials 5 --out results/experiments-2026-11-14/b0b_skill_tests.jsonl

No zombies are spawned. Each trial: set server-side hunger/thirst, give the needed item client-side, survey, run the skill, wait for the
client's action queue to empty (cap), survey again, judge success. One JSON line per trial with the client log lines of the skill.
"""
import argparse
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pzrl.env import PZParallelEnv
from pzrl.tasks import TASKS
from pzrl import hybrid

ap = argparse.ArgumentParser()
ap.add_argument("--trials", type=int, default=5)
ap.add_argument("--box", type=float, nargs=4, default=(10730, 9380, 10810, 9440))
ap.add_argument("--out", required=True)
a = ap.parse_args()

TASKS["fight"].zombies_per_agent = 0
env = PZParallelEnv(n_agents=1, task="fight", backend="rendered", max_steps=10 ** 6, seed=7, spawn_box=tuple(a.box), keep_alive=True)
log = open(a.out, "a", encoding="utf-8")


def items_total(name):
    m = re.search(r"items=(\d+)", hybrid.client_query(env, name, "invcount", "Base.BaseballBat", until="INVCOUNT", wait=5))
    return int(m.group(1)) if m else -1


def wait_idle(name, cap):
    env._read(env._game_seconds(2))
    waited = 2
    while waited < cap and hybrid.busy(env, name) != 0:
        env._read(env._game_seconds(1)); waited += 1
    return waited


try:
    env.reset()
    a0 = env.agents[0]
    for trial in range(1, a.trials + 1):
        for skill in ("eat", "drink", "loot"):
            env.channel.command(f"stats|{a0}|0.5|0.5")
            if skill == "eat":
                env.control[a0]._bot("giveitem", "Base.Apple")
            env._read(env._game_seconds(3))                          # let the server-side stats reach the client
            before, n0 = hybrid.survey(env, a0), items_total(a0)
            path = hybrid.newest_log(); start = os.path.getsize(path)
            if skill == "loot":
                env.channel.command(f"bot|{a0}|loot|{trial}|30|any")
            else:
                env.control[a0]._bot(skill)
            waited = wait_idle(a0, {"eat": 25, "drink": 20, "loot": 40}[skill])
            after, n1 = hybrid.survey(env, a0), items_total(a0)
            with open(path, "rb") as f:
                f.seek(start)
                skill_log = [l[l.index("RLBOT"):][:200] for l in f.read().decode("utf-8", "replace").splitlines()
                             if "RLBOT" in l and any(k in l for k in ("EAT", "DRINK", "LOOT", "eat ->", "drink ->", "loot ->"))]
            b, c = before["stats"], after["stats"]
            d = lambda k: (c.get(k) or 0) - (b.get(k) or 0)
            ok = {"eat": d("food") < 0 or d("hunger") < -0.01, "drink": d("drink") < 0 or d("thirst") < -0.01, "loot": n1 > n0 >= 0}[skill]
            row = {"trial": trial, "skill": skill, "success": bool(ok), "waited": waited, "hunger": [b.get("hunger"), c.get("hunger")],
                   "thirst": [b.get("thirst"), c.get("thirst")], "food": [b.get("food"), c.get("food")], "drink": [b.get("drink"), c.get("drink")],
                   "items": [n0, n1], "log": skill_log}
            log.write(json.dumps(row) + "\n"); log.flush()
            print(json.dumps({k: row[k] for k in ("trial", "skill", "success", "waited", "items")} | {"log": skill_log[:2]}), flush=True)
finally:
    log.close()
    env.close()
