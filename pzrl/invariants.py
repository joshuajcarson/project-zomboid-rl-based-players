"""Environment invariants as code: checks (with idempotent repairs) that run at every reset, so nobody has to remember or notice that the
agent has the expected inventory, is alive, and stands in the arena. Every result goes to logs/invariants.jsonl; a check that cannot be
repaired is returned as "failed" and the caller decides (the benchmark refuses to write such a run to the ledger).

A check is a function (env, name) -> (status, detail) with status "ok", "repaired" or "failed"."""
import json
import re
import time
from pathlib import Path

LOG = Path(__file__).resolve().parent.parent / "logs" / "invariants.jsonl"


def parse_inv(msg):
    """'items=12 weight=9.5 bats=1' -> {'items': 12, 'weight': 9.5, 'bats': 1}"""
    return {k: float(v) if "." in v else int(v) for k, v in re.findall(r"(\w+)=(-?[0-9.]+)", msg or "")}


def check_alive(env, name):
    st = env.state.get(name)
    if not st:
        return "failed", "no state for the player (not in the world)"
    if st.get("dead") or st.get("hp", 100) <= 0:
        return "failed", "character is dead"
    return "ok", ""


def client_count(env, name, item, wait=6.0):
    """The item count of the CLIENT's own inventory. The server's `inv` cannot be used: server-side AddItem never reaches a real client, so
    its view drifts (11 phantom bats against 1 real one on 2026-10-28). The bot logs INVCOUNT to the client's log; read it from there."""
    import glob, os
    logs = sorted(glob.glob(str(LOG.parent / "env-rendered-*.log")), key=os.path.getmtime)
    if not logs:
        return None
    path = logs[-1]
    start = os.path.getsize(path)
    env.control[name]._bot("invcount", item)
    short = item.split(".")[-1]
    deadline = time.time() + wait
    while time.time() < deadline:
        time.sleep(0.5)
        with open(path, "rb") as f:
            f.seek(start)
            m = re.search(rb"INVCOUNT " + short.encode() + rb"=(\d+)", f.read())
        if m:
            return int(m.group(1))
    return None


def check_one_bat(env, name):
    """Exactly one bat in the client's inventory. Extra bats weigh 2 each (48 of them slowed the character and drained endurance in the
    2026-10-28 runs); none means a fresh body fights bare-handed."""
    if not env.give_weapon or name not in env.rendered:
        return "ok", "not applicable"
    have = client_count(env, name, env.give_weapon)
    if have is None:                                        # an unreadable inventory is a failure, not a pass
        return "failed", "client inventory count unreadable"
    if have == 1:
        return "ok", ""
    env.control[name]._bot("tidy", env.give_weapon)         # client-side: keeps one bat when there are several
    if have == 0:
        env.control[name]._bot("giveitem", env.give_weapon)  # idempotent: adds one only when none is there
    now = client_count(env, name, env.give_weapon)
    return ("repaired", f"bats {have} -> {now}") if now == 1 else ("failed", f"bats {have} -> {now} after repair")


def check_in_arena(env, name):
    st = env.state.get(name)
    if not st:
        return "failed", "no state"
    x0, y0, x1, y1 = env.spawn_box
    margin = 25
    if x0 - margin <= st["x"] <= x1 + margin and y0 - margin <= st["y"] <= y1 + margin:
        return "ok", ""
    return "failed", f"player at {st['x']:.0f},{st['y']:.0f} is outside the arena box"


CHECKS = [check_alive, check_one_bat, check_in_arena]


def run_all(env, names=None, phase="reset"):
    """Run every check for every named agent, log the results, return the list of failures (empty = all fine)."""
    failures = []
    LOG.parent.mkdir(exist_ok=True)
    with open(LOG, "a") as f:
        for name in (names or env.possible_agents):
            for chk in CHECKS:
                try:
                    status, detail = chk(env, name)
                except Exception as e:
                    status, detail = "failed", f"check crashed: {e!r}"
                if status != "ok" or detail:
                    f.write(json.dumps({"t": time.strftime("%Y-%m-%d %H:%M:%S"), "phase": phase, "agent": name, "check": chk.__name__,
                                        "status": status, "detail": detail}) + "\n")
                if status == "failed":
                    failures.append((name, chk.__name__, detail))
                env.invariant_repairs = getattr(env, "invariant_repairs", 0) + (status == "repaired")
    return failures
