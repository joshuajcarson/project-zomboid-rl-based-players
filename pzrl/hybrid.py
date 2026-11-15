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
ONE_SHOT = {"eat": 20, "drink": 15, "bandage": 15, "loot": 35, "lootat": 35}   # cap in game seconds; the skill ends earlier when the action queue empties
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


def survey(env, name, r=30):
    """The character's stats, wounds and key items, plus the nearest containers (client-side `survey` command)."""
    text = client_query(env, name, "survey", r, until="SURVEYEND")
    stats, conts = {}, []
    for line in text.splitlines():
        if "RLBOT SURVEY " in line:
            stats = _kv(line.split("RLBOT SURVEY ", 1)[1])
        elif "RLBOT CONT " in line:
            conts.append(_kv(line.split("RLBOT CONT ", 1)[1]))
    return {"stats": stats, "containers": conts}


def state_text(env, name, sv, last="", failed=()):
    me = env.state[name]
    s = sv["stats"]
    zs = sorted(((math.hypot(z[0] - me["x"], z[1] - me["y"]), math.atan2(z[1] - me["y"], z[0] - me["x"])) for z in me["z"]), key=lambda t: t[0])
    zlines = ["%.1f tiles %s" % (d, _DIRS[int(round(a / (math.pi / 4))) % 8]) for d, a in zs[:4]] or ["none visible"]
    cl = ["%d: %s %.1f tiles away, %d items (food %d, water %d, bandages %d)%s" % (int(c.get("i", 0)), c.get("kind"), c.get("dist", 0),
          int(c.get("items", 0)), int(c.get("food", 0)), int(c.get("drink", 0)), int(c.get("bandages", 0)),
          " [looting here failed earlier]" if (int(c.get("x", 0)), int(c.get("y", 0))) in failed else "") for c in sv["containers"]] or ["none in range"]
    return ("Health %.0f/100. Hunger %s, thirst %s, fatigue %s, endurance %s, panic %s. Bleeding wounds: %s, injuries: %s.\n"
            "Inventory: food %s, water %s, bandages %s.\nZombies (nearest first): %s.\nContainers nearby: %s.\nLast skill: %s.\nChoose the next skill."
            % (me["hp"], s.get("hunger"), s.get("thirst"), s.get("fatigue"), s.get("endurance"), s.get("panic"), s.get("bleeding"),
               s.get("wounds"), s.get("food"), s.get("drink"), s.get("bandages"), "; ".join(zlines), "; ".join(cl), last or "none yet"))


def ask(text, model="sonnet", timeout=60, system=None):
    """One planner decision. Returns (decision dict or None, seconds, error text or None)."""
    t0 = time.time()
    cmd = ["claude", "-p", "--model", model, "--tools", "", "--no-session-persistence", "--strict-mcp-config", "--setting-sources", "",
           "--output-format", "json", "--json-schema", SCHEMA, "--system-prompt", system or SYSTEM, text]
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


def busy(env, name):
    """Length of the client's timed-action queue (0 = idle, -1 = unknown)."""
    m = re.search(r"BUSY n=(-?\d+)", client_query(env, name, "busy", until="BUSY n=", wait=4.0))
    return int(m.group(1)) if m else -1


def run_one_shot(env, name, skill, arg="", arg2="", arg3=""):
    """Queue a timed-action skill and wait (one game second at a time, no movement commands) until the client's action queue is empty or
    the cap is reached. Returns the game seconds waited."""
    if arg3 != "":
        env.channel.command(f"bot|{name}|{skill}|{arg}|{arg2}|{arg3}")      # the bot relay passes 3 arguments
    else:
        env.control[name]._bot(skill, arg, arg2)
    waited = 0
    env._read(env._game_seconds(2)); waited += 2                       # give the queue time to fill
    while waited < ONE_SHOT[skill]:
        if busy(env, name) == 0:
            break
        env._read(env._game_seconds(1)); waited += 1
    return waited


def outcome(skill, eff, waited):
    """One line for the planner about what its last skill did."""
    if eff is None:
        return skill
    parts = ["%s %+g" % (k, eff[k]) for k in ("food", "drink", "bandages", "hunger", "thirst", "bleeding", "hp") if eff.get(k)]
    return "%s took %d s: %s" % (skill, waited, ", ".join(parts) if parts else "no change (interrupted, nothing to take, or nothing to do)")


def rule_decide(env, name, sv, failed=()):
    """Hand-written priority planner over the same skills (the H-B baseline). Same output shape as ask()."""
    me, s = env.state[name], sv["stats"]
    zd = sorted(math.hypot(z[0] - me["x"], z[1] - me["y"]) for z in me["z"])
    near = zd[0] if zd else 99.0
    g = lambda k: s.get(k) if isinstance(s.get(k), float) else 0.0
    if g("bleeding") > 0 and g("bandages") > 0 and near > 3:
        return {"skill": "bandage", "reason": "rule: bleeding"}
    if near <= 3:
        return {"skill": "flee" if me["hp"] < 35 else "fight", "reason": "rule: zombie close"}
    if g("hunger") > 0.3 and g("food") > 0:
        return {"skill": "eat", "reason": "rule: hungry"}
    if g("thirst") > 0.3 and g("drink") > 0:
        return {"skill": "drink", "reason": "rule: thirsty"}
    if near > 8 and (g("food") == 0 or g("drink") == 0 or g("bandages") == 0):
        for c in sv["containers"]:
            if (c.get("food", 0) + c.get("drink", 0) + c.get("bandages", 0)) > 0 and (int(c.get("x", 0)), int(c.get("y", 0))) not in failed:
                return {"skill": "loot", "container": int(c.get("i", 1)), "reason": "rule: missing supplies"}
    if near <= 6:
        return {"skill": "fight", "reason": "rule: zombie approaching"}
    return {"skill": "wait", "reason": "rule: nothing to do"}


# ---- lessons file (track H-L1, docs/planner-learning.md) ------------------------------------------------------------------------------
LESSONS_MAX, LESSON_WORDS = 8, 25
LESSONS_SCHEMA = json.dumps({"type": "object", "properties": {
    "lessons": {"type": "array", "items": {"type": "string"}, "maxItems": LESSONS_MAX},
    "kind": {"type": "array", "items": {"type": "string", "enum": ["general", "scenario"]}, "maxItems": LESSONS_MAX}},
    "required": ["lessons", "kind"]})
REFLECT_SYSTEM = ("You coach the high-level planner of a survivor in Project Zomboid. The planner picks one skill at a time (fight, flee, wait, "
                  "eat, drink, bandage, loot a listed container). You get the current list of lessons and the log of one finished episode: "
                  "each decision with the state it saw and what the skill achieved, and how the episode ended. Rewrite the lessons list so the "
                  "planner does better next time on its goals: stay alive, stop bleeding, keep hunger and thirst low, gather supplies. Keep "
                  "lessons that still hold, merge duplicates, drop ones the episode contradicts, add at most two new ones. At most %d lessons, "
                  "each a concrete instruction under %d words. For each lesson say whether it is 'general' (true in any place) or 'scenario' "
                  "(about this map, these containers or positions). Answer with the JSON object only." % (LESSONS_MAX, LESSON_WORDS))


def lessons_system(lessons):
    """The planner's system prompt with the lessons appended (empty list = the plain prompt)."""
    if not lessons:
        return SYSTEM
    return SYSTEM + "\nLessons from earlier episodes (follow them unless the current state clearly says otherwise):\n" + "\n".join("- " + l for l in lessons)


def episode_log(trace, end):
    """Compact text log of one episode for reflect(): one line per decision plus the ending."""
    lines = []
    for r in trace[-60:]:
        s = r.get("stats") or {}
        lines.append("t=%ss hp=%s hunger=%s thirst=%s carried food/water/bandages=%s/%s/%s zombies=%s -> %s%s. Result: %s" % (
            r.get("step"), s.get("hp"), s.get("hunger"), s.get("thirst"), s.get("food"), s.get("drink"), s.get("bandages"),
            r.get("nearest", "?"), r.get("skill"), (" container %s" % r.get("container")) if r.get("skill") == "loot" else "",
            r.get("outcome") or "continuing"))
    e = end.get("end") or {}
    lines.append("END: %s after %s s, hp %s, hunger %s, thirst %s." % ("DIED" if end.get("dead") else "survived", end.get("steps"), end.get("hp"),
                 e.get("hunger"), e.get("thirst")))
    return "\n".join(lines)


def reflect(lessons, log_text, model="sonnet", timeout=90):
    """Rewrite the lessons list from one episode's log. Returns (lessons, kinds, seconds, error); on error the old lessons are kept."""
    t0 = time.time()
    text = "Current lessons:\n" + ("\n".join("- " + l for l in lessons) or "(none yet)") + "\n\nEpisode log:\n" + log_text
    cmd = ["claude", "-p", "--model", model, "--tools", "", "--no-session-persistence", "--strict-mcp-config", "--setting-sources", "",
           "--output-format", "json", "--json-schema", LESSONS_SCHEMA, "--system-prompt", REFLECT_SYSTEM, text]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=timeout, cwd=tempfile.gettempdir())
        d = json.loads(out.stdout).get("structured_output") or {}
        new = [" ".join(str(l).split()[:LESSON_WORDS]) for l in d.get("lessons", [])][:LESSONS_MAX]
        if not new and lessons:
            return lessons, [], time.time() - t0, "empty reply: kept the old lessons"
        return new, list(d.get("kind", []))[:len(new)], time.time() - t0, None
    except Exception as e:
        return lessons, [], time.time() - t0, repr(e)[:300]


if __name__ == "__main__":                                   # self-check of the pure helpers (no game, no model call)
    assert lessons_system([]) == SYSTEM
    assert lessons_system(["eat first"]).endswith("- eat first")
    log = episode_log([{"step": 3, "stats": {"hp": 90.0, "hunger": 0.6}, "skill": "loot", "container": 2, "outcome": "loot took 20 s: food +3"}],
                      {"dead": False, "steps": 120, "hp": 80.0, "end": {"hunger": 0.2, "thirst": 0.1}})
    assert "container 2" in log and log.endswith("thirst 0.1.")
    print("hybrid lessons self-check ok")
