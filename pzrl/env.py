"""PettingZoo-style parallel environment: several fake-client survivors in one Project Zomboid server.

Interface follows pettingzoo.ParallelEnv (reset/step/agents/possible_agents/observation_space/action_space) without
requiring pettingzoo to be installed. One step is `step_seconds` of GAME time regardless of the clock factor
`time_scale`, so a larger time_scale means more training steps per real second.
"""
import math
import random
import re
import time

import numpy as np

from .channel import ClientControl, ServerChannel
from .rendered import RenderedControl
from .launcher import TILES_PER_GAME_SECOND, Launcher
from .spaces import Box, Discrete
from .tasks import DEATH_HP, TASKS, dist, nearest_other, sample_spawns

# stay + 8 compass moves (world x grows east, y grows south)
MOVES = [(0, 0), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
ATTACK = len(MOVES)            # extra action id: explicit melee at the nearest zombie within 2 tiles
TICKS_PER_GAME_SECOND = 10
OBS_EVERY_TICKS = 5      # must match cfg.obsEvery in mods/RLBridge
ZOMBIE_SLOTS, MATE_SLOTS = 4, 2
OBS_DIM = 6 + 3 * ZOMBIE_SLOTS + 3 * MATE_SLOTS + 1


class AgentDisconnected(RuntimeError):
    """An agent's client left the server (kick, crash, closed window)."""


class PZParallelEnv:
    metadata = {"name": "pz_rl_v0"}

    def __init__(self, n_agents=2, task="survive", time_scale=1.0, step_seconds=1.0, max_steps=300,
                 base_id=40, seed=None, spawn_box=(10450, 9350, 10900, 10300), launcher=None,
                 give_weapon="Base.BaseballBat", player_damage=1.0, zombie_ring=(12, 22), zombie_behaviour="Normal",
                 explicit_melee=True, backend="fake", keep_alive=False):
        if backend not in ("fake", "rendered"):
            raise ValueError("backend must be 'fake' (headless fake clients, scalable) or 'rendered' (real graphical clients, 1x)")
        if backend == "rendered" and time_scale != 1.0:
            raise ValueError("rendered clients run at real time only (time_scale=1)")
        self.backend = backend
        self.keep_alive = keep_alive      # leave rendered clients running on close() and reuse them next time (fast iteration)
        self.task = TASKS[task]
        self.n_agents = n_agents
        self.step_seconds = step_seconds
        self.max_steps = max_steps
        self.rng = random.Random(seed)
        self.spawn_box = spawn_box
        self.ids = [base_id + i for i in range(n_agents)]
        self.possible_agents = [f"Client{i}" for i in self.ids]
        self.agents = []
        self.launcher = launcher or Launcher(time_scale=time_scale)
        self.time_scale = time_scale
        self.give_weapon = give_weapon
        self.player_damage = player_damage
        self.explicit_melee = explicit_melee
        self.zombie_behaviour = zombie_behaviour
        self.zombie_ring = zombie_ring
        self.channel = None
        self.control = {}
        self.state = {}      # username -> latest published player dict
        self.prev = {}
        self.steps = 0
        self.last_message = None
        self._started = False
        self._missing = {}

    # ---- spaces -----------------------------------------------------------------------------------------------------
    def observation_space(self, agent):
        return Box(-1.0, 1.0, (OBS_DIM,), np.float32)

    def action_space(self, agent):
        return Discrete(len(MOVES) + 1)

    # ---- process / connection management ------------------------------------------------------------------------------
    def _start(self):
        L = self.launcher
        L.start_server(reuse=True)
        if self.backend == "rendered":
            return self._start_rendered()
        spawns = sample_spawns(self.n_agents, self.task, self.rng, self.spawn_box)
        scen = L.write_scenario(self.ids, spawns, name=f"env-{self.n_agents}", damage=self.player_damage,
                                zombie_behaviour=self.zombie_behaviour)
        self._scenario = scen
        for i in self.ids:
            port = L.start_client(i, scen)
            self.control[f"Client{i}"] = ClientControl(port)
        self.channel = ServerChannel(L.channel_port)
        deadline = time.time() + 420
        retry_at, retries = time.time() + 75, 0
        while time.time() < deadline:
            msg = self.channel.wait_obs(1)
            present = {p["u"] for p in msg["p"]}
            if set(self.possible_agents) <= present:
                break
            if time.time() > retry_at and retries < 3:      # a client that never reached the server (stuck connect): start it again
                retries += 1; retry_at = time.time() + 75
                for name in self.possible_agents:
                    if name not in present:
                        self._revive(name)
        else:
            raise TimeoutError("agents did not all connect")
        self.channel.command(f"cfg|biteDamage|{self.task.bite_damage}")
        for name in self.control:
            self._prepare_fake(name)
        self._started = True

    def _prepare_fake(self, name):
        ctl = self.control[name]
        info = ctl.info()
        ctl.goto(info["x"], info["y"])
        # admin role: the server only honours a fake client's teleport requests if it is an admin
        ack = self.channel.command(f"admin|{name}")
        if not ack["ok"]:
            raise RuntimeError(f"could not promote {name}: {ack['msg']}")
        if self.give_weapon:
            self._equip(name, self.give_weapon)
        if self.explicit_melee:
            ctl.autoattack(False)

    def _revive(self, name):
        """A character that really died (health 0) cannot be healed: relaunch its client, which logs in and gets a new character."""
        i = int(name[len("Client"):])
        L = self.launcher
        L.stop_client(i)
        self.control.pop(name, None)
        self.state.pop(name, None)
        time.sleep(6)                       # let the server notice the disconnect before the same account logs in again
        if self.backend == "rendered":
            L.start_rendered(i)
            self.control[name] = RenderedControl(self.channel, name, state=lambda n=name: self.state.get(n))
        else:
            self.control[name] = ClientControl(L.start_client(i, self._scenario))
        deadline = time.time() + 240
        while time.time() < deadline:
            msg = self._read(1)
            if any(p["u"] == name and not p["dead"] for p in msg["p"]):
                break
        else:
            raise TimeoutError(f"{name} did not come back after dying")
        self._missing[name] = 0
        if self.backend == "rendered":
            self.control[name]._bot("reload")
            if self.give_weapon:
                self.channel.command(f"give|{name}|{self.give_weapon}")
                self.control[name].equip(self.give_weapon)
        else:
            self._prepare_fake(name)

    def _start_rendered(self):
        """Rendered backend: real graphical clients are driven by RLBot.lua through the server channel; the observations are the
        same server-side bridge messages, so the same policies run unchanged."""
        L = self.launcher
        self.channel = ServerChannel(L.channel_port)
        msg = self.channel.wait_obs(1)
        running = {p["u"] for p in msg["p"]}
        for i in self.ids:
            if f"Client{i}" not in running:
                L.start_rendered(i)
                time.sleep(20)      # stagger: each client loads for a while and the server handles one login at a time
            self.control[f"Client{i}"] = RenderedControl(self.channel, f"Client{i}", state=lambda n=f"Client{i}": self.state.get(n))
        deadline = time.time() + 600
        while time.time() < deadline:
            msg = self.channel.wait_obs(1)
            if set(self.possible_agents) <= {p["u"] for p in msg["p"]}:
                break
        else:
            raise TimeoutError("rendered clients did not all enter the world")
        self.channel.command(f"cfg|biteDamage|0")      # real zombies do the damage here, no synthetic bite rule
        for ctl in self.control.values():
            ctl._bot("reload")                          # picks up <cache>/Lua/rl_bot_dev.lua when present (no-op otherwise)
        for name, ctl in self.control.items():
            if self.give_weapon:
                self.channel.command(f"give|{name}|{self.give_weapon}")
                ctl.equip(self.give_weapon)
        self._started = True

    def close(self):
        for c in self.control.values():
            c.close()
        if self.channel:
            self.channel.close()
        if not (self.keep_alive and self.backend == "rendered"):
            self.launcher.stop_all()
        self._started = False

    # ---- helpers ----------------------------------------------------------------------------------------------------
    def _equip(self, name, item_type):
        """Give the item on the server and make the fake client wield it (it sends an Equip packet)."""
        ack = self.channel.command(f"give|{name}|{item_type}")
        m = re.search(r"id=(\d+)", ack["msg"])
        if not (ack["ok"] and m):
            raise RuntimeError(f"give {item_type} to {name} failed: {ack['msg']}")
        self.control[name].weapon(int(m.group(1)))

    def _read(self, n_messages):
        msg = self.channel.wait_obs(n_messages)
        self.last_message = msg
        here = {p["u"] for p in msg["p"]}
        for p in msg["p"]:
            if p["u"] in self.possible_agents:
                self.state[p["u"]] = p
        if self._started:                    # a kicked or crashed client would otherwise leave stale state that looks like an idle agent
            for name in self.possible_agents:
                self._missing[name] = 0 if name in here else self._missing.get(name, 0) + 1
                if self._missing[name] >= 12:
                    raise AgentDisconnected(f"{name} has been missing from the server for {self._missing[name]} observations")
        return msg

    def _game_seconds(self, seconds):
        return max(1, round(seconds * TICKS_PER_GAME_SECOND / OBS_EVERY_TICKS))

    def _obs(self, name):
        me = self.state[name]
        v = np.zeros(OBS_DIM, np.float32)
        v[0] = np.clip(me["hp"] / 100.0, 0, 1)
        v[1], v[2], v[3] = np.clip([me["hunger"], me["thirst"], me["fatigue"]], 0, 1)
        v[4] = 1.0 if me["weapon"] else 0.0
        v[5] = 1.0 if me["bag"] else 0.0
        o = 6
        zs = sorted(me["z"], key=lambda z: (z[0] - me["x"]) ** 2 + (z[1] - me["y"]) ** 2)[:ZOMBIE_SLOTS]
        for z in zs:
            v[o:o + 3] = [np.clip((z[0] - me["x"]) / 30, -1, 1), np.clip((z[1] - me["y"]) / 30, -1, 1), 1.0]
            o += 3
        o = 6 + 3 * ZOMBIE_SLOTS
        mates = sorted((p for u, p in self.state.items() if u != name), key=lambda p: dist(me, p))[:MATE_SLOTS]
        for m in mates:
            v[o:o + 3] = [np.clip((m["x"] - me["x"]) / 100, -1, 1), np.clip((m["y"] - me["y"]) / 100, -1, 1), 1.0]
            o += 3
        v[-1] = min(me["zn"], 10) / 10.0
        return v

    def _info(self, name):
        p = self.state[name]
        return {"x": p["x"], "y": p["y"], "hp": p["hp"], "kills": p["kills"], "weapon": p["weapon"], "bag": p["bag"]}

    # ---- API --------------------------------------------------------------------------------------------------------
    def reset(self, seed=None, options=None):
        if seed is not None:
            self.rng = random.Random(seed)
        if not self._started:
            self._start()
        spawns = sample_spawns(self.n_agents, self.task, self.rng, self.spawn_box)
        self.channel.command(f"cfg|biteDamage|{self.task.bite_damage}")   # the task may have changed since startup
        for name in self.possible_agents:
            if self.state.get(name, {}).get("dead"):
                self._revive(name)
        for name, (sx, sy) in zip(self.possible_agents, spawns):
            self.channel.command(f"heal|{name}")
            self.control[name].tp(sx, sy, 0)
        # a teleport takes a moment to show up (and chunks must load around the new spot): clear and spawn only once every
        # agent has really arrived, otherwise the clear and the spawn happen around its old position
        for _ in range(40):
            self._read(1)
            if all(math.hypot(self.state[n]["x"] - sx, self.state[n]["y"] - sy) < 4.0
                   for n, (sx, sy) in zip(self.possible_agents, spawns) if n in self.state):
                break
        self._read(self._game_seconds(4))           # arriving loads chunks, which brings the world's own zombies: let that finish
        for name, (sx, sy) in zip(self.possible_agents, spawns):
            # same start on every backend: clear everything the observation can see (zRadius 30 plus margin), then exactly N
            # zombies, each at its own random angle on the ring
            self.channel.command(f"zclear|{sx:.0f}|{sy:.0f}|45")
            for _ in range(self.task.zombies_per_agent):
                ring = self.rng.uniform(*self.zombie_ring)
                ang = self.rng.uniform(0, 2 * math.pi)
                self.channel.command(f"zspawn|{sx + ring * math.cos(ang):.0f}|{sy + ring * math.sin(ang):.0f}|1")
        self._read(self._game_seconds(4))          # let chunks and ownership settle
        self.agents = [a for a in self.possible_agents if a in self.state]
        self.prev = {a: dict(self.state[a]) for a in self.agents}
        self.steps = 0
        return {a: self._obs(a) for a in self.agents}, {a: self._info(a) for a in self.agents}

    def step(self, actions):
        move_len = TILES_PER_GAME_SECOND * self.step_seconds * 1.5
        for name, a in actions.items():
            if name not in self.agents:
                continue
            me = self.state[name]
            a = int(a)
            if a == ATTACK:
                self.control[name].attack()
                a = 0                                 # attacking means standing still this step
            dx, dy = MOVES[a]
            n = math.hypot(dx, dy) or 1.0
            self.control[name].goto(me["x"] + dx / n * move_len, me["y"] + dy / n * move_len)
        self._read(self._game_seconds(self.step_seconds))
        self.steps += 1
        obs, rewards, terms, truncs, infos = {}, {}, {}, {}, {}
        for name in list(self.agents):
            cur = self.state[name]
            rewards[name] = self.task.reward(self.prev[name], cur, self.state)
            dead = cur["dead"] or cur["hp"] <= DEATH_HP
            terms[name] = dead
            truncs[name] = (not dead) and self.steps >= self.max_steps
            obs[name] = self._obs(name)
            infos[name] = self._info(name)
            self.prev[name] = dict(cur)
        self.agents = [a for a in self.agents if not (terms[a] or truncs[a])]
        return obs, rewards, terms, truncs, infos
