"""Compare the arms of an interleaved lab run (episodes alternate between arms inside ONE session, which controls block-to-block drift).
    python scripts/compare_arms.py out.txt [--by arm|policy]
Prints n, kills, damage (with standard errors), deaths (>=80 damage) and a z score for the first two groups. A difference under ~2 z is
noise: per-episode damage has sd ~27 with a heavy tail, so 20 episodes per arm resolve ~15 damage and 0.4 kills at best."""
import json, math, statistics as st, sys

path = sys.argv[1]
by = sys.argv[sys.argv.index("--by") + 1] if "--by" in sys.argv else "arm"
eps = [json.loads(l) for l in open(path, errors="replace") if l.startswith('{"ep"')]
real = [e for e in eps if e["steps"] >= 5]            # drop 1-step resets after deaths
groups = {}
for e in real:
    groups.setdefault(e.get(by) or "?", []).append(e)
print("lines %d, real episodes %d" % (len(eps), len(real)))
stats = {}
for g, x in sorted(groups.items()):
    k = [e["zombies_start"] - e["zombies_end"] for e in x]; d = [e["damage_end"] for e in x]
    stats[g] = (k, d)
    print("%-16s n=%2d kills %.2f (se %.2f)  dmg %.1f (se %.1f)  deaths>=80 %d  low-hp %d" % (
        g, len(x), st.mean(k), st.stdev(k) / math.sqrt(len(x)), st.mean(d), st.stdev(d) / math.sqrt(len(x)),
        sum(v >= 80 for v in d), sum(e["min_hp"] < 15 for e in x)))
names = sorted(stats)
if len(names) >= 2:
    for label, i in (("kills", 0), ("damage", 1)):
        a, b = stats[names[0]][i], stats[names[1]][i]
        se = math.sqrt(st.variance(a) / len(a) + st.variance(b) / len(b))
        print("%s: %s - %s = %.2f (se %.2f, z %.2f)" % (label, names[1], names[0], st.mean(b) - st.mean(a), se, (st.mean(b) - st.mean(a)) / se))
