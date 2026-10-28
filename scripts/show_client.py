"""Start one rendered client, put its character in the arena with godmode on, and leave it running for a person to play (e.g. to look for
a hutch or pen). Usage: python scripts/show_client.py [x y z]   (default: middle of the fight arena)."""
import sys, time
sys.path.insert(0, ".")
from pzrl import ServerChannel
from pzrl.launcher import Launcher

x, y, z = ([a for a in sys.argv[1:] if not a.startswith("--")][:3]) if len([a for a in sys.argv[1:] if not a.startswith("--")]) > 2 else ("10770", "9410", "0")
ch = ServerChannel(connect_timeout=30)
L = Launcher()
L.start_rendered(40)
deadline = time.time() + 600
while time.time() < deadline:
    msg = ch.wait_obs(1)
    if "Client40" in {p["u"] for p in msg["p"]}:
        break
else:
    sys.exit("client did not enter the world")
time.sleep(25)
for cmd in ("bot|Client40|god|1", "bot|Client40|tp|%s|%s|%s" % (x, y, z)):
    print(cmd, ch.command(cmd, timeout=15))
if "--rmhutch" in sys.argv:       # remove animal hutches / dog houses around the arena while its chunks are loaded (they crash clients on unload)
    for _ in range(3):
        print("hutches", ch.command("hutches|10730|9411|45|1", timeout=60), flush=True)
        time.sleep(3)
print("ready: Client40 is at %s,%s,%s with godmode on" % (x, y, z))
