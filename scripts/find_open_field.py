"""Tour candidate coordinates with one rendered client and rate how obstructed each is, using the client's own loaded squares (bot command
`openness`, logged as OPENNESS in the client log; the server's grid is empty away from loaded chunks). The best sites for fight experiments have
blocked, building, fence and hutch all at 0 within the radius. Candidates come from pzmap.net data (no forest, water or shops nearby; houses
and fences are not in that data, so the in-game scan decides).
Usage: python scripts/find_open_field.py x,y x,y ...   (appends to logs/open_fields.jsonl)"""
import glob, json, os, re, sys, time
sys.path.insert(0, ".")
from pzrl import ServerChannel
from pzrl.launcher import Launcher

sites = [tuple(float(v) for v in a.split(",")) for a in sys.argv[1:]]
L = Launcher()
L.start_server(reuse=True)             # boots it (about 5 minutes) when it is not running
ch = ServerChannel(connect_timeout=60)
if not ch.wait_obs(1)["p"]:
    L.start_rendered(40)
    while not ch.wait_obs(1)["p"]:
        pass
    time.sleep(25)


ch.command("bot|Client40|reload"); time.sleep(3)      # load .pzclient/Lua/rl_bot_dev.lua (commands openness, god, ...)


def newest_log():
    return sorted(glob.glob("logs/env-rendered-*.log"), key=os.path.getmtime)[-1]


out = open("logs/open_fields.jsonl", "a")
for x, y in sites:
    ch.command("bot|Client40|god|1")
    tp = ch.command("bot|Client40|tp|%d|%d|0" % (x, y), timeout=20)   # the client owns its position: a server-side tp does not move it
    time.sleep(20)                                   # let the chunks around the new position load
    path = newest_log(); start = os.path.getsize(path)
    ch.command("bot|Client40|openness|30")
    scan = None
    for _ in range(20):
        time.sleep(0.5)
        with open(path, "rb") as f:
            f.seek(start); m = re.search(rb"OPENNESS (.*)", f.read())
        if m:
            scan = m.group(1).decode().strip(); break
    pl = [p for p in ch.wait_obs(1)["p"] if p["u"] == "Client40"]
    row = {"x": x, "y": y, "tp": tp["msg"], "server_pos": [round(pl[0]["x"]), round(pl[0]["y"])] if pl else None, "scan": scan}
    print(json.dumps(row), flush=True)
    out.write(json.dumps(row) + "\n"); out.flush()
print("TOURDONE", flush=True)
