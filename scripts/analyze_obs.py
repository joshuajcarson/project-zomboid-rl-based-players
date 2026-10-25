"""Summarise RLOBS lines from a server log, per user: speed, health, kills, nearby zombies.
Usage: python scripts/analyze_obs.py [logfile]   (default: newest logs/server-*.log)
Speed is measured between consecutive observations using the log's own millisecond clock."""
import glob, json, math, os, re, sys, statistics as st

scale = "--scale" in sys.argv
tail_user = sys.argv[sys.argv.index("--tail") + 1] if "--tail" in sys.argv else None
snap_user = None
args = [a for a in sys.argv[1:] if not a.startswith("--") and a != tail_user and (a not in sys.argv or sys.argv[sys.argv.index(a) - 1] != "--snap")]
path = args[0] if args else max(glob.glob(os.path.join("logs", "server-*.log")), key=os.path.getmtime)
pat = re.compile(r"st:([\d,]+)>\s+RLBRIDGE RLOBS (\{.*\})")
rows = {}
with open(path, "rb") as f:
    for raw in f:
        m = pat.search(raw.decode("utf-8", "ignore").replace("\x00", ""))
        if m:
            d = json.loads(m.group(2)); d["t"] = int(m.group(1).replace(",", "")) / 1000.0
            rows.setdefault(d["user"], []).append(d)

snap_user = sys.argv[sys.argv.index("--snap") + 1] if "--snap" in sys.argv else None
if snap_user:
    r = rows[snap_user]
    x = r[-1]
    print(json.dumps({"n": len(r), "x": x["x"], "y": x["y"], "hunger": x["hunger"], "thirst": x["thirst"], "health": x["health"], "ageH": x.get("ageH"), "mpd": x.get("mpd")}))
    sys.exit(0)
if tail_user:
    r = rows[tail_user][-13:]
    for a, b in zip(r, r[1:]):
        v = math.hypot(b["x"] - a["x"], b["y"] - a["y"]) / (b["t"] - a["t"])
        print(f"{v:6.2f} tiles/s ({b['x']:.0f},{b['y']:.0f}) hp {b['health']:.0f}" + ("  <-- jump" if v >= 12 else ""))
    sys.exit(0)
if scale:
    # last 60 s of the log: observer tick rate (60 ticks per observation) and kills per minute across players
    tmax = max(r[-1]["t"] for r in rows.values())
    hz, kills = [], 0
    for user, r in rows.items():
        recent = [x for x in r if x["t"] >= tmax - 60]
        for a, b in zip(recent, recent[1:]):
            if b["t"] > a["t"]:
                hz.append(60 / (b["t"] - a["t"]))
        if len(recent) > 1:
            kills += recent[-1]["kills"] - recent[0]["kills"]
    users = sum(1 for r in rows.values() if r[-1]["t"] >= tmax - 60)
    print(f"{users} players observed | server Lua tick median {st.median(hz):.1f} Hz (min {min(hz):.1f}) | {kills} kills in last 60 s" if hz else "no data")
    sys.exit(0)
print(f"log: {path}")
for user, r in rows.items():
    speeds = []
    for a, b in zip(r, r[1:]):
        dt = b["t"] - a["t"]
        if dt > 0:
            v = math.hypot(b["x"] - a["x"], b["y"] - a["y"]) / dt
            if v < 12:  # ignore teleports (the fastest legitimate movement is a few tiles/s)
                speeds.append(v)
    if not speeds:
        print(f"{user}: {len(r)} obs (too few for speeds)")
        continue
    moving = [s for s in speeds if s > 0.3]
    print(f"{user}: {len(r)} obs over {r[-1]['t'] - r[0]['t']:.0f}s | "
          f"speed tiles/s median {st.median(speeds):.2f} max {max(speeds):.2f} "
          f"(moving-only median {st.median(moving) if moving else 0:.2f}) | "
          f"health {r[0]['health']:.0f}->{r[-1]['health']:.0f} min {min(x['health'] for x in r):.0f} | "
          f"kills {r[0]['kills']}->{r[-1]['kills']} | max zombiesNear {max(x['zombiesNear'] for x in r)}")
