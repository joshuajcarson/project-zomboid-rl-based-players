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
_cfg = os.path.join(".pzclient", "Lua", "rl_bot_cfg.txt")        # bot settings read by rl_bot_dev.lua at reload
os.makedirs(os.path.dirname(_cfg), exist_ok=True)
open(_cfg, "w").write("headSign=" + os.environ.get("PZ_HEAD_SIGN", "0") + " giveup=" + os.environ.get("PZ_GIVEUP", "0") + " noblock=" + os.environ.get("PZ_NOBLOCK", "0"))
PROTOCOL = os.environ.get("PZ_PROTOCOL", "fight-v1")
# fight-v1/v2: the old arena in Muldraugh (shed, dog house, fences, playground); fight-v3: an open field (the user's map coordinate 4010,11767;
# the in-game scan found 0 blocked / building / fence / hutch squares within 30 tiles, scripts/find_open_field.py)
# fight-v4: the dirt field at 5377,10114 (user tip): scan r=30 gives blocked 0, building 0, hutch 0 and bush 0, i.e. no corn; fight-v3 was the cornfield,
# where `hasBush()` is true on about 2440 of 3721 squares (the `openness` scan detects corn through bush=, not veg/cut/sight/spear, which stay 0)
SPAWN_BOX = {"fight-v3": (3995, 11752, 4025, 11782), "fight-v4": (5362, 10099, 5392, 10129)}.get(PROTOCOL, (10730, 9380, 10810, 9440))
env = PZParallelEnv(n_agents=1, task="fight", backend=backend, max_steps=steps, seed=int(os.environ.get("PZ_SEED", "7")), zombie_ring=(5, 8), time_scale=float(os.environ.get("PZ_TIME_SCALE", "1.0")) if backend != "fake" else 4.0,
                    spawn_box=SPAWN_BOX, keep_alive=True, end_when_clear=PROTOCOL in ("fight-v2", "fight-v3", "fight-v4"))
env.status_text = os.environ.get("PZ_STATUS") or ("fight lab: " + policy)   # shown above the character in the game window
try:
    for ep in range(episodes):
        obs, _ = env.reset(); a0 = env.agents[0]
        env.say(f"{env.status_text} | episode {ep + 1}/{episodes} | fighting")
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
