"""Do spawned zombies approach an idle agent? Prints nearest-zombie distance and health per game second.
Usage: python scripts/zombie_probe.py [time_scale] [spawn_mode: lua|none] ; starts its own server."""
import sys, math, time
sys.path.insert(0, ".")
from pzrl.env import PZParallelEnv
from pzrl.tasks import TASKS

K = float(sys.argv[1]) if len(sys.argv) > 1 else 4.0
mode = sys.argv[2] if len(sys.argv) > 2 else "lua"
env = PZParallelEnv(n_agents=1, task="survive", time_scale=K, max_steps=60, seed=3, zombie_behaviour="Attack",
                    zombie_ring=(8, 8))
TASKS["survive"].zombies_per_agent = 14 if mode == "lua" else 0
try:
    env.reset()
    name = env.possible_agents[0]
    for step in range(60):
        env.step({name: 0})
        me = env.state[name]
        ds = sorted(math.hypot(z[0] - me["x"], z[1] - me["y"]) for z in me["z"])
        if step % 5 == 0:
            print(f"t={step:3d}s hp={me['hp']:5.1f} zn(30 tiles)={me['zn']:3d} nearest={[round(d,1) for d in ds[:4]]}", flush=True)
finally:
    env.close()
