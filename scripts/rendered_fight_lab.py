"""Fast iteration on rendered fighting: reuses a running rendered client (starts one if needed and leaves it running).
Edit <repo>/.pzclient/Lua/rl_bot_dev.lua between runs (the env sends 'reload' at start).
Usage: python scripts/rendered_fight_lab.py [episodes] [steps] [policy]"""
import json, math, sys, time
sys.path.insert(0, ".")
import numpy as np
from pzrl.env import PZParallelEnv
from pzrl.tasks import TASKS
from pzrl.baselines import BASELINES, idle, parse_policy
net = None
import os
saved = {"X": [], "Y": []}      # PZ_SAVE_OBS=path.npz: keep every observation with the scripted fighter's action as its label (DAgger data)

episodes = int(sys.argv[1]) if len(sys.argv) > 1 else 3
steps = int(sys.argv[2]) if len(sys.argv) > 2 else 45
policy = sys.argv[3] if len(sys.argv) > 3 else "scripted"
backend = sys.argv[4] if len(sys.argv) > 4 else "rendered"      # rendered | fake (same task settings, fake at 4x)
TASKS["fight"].zombies_per_agent = 2
if policy.endswith(".pt"):            # a trained checkpoint (greedy)
    import torch
    from pzrl.train import ActorCritic
    net = ActorCritic(25, 10); net.load_state_dict(torch.load(policy))
env = PZParallelEnv(n_agents=1, task="fight", backend=backend, max_steps=steps, seed=7, zombie_ring=(5, 8), time_scale=1.0 if backend != "fake" else 4.0,
                    spawn_box=(10730, 9380, 10810, 9440), keep_alive=True)
try:
    for ep in range(episodes):
        obs, _ = env.reset(); a0 = env.agents[0]
        hp0 = env.state[a0]["hp"]; zn0 = env.state[a0]["zn"]; zmin = zn0; hpmin = hp0; swings = 0
        while env.agents:
            act = {a: (net.act(obs[a], greedy=True)[0] if net else idle(obs[a]) if policy == "idle" else (parse_policy(policy) or BASELINES["fight"])(obs[a])) for a in env.agents}
            if os.environ.get("PZ_SAVE_OBS"):
                for a in env.agents:
                    saved["X"].append(obs[a].copy()); saved["Y"].append(BASELINES["fight"](obs[a]))
            swings += sum(1 for v in act.values() if v == 9)
            obs, rew, term, trunc, info = env.step(act)
            st = env.state[a0]; zmin = min(zmin, st["zn"]); hpmin = min(hpmin, st["hp"])
        print(json.dumps({"ep": ep, "steps": env.steps, "attack_actions": swings, "zombies_start": zn0, "zombies_min": zmin,
                          "zombies_end": env.state[a0]["zn"], "damage_end": round(hp0 - env.state[a0]["hp"], 1), "min_hp": round(hpmin, 1),
                          "combat": {k: round(v, 2) for k, v in getattr(env, "combat_stats", {}).items()}}), flush=True)
finally:
    env.close()

if os.environ.get("PZ_SAVE_OBS") and saved["X"]:
    import numpy as np
    np.savez_compressed(os.environ["PZ_SAVE_OBS"], X=np.array(saved["X"], np.float32), Y=np.array(saved["Y"], np.int64))
    print("saved", len(saved["Y"]), "labelled observations to", os.environ["PZ_SAVE_OBS"])
