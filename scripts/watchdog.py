"""Live validity watchdog for long runs: reads a run's JSONL as it grows and prints one ALERT line per new problem, so an invalid run is
stopped within an episode or two instead of being found at the end (2026-11-14).

    python scripts/watchdog.py results/experiments-2026-11-14/hb_s2.jsonl --arms llm,rule,idle --hunger 0.6 --known thirst
    python scripts/watchdog.py --selftest

Run it under a Monitor next to every long run. Each check is one function in CHECKS: (rows, cfg) -> list of (key, message); a key
alerts once. ADD A CHECK whenever a run turns out invalid in a way this did not catch (log it in docs/watchdog.md with the incident).
Rows are hybrid_run.py rows (decision rows with "step", episode rows with "episode_end").
"""
import argparse
import json
import os
import statistics
import sys
import time


def episodes(rows):
    """{episode: {"rows": [decision rows], "end": end row or None}}"""
    eps = {}
    for r in rows:
        if "episode_end" in r:
            eps.setdefault(r["episode_end"], {"rows": [], "end": None})["end"] = r
        elif "episode" in r:
            eps.setdefault(r["episode"], {"rows": [], "end": None})["rows"].append(r)
    return eps


# ---- checks (incident that motivated each one in the comment) ----------------------------------------------------------------------
def step1_death(rows, cfg):
    """H-B s1 run 2: a death during the reset was charged to the next episode (dead at step <= 1)."""
    return [("step1:%s" % r["episode_end"], "episode %s (%s) dead at step %s: death carried over from the reset" % (r["episode_end"], r["arm"], r["steps"]))
            for r in rows if "episode_end" in r and r["dead"] and r["steps"] <= 1]


def stall(rows, cfg):
    """H-B s1 run 1: the rule arm decided hundreds of times without the game step advancing."""
    out = []
    for ep, e in episodes(rows).items():
        run, last = 0, None
        for r in e["rows"]:
            run = run + 1 if r["step"] == last else 1
            last = r["step"]
            if run >= cfg.stall:
                out.append(("stall:%s" % ep, "episode %s (%s): %d decisions at step %s without the game advancing" % (ep, r["arm"], run, last)))
                break
    return out


def short_episode(rows, cfg):
    """An episode that ends alive before its length (other than the session's last) means the loop broke out early."""
    ends = [r for r in rows if "episode_end" in r]
    return [("short:%s" % r["episode_end"], "episode %s (%s) ended alive at step %s < %d" % (r["episode_end"], r["arm"], r["steps"], cfg.steps))
            for r in ends[:-1] if not r["dead"] and r["steps"] < cfg.steps]


def start_state(rows, cfg):
    """H-B: the server set hunger but not thirst. Check the first survey of every episode against the configured start."""
    out = []
    for ep, e in episodes(rows).items():
        if not e["rows"]:
            continue
        first = [r.get("stats") or {} for r in e["rows"][:3]]
        ready = len(first) >= 3 or e["end"] is not None    # wait for 3 surveys: the server's stat change can reach the client one survey late
        for k in ("hunger", "thirst") if ready else ():
            want = getattr(cfg, k)
            if want is None or k in cfg.known:
                continue
            got = [s.get(k) for s in first]
            if not any(isinstance(g, (int, float)) and abs(g - want) <= cfg.tol for g in got):
                out.append(("start:%s:%s" % (k, ep), "episode %s: first surveys %s %s, expected %s" % (ep, k, got, want)))
        if cfg.supplies and "supplies" not in cfg.known:
            conts = e["rows"][0].get("containers") or []
            if not any((c.get("food", 0) + c.get("drink", 0) + c.get("bandages", 0)) > 0 for c in conts):
                out.append(("supplies:%s" % ep, "episode %s: no container with supplies in the first survey" % ep))
    return out


def arm_rotation(rows, cfg):
    """Arms must alternate by episode in the configured order (interleaving is what makes the comparison valid)."""
    if not cfg.arms:
        return []
    arms = cfg.arms.split(",")
    return [("arm:%s" % r["episode_end"], "episode %s ran arm %s, expected %s" % (r["episode_end"], r["arm"], arms[(r["episode_end"] - 1) % len(arms)]))
            for r in rows if "episode_end" in r and r["arm"] != arms[(r["episode_end"] - 1) % len(arms)]]


def planner_health(rows, cfg):
    """Gate H-A bounds: >= 95% valid decisions and median latency <= 15 s (over the last 20 planner decisions)."""
    d = [r for r in rows if "step" in r and r.get("arm") == "llm"][-20:]
    if len(d) < 10:
        return []
    out = []
    valid = sum(1 for r in d if r.get("valid")) / len(d)
    if valid < 0.95:
        out.append(("valid:%d" % len(rows), "planner valid rate %.0f%% over the last %d decisions (errors: %s)" % (100 * valid, len(d), d[-1].get("error"))))
    lat = statistics.median(r.get("latency_s", 0) for r in d)
    if lat > 15:
        out.append(("latency:%d" % len(rows), "planner median latency %.1f s over the last %d decisions" % (lat, len(d))))
    return out


def stray_supplies(rows, cfg):
    """HBfix: leftover seeds in other containers (they come back on every server boot) lured the planner to far, unreachable containers."""
    if not cfg.supplies_at:
        return []
    sx, sy = (int(v) for v in cfg.supplies_at.split(","))
    out = []
    for ep, e in episodes(rows).items():
        if not e["rows"]:
            continue
        stray = [c for c in e["rows"][0].get("containers") or [] if (int(c.get("x", 0)), int(c.get("y", 0))) != (sx, sy)
                 and c.get("kind") in cfg.stray_kinds and (c.get("food", 0) + c.get("drink", 0) + c.get("bandages", 0)) >= cfg.stray_min]
        if stray:
            c = stray[0]
            out.append(("stray:%s" % ep, "episode %s: %d other containers hold supplies, e.g. %s at %d,%d (food %d, water %d, bandages %d)"
                        % (ep, len(stray), c.get("kind"), c.get("x"), c.get("y"), c.get("food", 0), c.get("drink", 0), c.get("bandages", 0))))
    return out


def skill_health(rows, cfg):
    """HBfix: 60 planner loots with 5 effective went unnoticed until the end. Alert when the last 10 uses of a one-shot skill are < 30% effective."""
    out = []
    for skill, gain in (("loot", lambda e: (e.get("food") or 0) + (e.get("drink") or 0) + (e.get("bandages") or 0) > 0),
                        ("eat", lambda e: (e.get("food") or 0) < 0 or (e.get("hunger") or 0) < -0.01),
                        ("drink", lambda e: (e.get("drink") or 0) < 0 or (e.get("thirst") or 0) < -0.01)):
        uses = [r for r in rows if "step" in r and r.get("skill") == skill and r.get("effect") is not None][-10:]
        if len(uses) == 10 and sum(1 for r in uses if gain(r["effect"])) < 3:
            out.append(("skill:%s:%d" % (skill, len(rows) // 50), "%s effective in %d of its last 10 uses (arms %s)"
                        % (skill, sum(1 for r in uses if gain(r["effect"])), sorted({r["arm"] for r in uses}))))
    return out


CHECKS = [step1_death, stall, short_episode, start_state, arm_rotation, planner_health, stray_supplies, skill_health]


def check(rows, cfg):
    return [a for chk in CHECKS for a in chk(rows, cfg)]


def read_rows(path):
    rows = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass                                        # a line being written right now
    return rows


def parse(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("--arms", default="")
    ap.add_argument("--steps", type=int, default=120, help="episode length in game seconds")
    ap.add_argument("--hunger", type=float, default=None)
    ap.add_argument("--thirst", type=float, default=None)
    ap.add_argument("--tol", type=float, default=0.05)
    ap.add_argument("--supplies", action="store_true", help="a container with supplies must be in every episode's first survey")
    ap.add_argument("--supplies-at", default="", help="x,y of the seeded container: other storage containers holding supplies are strays")
    ap.add_argument("--stray-min", type=int, default=3, help="supplies in one other container that count as a stray seed")
    ap.add_argument("--known", default="", help="comma-separated known deviations to skip (e.g. thirst), recorded on the card")
    ap.add_argument("--stall", type=int, default=30, help="decisions at one game step that count as a stall")
    ap.add_argument("--idle-minutes", type=float, default=10, help="alert when the file stops growing this long")
    ap.add_argument("--every", type=float, default=30, help="seconds between scans")
    ap.add_argument("--once", action="store_true", help="scan once and exit (1 if any alert)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    a.known = set(x for x in a.known.split(",") if x)
    a.stray_kinds = {"crate", "metal_shelves", "shelves", "counter", "fridge", "wardrobe", "dresser", "desk", "sidetable", "smallbox",
                     "cardboardbox", "militarycrate", "fireplace"}             # where the old seed commands put items
    return a


def selftest():
    cfg = parse(["--arms", "llm,rule,idle", "--hunger", "0.6", "--thirst", "0.6", "--supplies"])
    dec = lambda ep, arm, step, **kw: {"episode": ep, "arm": arm, "step": step, "valid": True, "latency_s": 2.5,
                                       "stats": {"hunger": 0.6, "thirst": 0.6}, "containers": [{"food": 1}], **kw}
    end = lambda ep, arm, steps, dead: {"episode_end": ep, "arm": arm, "steps": steps, "dead": dead}
    good = [dec(1, "llm", 3), end(1, "llm", 120, False), dec(2, "rule", 1), end(2, "rule", 40, True), dec(3, "idle", 1), end(3, "idle", 120, False)]
    assert check(good, cfg) == [], check(good, cfg)
    keys = lambda rows, c=cfg: {k.split(":")[0] for k, _ in check(rows, c)}
    assert keys(good + [dec(4, "llm", 1), end(4, "llm", 1, True)]) == {"step1"}
    assert keys(good + [dec(4, "llm", 3)] * 30) == {"stall"}
    late = [dec(1, "llm", 3, stats={"hunger": 0.0, "thirst": 0.6}), dec(1, "llm", 4), dec(1, "llm", 5)]
    assert keys(late) == set(), "a stat that arrives one survey late is not an alert"
    assert keys([dec(1, "llm", 3, stats={"hunger": 0.6, "thirst": 0.0})] * 3) == {"start"}
    assert keys([dec(1, "llm", 3, stats={"hunger": 0.6, "thirst": 0.0})] * 3, parse(["--thirst", "0.6", "--known", "thirst"])) == set()
    assert keys([dec(1, "llm", 3, containers=[{"food": 0}])]) == {"supplies"}
    assert keys([end(1, "rule", 120, False), end(2, "rule", 120, False)]) == {"arm"}
    assert keys([end(1, "llm", 50, False), end(2, "rule", 120, False)]) == {"short"}
    assert keys([dec(1, "llm", i, valid=False) for i in range(12)]) == {"valid"}
    cs = parse(["--supplies-at", "10753,9407"])
    assert keys([dec(1, "llm", 3, containers=[{"x": 10753, "y": 9407, "kind": "metal_shelves", "food": 3},
                                              {"x": 10781, "y": 9411, "kind": "shelves", "food": 12, "drink": 8}])], cs) == {"stray"}
    assert keys([dec(1, "llm", 3, containers=[{"x": 10753, "y": 9407, "kind": "metal_shelves", "food": 3},
                                              {"x": 10781, "y": 9414, "kind": "counter", "drink": 2}])], cs) == set()
    bad = [dec(1, "llm", i, skill="loot", effect={"food": 0}) for i in range(10)]
    assert keys(bad) == {"skill"}
    print("watchdog selftest ok")


def main(argv):
    a = parse(argv)
    if a.selftest:
        return selftest()
    seen, last_size, last_grow = set(), -1, time.time()
    print("watchdog on %s: %s" % (a.file, ", ".join(c.__name__ for c in CHECKS)), flush=True)
    while True:
        rows = read_rows(a.file)
        new = [(k, m) for k, m in check(rows, a) if k not in seen]
        for k, m in new:
            seen.add(k)
            print("ALERT %s %s" % (time.strftime("%H:%M:%S"), m), flush=True)
        size = os.path.getsize(a.file) if os.path.exists(a.file) else 0
        if size != last_size:
            last_size, last_grow = size, time.time()
            seen.discard("idle")
        elif time.time() - last_grow > a.idle_minutes * 60 and "idle" not in seen:
            seen.add("idle")
            print("ALERT %s no new rows for %.0f min (stalled run?)" % (time.strftime("%H:%M:%S"), a.idle_minutes), flush=True)
        if a.once:
            return 1 if new else 0
        time.sleep(a.every)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
