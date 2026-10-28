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


def check_one_bat(env, name):
    """Exactly one bat in the whole inventory. Extra bats weigh 2 each (48 of them slowed the character and drained endurance in the
    2026-10-28 runs); none means a fresh body fights bare-handed."""
    if not env.give_weapon or name not in env.rendered:
        return "ok", "not applicable"
    short = env.give_weapon
    try:
        a = env.channel.command(f"inv|{name}", timeout=10)
        have = parse_inv(a["msg"]).get("bats", -1)
    except Exception as e:                                  # an unreadable inventory is a failure, not a pass
        return "failed", f"inventory unreadable: {e}"
    if have == 1:
        return "ok", ""
    env.control[name]._bot("tidy", short)                   # client-side: keeps one bat when there are several
    if have == 0:
        env.control[name]._bot("giveitem", short)           # idempotent: adds one only when none is there
    time.sleep(1.0)
    try:
        now = parse_inv(env.channel.command(f"inv|{name}", timeout=10)["msg"]).get("bats", -1)
    except Exception:
        now = -1
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
