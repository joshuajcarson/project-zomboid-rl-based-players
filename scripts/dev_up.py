"""Bring up the server and one real client at the hybrid spawn box (no zombies) and leave them running for interactive debugging.
    python scripts/dev_up.py      (then send bot commands with pzrl.channel.ServerChannel(17600); stop with scripts/cleanup.py)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pzrl.env import PZParallelEnv
from pzrl.tasks import TASKS
TASKS["fight"].zombies_per_agent = 0
env = PZParallelEnv(n_agents=1, task="fight", backend="rendered", max_steps=10 ** 6, seed=7, spawn_box=(10730, 9380, 10810, 9440), keep_alive=True)
env.reset()
print("DEV UP", env.agents, flush=True)
os._exit(0)          # leave the server and client running (env.close() would stop them)
