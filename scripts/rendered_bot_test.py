"""Drive a rendered client through the bridge: equip bat, walk, spawn zombies next to it, attack.
Usage: python scripts/rendered_bot_test.py Client47"""
import math
import sys
import time

sys.path.insert(0, ".")
from pzrl.channel import ServerChannel
from pzrl.rendered import RenderedControl

user = sys.argv[1]
ch = ServerChannel()
rc = RenderedControl(ch, user)


def me():
    msg = ch.wait_obs(timeout=10)
    return next(p for p in msg["p"] if p["u"] == user), msg


p, _ = me()
print("start", p["x"], p["y"], "hp", p["hp"], "kills", p["kills"])
print("equip", rc.equip())
print("info", rc.info())
tx, ty = p["x"] + 8, p["y"]
print("goto", rc.goto(tx, ty))
for _ in range(12):
    time.sleep(1)
    p, _ = me()
    print(f"  at {p['x']:.1f},{p['y']:.1f} dist {math.hypot(tx - p['x'], ty - p['y']):.1f}")
print("zspawn", ch.command(f"zspawn|{p['x'] + 3:.0f}|{p['y']:.0f}|3"))
for _ in range(20):
    time.sleep(1)
    print("attack", rc.attack().get("msg"))
    p, msg = me()
    print(f"  hp {p['hp']} kills {p['kills']} zn {p['zn']}")
