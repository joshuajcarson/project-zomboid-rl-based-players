"""Analyse H-B (planner vs rules vs idle) episode_end rows against the pre-registered criteria.

    python scripts/hb_analyze.py results/experiments-2026-11-14/hb_s1.jsonl [hb_s2.jsonl ...]

Dead episodes count as end hp 0; needs (hunger + thirst) and supplies use survivors only (the dead have no end survey).
An episode cut by the session clock (steps < 120 and alive) is dropped.
"""
import json
import math
import sys


def mse(xs):
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan"), 0
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else float("nan")
    return m, sd / math.sqrt(n), n


def z(a, b):
    return (a[0] - b[0]) / math.sqrt(a[1] ** 2 + b[1] ** 2) if a[2] > 1 and b[2] > 1 else float("nan")


arms = {}
for path in sys.argv[1:]:
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if "episode_end" not in r or (not r["dead"] and r["steps"] < 120):
            continue
        e, d = r["end"], arms.setdefault(r["arm"], {"died": [], "hp": [], "needs": [], "supplies": []})
        d["died"].append(1.0 if r["dead"] else 0.0)
        d["hp"].append(0.0 if r["dead"] else float(r["hp"]))
        if not r["dead"] and isinstance(e.get("hunger"), float):
            d["needs"].append(e["hunger"] + (e.get("thirst") or 0.0))
            d["supplies"].append(sum(e.get(k) or 0.0 for k in ("food", "drink", "bandages")))

S = {a: {k: mse(v) for k, v in d.items()} for a, d in arms.items()}
for a in ("llm", "rule", "idle"):
    if a in S:
        print("%-5s n=%2d  died %.2f (se %.2f)  hp %5.1f (se %4.1f)  needs %.3f (se %.3f, n %d)  supplies %.1f"
              % (a, S[a]["died"][2], S[a]["died"][0], S[a]["died"][1], S[a]["hp"][0], S[a]["hp"][1],
                 S[a]["needs"][0], S[a]["needs"][1], S[a]["needs"][2], S[a]["supplies"][0]))
if all(a in S for a in ("llm", "rule", "idle")):
    L, R, I = S["llm"], S["rule"], S["idle"]
    zi = z(L["hp"], I["hp"])
    print("llm-rule: died %+.2f  needs %+.3f  hp %+.1f (z %.2f);  llm-idle hp %+.1f (z %.2f)"
          % (L["died"][0] - R["died"][0], L["needs"][0] - R["needs"][0], L["hp"][0] - R["hp"][0], z(L["hp"], R["hp"]), L["hp"][0] - I["hp"][0], zi))
    succ = L["died"][0] <= R["died"][0] + 0.10 and L["needs"][0] <= R["needs"][0] + 0.10 and L["hp"][0] > I["hp"][0] and zi >= 2
    fail = L["died"][0] > R["died"][0] + 0.25 or L["hp"][0] < R["hp"][0] - 20 or zi < 1
    print("criteria:", "SUCCESS" if succ else "FAILURE" if fail else "INCONCLUSIVE")
