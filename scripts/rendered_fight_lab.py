"""Fast iteration on rendered fighting: reuses a running rendered client (starts one if needed and leaves it running).
Edit <repo>/.pzclient/Lua/rl_bot_dev.lua between runs (the env sends 'reload' at start).
Usage: python scripts/rendered_fight_lab.py [episodes] [steps] [policy]"""
import json, math, sys, time
sys.path.insert(0, ".")
import numpy as np
from pzrl.env import PZParallelEnv
from pzrl.tasks import TASKS
from pzrl.baselines import BASELINES, idle

episodes = int(sys.argv[1]) if len(sys.argv) > 1 else 3
steps = int(sys.argv[2]) if len(sys.argv) > 2 else 45
policy = sys.argv[3] if len(sys.argv) > 3 else "scripted"
TASKS["fight"].zombies_per_agent = 2
env = PZParallelEnv(n_agents=1, task="fight", backend="rendered", max_steps=steps, seed=7, zombie_ring=(5, 8),
                    spawn_box=(10730, 9380, 10810, 9440), keep_alive=True)
try:
    for ep in range(episodes):
        obs, _ = env.reset(); a0 = env.agents[0]
        hp0 = env.state[a0]["hp"]; zn0 = env.state[a0]["zn"]; zmin = zn0; hpmin = hp0; swings = 0
        while env.agents:
            act = {a: (idle(obs[a]) if policy == "idle" else BASELINES["fight"](obs[a])) for a in env.agents}
            swings += sum(1 for v in act.values() if v == 9)
            obs, rew, term, trunc, info = env.step(act)
            st = env.state[a0]; zmin = min(zmin, st["zn"]); hpmin = min(hpmin, st["hp"])
        print(json.dumps({"ep": ep, "steps": env.steps, "attack_actions": swings, "zombies_start": zn0, "zombies_min": zmin,
                          "zombies_end": env.state[a0]["zn"], "damage_end": round(hp0 - env.state[a0]["hp"], 1), "min_hp": round(hpmin, 1)}), flush=True)
finally:
    env.close()
