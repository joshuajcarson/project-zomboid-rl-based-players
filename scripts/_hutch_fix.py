"""Start the server (loads the hutches command), list hutches near the arena's west edge, remove them, then leave the server running."""
import sys
sys.path.insert(0, ".")
from pzrl import ServerChannel
from pzrl.launcher import Launcher
L = Launcher()
L.start_server(reuse=True)
ch = ServerChannel(connect_timeout=60)
print("scan", ch.command("hutches|10730|9411|40|0", timeout=60), flush=True)
