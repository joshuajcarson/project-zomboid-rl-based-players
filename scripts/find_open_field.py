"""Tour candidate coordinates with one rendered client and rate how obstructed each is (server `openness|x|y|r`): the best sites for
fight experiments have blocked=building=fence=hutch=0 within the radius. Candidates come from pzmap.net data (no forest, water or
shops nearby; houses and fences are not in that data, so the in-game scan decides). Needs the RLBridge mod with the openness command.
Usage: python scripts/find_open_field.py x,y x,y ...   (writes logs/open_fields.jsonl)"""
import json, sys, time
sys.path.insert(0, ".")
from pzrl import ServerChannel
from pzrl.launcher import Launcher
sites = [tuple(float(v) for v in a.split(",")) for a in sys.argv[1:]]
ch = ServerChannel(connect_timeout=60)
L = Launcher()
if not ch.wait_obs(1)["p"]:
    L.start_rendered(40)
    while not ch.wait_obs(1)["p"]:
        pass
    time.sleep(25)
out = open("logs/open_fields.jsonl", "a")
for x, y in sites:
    ch.command("bot|Client40|god|1")
    tp = ch.command("tp|Client40|%d|%d|0" % (x, y), timeout=20)
    time.sleep(10)                                   # let the chunks around the new position load
    res = ch.command("openness|%d|%d|30" % (x, y), timeout=30)["msg"]
    row = {"x": x, "y": y, "tp": tp["msg"], "scan": res}
    print(json.dumps(row), flush=True)
    out.write(json.dumps(row) + "\n"); out.flush()
print("TOURDONE", flush=True)
