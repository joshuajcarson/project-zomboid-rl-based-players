"""Starts and stops the server and fake-client processes for an RL run (Windows, PowerShell scripts from scripts/)."""
import json
import pathlib
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"
GENERATED = ROOT / "scenarios" / "generated"
_FLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)

# Speed value for the scenario's "run" motion; about 0.29 tiles per game second per unit (calibrated, docs/approach.md).
RUN_SPEED_UNITS = 8
TILES_PER_GAME_SECOND = 2.33


def _ps(args, **kw):
    return subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", *args],
                            creationflags=_FLAGS, **kw)


def kill_clients():
    """Stop leftover fake-client JVMs of this repo (leaves a reused server alone)."""
    script = (
        "Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | "
        f"Where-Object {{ $_.CommandLine -match [regex]::Escape('{ROOT}') -and $_.CommandLine -match 'FakeClientManager' }} | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", script], creationflags=_FLAGS, check=False)
    time.sleep(1)


def kill_stale():
    """Stop leftover game server / fake client JVMs that belong to this repo (matched by repo path in the command line)."""
    script = (
        "Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | "
        f"Where-Object {{ $_.CommandLine -match [regex]::Escape('{ROOT}') -and $_.CommandLine -match 'GameServer|FakeClientManager' }} | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", script], creationflags=_FLAGS, check=False)
    time.sleep(2)


class Launcher:
    def __init__(self, time_scale=1.0, channel_port=17600, control_base=17700):
        self.time_scale = float(time_scale)
        self.channel_port = channel_port
        self.control_base = control_base
        self.server = None
        self.server_log = None
        self.clients = {}  # id -> Popen

    # ---- server -------------------------------------------------------------------------------------------------
    def server_running(self):
        """True when a server with the bridge channel is already listening (lets tests reuse a long-lived server)."""
        import socket
        try:
            socket.create_connection(("127.0.0.1", self.channel_port), timeout=1).close()
            return True
        except OSError:
            return False

    def start_server(self, mods=("RLBridge",), ready_timeout=900, reuse=False):
        if reuse and self.server_running():
            kill_clients()   # a duplicate login would kick the new client, so clear old ones first
            return
        kill_stale()
        LOGS.mkdir(exist_ok=True)
        _ps(["-File", str(ROOT / "scripts" / "install-mods.ps1"), "-Enable", ",".join(mods)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).wait()
        self.server_log = LOGS / f"env-server-{time.strftime('%Y%m%d-%H%M%S')}.log"
        out = open(self.server_log, "wb")
        self.server = _ps(["-File", str(ROOT / "scripts" / "start-server.ps1"),
                           "-JavaAgent", str(ROOT / "agent" / "rl-agent.jar"),
                           "-TimeScale", str(self.time_scale), "-ChannelPort", str(self.channel_port)],
                          stdout=out, stderr=subprocess.STDOUT)
        deadline = time.time() + ready_timeout
        while time.time() < deadline:
            if self.server.poll() is not None:
                raise RuntimeError(f"server exited early, see {self.server_log}")
            try:
                if b"*** SERVER STARTED" in self.server_log.read_bytes().replace(b"\x00", b""):
                    return
            except OSError:
                pass
            time.sleep(5)
        raise TimeoutError(f"server not ready, see {self.server_log}")

    # ---- clients ------------------------------------------------------------------------------------------------
    def write_scenario(self, ids, spawns, name="env"):
        """Scenario with one 'Line' mover per id (we steer it through the control socket)."""
        GENERATED.mkdir(parents=True, exist_ok=True)
        base = json.loads((ROOT / "scenarios" / "multi-4.json").read_text())
        base["config"]["client"]["statistics"] = {"id": 0, "period": 0}
        # a client connects after (connection.interval x its id) ms, so keep the interval small for larger ids
        base["config"]["client"]["connection"]["interval"] = 200
        base["config"]["movement"]["motion"]["run"] = RUN_SPEED_UNITS
        base["movements"] = [
            {"id": i, "description": f"env agent {i}", "motion": "Run", "type": "Line",
             "spawn": {"x": int(sx), "y": int(sy)}}
            for i, (sx, sy) in zip(ids, spawns)
        ]
        path = GENERATED / f"{name}.json"
        path.write_text(json.dumps(base, indent=2))
        return path.relative_to(ROOT)

    def start_client(self, client_id, scenario_rel):
        LOGS.mkdir(exist_ok=True)
        out = open(LOGS / f"env-client-{client_id}-{time.strftime('%Y%m%d-%H%M%S')}.log", "wb")
        self.clients[client_id] = _ps(
            ["-File", str(ROOT / "scripts" / "run-fake-client.ps1"), "-Scenario", str(scenario_rel),
             "-Id", str(client_id), "-LogLevel", "1", "-TimeScale", str(self.time_scale),
             "-ControlPort", str(self.control_base + client_id)],
            stdout=out, stderr=subprocess.STDOUT)
        return self.control_base + client_id

    def stop_client(self, client_id):
        p = self.clients.pop(client_id, None)
        if p is not None:
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True, creationflags=_FLAGS)

    def stop_all(self):
        for cid in list(self.clients):
            self.stop_client(cid)
        if self.server is not None:
            subprocess.run(["taskkill", "/PID", str(self.server.pid), "/T", "/F"], capture_output=True, creationflags=_FLAGS)
            self.server = None
            kill_stale()
        else:
            kill_clients()
