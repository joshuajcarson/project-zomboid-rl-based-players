"""Low-level smoke test of the bridge: server channel, client control, items, heal, teleport.
Usage: python scripts/bridge_smoke.py [time_scale]   (starts and stops its own server and two fake clients)"""
import sys, time, json, random
sys.path.insert(0, ".")
from pzrl import ServerChannel, ClientControl, Launcher

K = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
L = Launcher(time_scale=K)
try:
    print("starting server (about 4 min)...", flush=True)
    L.start_server(reuse=True)
    ids = [30, 31]
    scen = L.write_scenario(ids, [(10650, 9800), (10700, 9850)], name="smoke")
    ctl = {}
    for i in ids:
        port = L.start_client(i, scen)
        ctl[i] = ClientControl(port)
    ch = ServerChannel(L.channel_port)
    print("channel connected; waiting for players", flush=True)
    t0 = time.time()
    while True:
        m = ch.wait_obs(1, timeout=60)
        users = {p["u"] for p in m["p"]}
        if {"Client30", "Client31"} <= users or time.time() - t0 > 120:
            break
    print("players:", sorted(users))
    for i in ids:
        info = ctl[i].info(); ctl[i].goto(info["x"], info["y"])
        print("client", i, "info", info)
    m = ch.wait_obs(2)
    for p in m["p"]:
        print({k: p[k] for k in ("u", "x", "y", "hp", "items", "weapon", "bag", "zn", "kills")})
    print("give bat:", ch.command("give|Client30|Base.BaseballBat"))
    print("say additem:", ctl[30].say('/additem "Client30" Base.BaseballBat'))
    time.sleep(3)
    print("client30 info after bat:", ctl[30].info())
    print("walk east 20 tiles and measure:")
    a = ctl[30].info(); ctl[30].goto(a["x"] + 40, a["y"]); m0 = ch.wait_obs(1); time.sleep(8 / K); m1 = ch.wait_obs(1)
    p0 = next(p for p in m0["p"] if p["u"] == "Client30"); p1 = next(p for p in m1["p"] if p["u"] == "Client30")
    print("moved", round(p1["x"] - p0["x"], 1), "tiles between observations; tick delta", m1["tick"] - m0["tick"])
    print("heal:", ch.command("heal|Client30"))
    print("zspawn:", ch.command(f"zspawn|{a['x']+10}|{a['y']}|5"))
    print("teleport:", ctl[31].tp(10600, 9700, 0))
    time.sleep(6 / K)
    m = ch.wait_obs(1)
    print({p["u"]: (round(p["x"]), round(p["y"])) for p in m["p"]})
finally:
    L.stop_all()
