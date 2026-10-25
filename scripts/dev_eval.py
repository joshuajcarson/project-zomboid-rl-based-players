"""Send one or more bridge commands to a running dev server (started with start-server.ps1 -Dev) and print the acks.
Examples:
  python scripts/dev_eval.py "get|zombie.network.GameServer.Players.size()"
  python scripts/dev_eval.py "lua|getOnlinePlayers():size()"
Commands are sent exactly as given (the server splits on '|')."""
import sys
sys.path.insert(0, ".")
from pzrl import ServerChannel

ch = ServerChannel(connect_timeout=5)
for line in sys.argv[1:]:
    try:
        a = ch.command(line, timeout=15)
        print(("OK  " if a["ok"] else "FAIL"), a["msg"])
    except TimeoutError as e:
        print("TIMEOUT", e)
ch.close()
