"""Spawn one zombie near a rendered client, walk up to it, swing until it dies. Usage: python scripts/rendered_attack_test.py Client53"""
import math, sys, time
sys.path.insert(0, ".")
from pzrl.channel import ServerChannel
from pzrl.rendered import RenderedControl
u = sys.argv[1]; ch = ServerChannel(); rc = RenderedControl(ch, u)
def me():
    m = ch.wait_obs(timeout=10); return next(p for p in m["p"] if p["u"] == u)
p = me(); rc.equip()
ch.command(f"zspawn|{p['x'] + 5:.0f}|{p['y']:.0f}|1"); time.sleep(2)
for i in range(15):
    q = me()
    if not q["z"]: print("no zombie left, kills", q["kills"]); break
    zx, zy = min(q["z"], key=lambda z: math.hypot(z[0] - q["x"], z[1] - q["y"]))
    d = math.hypot(zx - q["x"], zy - q["y"])
    print(i, "dist", round(d, 2), "hp", q["hp"], "kills", q["kills"])
    if d > 1.6:
        k = (d - 1.2) / d; rc.goto(q["x"] + (zx - q["x"]) * k, q["y"] + (zy - q["y"]) * k)
    else:
        rc.attack()
    time.sleep(1.2)
    ch.command(f"heal|{u}")
