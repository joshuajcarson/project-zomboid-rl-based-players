"""Run the hybrid planner on the real client and log every decision (Stage A plumbing test and later stages).

    python scripts/hybrid_run.py --minutes 30 --model sonnet --out results/experiments-2026-11-14/a_plumbing.jsonl

Each episode: reset at the spawn box (zombies on a ring), start the character hungry and thirsty, then loop: survey + state text +
planner call in a background thread while the current skill keeps running; apply the decision (continuous skill, or a one-shot timed
action left to run for a few game seconds); verify one-shot effects with a survey before and after. One JSON line per decision.
"""
import argparse
import concurrent.futures as cf
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pzrl.env import PZParallelEnv
from pzrl.tasks import TASKS
from pzrl import hybrid

ap = argparse.ArgumentParser()
ap.add_argument("--minutes", type=float, default=30)
ap.add_argument("--model", default="sonnet")
ap.add_argument("--episode-seconds", type=int, default=120, help="game seconds per episode")
ap.add_argument("--zombies", type=int, default=2)
ap.add_argument("--ring", type=float, nargs=2, default=(8, 14))
ap.add_argument("--box", type=float, nargs=4, default=(10730, 9380, 10810, 9440), help="spawn box near buildings with containers")
ap.add_argument("--hunger", type=float, default=0.6)
ap.add_argument("--thirst", type=float, default=0.6)
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--out", required=True)
a = ap.parse_args()

TASKS["fight"].zombies_per_agent = a.zombies
env = PZParallelEnv(n_agents=1, task="fight", backend="rendered", max_steps=10 ** 6, seed=a.seed, zombie_ring=tuple(a.ring),
                    spawn_box=tuple(a.box), keep_alive=True)
os.makedirs(os.path.dirname(a.out), exist_ok=True)
log = open(a.out, "a", encoding="utf-8")
pool = cf.ThreadPoolExecutor(1)
t_stop = time.time() + a.minutes * 60
ep = 0


def effect(before, after):
    b, c = before["stats"], after["stats"]
    keys = ("hunger", "thirst", "food", "drink", "bandages", "bleeding", "hp")
    return {k: (round(c[k] - b[k], 3) if isinstance(b.get(k), float) and isinstance(c.get(k), float) else None) for k in keys}


try:
    while time.time() < t_stop:
        obs, _ = env.reset()
        a0 = env.agents[0]
        ep += 1
        env.control[a0]._bot("setstats", a.hunger, a.thirst)
        env.say(f"hybrid stage A | episode {ep} | planner {a.model}")
        current, pending, steps, dead = "wait", None, 0, False
        while steps < a.episode_seconds and time.time() < t_stop:
            if pending is None:
                sv = hybrid.survey(env, a0)
                text = hybrid.state_text(env, a0, sv)
                pending = pool.submit(hybrid.ask, text, a.model)
            if pending.done():
                dec, secs, err = pending.result()
                pending = None
                row = {"t": time.strftime("%H:%M:%S"), "episode": ep, "step": steps, "model": a.model, "latency_s": round(secs, 2),
                       "valid": dec is not None, "error": err, "skill": dec and dec.get("skill"), "container": dec and dec.get("container"),
                       "reason": (dec or {}).get("reason", "")[:200], "stats": sv["stats"], "n_containers": len(sv["containers"]),
                       "zombies": len(env.state[a0]["z"])}
                if dec and dec["skill"] in hybrid.ONE_SHOT:
                    arg = dec.get("container") or 1 if dec["skill"] == "loot" else ""
                    env.control[a0]._bot(dec["skill"], arg)
                    env._read(env._game_seconds(hybrid.ONE_SHOT[dec["skill"]]))      # let the timed action run; no movement commands
                    steps += hybrid.ONE_SHOT[dec["skill"]]
                    row["effect"] = effect(sv, hybrid.survey(env, a0))
                    current = "wait"
                elif dec:
                    current = dec["skill"]
                log.write(json.dumps(row) + "\n"); log.flush()
                print(json.dumps({k: row[k] for k in ("episode", "step", "latency_s", "valid", "skill")} | {"effect": row.get("effect")}), flush=True)
                if a0 not in env.state or env.state[a0].get("dead") or env.state[a0]["hp"] <= 0:
                    dead = True
                    break
                continue
            obs, rew, term, trunc, info = env.step({a0: hybrid.step_action(current, obs[a0])})
            steps += 1
            if term.get(a0) or a0 not in env.agents:
                dead = True
                break
        log.write(json.dumps({"episode_end": ep, "steps": steps, "dead": dead, "hp": env.state.get(a0, {}).get("hp")}) + "\n"); log.flush()
        if pending is not None:
            pending.result()                                   # do not leak a planner call into the next episode
finally:
    log.close()
    env.close()
