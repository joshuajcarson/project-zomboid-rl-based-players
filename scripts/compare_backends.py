"""Same task, same baselines, fake-client backend vs rendered backend: kills, damage taken, movement.
Usage: python scripts/compare_backends.py [task] [steps] [episodes] [zombies]
Needs a running server (start-server.ps1 -JavaAgent agent\rl-agent.jar -ChannelPort 17600) or starts one. Both backends run at 1x."""
import json, math, sys, time
sys.path.insert(0, ".")
import numpy as np
from pzrl.env import PZParallelEnv
from pzrl.tasks import TASKS
from pzrl.baselines import BASELINES, idle

task = sys.argv[1] if len(sys.argv) > 1 else "fight"
steps = int(sys.argv[2]) if len(sys.argv) > 2 else 60
episodes = int(sys.argv[3]) if len(sys.argv) > 3 else 3
TASKS[task].zombies_per_agent = int(sys.argv[4]) if len(sys.argv) > 4 else 2
rows = []
for backend in ("fake", "rendered"):
    env = PZParallelEnv(n_agents=1, task=task, backend=backend, max_steps=steps, seed=1, zombie_ring=(5, 8), time_scale=1.0)
    try:
        for policy in ("idle", "scripted"):
            for ep in range(episodes):
                obs, _ = env.reset()
                a0 = env.agents[0]
                hp0, zn0, k0 = env.state[a0]["hp"], env.state[a0]["zn"], env.state[a0]["kills"]
                pos = [(env.state[a0]["x"], env.state[a0]["y"])]; hps = [hp0]; zns = [zn0]
                t0 = time.time()
                while env.agents:
                    act = {a: (idle(obs[a]) if policy == "idle" else BASELINES[task](obs[a])) for a in env.agents}
                    obs, rew, term, trunc, info = env.step(act)
                    st = env.state[a0]; pos.append((st["x"], st["y"])); hps.append(st["hp"]); zns.append(st["zn"])
                path = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pos, pos[1:]))
                row = {"backend": backend, "policy": policy, "ep": ep, "steps": len(pos) - 1, "real_s": round(time.time() - t0, 1),
                       "kills_counter": env.state[a0]["kills"] - k0, "zombies_start": zn0, "zombies_min": min(zns), "zombies_end": zns[-1],
                       "damage_taken": round(hp0 - hps[-1], 1), "min_hp": round(min(hps), 1),
                       "path_tiles": round(path, 1), "net_tiles": round(math.hypot(pos[-1][0] - pos[0][0], pos[-1][1] - pos[0][1]), 1)}
                print(json.dumps(row), flush=True); rows.append(row)
    finally:
        env.close()
json.dump(rows, open("logs/compare_backends.json", "w"), indent=1)
print("\nmean per backend/policy")
for b in ("fake", "rendered"):
    for pol in ("idle", "scripted"):
        r = [x for x in rows if x["backend"] == b and x["policy"] == pol]
        if r:
            print(b, pol, {k: round(float(np.mean([x[k] for x in r])), 1) for k in
                           ("kills_counter", "zombies_start", "zombies_min", "damage_taken", "path_tiles", "net_tiles")})
