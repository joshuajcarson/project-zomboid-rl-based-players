"""Summarise RLOBS lines from a server log, per user: speed, health, kills, nearby zombies.
Usage: python scripts/analyze_obs.py [logfile]   (default: newest logs/server-*.log)
Speed is measured between consecutive observations using the log's own millisecond clock."""
import glob, json, math, os, re, sys, statistics as st

path = sys.argv[1] if len(sys.argv) > 1 else max(glob.glob(os.path.join("logs", "server-*.log")), key=os.path.getmtime)
pat = re.compile(r"st:([\d,]+)>\s+RLBRIDGE RLOBS (\{.*\})")
rows = {}
with open(path, "rb") as f:
    for raw in f:
        m = pat.search(raw.decode("utf-8", "ignore").replace("\x00", ""))
        if m:
            d = json.loads(m.group(2)); d["t"] = int(m.group(1).replace(",", "")) / 1000.0
            rows.setdefault(d["user"], []).append(d)

print(f"log: {path}")
for user, r in rows.items():
    speeds = []
    for a, b in zip(r, r[1:]):
        dt = b["t"] - a["t"]
        if dt > 0:
            v = math.hypot(b["x"] - a["x"], b["y"] - a["y"]) / dt
            if v < 12:  # ignore teleports (the fastest legitimate movement is a few tiles/s)
                speeds.append(v)
    moving = [s for s in speeds if s > 0.3]
    print(f"{user}: {len(r)} obs over {r[-1]['t'] - r[0]['t']:.0f}s | "
          f"speed tiles/s median {st.median(speeds):.2f} max {max(speeds):.2f} "
          f"(moving-only median {st.median(moving) if moving else 0:.2f}) | "
          f"health {r[0]['health']:.0f}->{r[-1]['health']:.0f} min {min(x['health'] for x in r):.0f} | "
          f"kills {r[0]['kills']}->{r[-1]['kills']} | max zombiesNear {max(x['zombiesNear'] for x in r)}")
