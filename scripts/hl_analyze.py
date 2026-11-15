"""Analyse a planner-learning evaluation (H-L1): per-arm deaths, end hp, needs and wasted loots, and the z score of arm B minus arm A.

    python scripts/hl_analyze.py --a llm --b llmL results/experiments-2026-11-15/hl1_eval_s1.jsonl [more files]

Wasted loot = a loot that took nothing, or a loot started while already carrying food, water and bandages (over-gathering).
Dead episodes count as end hp 0; needs (end hunger + thirst) use survivors only. An episode cut by the session clock (alive, < 120 steps)
is dropped. Prints the pre-registered verdict of docs/experiments/2026-11-15-hl1-lessons.md.
"""
import argparse
import json
import math


def mse(xs):
    n = len(xs)
    if n < 2:
        return (xs[0] if xs else float("nan")), float("nan"), n
    m = sum(xs) / n
    return m, math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1) / n), n


def z(b, a):
    return (b[0] - a[0]) / math.sqrt(a[1] ** 2 + b[1] ** 2) if a[2] > 1 and b[2] > 1 and (a[1] > 0 or b[1] > 0) else float("nan")


def wasted(r):
    e, s = r.get("effect") or {}, r.get("stats") or {}
    took = (e.get("food") or 0) + (e.get("drink") or 0) + (e.get("bandages") or 0) > 0
    supplied = all((s.get(k) or 0) >= 1 for k in ("food", "drink", "bandages"))
    return (not took) or supplied


def load(paths):
    eps = {}
    for path in paths:
        rows = [json.loads(l) for l in open(path, encoding="utf-8")]
        for r in rows:
            if "episode_end" in r:
                eps[(path, r["episode_end"])] = {"end": r, "loots": []}
        for r in rows:
            if r.get("skill") == "loot" and (path, r.get("episode")) in eps:
                eps[(path, r["episode"])]["loots"].append(r)
    return eps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--a", default="llm")
    ap.add_argument("--b", default="llmL")
    a = ap.parse_args()
    arms = {}
    for e in load(a.files).values():
        r = e["end"]
        if not r["dead"] and r["steps"] < 120:
            continue
        d = arms.setdefault(r["arm"], {"died": [], "hp": [], "needs": [], "wasted": [], "loots": []})
        d["died"].append(1.0 if r["dead"] else 0.0)
        d["hp"].append(0.0 if r["dead"] else float(r["hp"]))
        if not r["dead"] and isinstance((r.get("end") or {}).get("hunger"), float):
            d["needs"].append(r["end"]["hunger"] + (r["end"].get("thirst") or 0.0))
        d["wasted"].append(float(sum(1 for l in e["loots"] if wasted(l))))
        d["loots"].append(float(len(e["loots"])))
    S = {k: {m: mse(v) for m, v in d.items()} for k, d in arms.items()}
    for k in sorted(S):
        s = S[k]
        print("%-5s n=%2d died %.2f  hp %5.1f (se %4.1f)  needs %.3f (se %.3f)  loots/ep %.2f  wasted/ep %.2f (se %.2f)"
              % (k, s["died"][2], s["died"][0], s["hp"][0], s["hp"][1], s["needs"][0], s["needs"][1], s["loots"][0], s["wasted"][0], s["wasted"][1]))
    if a.a in S and a.b in S:
        A, B = S[a.a], S[a.b]
        zh, zw, zd = z(B["hp"], A["hp"]), z(B["wasted"], A["wasted"]), z(B["died"], A["died"])
        dn = B["needs"][0] - A["needs"][0]
        print("%s - %s: hp %+.1f (z %.2f)  wasted/ep %+.2f (z %.2f)  died %+.2f (z %.2f)  needs %+.3f"
              % (a.b, a.a, B["hp"][0] - A["hp"][0], zh, B["wasted"][0] - A["wasted"][0], zw, B["died"][0] - A["died"][0], zd, dn))
        succ = (zh >= 2 and dn <= 0.10) or (zw <= -2 and zh > -1 and dn <= 0.10)
        fail = zh <= -1 or dn > 0.15 or zw >= 2
        print("criteria:", "SUCCESS" if succ else "FAILURE" if fail else "INCONCLUSIVE")


if __name__ == "__main__":
    main()
