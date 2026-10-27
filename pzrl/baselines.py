"""Scripted policies used to sanity-check the reward shaping (a good reward should rank them above random)."""
import math

import numpy as np

from .env import ATTACK, MOVES, ZOMBIE_SLOTS


def _dir_to_action(dx, dy):
    """Pick the compass move that points closest to (dx, dy); (0, 0) means stay."""
    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
        return 0
    best, best_dot = 0, -2.0
    n = math.hypot(dx, dy)
    for i, (mx, my) in enumerate(MOVES[1:], start=1):
        dot = (mx * dx + my * dy) / (math.hypot(mx, my) * n)
        if dot > best_dot:
            best, best_dot = i, dot
    return best


def nearest_zombie_vec(obs):
    """(dx, dy) to the nearest visible zombie from the observation vector, or None."""
    z = obs[6:6 + 3 * ZOMBIE_SLOTS].reshape(ZOMBIE_SLOTS, 3)
    z = z[z[:, 2] > 0]
    if len(z) == 0:
        return None
    i = np.argmin(z[:, 0] ** 2 + z[:, 1] ** 2)
    return float(z[i, 0]), float(z[i, 1])


def nearest_mate_vec(obs):
    base = 6 + 3 * ZOMBIE_SLOTS
    m = obs[base:base + 3]
    return (float(m[0]), float(m[1])) if m[2] > 0 else None


def flee(obs):
    v = nearest_zombie_vec(obs)
    return 0 if v is None else _dir_to_action(-v[0], -v[1])


def seek_mate(obs):
    v = nearest_mate_vec(obs)
    return 0 if v is None else _dir_to_action(*v)


def charge(obs):
    """Walk to the nearest zombie and swing once it is within reach (about 2 tiles; offsets are scaled by 30)."""
    v = nearest_zombie_vec(obs)
    if v is None:
        return 0
    return ATTACK if math.hypot(v[0], v[1]) * 30 < 1.8 else _dir_to_action(*v)


def charge_param(swing_dist=1.8, flee_hp=0.0, flee_dist=3.0):
    """charge with two knobs: swing only inside `swing_dist` tiles (otherwise keep closing in), and walk away from the nearest zombie
    when health is below `flee_hp` and it is within `flee_dist` tiles. Written as a pure function of the observation so it can label
    observations for imitation. charge_param(1.8, 0) is `charge`."""
    def policy(obs):
        v = nearest_zombie_vec(obs)
        if v is None:
            return 0
        d = math.hypot(v[0], v[1]) * 30
        if obs[0] * 100 < flee_hp and d < flee_dist:
            return _dir_to_action(-v[0], -v[1])
        return ATTACK if d < swing_dist else _dir_to_action(*v)
    return policy


def parse_policy(spec):
    """'charge:1.2:35' -> charge_param(1.2, 35); anything else is looked up by name."""
    if spec.startswith("charge:"):
        parts = [float(x) for x in spec.split(":")[1:]]
        return charge_param(*parts)
    return None


def idle(obs):
    return 0


BASELINES = {"survive": flee, "rendezvous": seek_mate, "rendezvous_safe": seek_mate, "fight": charge}
