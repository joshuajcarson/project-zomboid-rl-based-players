"""Swing model for the fake backend, fitted to real-client measurements (2026-10-26, 171 swings of a scripted-charge bot with a baseball
bat, Strength 5, Blunt 0, default Apocalypse zombies, endurance always near full; see docs/approach.md and scripts/analyze_combat.py).

UPDATE 2026-10-26: the numbers below were measured while the real bot held the bat in ONE hand (and was often empty-handed); with the bat held in
both hands the real client measured: hit rate 0.46, damage per hit median 0.30 / mean 0.36 / 90th percentile at the 1.0 cap, 5 swings per kill; the
constants below the table were updated accordingly (flat hit chance 0.46, lognormal median 0.30 sigma 0.9).

Measured on the real client (one-handed, superseded):
  * a swing hurts the zombie in about 27% of swings; by distance to the zombie: under 0.7 tiles 22%, 0.7-1.3 tiles 40%, 1.3-2 tiles 12%
  * calm characters hit 36% of swings, characters in pain or panic 18%
  * damage when a swing hits (zombie health is 1.0): median 0.10, mean 0.19, 90th percentile 0.39, maximum 0.95
  * a kill therefore takes about 5 hits, about 20 swings
The real game's per-swing effect of Strength, weapon skill, endurance (full in these tests) and strain is not modelled yet.
"""
import math
import os

# (upper distance in tiles, chance that a calm swing hurts the zombie)
# The fake world has no stand-off: its zombies end up on top of the agent (distance 0.0-0.2), so the real distance bands do not apply;
# within reach every zombie gets the overall real calm hit rate. HIT_CHANCE_BY_DISTANCE_REAL keeps the measured bands for reference.
HIT_CHANCE_BY_DISTANCE = [(2.0, 0.46)]      # two-handed bat (85 swings, 2026-10-26); the one-handed bat measured 0.36 calm / 0.27 overall
HIT_CHANCE_BY_DISTANCE_REAL = [(0.7, 0.22), (1.3, 0.40), (2.0, 0.12)]
HURT_FACTOR = float(os.environ.get("PZ_HURT_FACTOR", "1.0"))             # 0.18 / 0.36: a character in pain or panic hits half as often
DAMAGE_MEDIAN = 0.30         # lognormal fit to the damage of swings that hit: median 0.104, 90th percentile 0.39
DAMAGE_SIGMA = 0.90      # two-handed: median 0.30, mean 0.36, 90th percentile at the 1.0 cap (one-handed: median 0.10, sigma 1.03)
MAX_DAMAGE = 1.0
HIT_SCALE = float(os.environ.get("PZ_HIT_SCALE", "1.0"))     # global multiplier on the hit chance, for fitting aggregate fight outcomes


def hit_chance(distance, hurt):
    for limit, p in HIT_CHANCE_BY_DISTANCE:
        if distance < limit:
            return min(1.0, p * HIT_SCALE * (HURT_FACTOR if hurt else 1.0))
    return 0.0


def sample_swing(distance, hurt, rng, hit_scale=1.0):
    """Damage this swing does to the zombie (0.0 for a swing that does nothing)."""
    if rng.random() >= hit_chance(distance, hurt) * hit_scale:
        return 0.0
    return min(MAX_DAMAGE, DAMAGE_MEDIAN * math.exp(DAMAGE_SIGMA * rng.gauss(0.0, 1.0)))
