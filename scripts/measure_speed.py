"""Straight-line walking speed of the fake mover vs a real client, measured per server tick (the clock zombies share).
Usage: python scripts/measure_speed.py mixed|fake [time_scale]   (mixed: Client40 real, Client41 fake)"""
import json, math, sys
sys.path.insert(0, ".")
from pzrl.env import PZParallelEnv
from pzrl.tasks import TASKS

backend = sys.argv[1] if len(sys.argv) > 1 else "mixed"
K = float(sys.argv[2]) if len(sys.argv) > 2 else (1.0 if backend == "mixed" else 4.0)
TASKS["rendezvous"].zombies_per_agent = 0
env = PZParallelEnv(n_agents=2, task="rendezvous", backend=backend, time_scale=K, max_steps=14, seed=5,
                    spawn_box=(10650, 9380, 10750, 9440), keep_alive=True)
try:
    for trial in range(3):
        env.reset()
        for n in env.agents:
            print('inventory', n, env.channel.command('inv|' + n)['msg'], flush=True)
        for _ in range(8): env._read(1)
        samples = {n: [] for n in env.agents}
        tick0 = env.last_message["tick"]
        for step in range(12):
            obs, rew, term, trunc, _ = env.step({n: 3 for n in env.agents})     # action 3 = east
            for n in env.agents:
                samples[n].append((env.last_message["tick"], env.state[n]["x"], env.state[n]["y"]))
        for n, s in samples.items():
            (t0, x0, y0), (t1, x1, y1) = s[2], s[-1]            # skip the start-up steps
            d = math.hypot(x1 - x0, y1 - y0); dt = t1 - t0
            print(json.dumps({"backend": backend, "K": K, "trial": trial, "agent": n, "real": n in env.rendered,
                              "tiles": round(d, 1), "ticks": dt, "tiles_per_100_ticks": round(100 * d / dt, 2)}), flush=True)
finally:
    env.close()
