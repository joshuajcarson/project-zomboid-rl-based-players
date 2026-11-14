"""Hybrid planner (Stage A, 2026-11-14): a language model picks one high-level skill at a time; the skills run in the game.

fight / flee / wait are short scripted step loops (the scripted charge fighter, running away from the nearest zombie, standing still);
eat / drink / bandage / loot queue the game's own timed actions through the client bot (scripts/rl_bot_dev.lua). The model is called
through the Claude CLI (`claude -p`, structured JSON output, no tools), so it runs on the plan's usage and needs no API key.
While the model thinks, the current skill keeps running, so the character is never frozen waiting for a decision.
"""
import glob
import json
import math
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

from .baselines import charge_param, nearest_zombie_vec, _dir_to_action

LOGS = Path(__file__).resolve().parent.parent / "logs"
SKILLS = ["fight", "flee", "wait", "eat", "drink", "bandage", "loot"]
ONE_SHOT = {"eat": 8, "drink": 6, "bandage": 6, "loot": 10}     # game seconds the timed action is left to run
SCHEMA = json.dumps({"type": "object", "properties": {
    "skill": {"type": "string", "enum": SKILLS},
    "container": {"type": "integer", "description": "for loot: the container number from the list (1 = nearest)"},
    "reason": {"type": "string"}}, "required": ["skill", "reason"]})
SYSTEM = ("You are the high-level planner for a survivor in Project Zomboid, a zombie survival game. Each turn you get the character's "
          "state and choose ONE skill. Skills: fight = attack the nearest zombie for a few seconds (a baseball bat is equipped); flee = run "
          "away from the nearest zombie for a few seconds; wait = stand still; eat = eat food from the inventory; drink = drink water from the "
          "inventory; bandage = bandage a bleeding wound; loot = walk to a listed container and take its food, water and bandages (give its "
          "number). Goals in order: stay alive, stop bleeding, keep hunger and thirst low, gather supplies. Eating, drinking, bandaging and "
          "looting take several seconds and leave you defenceless, so do them when no zombie is close. Hunger and thirst run from 0 (fine) "
          "to 1 (starving). Answer with the JSON object only.")
_fight = charge_param(1.8, 0.0)
_DIRS = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]       # world x grows east, y grows south


def newest_log():
    logs = sorted(glob.glob(str(LOGS / "env-rendered-*.log")), key=os.path.getmtime)
    return logs[-1] if logs else None


def client_query(env, name, cmd, arg="", until=None, wait=8.0):
    """Send a bot command; return the client log text written after it (up to the `until` marker, or what arrived within `wait`)."""
    path = newest_log()
    start = os.path.getsize(path)
    env.control[name]._bot(cmd, arg)
    text, deadline = "", time.time() + wait
    while time.time() < deadline:
        time.sleep(0.3)
        with open(path, "rb") as f:
            f.seek(start)
            text = f.read().decode("utf-8", "replace")
        if until is None or until in text:
            break
    return text


def _kv(line):
    return {k: (float(v) if re.fullmatch(r"-?[0-9.]+", v) else v) for k, v in re.findall(r"(\w+)=(\S+)", line)}


def survey(env, name, r=15):
    """The character's stats, wounds and key items, plus the nearest containers (client-side `survey` command)."""
    text = client_query(env, name, "survey", r, until="SURVEYEND")
    stats, conts = {}, []
    for line in text.splitlines():
        if "RLBOT SURVEY " in line:
            stats = _kv(line.split("RLBOT SURVEY ", 1)[1])
        elif "RLBOT CONT " in line:
            conts.append(_kv(line.split("RLBOT CONT ", 1)[1]))
    return {"stats": stats, "containers": conts}


def state_text(env, name, sv):
    me = env.state[name]
    s = sv["stats"]
    zs = sorted(((math.hypot(z[0] - me["x"], z[1] - me["y"]), math.atan2(z[1] - me["y"], z[0] - me["x"])) for z in me["z"]), key=lambda t: t[0])
    zlines = ["%.1f tiles %s" % (d, _DIRS[int(round(a / (math.pi / 4))) % 8]) for d, a in zs[:4]] or ["none visible"]
    cl = ["%d: %s %.1f tiles away, %d items (food %d, water %d, bandages %d)" % (int(c.get("i", 0)), c.get("kind"), c.get("dist", 0),
          int(c.get("items", 0)), int(c.get("food", 0)), int(c.get("drink", 0)), int(c.get("bandages", 0))) for c in sv["containers"]] or ["none in range"]
    return ("Health %.0f/100. Hunger %s, thirst %s, fatigue %s, endurance %s, panic %s. Bleeding wounds: %s, injuries: %s.\n"
            "Inventory: food %s, water %s, bandages %s.\nZombies (nearest first): %s.\nContainers nearby: %s.\nChoose the next skill."
            % (me["hp"], s.get("hunger"), s.get("thirst"), s.get("fatigue"), s.get("endurance"), s.get("panic"), s.get("bleeding"),
               s.get("wounds"), s.get("food"), s.get("drink"), s.get("bandages"), "; ".join(zlines), "; ".join(cl)))


def ask(text, model="sonnet", timeout=60):
    """One planner decision. Returns (decision dict or None, seconds, error text or None)."""
    t0 = time.time()
    cmd = ["claude", "-p", "--model", model, "--tools", "", "--no-session-persistence", "--strict-mcp-config", "--setting-sources", "",
           "--output-format", "json", "--json-schema", SCHEMA, "--system-prompt", SYSTEM, text]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=timeout, cwd=tempfile.gettempdir())
        d = json.loads(out.stdout)
        dec = d.get("structured_output")
        if d.get("is_error") or not isinstance(dec, dict) or dec.get("skill") not in SKILLS:
            return None, time.time() - t0, "invalid: " + out.stdout[-300:]
        return dec, time.time() - t0, None
    except Exception as e:                          # timeout, CLI missing, bad JSON
        return None, time.time() - t0, repr(e)[:300]


def step_action(skill, obs):
    """Low-level action for one game second of a continuous skill."""
    if skill == "fight":
        return _fight(obs)
    if skill == "flee":
        v = nearest_zombie_vec(obs)
        return 0 if v is None else _dir_to_action(-v[0], -v[1])
    return 0
