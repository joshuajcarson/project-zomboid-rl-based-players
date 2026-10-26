"""Run a task on REAL rendered clients (1x speed) with a baseline policy, to compare with the fake-client backend.
Usage: python scripts/env_rendered_demo.py [task] [policy] [steps] [n_agents] [zombies]
Reuses a running server (start one with start-server.ps1 -JavaAgent agent\rl-agent.jar -ChannelPort 17600) or starts its own."""
import json, sys, time
sys.path.insert(0, ".")
import numpy as np
from pzrl.env import PZParallelEnv
from pzrl.tasks import TASKS
from pzrl.baselines import BASELINES, idle

task = sys.argv[1] if len(sys.argv) > 1 else "fight"
policy = sys.argv[2] if len(sys.argv) > 2 else "scripted"
steps = int(sys.argv[3]) if len(sys.argv) > 3 else 60
n = int(sys.argv[4]) if len(sys.argv) > 4 else 1
if len(sys.argv) > 5:
    TASKS[task].zombies_per_agent = int(sys.argv[5])
env = PZParallelEnv(n_agents=n, task=task, backend="rendered", max_steps=steps, seed=1, zombie_ring=(5, 8))
try:
    obs, _ = env.reset()
    kills0 = {a: env.state[a]["kills"] for a in env.agents}
    zn0 = {a: env.state[a]["zn"] for a in env.agents}
    total = {a: 0.0 for a in env.agents}; t0 = time.time(); k = 0
    while env.agents:
        act = {a: (idle(obs[a]) if policy == "idle" else env.action_space(a).sample() if policy == "random"
                   else BASELINES[task](obs[a])) for a in env.agents}
        obs, rew, term, trunc, info = env.step(act)
        for a in rew: total[a] += rew[a]
        k += 1
        print(k, {a: (round(env.state[a]["hp"]), env.state[a]["zn"], round(env.state[a]["x"]), round(env.state[a]["y"])) for a in env.state}, flush=True)
    print(json.dumps({"backend": "rendered", "task": task, "policy": policy, "steps": k, "real_s": round(time.time() - t0, 1),
                      "mean_return": round(float(np.mean(list(total.values()))), 2),
                      "zombies_start_end": [zn0, {a: env.state[a]["zn"] for a in zn0}],
                      "final_hp": {a: env.state[a]["hp"] for a in env.state}}))
finally:
    env.close()
