"""Run the three curriculum tasks with a random policy and a scripted baseline, report reward and speed.
Starts its own server and clients at the given time scale (stop any other server first).
Usage: python scripts/env_tasks_demo.py [n_agents] [time_scale] [steps]"""
import sys, time, json
sys.path.insert(0, ".")
import numpy as np
from pzrl.env import PZParallelEnv
from pzrl.tasks import TASKS
from pzrl.baselines import BASELINES, idle

n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
K = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0
steps = int(sys.argv[3]) if len(sys.argv) > 3 else 60
tasks = sys.argv[4].split(",") if len(sys.argv) > 4 else ["survive", "rendezvous", "fight"]
policies = sys.argv[5].split(",") if len(sys.argv) > 5 else ["random", "scripted"]
damage = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
ring = (float(sys.argv[7]), float(sys.argv[8])) if len(sys.argv) > 8 else (12, 22)
behaviour = sys.argv[9] if len(sys.argv) > 9 else "Normal"
weapon = sys.argv[10] if len(sys.argv) > 10 else "Base.BaseballBat"
weapon = None if weapon.lower() == "none" else weapon
zombies = int(sys.argv[11]) if len(sys.argv) > 11 else None
env = PZParallelEnv(n_agents=n, task="survive", time_scale=K, max_steps=steps, seed=1, player_damage=damage,
                    zombie_ring=ring, zombie_behaviour=behaviour, give_weapon=weapon)
if zombies is not None:
    for t in TASKS.values():
        t.zombies_per_agent = zombies
rows = []
try:
    for task in tasks:
        env.task = TASKS[task]
        for policy in policies:
            obs, _ = env.reset()
            total = {a: 0.0 for a in env.agents}
            kills0 = {a: env.state[a]["kills"] for a in env.agents}
            t0 = time.time(); k = 0; dmin = []
            while env.agents:
                if policy == "random":
                    act = {a: env.action_space(a).sample() for a in env.agents}
                elif policy == "idle":
                    act = {a: idle(obs[a]) for a in env.agents}
                else:
                    act = {a: BASELINES[task](obs[a]) for a in env.agents}
                obs, rew, term, trunc, info = env.step(act)
                for a in rew: total[a] += rew[a]
                k += 1
                if task == "rendezvous":
                    ps = list(env.state.values())
                    dmin.append(min(np.hypot(p["x"] - q["x"], p["y"] - q["y"]) for p in ps for q in ps if p is not q))
            dt = time.time() - t0
            kills = sum(env.state[a]["kills"] - kills0[a] for a in kills0)
            hp = [env.state[a]["hp"] for a in kills0]; deaths = sum(1 for h in hp if h <= 10)
            r = {"task": task, "policy": policy, "steps": k, "real_s": round(dt, 1),
                 "game_s_per_real_s": round(k * env.step_seconds / dt, 2),
                 "mean_return": round(float(np.mean(list(total.values()))), 2), "kills": kills,
                 "mean_final_hp": round(float(np.mean(hp)), 1), "deaths": deaths,
                 "min_pair_distance_end": round(dmin[-1], 1) if dmin else None}
            print(json.dumps(r), flush=True); rows.append(r)
finally:
    env.close()
json.dump(rows, open("logs/env_tasks_demo.json", "w"), indent=1)
