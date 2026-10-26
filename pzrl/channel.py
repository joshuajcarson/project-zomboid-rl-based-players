"""Sockets to the Java agent: the server channel (observations + commands via server Lua) and per-client control."""
import json
import socket
import threading
import time
from collections import deque


class ServerChannel:
    """Newline-delimited JSON from server Lua (observations and command acks); newline-delimited text commands back.

    Observation messages look like {"tick":..,"ageH":..,"nz":..,"p":[{"u":"Client20","x":..,...}]}. Acks look like
    {"ack":"<command>","ok":true,"msg":".."}.
    """

    def __init__(self, port=17600, host="127.0.0.1", connect_timeout=60.0):
        deadline = time.time() + connect_timeout
        last = None
        while True:
            try:
                self.sock = socket.create_connection((host, port), timeout=5)
                break
            except OSError as e:
                last = e
                if time.time() > deadline:
                    raise ConnectionError(f"server channel {host}:{port} unreachable: {last}")
                time.sleep(1)
        self.sock.settimeout(None)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._cond = threading.Condition()
        self._obs = deque(maxlen=256)  # (sequence number, message)
        self._seq = 0
        self._acks = deque(maxlen=256)
        self._closed = False
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        buf = b""
        try:
            while not self._closed:
                chunk = self.sock.recv(65536)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    try:
                        msg = json.loads(line)
                    except ValueError:
                        continue
                    with self._cond:
                        if "ack" in msg:
                            self._acks.append(msg)
                        else:
                            self._seq += 1
                            self._obs.append((self._seq, msg))
                        self._cond.notify_all()
        except OSError:
            pass
        with self._cond:
            self._closed = True
            self._cond.notify_all()

    @property
    def seq(self):
        return self._seq

    def send(self, line):
        self.sock.sendall((line + "\n").encode("utf-8"))

    def command(self, line, timeout=10.0):
        """Send a command and wait for its ack (matched by the echoed command text)."""
        self.send(line)
        deadline = time.time() + timeout
        with self._cond:
            while True:
                for i, a in enumerate(self._acks):
                    if a.get("ack") == line:
                        del self._acks[i]
                        return a
                left = deadline - time.time()
                if left <= 0 or self._closed:
                    raise TimeoutError(f"no ack for {line!r}")
                self._cond.wait(left)

    def wait_obs(self, count=1, timeout=30.0):
        """Wait for `count` new observation messages after this call and return the last one."""
        with self._cond:
            target = self._seq + count
            deadline = time.time() + timeout
            while self._seq < target:
                left = deadline - time.time()
                if left <= 0 or self._closed:
                    raise TimeoutError("no observation from the server channel")
                self._cond.wait(left)
            return self._obs[-1][1]

    def latest(self):
        with self._cond:
            return self._obs[-1][1] if self._obs else None

    def close(self):
        self._closed = True
        try:
            self.sock.close()
        except OSError:
            pass


class ClientControl:
    """Request/response socket to one fake client's control agent (see agent/src/RLClientControl.java)."""

    def __init__(self, port, host="127.0.0.1", connect_timeout=60.0):
        deadline = time.time() + connect_timeout
        while True:
            try:
                self.sock = socket.create_connection((host, port), timeout=5)
                break
            except OSError as e:
                if time.time() > deadline:
                    raise ConnectionError(f"client control {host}:{port} unreachable: {e}")
                time.sleep(1)
        self.sock.settimeout(10)
        self._file = self.sock.makefile("rw", encoding="utf-8", newline="\n")
        self._lock = threading.Lock()

    def request(self, line):
        with self._lock:
            self._file.write(line + "\n")
            self._file.flush()
            return self._file.readline().strip()

    def ok(self, line, retries=20, delay=0.5):
        """Send a command; the control socket answers 'err not-ready' until the player exists, so retry that."""
        for _ in range(retries):
            r = self.request(line)
            if r in ("ok", "miss") or r.startswith(("info", "hit", "swing")):
                return r
            if r != "err not-ready":
                raise RuntimeError(f"{line!r} -> {r}")
            time.sleep(delay)
        raise TimeoutError(f"client not ready for {line!r}")

    def goto(self, x, y):
        return self.ok(f"goto {x:.2f} {y:.2f}")

    def speed(self, v):
        return self.ok(f"speed {v}")

    def say(self, text):
        return self.ok(f"say {text}")

    def tp(self, x, y, z=0):
        return self.ok(f"tp {x:.2f} {y:.2f} {z}")

    def autoattack(self, on):
        return self.ok("autoattack " + ("on" if on else "off"))

    def attack(self, damage=None):
        """Explicit melee at the nearest zombie within 2 tiles. `damage` is what the swing does to the zombie's 1.0 health
        (0 = a swing that does nothing); None uses the scenario's fixed damage. Returns True when a zombie was hit."""
        return self.ok("attack" if damage is None else f"attack {damage:.4f}", retries=1).startswith("hit")

    def weapon(self, item_id):
        return self.ok(f"weapon {int(item_id)}")

    def info(self):
        parts = self.ok("info").split()
        return {"x": float(parts[1]), "y": float(parts[2]), "z": float(parts[3]), "weaponId": int(parts[4])}

    def close(self):
        try:
            self._file.close()
            self.sock.close()
        except OSError:
            pass
