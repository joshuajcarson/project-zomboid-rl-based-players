"""PettingZoo-style parallel environment: several fake-client survivors in one Project Zomboid server.

Interface follows pettingzoo.ParallelEnv (reset/step/agents/possible_agents/observation_space/action_space) without
requiring pettingzoo to be installed. One step is `step_seconds` of GAME time regardless of the clock factor
`time_scale`, so a larger time_scale means more training steps per real second.
"""
import collections
import math
import os
import random
import re
import time

import numpy as np

from .channel import ClientControl, ServerChannel
from .combat import sample_swing
from .rendered import RenderedControl
from .launcher import RUN_SPEED_UNITS, TILES_PER_GAME_SECOND, Launcher, kill_rendered, rendered_alive
from .spaces import Box, Discrete
from .tasks import DEATH_HP, TASKS, dist, nearest_other, sample_spawns

# stay + 8 compass moves (world x grows east, y grows south)
MOVES = [(0, 0), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
ATTACK = len(MOVES)            # extra action id: explicit melee at the nearest zombie within 2 tiles
TICKS_PER_GAME_SECOND = 10
OBS_EVERY_TICKS = 5      # must match cfg.obsEvery in mods/RLBridge
ZOMBIE_SLOTS, MATE_SLOTS = 4, 2
OBS_DIM = 6 + 3 * ZOMBIE_SLOTS + 3 * MATE_SLOTS + 1


STAGGER_STEPS = int(os.environ.get("PZ_STAGGER_STEPS", "3"))              # seconds a landed hit keeps the nearby zombies' bites weak (to be fitted against real fights)
STAGGER_BITE_SCALE = float(os.environ.get("PZ_STAGGER_SCALE", "0.45"))
REAL_STEP_LEN = 3.5      # target distance per step given to a real client: it walks at its own speed (about 16 tiles per 100 ticks)


class AgentDisconnected(RuntimeError):
    """An agent's client left the server (kick, crash, closed window)."""
    def __init__(self, message, name=None):
        super().__init__(message)
        self.name = name


class PZParallelEnv:
    metadata = {"name": "pz_rl_v0"}

    def __init__(self, n_agents=2, task="survive", time_scale=1.0, step_seconds=1.0, max_steps=300,
                 base_id=40, seed=None, spawn_box=(10450, 9350, 10900, 10300), launcher=None,
                 give_weapon="Base.BaseballBat", player_damage=1.0, zombie_ring=(12, 22), zombie_behaviour="Normal",
                 explicit_melee=True, backend="fake", keep_alive=False, rendered_agents=None, walk_speed=17.7, death_hp=None, calibrated_combat=True):
        if backend not in ("fake", "rendered", "mixed"):
            raise ValueError("backend must be 'fake' (headless fake clients, scalable), 'rendered' (real graphical clients, 1x) "
                             "or 'mixed' (the first agent, or `rendered_agents`, is a real client and the others are fake clients)")
        if backend != "fake" and time_scale != 1.0:
            raise ValueError("rendered clients run at real time only (time_scale=1)")
        self.backend = backend
        self.calibrated_combat = calibrated_combat   # fake swings use pzrl.combat (fitted to the real client) instead of one lethal hit
        self.combat_rng = random.Random(0 if seed is None else seed + 1)
        self.combat_stats = {"swings": 0, "hits": 0, "damage": 0.0, "dist_sum": 0.0}   # what the calibrated swing model delivered (for fitting)
        self._dealt = {}                             # per agent: damage its swings have dealt to zombies this episode (calibrated backend)
        self._zombie_hp = {}                         # server zombie id -> health left under the calibrated swing model
        self._target = {}                            # per agent: server id of the zombie its swings go to
        self._stagger = {}                           # per agent: steps left in which a landed hit still keeps the zombies' bites weak
        self._loss = {}                              # per agent: health lost in each of the last few steps (a hurt character hits less)
        self.walk_speed = walk_speed      # target walking speed of fake clients in tiles per 100 server ticks (a real runner: about 16); None = leave as is
        self.keep_alive = keep_alive      # leave rendered clients running on close() and reuse them next time (fast iteration)
        self.task = TASKS[task]
        if death_hp is not None:
            self.task.death_hp = death_hp
        self.n_agents = n_agents
        self.step_seconds = step_seconds
        self.max_steps = max_steps
        self.rng = random.Random(seed)
        self.spawn_box = spawn_box
        self.ids = [base_id + i for i in range(n_agents)]
        self.possible_agents = [f"Client{i}" for i in self.ids]
        self.rendered = (set(self.possible_agents) if backend == "rendered" else
                         set(rendered_agents if rendered_agents is not None else self.possible_agents[:1]) if backend == "mixed" else set())
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
        self._reviving = set()

    # ---- spaces -----------------------------------------------------------------------------------------------------
    def observation_space(self, agent):
        return Box(-1.0, 1.0, (OBS_DIM,), np.float32)

    def action_space(self, agent):
        return Discrete(len(MOVES) + 1)

    # ---- process / connection management ------------------------------------------------------------------------------
    def _start(self):
        L = self.launcher
        L.start_server(reuse=True)
        fake_names = [n for n in self.possible_agents if n not in self.rendered]
        self.channel = ServerChannel(L.channel_port)
        if fake_names:                      # fake clients are always launched fresh (keep_alive only keeps rendered ones)
            self._wait_gone(fake_names)     # a client killed a moment ago is still listed: a second login with its name gets kicked
            time.sleep(25)                  # ... and the server keeps the dead connection for a while after the player is gone
        if fake_names:
            fake_ids = [int(n[len("Client"):]) for n in fake_names]
            spawns = sample_spawns(len(fake_ids), self.task, self.rng, self.spawn_box)
            scen = L.write_scenario(fake_ids, spawns, name=f"env-{len(fake_ids)}", damage=self.player_damage,
                                    zombie_behaviour=self.zombie_behaviour)
            self._scenario = scen
            for i in fake_ids:
                self.control[f"Client{i}"] = ClientControl(L.start_client(i, scen))
        self._wait_connected(fake_names)
        # the synthetic bite rule stands in for zombie damage the fake clients do not take; real clients take the real thing
        self.channel.command(f"cfg|biteDamage|{self.task.bite_damage if not self.rendered else 0}")
        for name in fake_names:
            self._prepare_fake(name)
        if self.rendered:
            self._start_rendered()
        self._started = True

    def _wait_gone(self, names, timeout=60):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not ({p["u"] for p in self.channel.wait_obs(1)["p"]} & set(names)):
                return
            time.sleep(1)

    def _wait_connected(self, names):
        deadline = time.time() + 420
        retry_at, retries = time.time() + 75, 0
        while time.time() < deadline:
            msg = self.channel.wait_obs(1)
            present = {p["u"] for p in msg["p"]}
            if set(names) <= present:
                return
            if time.time() > retry_at and retries < 3:      # a client that never reached the server (stuck connect): start it again
                retries += 1; retry_at = time.time() + 75
                for name in names:
                    if name not in present:
                        self._revive(name)
        raise TimeoutError("agents did not all connect")

    def _prepare_fake(self, name):
        ctl = self.control[name]
        info = ctl.info()
        ctl.goto(info["x"], info["y"])
        # admin role: the server only honours a fake client's teleport requests if it is an admin
        for attempt in range(12):           # the connection can lag a moment behind the first observation (or be a stale duplicate)
            ack = self.channel.command(f"admin|{name}")
            if ack["ok"]:
                break
            if "no such connection" in ack["msg"]:
                time.sleep(3 if attempt < 8 else 0)
                if attempt == 8 and self.control.get(name) is not None:
                    self._revive(name)      # still nothing: the client was probably kicked, start it again
                    return
                continue
            raise RuntimeError(f"could not promote {name}: {ack['msg']}")
        else:
            raise RuntimeError(f"could not promote {name}: {ack['msg']}")
        if self.give_weapon:
            self._equip(name, self.give_weapon)
        if self.explicit_melee:
            ctl.autoattack(False)

    def _prepare_rendered(self, name):
        self.control[name]._bot("reload")       # picks up <cache>/Lua/rl_bot_dev.lua when present (no-op otherwise)
        if self.give_weapon:
            self.control[name]._bot("tidy", self.give_weapon)    # a real client owns its inventory: drop extra copies of the weapon there
            self.channel.command(f"ensure|{name}|{self.give_weapon}")     # one bat, normally the one in the starter-kit backpack
            self.control[name].equip(self.give_weapon)

    def recover(self, error=None):
        """Relaunch every agent that has dropped out (or just the one named by an AgentDisconnected)."""
        names = [error.name] if error is not None and error.name else [n for n, c in self._missing.items() if c >= 12]
        for name in names:
            self._revive(name)

    def _revive(self, name):
        """A character that really died (health 0) cannot be healed: relaunch its client, which logs in and gets a new character."""
        i = int(name[len("Client"):])
        L = self.launcher
        self._reviving.add(name)
        L.stop_client(i)
        if name in self.rendered:
            kill_rendered()                 # the old client may have been started by an earlier run (keep_alive): only one fits anyway
        self.control.pop(name, None)
        self.state.pop(name, None)
        time.sleep(30 if name in self.rendered else 6)                       # let the server notice the disconnect before the same account logs in again
        if name in self.rendered:
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
        self._reviving.discard(name)
        if name in self.rendered:
            time.sleep(20)
            self._prepare_rendered(name)
        else:
            self._prepare_fake(name)

    def _start_rendered(self):
        """Real graphical clients are driven by RLBot.lua through the server channel; the observations are the same
        server-side bridge messages, so the same policies run unchanged."""
        L = self.launcher
        msg = self.channel.wait_obs(1)
        running = {p["u"] for p in msg["p"]} if rendered_alive() else set()   # the server's list still shows a client killed seconds ago
        if not running and any(n in {p["u"] for p in msg["p"]} for n in self.rendered):
            self._wait_gone(sorted(self.rendered), timeout=90)             # let the server drop the dead session before logging in again
        for name in self.possible_agents:
            if name not in self.rendered:
                continue
            if name not in running:
                L.start_rendered(int(name[len("Client"):]))
                time.sleep(20)      # stagger: each client loads for a while and the server handles one login at a time
            self.control[name] = RenderedControl(self.channel, name, state=lambda n=name: self.state.get(n))
        deadline = time.time() + 600
        while time.time() < deadline:
            msg = self.channel.wait_obs(1)
            if set(self.possible_agents) <= {p["u"] for p in msg["p"]}:
                break
        else:
            raise TimeoutError("rendered clients did not all enter the world")
        time.sleep(20)          # a teleport in the first seconds after entering the world leaves the player unable to walk
        for name in self.rendered:
            self._prepare_rendered(name)

    def close(self):
        for c in self.control.values():
            c.close()
        if self.channel:
            self.channel.close()
        if self.keep_alive and self.rendered:
            L = self.launcher                   # leave the real clients running for the next run, stop the fake ones
            for name in self.possible_agents:
                if name not in self.rendered:
                    L.stop_client(int(name[len("Client"):]))
        else:
            self.launcher.stop_all()
        self._started = False

    # ---- helpers ----------------------------------------------------------------------------------------------------
    def _equip(self, name, item_type):
        """Give the item on the server and make the fake client wield it (it sends an Equip packet)."""
        ack = self.channel.command(f"ensureroot|{name}|{item_type}")    # one copy, in the main inventory (a fake client cannot wield from a bag)
        m = re.search(r"id=(\d+)", ack["msg"])
        if not (ack["ok"] and m):
            raise RuntimeError(f"ensure {item_type} for {name} failed: {ack['msg']}")
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
                if name in self._reviving:
                    continue
                self._missing[name] = 0 if name in here else self._missing.get(name, 0) + 1
                if self._missing[name] >= 12:
                    raise AgentDisconnected(f"{name} has been missing from the server for {self._missing[name]} observations", name)
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

    def _swing_damage(self, name):
        """Damage of this swing from the calibrated model (fake clients only); None = leave it to the client."""
        if not self.calibrated_combat or name in self.rendered:
            return None, None
        me = self.state[name]
        zs = sorted(me["z"], key=lambda z: math.hypot(z[0] - me["x"], z[1] - me["y"]))
        dists = [math.hypot(z[0] - me["x"], z[1] - me["y"]) for z in zs]
        if not dists:
            return None, None
        target = self._target.get(name)
        if target is None or target not in {z[2] for z in zs if len(z) > 2}:
            target = zs[0][2] if len(zs[0]) > 2 else None        # keep hitting one zombie until it is gone, like a player facing it
        self._target[name] = target
        hurt = sum(self._loss.get(name, ())) >= 10.0        # lost 10+ health in the last 10 steps: pain and panic
        d = sample_swing(dists[0], hurt, self.combat_rng)
        cs = self.combat_stats
        cs["swings"] += 1; cs["hits"] += 1 if d > 0 else 0; cs["damage"] += d; cs["dist_sum"] += min(dists)
        return d, target

    def _move_len(self, name):
        """How far ahead the target of a move action is. A fake client walks to its target and stops there, so this distance per
        step IS its speed: walk_speed (tiles per 100 ticks, measured on a real runner) turns into tiles per step. A real client
        walks at its own pace, so it just gets a target far enough ahead to keep moving."""
        if name in self.rendered or not self.walk_speed:
            return REAL_STEP_LEN if name in self.rendered else TILES_PER_GAME_SECOND * self.step_seconds * 1.5
        return self.walk_speed / 100.0 * TICKS_PER_GAME_SECOND * self.step_seconds

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
            try:
                self._read(1)
            except AgentDisconnected as e:      # kicked or crashed during the teleport: start it again and carry on
                self.recover(e)
            if all(math.hypot(self.state[n]["x"] - sx, self.state[n]["y"] - sy) < 4.0
                   for n, (sx, sy) in zip(self.possible_agents, spawns) if n in self.state):
                break
        self._zombie_hp.clear(); self._target.clear(); self._dealt.clear()
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
        for name, a in actions.items():
            if name not in self.agents:
                continue
            me = self.state[name]
            a = int(a)
            if a == ATTACK:
                dmg, zid = self._swing_damage(name)
                if dmg is not None and zid is not None:
                    # The server only removes a zombie when it gets a full-strength hit from its owner, so partial damage is tracked here:
                    # the calibrated hits wear the zombie down and the swing that finishes it is sent as a lethal hit.
                    if dmg > 0:
                        self._dealt[name] = self._dealt.get(name, 0.0) + min(dmg, self._zombie_hp.get(zid, 1.0))
                        left = self._zombie_hp.get(zid, 1.0) - dmg
                        if left <= 0:
                            self._zombie_hp.pop(zid, None)
                            self.control[name].attack(1.0, zid)
                            self._target.pop(name, None)
                        else:
                            self._zombie_hp[zid] = left
                else:
                    self.control[name].attack(dmg, zid)
                if dmg:                                    # a landed hit staggers the zombies around: they bite less for a moment
                    self._stagger[name] = STAGGER_STEPS
                    self.channel.command(f"bitescale|{name}|{STAGGER_BITE_SCALE}")
                a = 0                                 # attacking means standing still this step
            dx, dy = MOVES[a]
            n = math.hypot(dx, dy) or 1.0
            move_len = self._move_len(name)
            self.control[name].goto(me["x"] + dx / n * move_len, me["y"] + dy / n * move_len)
        self._read(self._game_seconds(self.step_seconds))
        for name in self.agents:
            if name in self.state:
                self.state[name]["dealt"] = self._dealt.get(name, 0.0)
        for name in list(self._stagger):
            self._stagger[name] -= 1
            if self._stagger[name] <= 0:
                del self._stagger[name]
                self.channel.command(f"bitescale|{name}|1.0")
        for name in self.agents:
            lost = max(0.0, self.prev[name]["hp"] - self.state[name]["hp"]) if name in self.prev and name in self.state else 0.0
            self._loss.setdefault(name, collections.deque(maxlen=10)).append(lost)
        self.steps += 1
        obs, rewards, terms, truncs, infos = {}, {}, {}, {}, {}
        for name in list(self.agents):
            cur = self.state[name]
            rewards[name] = self.task.reward(self.prev[name], cur, self.state)
            dead = cur["dead"] or cur["hp"] <= self.task.death_hp
            terms[name] = dead
            truncs[name] = (not dead) and self.steps >= self.max_steps
            obs[name] = self._obs(name)
            infos[name] = self._info(name)
            self.prev[name] = dict(cur)
        self.agents = [a for a in self.agents if not (terms[a] or truncs[a])]
        return obs, rewards, terms, truncs, infos
