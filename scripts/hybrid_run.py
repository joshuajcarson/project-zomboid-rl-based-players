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
ap.add_argument("--arms", default="llm", help="comma-separated planners alternating by episode: llm, rule, idle (H-B)")
ap.add_argument("--episode-seconds", type=int, default=120, help="game seconds per episode")
ap.add_argument("--zombies", type=int, default=2)
ap.add_argument("--ring", type=float, nargs=2, default=(8, 14))
ap.add_argument("--box", type=float, nargs=4, default=(10730, 9380, 10810, 9440), help="spawn box near buildings with containers")
ap.add_argument("--hunger", type=float, default=0.6)
ap.add_argument("--thirst", type=float, default=0.6)
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--supplies-at", default="", help="x,y of a known reachable container to seed into (default: the nearest storage container)")
ap.add_argument("--supplies", default="", help="server-side seeding at episode start, e.g. Base.Apple:3,Base.WaterBottle:2,Base.Bandage:2 (into the container nearest the player)")
ap.add_argument("--fixes", action="store_true", help="scenario fixes (2026-11-14): auto-drink off, carried supplies stripped, seeded types cleared "
                "from the --supplies-at container (and from every other container within 45 squares) before seeding, first decision only once the survey shows the set hunger")
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
        if a.fixes and a.supplies_at:
            # mobility probe: some spawns are fenced-in pockets where the character cannot move at all (HBfix ep 1, HBfix3 ep 5); walk
            # toward the supplies for 3 game seconds and draw a new spawn when it did not move a tile (max 3 redraws)
            px, py = (int(v) for v in a.supplies_at.split(","))
            for attempt in range(4):
                x0, y0 = env.state[a0]["x"], env.state[a0]["y"]
                env.control[a0]._bot("goto", px, py - 1)
                env._read(env._game_seconds(3))
                env.control[a0]._bot("stop")
                moved = ((env.state[a0]["x"] - x0) ** 2 + (env.state[a0]["y"] - y0) ** 2) ** 0.5
                if moved >= 1.0 or attempt == 3:
                    break
                log.write(json.dumps({"probe_fail": ep, "x": x0, "y": y0, "moved": round(moved, 2)}) + "\n"); log.flush()
                obs, _ = env.reset()
                a0 = env.agents[0]
            obs = {n: env._obs(n) for n in env.agents}
        if a.fixes:
            env.control[a0]._bot("autodrink", 0)
            env.control[a0]._bot("strip")
            if a.supplies_at:
                sx, sy = a.supplies_at.split(",")
                types = ",".join(x.split(":")[0] for x in a.supplies.split(",") if x)
                env.channel.command(f"clearat|{sx}|{sy}|{types}")
                env.channel.command(f"clearnear|{sx}|{sy}|45|{types}")     # stray seeds elsewhere come back on every server boot
        for spec in [x for x in a.supplies.split(",") if x]:
            itype, n = spec.split(":")
            if a.supplies_at:
                sx, sy = a.supplies_at.split(",")
                env.channel.command(f"seedat|{sx}|{sy}|{itype}|{n}")
            else:
                env.channel.command(f"seed|{a0}|{itype}|{n}|30")
        env.channel.command(f"stats|{a0}|{a.hunger}|{a.thirst}")        # server-side: Build 42 reverts client-side stat changes
        if a.fixes:                                                    # the server's stat change reaches the client a moment later
            for _ in range(6):
                h = hybrid.survey(env, a0)["stats"].get("hunger")
                if isinstance(h, float) and abs(h - a.hunger) <= 0.05:
                    break
                env._read(env._game_seconds(1))
        arm = a.arms.split(",")[(ep - 1) % len(a.arms.split(","))]
        env.say(f"hybrid | episode {ep} | arm {arm}")
        current, pending, steps, dead, last = "wait", None, 0, False, ""
        if ep == 1:
            stuck = set()          # --fixes: containers whose loot ended within 3 s with nothing taken (no path / nothing queued): whole session
        failed = set(stuck)        # plus any failed loot this episode (an interrupted loot must not blacklist the shelf for good, HBfix4)
        while steps < a.episode_seconds and time.time() < t_stop:
            if pending is None:
                sv = hybrid.survey(env, a0)
                if a.fixes and a.supplies_at:          # the scenario's supplies are in this building: natural containers in the next building
                    qx, qy = (int(v) for v in a.supplies_at.split(","))     # can be walked to but never looted (HBfix4-5), so neither planner sees them
                    sv["containers"] = [c for c in sv["containers"] if ((c.get("x", 0) - qx) ** 2 + (c.get("y", 0) - qy) ** 2) ** 0.5 <= 12]
                text = hybrid.state_text(env, a0, sv, last, failed)
                if arm == "llm":
                    pending = pool.submit(hybrid.ask, text, a.model)
                else:                                               # rule / idle decide instantly, through the same dispatch path
                    dec0 = hybrid.rule_decide(env, a0, sv, failed) if arm == "rule" else {"skill": "wait", "reason": "idle"}
                    pending = pool.submit(lambda d=dec0: (d, 0.0, None))
            if pending.done():
                dec, secs, err = pending.result()
                pending = None
                row = {"t": time.strftime("%H:%M:%S"), "episode": ep, "arm": arm, "step": steps, "model": a.model, "latency_s": round(secs, 2),
                       "valid": dec is not None, "error": err, "skill": dec and dec.get("skill"), "container": dec and dec.get("container"),
                       "reason": (dec or {}).get("reason", "")[:200], "stats": sv["stats"], "n_containers": len(sv["containers"]), "containers": sv["containers"],
                       "zombies": len(env.state[a0]["z"])}
                if dec and dec["skill"] in hybrid.ONE_SHOT:
                    skill, arg, arg2, arg3 = dec["skill"], "", "", ""
                    if skill == "loot":                                          # by the coordinates the planner saw (numbering moves with the player)
                        c = next((c for c in sv["containers"] if int(c.get("i", 0)) == (dec.get("container") or 1)), None)
                        skill, arg, arg2 = ("lootat", int(c["x"]), int(c["y"])) if c else ("loot", 1, "")
                        if c and a.fixes:
                            arg3 = int(c.get("ci", 1))                           # which container on that square (HBfix2)
                    waited = hybrid.run_one_shot(env, a0, skill, arg, arg2, arg3)  # waits for the action queue; no movement commands
                    steps += waited
                    row["effect"] = effect(sv, hybrid.survey(env, a0))
                    row["waited"] = waited
                    last = hybrid.outcome(dec["skill"], row["effect"], waited)
                    e = row["effect"] or {}
                    if skill == "lootat" and (e.get("food") or 0) + (e.get("drink") or 0) + (e.get("bandages") or 0) <= 0:
                        failed.add((arg, arg2))                                       # remembered for this episode, shown to the planner
                        if a.fixes and waited <= 3 and f"{arg},{arg2}" != a.supplies_at:
                            stuck.add((arg, arg2))
                    current = "wait"
                elif dec:
                    if dec["skill"] != current:
                        last = "%s (started)" % dec["skill"]
                    current = dec["skill"]
                log.write(json.dumps(row) + "\n"); log.flush()
                print(json.dumps({k: row[k] for k in ("episode", "step", "latency_s", "valid", "skill")} | {"effect": row.get("effect")}), flush=True)
                if a0 not in env.state or env.state[a0].get("dead") or env.state[a0]["hp"] <= 0:
                    dead = True
                    break
                if arm == "llm":
                    continue                                       # rule / idle fall through: one game step per decision
            obs, rew, term, trunc, info = env.step({a0: hybrid.step_action(current, obs[a0])})
            steps += 1
            if term.get(a0) or a0 not in env.agents:
                dead = True
                break
        end_sv = hybrid.survey(env, a0) if not dead and a0 in env.state else {"stats": {}}
        log.write(json.dumps({"episode_end": ep, "arm": arm, "steps": steps, "dead": dead, "hp": env.state.get(a0, {}).get("hp"), "end": end_sv["stats"]}) + "\n"); log.flush()
        if pending is not None:
            pending.result()                                   # do not leak a planner call into the next episode
finally:
    log.close()
    env.close()
