"""Exploratory: reconstruct each episode's zombie spawn geometry from the env's seeded RNG and relate it to outcomes.
ASSUMES one reset per episode line, no reseed, no extra resets (fake clients draw 2 values at env start). Validated only on the fake backend
(angular separation vs damage r=0.25); on the real client the effect is not detectable at n=145. Prefer logged geometry once the env records it.
"""
import json, math, random, statistics as st, collections, sys
BOX = (5362, 10099, 5392, 10129)
def geometry(seed, n_eps, fake):
    """Reconstruct per-episode (ring1, ang1, ring2, ang2) from the env's seeded RNG: fake clients draw 2 values at start; each reset draws
    2 (agent spawn) + 2 per zombie (ring, angle). ASSUMES: one reset per episode line, no reseed, no extra resets."""
    rng = random.Random(seed)
    if fake: rng.uniform(BOX[0], BOX[2]); rng.uniform(BOX[1], BOX[3])
    out = []
    for _ in range(n_eps):
        rng.uniform(BOX[0], BOX[2]); rng.uniform(BOX[1], BOX[3])
        z = []
        for _ in range(2):
            ring = rng.uniform(5, 8); ang = rng.uniform(0, 2 * math.pi); z.append((ring, ang))
        out.append(z)
    return out
def feats(z):
    (r1, a1), (r2, a2) = z
    d = abs((a1 - a2 + math.pi) % (2 * math.pi) - math.pi)          # angular separation 0..pi
    sep = math.sqrt(max(0.0, r1 * r1 + r2 * r2 - 2 * r1 * r2 * math.cos(d)))   # distance between the two zombies
    return math.degrees(d), sep, min(r1, r2)
SETS = [  # (file, seed, fake, label, policy filter)
 ("b1_m1_s1.jsonl", 7, False, "real B1 S1"), ("b1_m1_s2.jsonl", 11, False, "real B1 S2"),
 ("drift_noon_vs_1am.jsonl", 7, False, "real noon/1AM"), ("drift_cleared_vs_pile250.jsonl", 7, False, "real cleared/pile"),
 ("b9_m2_fake_s1.jsonl", 7, True, "fake B9 S1"), ("b9_m2_fake_s2.jsonl", 11, True, "fake B9 S2"), ("b11_m3a_bc_gate.jsonl", 7, True, "fake B11")]
rows = []
for f, seed, fake, label in SETS:
    eps = [json.loads(l) for l in open("results/experiments-2026-10-30/" + f)]
    geo = geometry(seed, len(eps), fake)
    for e, z in zip(eps, geo):
        if e["steps"] >= 5:
            ang, sep, mind = feats(z)
            rows.append(dict(label=label, real=not fake, ang=ang, sep=sep, mind=mind, dmg=e["damage_end"], kills=e["zombies_start"] - e["zombies_end"], steps=e["steps"]))
def report(name, rs):
    print("== " + name + " n=%d" % len(rs))
    for lo, hi, nm in ((0, 60, "next to each other (<60 deg)"), (60, 120, "60-120 deg"), (120, 181, "nearly opposite (>120 deg)")):
        x = [r for r in rs if lo <= r["ang"] < hi]
        if len(x) >= 3:
            d = [r["dmg"] for r in x]
            print("  %-30s n=%3d dmg %.1f (se %.1f) kills %.2f deaths>=80 %d (%.0f%%) median dmg %.1f" % (nm, len(x), st.mean(d), st.stdev(d) / math.sqrt(len(x)), st.mean(r["kills"] for r in x), sum(v >= 80 for v in d), 100 * sum(v >= 80 for v in d) / len(x), sorted(d)[len(d) // 2]))
def corr(xs, ys):
    mx, my = st.mean(xs), st.mean(ys); c = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    return c / math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
for name, rs in (("REAL (all four real sets)", [r for r in rows if r["real"]]), ("REAL B1 only", [r for r in rows if r["label"].startswith("real B1")]), ("FAKE (B9, B11)", [r for r in rows if not r["real"]])):
    report(name, rs)
    print("  Pearson r(angular separation, damage) = %.2f ; r(zombie-to-zombie distance, damage) = %.2f ; r(nearest ring, damage) = %.2f" % (corr([r["ang"] for r in rs], [r["dmg"] for r in rs]), corr([r["sep"] for r in rs], [r["dmg"] for r in rs]), corr([r["mind"] for r in rs], [r["dmg"] for r in rs])))
