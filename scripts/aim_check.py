"""Start (or reuse) the rendered client, put a zombie nearby and log the aim-vector error with and without the override.
Usage: python scripts/aim_check.py   then read the RLBOT aimcheck lines in .pzclient/Logs/*DebugLog*"""
import sys, time
sys.path.insert(0, ".")
from pzrl.env import PZParallelEnv
from pzrl.tasks import TASKS
TASKS["fight"].zombies_per_agent = 2
env = PZParallelEnv(n_agents=1, task="fight", backend="rendered", max_steps=20, seed=3, zombie_ring=(5, 8),
                    spawn_box=(10730, 9380, 10810, 9440), keep_alive=True)
try:
    env.reset()
    rc = env.control[env.agents[0]]
    for i in range(5):
        rc._bot("aimcheck"); time.sleep(1.5)
finally:
    env.close()
