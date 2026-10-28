"""Boot the server if needed, start one rendered client, and check that zspawn creates zombies in the current population setting."""
import sys, time
sys.path.insert(0, ".")
from pzrl import ServerChannel
from pzrl.launcher import Launcher
L = Launcher(); L.start_server(reuse=True)
ch = ServerChannel(connect_timeout=60)
L.start_rendered(40)
deadline = time.time() + 600
while time.time() < deadline:
    m = ch.wait_obs(1)
    if m["p"]: break
time.sleep(25)
print(ch.command("tp|Client40|10770|9410|0", timeout=15), flush=True)
time.sleep(8)
print("zspawn", ch.command("zspawn|10776|9410|3", timeout=30), flush=True)
time.sleep(4)
print("nz", ch.wait_obs(1)["nz"], flush=True)
print("PROBEDONE", flush=True)
