"""Process control helpers that never match their own command line.
  python scripts/pz_ctl.py list            show java processes (server / rendered client / fake client) and repo python runs
  python scripts/pz_ctl.py stop-clients    stop rendered and fake clients, leave the server
  python scripts/pz_ctl.py stop-runs       stop repo python experiment scripts (compare_backends, env_*_demo, ...)
  python scripts/pz_ctl.py stop-all        stop everything above including the server"""
import subprocess, sys, os

SELF = os.getpid()

def procs():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(java|python|bash)' } | "
        "ForEach-Object { \"$($_.ProcessId)`t$($_.Name)`t$($_.CommandLine)\" }"], capture_output=True, text=True).stdout
    for line in out.splitlines():
        parts = line.split("\t", 2)
        if len(parts) == 3 and parts[0].isdigit():
            yield int(parts[0]), parts[1], parts[2]

def kind(name, cmd):
    if name.startswith("java"):
        if "rl-agent-client" in cmd: return "rendered"
        if "FakeClientManager" in cmd: return "fake"
        if "GameServer" in cmd or "rl-agent.jar" in cmd: return "server"
        return "java"
    c = cmd.replace("\\", "/")
    if "pz_ctl" not in c and any(k in c for k in ("compare_", "_demo", "_test", "_run_", "_policy_study", "_fit_fight", "_eval_bc", "_record_",
                                                  "rendered_fight_lab", "eval_transfer", "measure_speed", "aim_check", "pzrl.train", "pzrl.imitate",
                                                  "_transfer_zombies", "_speed_check", "start-client.ps1")):
        return "run"
    return None

def kill(pid):
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)

cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
rows = [(pid, kind(n, c), c) for pid, n, c in procs() if pid != SELF]
rows = [(pid, k, c) for pid, k, c in rows if k]
if cmd == "list":
    for pid, k, c in rows: print(pid, k, c[:100])
else:
    want = {"stop-clients": {"rendered", "fake"}, "stop-runs": {"run"}, "stop-all": {"rendered", "fake", "run", "server"}}[cmd]
    for pid, k, c in rows:
        if k in want: kill(pid); print("stopped", pid, k)
