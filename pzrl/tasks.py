"""Reward and spawn definitions for the three curriculum stages. Each task gets the previous and current per-agent
state dicts (the "p" entries published by RLBridge.lua, plus 'alive_steps') and returns a reward."""
import math
import random

DEATH_HP = 10.0  # an agent below this health counts as dead for the episode (the character is healed on reset)


def dist(a, b):
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


def nearest_other(me, everyone):
    others = [p for u, p in everyone.items() if u != me["u"]]
    return min(others, key=lambda o: dist(me, o)) if others else None


class Task:
    name = "base"
    zombies_per_agent = 0   # extra zombies spawned around each agent at reset
    min_separation = 0.0    # agents are spawned at least this far apart (tiles)
    bite_damage = 1.5       # hit points per adjacent zombie per game second (server-side rule, see RLBridge.lua)

    def reward(self, prev, cur, everyone):
        raise NotImplementedError

    @staticmethod
    def survive_terms(prev, cur):
        r = 0.01                                   # small bonus for every step alive
        r -= max(0.0, prev["hp"] - cur["hp"]) / 100.0 * 2.0   # losing health hurts
        if cur["hp"] <= DEATH_HP:
            r -= 5.0
        return r


class Survive(Task):
    """Stage 1: do not die. Zombies are placed near the agent; run away and keep health up."""
    name = "survive"
    zombies_per_agent = 14

    def reward(self, prev, cur, everyone):
        return self.survive_terms(prev, cur)


class Rendezvous(Task):
    """Stage 2: find each other. Agents start far apart with few zombies; reward closing the distance to the nearest teammate."""
    name = "rendezvous"
    zombies_per_agent = 2
    min_separation = 60.0
    meet_radius = 6.0

    def reward(self, prev, cur, everyone):
        r = self.survive_terms(prev, cur)
        other_now = nearest_other(cur, everyone)
        other_before = nearest_other(prev, everyone)
        if other_now is not None and other_before is not None:
            d_now, d_before = dist(cur, other_now), dist(prev, other_before)
            r += 0.05 * (d_before - d_now)         # about +0.1 for closing 2 tiles in a step
            if d_now <= self.meet_radius:
                r += 0.5
        return r


class Fight(Task):
    """Stage 3: kill zombies. Reward kills, keep the survival terms."""
    name = "fight"
    zombies_per_agent = 10

    def reward(self, prev, cur, everyone):
        return self.survive_terms(prev, cur) + 1.0 * max(0, cur["kills"] - prev["kills"])


TASKS = {t.name: t for t in (Survive(), Rendezvous(), Fight())}


def sample_spawns(n, task, rng, box=(10450, 9350, 10900, 10300)):
    """Random spawn points inside the town box, honouring the task's minimum separation (best effort)."""
    x0, y0, x1, y1 = box
    pts = []
    for _ in range(n):
        for _try in range(200):
            p = (rng.uniform(x0, x1), rng.uniform(y0, y1))
            if all(math.hypot(p[0] - q[0], p[1] - q[1]) >= task.min_separation for q in pts):
                break
        pts.append(p)
    return pts
