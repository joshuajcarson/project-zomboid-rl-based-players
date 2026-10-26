"""Summarise the RLBOT COMBAT lines the rendered client wrote during fights (rl_bot_dev.lua instrumentation).
Usage: python scripts/analyze_combat.py [client DebugLog path]"""
import glob, re, sys, collections, statistics as st
path = sys.argv[1] if len(sys.argv) > 1 else glob.glob(".pzclient/Logs/*DebugLog*")[0]
rows = []
for line in open(path, "rb").read().replace(b"\x00", b"").decode("utf-8", "replace").splitlines():
    if "RLBOT COMBAT" not in line: continue
    d = dict(re.findall(r"(\w+)=(-?\d+(?:\.\d+)?)", line))
    d = {k: float(v) for k, v in d.items()}
    d["kind"] = "end" if "COMBAT end" in line else "swing"
    rows.append(d)
by = collections.defaultdict(list)
for r in rows:
    if "zid" in r: by[int(r["zid"])].append(r)
swings_to_kill, first_hp, per_swing = [], [], []
for zid, rs in by.items():
    hps = [r["zhp"] for r in rs if r["kind"] == "swing"]
    killed = any(r["kind"] == "end" and r["zhp"] <= 0.001 for r in rs)
    seq = [r["zhp"] for r in rs]
    if len(seq) > 1:
        first_hp.append(seq[0])
        per_swing += [a - b for a, b in zip(seq, seq[1:]) if a - b >= -0.001]
    if killed: swings_to_kill.append(len([r for r in rs if r["kind"] == "swing"]))
print("zombies seen", len(by), "killed", len(swings_to_kill), "swing lines", sum(1 for r in rows if r["kind"] == "swing"))
if swings_to_kill: print("swings per kill: mean %.1f median %s min %d max %d" % (st.mean(swings_to_kill), st.median(swings_to_kill), min(swings_to_kill), max(swings_to_kill)))
if per_swing:
    per_swing.sort()
    print("health lost between successive swings of a zombie: n=%d mean %.3f median %.3f p10 %.3f p90 %.3f max %.3f" % (
        len(per_swing), st.mean(per_swing), st.median(per_swing), per_swing[len(per_swing)//10], per_swing[9*len(per_swing)//10], per_swing[-1]))
sw = [r for r in rows if r["kind"] == "swing"]
for key in ("endurance", "panic", "stress", "fatigue", "pain", "stiff", "dist", "frames"):
    vals = [r[key] for r in sw if key in r]
    if vals: print("%-10s min %.2f mean %.2f max %.2f" % (key, min(vals), st.mean(vals), max(vals)))
print("levels: strength", {int(r['str']) for r in sw}, "blunt", {int(r['blunt']) for r in sw}, "fitness", {int(r['fit']) for r in sw})
