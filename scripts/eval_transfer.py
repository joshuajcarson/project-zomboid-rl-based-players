"""Does a policy trained on fake clients work when one agent is a real rendered client?
Runs rendezvous with Client40 rendered (real game, 1x) and Client41 fake, both driven by the same policy, and compares with
the same policy on two fake agents. Usage: python scripts/eval_transfer.py [checkpoint] [episodes] [backend: mixed|fake]"""
import json, math, sys, time
sys.path.insert(0, ".")
import numpy as np
import torch
from pzrl.env import PZParallelEnv
from pzrl.tasks import TASKS
from pzrl.baselines import BASELINES
from pzrl.train import ActorCritic

ckpt = sys.argv[1] if len(sys.argv) > 1 else "models/rendezvous.pt"
episodes = int(sys.argv[2]) if len(sys.argv) > 2 else 5
backend = sys.argv[3] if len(sys.argv) > 3 else "mixed"
net = None
if ckpt != "scripted":
    net = ActorCritic(25, 10); net.load_state_dict(torch.load(ckpt))
TASKS["rendezvous"].zombies_per_agent = 0
env = PZParallelEnv(n_agents=2, task="rendezvous", backend=backend, time_scale=1.0 if backend != "fake" else 4.0, max_steps=40,
                    seed=11, spawn_box=(10650, 9350, 10800, 9500), keep_alive=True)
rows = []
try:
    for ep in range(episodes):
        obs, _ = env.reset()
        d0 = None; paths = {a: 0.0 for a in env.agents}; last = {a: (env.state[a]["x"], env.state[a]["y"]) for a in env.agents}
        ps = list(env.state.values()); d0 = math.hypot(ps[0]["x"] - ps[1]["x"], ps[0]["y"] - ps[1]["y"])
        ret = 0.0; t0 = time.time()
        while env.agents:
            acts = {a: (net.act(obs[a], greedy=True)[0] if net else BASELINES["rendezvous"](obs[a])) for a in env.agents}
            obs, rew, term, trunc, _ = env.step(acts)
            ret += float(np.mean(list(rew.values()))) if rew else 0.0
            for a in paths:
                if a in env.state:
                    p = env.state[a]; paths[a] += math.hypot(p["x"] - last[a][0], p["y"] - last[a][1]); last[a] = (p["x"], p["y"])
        ps = list(env.state.values())
        row = {"backend": backend, "policy": ckpt, "ep": ep, "start_distance": round(d0, 1),
               "final_distance": round(math.hypot(ps[0]["x"] - ps[1]["x"], ps[0]["y"] - ps[1]["y"]), 1),
               "return": round(ret, 2), "path_tiles": {a: round(v, 1) for a, v in paths.items()}, "real_s": round(time.time() - t0, 1)}
        print(json.dumps(row), flush=True); rows.append(row)
finally:
    env.close()
json.dump(rows, open(f"logs/eval_transfer_{backend}.json", "w"), indent=1)
