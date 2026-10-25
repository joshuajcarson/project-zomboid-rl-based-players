"""Second bridge probe: server-side teleport, wielding a bat, and how fast a fake client kills with it.
Usage: python scripts/bridge_probe2.py   (reuses a running server; starts two fake clients)"""
import re, sys, time
sys.path.insert(0, ".")
from pzrl import ServerChannel, ClientControl, Launcher

L = Launcher()
try:
    L.start_server(reuse=True)
    ids = [30, 31]
    scen = L.write_scenario(ids, [(10650, 9800), (10700, 9850)], name="probe2")
    ctl = {i: ClientControl(L.start_client(i, scen)) for i in ids}
    ch = ServerChannel(L.channel_port)
    while True:
        m = ch.wait_obs(1, timeout=60)
        if {"Client30", "Client31"} <= {p["u"] for p in m["p"]}:
            break
    for i in ids:
        a = ctl[i].info(); ctl[i].goto(a["x"], a["y"])
    def me(u): return next(p for p in ch.wait_obs(1)["p"] if p["u"] == u)
    print("start", {u: (round(me(u)["x"]), round(me(u)["y"])) for u in ("Client30", "Client31")})

    print("server tp:", ch.command("tp|Client31|10600|9700|0"))
    time.sleep(6)
    print("after server tp:", (round(me("Client31")["x"]), round(me("Client31")["y"])), "client says", ctl[31].info())

    g = ch.command("give|Client30|Base.BaseballBat"); print("give:", g)
    item_id = int(re.search(r"id=(\d+)", g["msg"]).group(1))
    print("weapon:", ctl[30].weapon(item_id), "client says", ctl[30].info(), "server weapon:", me("Client30")["weapon"])
finally:
    L.stop_all()
