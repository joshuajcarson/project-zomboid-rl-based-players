#!/bin/bash
# exits 0 once the server channel delivers an observation
cd /c/bench/project-zomboid-rl-based-players
until timeout 20 python - <<'PY' 2>/dev/null
import socket, sys, time
s = socket.create_connection(("127.0.0.1", 17600), timeout=5); f = s.makefile("r")
t = time.time()
while time.time() - t < 15:
    line = f.readline()
    if line and '"tick"' in line: sys.exit(0)
sys.exit(1)
PY
do sleep 5; done
echo server-ready
