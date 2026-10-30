"""Stop everything this repo spawns for experiments and confirm that it is gone. Safe to run any time; exit code 0 = clean, 1 = something is left.

  python scripts/cleanup.py             report what is running and stop all of it (clients, server, runs, wrappers), then verify
  python scripts/cleanup.py --check     only report (exit 1 if anything is running or a port/lock is held)
  python scripts/cleanup.py --keep-server   stop clients, runs and wrappers but leave the game server up (saves the ~5 min boot)

Matched by command line, never by memory size, and never other projects' processes (image-gen etc.). Run it at the end of every run
or experiment batch, and whenever RAM or ports need to be freed. Background monitors/tasks started by the Claude session are
not processes of ours: stop those with TaskStop (they only poll log files and hold nothing).
"""
import os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _ancestors():
    """This process and every ancestor (the wrapper script, the shell that launched it): cleanup must never kill the thing that called it."""
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Process | ForEach-Object { \"$($_.ProcessId)`t$($_.ParentProcessId)\" }"], capture_output=True, text=True).stdout
    parent = {}
    for line in out.splitlines():
        a = line.split("	")
        if len(a) == 2 and a[0].strip().isdigit() and a[1].strip().isdigit():
            parent[int(a[0])] = int(a[1])
    seen, pid = set(), os.getpid()
    while pid and pid not in seen:
        seen.add(pid); pid = parent.get(pid, 0)
    return seen


SELF = _ancestors() | {os.getpid(), os.getppid()}
PORTS = [16261, 16262, 17600] + list(range(17700, 17721))     # game server, udp/tcp, channel, per-client control sockets
LOCK = os.path.join(ROOT, "logs", ".env.lock")


def procs():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(java|javaw|python|powershell|bash|cmd)' } | "
        "ForEach-Object { \"$($_.ProcessId)`t$($_.Name)`t$([int]($_.WorkingSetSize/1MB))`t$($_.CommandLine)\" }"],
        capture_output=True, text=True).stdout
    for line in out.splitlines():
        p = line.split("\t", 3)
        if len(p) == 4 and p[0].isdigit():
            yield int(p[0]), p[1].lower(), int(p[2] or 0), p[3]


def kind(name, cmd):
    """Classify a process as ours (server / client / run / wrapper) or None."""
    c = cmd.replace("\\", "/")
    if name.startswith("java"):
        if "rl-agent-client" in c: return "rendered"
        if "FakeClientManager" in c: return "fake"
        if "GameServer" in c or "rl-agent.jar" in c or ("ProjectZomboid" in c and ".pzdata" in c): return "server"
        return None
    if "cleanup.py" in c:
        return None
    mine = "project-zomboid-rl-based-players" in c or "pzrl" in c
    if name.startswith("powershell") and any(k in c for k in ("start-server.ps1", "run-fake-client.ps1", "start-client.ps1", "build-agent.ps1")) and mine:
        return "launcher"
    if name.startswith("bash") and "scripts/_" in c and ".sh" in c and " -c " not in c:    # a script wrapper, not a tool shell whose -c command line merely mentions it
        return "wrapper"
    if name.startswith("python") and mine and any(k in c for k in (
            "benchmark.py", "rendered_fight_lab", "_demo", "compare_", "_test", "pz_ctl", "show_client", "find_open_field", "probe_zspawn",
            "record_", "eval_", "pzrl.train", "pzrl.imitate", "measure_speed", "aim_check", "dev_eval", "env_")):
        return "run"
    return None


def ours():
    return [(pid, k, mb, cmd) for pid, n, mb, cmd in procs() if pid not in SELF and (k := kind(n, cmd))]


def listeners():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
        "Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | ForEach-Object { \"$($_.LocalPort)`t$($_.OwningProcess)\" }"],
        capture_output=True, text=True).stdout
    return sorted((int(a), int(b)) for a, b in (l.split("\t") for l in out.splitlines() if "\t" in l) if int(a) in PORTS)


def show(rows):
    for pid, k, mb, cmd in rows:
        print("  %-7d %-9s %5d MB  %s" % (pid, k, mb, cmd[:110]))


def main():
    check = "--check" in sys.argv
    keep_server = "--keep-server" in sys.argv
    rows = ours()
    print("running (ours): %d" % len(rows)); show(rows)
    if not check:
        # wrappers and launchers first, so they cannot respawn or wait on what we kill
        order = ["wrapper", "run", "launcher", "rendered", "fake"] + ([] if keep_server else ["server"])
        for k in order:
            for pid, kk, mb, cmd in rows:
                if kk == k:
                    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
        time.sleep(3)
        if os.path.exists(LOCK) and not [r for r in ours() if r[1] in ("run", "wrapper")]:
            os.remove(LOCK); print("removed stale", LOCK)
    left = [r for r in ours() if not (keep_server and r[1] in ("server", "launcher"))]
    held = [(p, o) for p, o in listeners() if not (keep_server and p in (16261, 16262, 17600))]
    ok = not left and not held
    print("\nCLEAN" if ok else "\nNOT CLEAN")
    if left: print("still running:"); show(left)
    if held: print("ports still listening (port, pid):", held)
    if os.path.exists(LOCK): print("env lock file present:", LOCK, "(harmless when no run is active)")
    sys.exit(0 if ok else 1)


main()
