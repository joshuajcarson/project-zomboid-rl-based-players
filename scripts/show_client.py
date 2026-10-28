"""Start one rendered client, put its character in the arena with godmode on, and leave it running for a person to play (e.g. to look for
a hutch or pen). Usage: python scripts/show_client.py [x y z]   (default: middle of the fight arena)."""
import sys, time
sys.path.insert(0, ".")
from pzrl import ServerChannel
from pzrl.launcher import Launcher

x, y, z = (sys.argv[1:4] + ["10770", "9410", "0"][len(sys.argv[1:4]):]) if len(sys.argv) > 3 else ("10770", "9410", "0")
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
for cmd in ("bot|Client40|god|1", "tp|Client40|%s|%s|%s" % (x, y, z)):
    print(cmd, ch.command(cmd, timeout=15))
print("ready: Client40 is at %s,%s,%s with godmode on" % (x, y, z))
