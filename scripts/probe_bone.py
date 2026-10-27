"""Ask the rendered bot to log the head-bone position of the nearest zombie (see commands.bone in rl_bot_dev.lua)."""
import sys, time
sys.path.insert(0, ".")
from pzrl.env import PZParallelEnv
from pzrl.tasks import TASKS
TASKS["fight"].zombies_per_agent = 2
env = PZParallelEnv(n_agents=1, task="fight", backend="rendered", max_steps=10, seed=7, zombie_ring=(3, 5), time_scale=1.0,
                    spawn_box=(10730, 9380, 10810, 9440), keep_alive=True)
try:
    env.reset(); a0 = env.agents[0]
    for _ in range(3):
        env.control[a0]._bot("bone"); env._read(2); time.sleep(1)
finally:
    env.close()
