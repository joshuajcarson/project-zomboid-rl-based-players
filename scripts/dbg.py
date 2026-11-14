"""Send bot commands to Client40 and print the client log lines they produce (interactive skill debugging).
    python scripts/dbg.py "survey|30" "eat" --wait 6        (several commands run in order, --wait seconds after each)
    python scripts/dbg.py --server "stats|Client40|0.5|0.5"  (a raw server command instead of a bot command)"""
import argparse, glob, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pzrl.channel import ServerChannel
ap = argparse.ArgumentParser(); ap.add_argument("cmds", nargs="+"); ap.add_argument("--wait", type=float, default=4); ap.add_argument("--server", action="store_true")
ap.add_argument("--user", default="Client40"); ap.add_argument("--all", action="store_true", help="print every new log line, not only RLBOT ones")
a = ap.parse_args()
ch = ServerChannel(17600)
f = sorted(glob.glob("logs/env-rendered-*.log"), key=os.path.getmtime)[-1]
for c in a.cmds:
    start = os.path.getsize(f)
    print(">>", c, ch.command(c if a.server else f"bot|{a.user}|{c}"))
    time.sleep(a.wait)
    for l in open(f, "rb").read()[start:].decode("utf-8", "replace").splitlines():
        if a.all or "RLBOT" in l or "ERROR" in l or "Exception" in l:
            print("  ", l[l.find("RLBOT"):][:260] if "RLBOT" in l else l[:260])
ch.close()
