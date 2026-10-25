"""Random-policy rollout of the PZ parallel env: shows reset/step, rewards and episode ends.
Usage: python scripts/env_demo.py [task] [n_agents] [time_scale] [episodes]
Reuses a running server (start-server.ps1 -JavaAgent agent\rl-agent.jar -ChannelPort 17600 [-TimeScale K]) or starts its own."""
import sys, time
sys.path.insert(0, ".")
import numpy as np
from pzrl.env import PZParallelEnv

task = sys.argv[1] if len(sys.argv) > 1 else "survive"
n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
K = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
episodes = int(sys.argv[4]) if len(sys.argv) > 4 else 2
env = PZParallelEnv(n_agents=n, task=task, time_scale=K, max_steps=60, seed=0)
env.launcher.start_server = (lambda f=env.launcher.start_server: f(reuse=True))   # reuse a running server
try:
    for ep in range(episodes):
        obs, info = env.reset()
        total = {a: 0.0 for a in env.agents}
        t0 = time.time(); steps = 0
        while env.agents:
            actions = {a: env.action_space(a).sample() for a in env.agents}
            obs, rew, term, trunc, info = env.step(actions)
            for a in rew: total[a] += rew[a]
            steps += 1
        dt = time.time() - t0
        print(f"episode {ep}: {steps} steps in {dt:.1f}s real ({steps * env.step_seconds / dt:.2f} game s per real s)",
              {a: round(r, 2) for a, r in total.items()}, "kills", {a: info[a]["kills"] for a in info})
finally:
    env.close()
