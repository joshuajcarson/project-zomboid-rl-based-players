"""Fixed fight benchmark: run policies through rendered_fight_lab.py and append one row each to results/ledger.jsonl.

    python scripts/benchmark.py --backend rendered --episodes 12 idle charge:1.8:0 models/fight_bc3.pt
    python scripts/benchmark.py --backend fake --episodes 12 --clip charge:1.8:0     # also a GIF in clips/ (git-ignored)
    python scripts/benchmark.py --report                                              # only rewrite docs/results.md

Conditions are the lab's defaults (2 zombies on a ring, 45 steps, two-handed bat). Change them and the rows are not comparable:
bump --protocol and say why in docs/results.md. Reference rows (idle, charge:1.8:0) are added automatically so a score always sits
next to simple bots measured the same day. One experiment at a time (the env lock), so run this when nothing else is.
"""
import argparse, datetime, hashlib, json, os, pathlib, subprocess, sys, time

LEDGER = pathlib.Path("results/ledger.jsonl")
PROTOCOL = "fight-v1"            # set from --protocol in main(); passed to the lab as PZ_PROTOCOL
IDLE_EPISODES = 10            # idle is near-deterministic (0 kills, damage from stray zombies): 10 episodes are enough
MAX_REF_AGE_DAYS = 0          # a reference row measured today (same protocol, backend, policy, >= 20 episodes or idle >= 10) is reused
REFERENCE = ["idle", "charge:1.8:0"]


def git_commit():
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()


STALL_SECONDS = 600           # no finished episode for this long = the lab is stuck (seen 2026-10-29: a dead character the env never recovered, 24 min lost)


def run_lab(cmd, env):
    """Run the lab, streaming its output to a file; kill it (and children) when no episode line appears for STALL_SECONDS."""
    path = pathlib.Path("logs/_lab_stream.out")
    with path.open("w") as f:
        proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, text=True, env=env)
        seen, last = 0, time.time()
        while proc.poll() is None:
            time.sleep(15)
            n = path.read_text(errors="replace").count('{"ep"')
            if n != seen:
                seen, last = n, time.time()
            elif time.time() - last > (STALL_SECONDS if seen else 3 * STALL_SECONDS):   # the first episode follows the server boot and client login
                print("WARNING: no episode finished for %d s, killing the stuck lab" % STALL_SECONDS, flush=True)
                subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
                break
    return path.read_text(errors="replace")


def run_policy(policy, backend, episodes, steps):
    """The rendered client sometimes drops out mid-run (AgentDisconnected after 10-20 episodes): restart it and carry on until the
    requested number of episodes is done (at most 4 launches, each with its own seed)."""
    pathlib.Path("logs").mkdir(exist_ok=True)
    eps, log = [], ""
    for attempt in range(4):
        env = dict(os.environ, PZ_SEED=str(7 + attempt), PZ_PROTOCOL=PROTOCOL)
        out = run_lab([sys.executable, "scripts/rendered_fight_lab.py", str(episodes - len(eps)), str(steps), policy, backend], env)
        log += out
        eps += [json.loads(l) for l in out.splitlines() if l.startswith('{"ep"')]
        if len(eps) >= episodes or backend == "fake":
            break
        print("WARNING: %s has %d of %d episodes after launch %d, restarting the client" % (policy, len(eps), episodes, attempt + 1), flush=True)
        subprocess.run([sys.executable, "scripts/pz_ctl.py", "stop-clients"])
        time.sleep(100)
    pathlib.Path("logs/bench_%s.out" % policy.replace("/", "_").replace("\\", "_").replace(":", "_")).write_text(log)
    if not eps:
        sys.exit("no episodes for %s: %s" % (policy, log[-1500:]))
    return eps


def row(policy, backend, eps, protocol, note):
    # a death makes the env relaunch the client and the next "episode" ends after 1 step with nothing measured: those are not episodes
    aborted = sum(1 for e in eps if e["steps"] < 5)
    eps = [e for e in eps if e["steps"] >= 5] or eps
    if aborted:
        note = (note + " ").lstrip() + "[%d aborted 1-step resets after deaths excluded]" % aborted
    n = len(eps)
    kills = [e["zombies_start"] - e["zombies_end"] for e in eps]
    ck = pathlib.Path(policy)
    return {"date": datetime.date.today().isoformat(), "commit": git_commit(), "protocol": protocol, "backend": backend,
            "policy": policy, "checkpoint_sha": hashlib.sha1(ck.read_bytes()).hexdigest()[:10] if ck.is_file() else "",
            "episodes": n, "kills": round(sum(kills) / n, 2), "of": eps[0]["zombies_start"],
            "damage": round(sum(e["damage_end"] for e in eps) / n, 1), "low_hp_episodes": sum(e["min_hp"] < 15 for e in eps),
            "note": note}


def report():
    rows = [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()] if LEDGER.exists() else []
    lines = ["# Results ledger", "", "Generated by `scripts/benchmark.py --report` from `results/ledger.jsonl`. Rows with the same protocol "
             "and backend are comparable; the real client is the one that counts. Kills are per episode (of the zombies spawned), damage is "
             "health lost, low-hp episodes finished under 15 hp.", ""]
    for proto in sorted({r["protocol"] for r in rows}):
        lines += ["## Protocol %s" % proto, "", "| date | backend | policy | episodes | kills | damage | low-hp eps | commit | note |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for r in sorted((r for r in rows if r["protocol"] == proto), key=lambda r: (r["backend"], r["date"], r["policy"])):
            lines.append("| %s | %s | %s | %d | %.2f of %d | %.1f | %d | %s | %s |" % (
                r["date"], r["backend"], r["policy"], r["episodes"], r["kills"], r["of"], r["damage"], r["low_hp_episodes"], r["commit"], r["note"] + ("" if r.get("interleaved") else " [unpaired]")))
        lines.append("")
    pathlib.Path("docs/results.md").write_text("\n".join(lines))
    print("wrote docs/results.md,", len(rows), "rows")


def have_reference(policy, backend, protocol, min_eps, setup):
    """True when the ledger already holds a row for this reference today (same protocol and backend): references cost half of every
    benchmark's wall time and do not change within a day."""
    if not LEDGER.exists():
        return False
    today = datetime.date.today().isoformat()
    need = 5 if policy == "idle" else min_eps          # idle rows keep only the real episodes (aborted resets after deaths are dropped)
    for l in LEDGER.read_text().splitlines():
        if l.strip():
            r = json.loads(l)
            if setup and r.get("setup") == setup and (r["date"], r["protocol"], r["backend"], r["policy"]) == (today, protocol, backend, policy) and r["episodes"] >= need                     and r.get("kills") is not None and (policy != "charge:1.8:0" or r["of"] > 0):
                return True
    return False


def run_interleaved(a):
    """One lab session whose episodes alternate between the given policies; one ledger row per arm, plus the z score of the first two arms.
    Drift between blocks (time, corpses, session age) hits every arm equally, so differences are comparable."""
    import math, statistics
    arms = a.policies
    if len(arms) < 2:
        sys.exit("--interleave needs at least two policies (the arms)")
    eps = run_policy(",".join(arms), a.backend, a.episodes * len(arms), a.steps)
    sid = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    stats = {}
    for arm in arms:
        mine = [e for e in eps if e.get("policy") == arm]
        if not mine:
            print("WARNING: no episodes for arm %s" % arm, flush=True); continue
        r = row(arm, a.backend, mine, a.protocol, (a.note + " [interleaved session %s]" % sid).strip())
        r["setup"] = a.setup; r["interleaved"] = True; r["session"] = sid
        with LEDGER.open("a") as f: f.write(json.dumps(r) + "\n")
        print(json.dumps(r), flush=True)
        real = [e for e in mine if e["steps"] >= 5] or mine
        stats[arm] = ([e["zombies_start"] - e["zombies_end"] for e in real], [e["damage_end"] for e in real])
    names = [x for x in arms if x in stats]
    if len(names) >= 2:
        for label, i in (("kills", 0), ("damage", 1)):
            x, y = stats[names[0]][i], stats[names[1]][i]
            if len(x) > 1 and len(y) > 1:
                se = math.sqrt(statistics.variance(x) / len(x) + statistics.variance(y) / len(y))
                print("%s: %s - %s = %.2f (se %.2f, z %.2f)" % (label, names[1], names[0], statistics.mean(y) - statistics.mean(x), se, (statistics.mean(y) - statistics.mean(x)) / se if se else 0), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("policies", nargs="*")
    ap.add_argument("--backend", default="rendered")
    ap.add_argument("--episodes", type=int, default=12)
    ap.add_argument("--steps", type=int, default=45)
    ap.add_argument("--protocol", default="fight-v1")
    ap.add_argument("--note", default="")
    ap.add_argument("--setup", default="", help="tag naming the world/bot setup (e.g. lowpop-hutchfree-floor-aim); a reference row with the same tag measured today is reused instead of rerun")
    ap.add_argument("--clip", default=None, help="policy to record a GIF of into clips/ after the runs")
    ap.add_argument("--interleave", action="store_true", help="the policies are ARMS of one comparison: one lab session alternates them by episode (controls block-to-block drift); --episodes is per arm; no references are added; rows are tagged interleaved=True and share a session id")
    ap.add_argument("--reuse-references", action="store_true", help="old behaviour: reuse a same-day reference row with the same --setup tag. Such a comparison is across blocks and NOT evidence (same policy scored 25.7 to 56.8 damage across blocks); rows get an [unpaired] note")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if not a.report:
        LEDGER.parent.mkdir(exist_ok=True)
        global PROTOCOL
        PROTOCOL = a.protocol
        if a.interleave:
            run_interleaved(a)
            report()
            return
        for policy in a.policies + [p for p in REFERENCE if p not in a.policies]:
            if a.reuse_references and policy in REFERENCE and policy not in a.policies and have_reference(policy, a.backend, a.protocol, min(a.episodes, 20), a.setup):
                print("reference %s already measured today for %s/%s: skipped" % (policy, a.backend, a.protocol), flush=True)
                continue
            n = IDLE_EPISODES if policy == "idle" else a.episodes
            r = row(policy, a.backend, run_policy(policy, a.backend, n, a.steps), a.protocol, a.note)
            r["setup"] = a.setup
            with LEDGER.open("a") as f: f.write(json.dumps(r) + "\n")
            print(json.dumps(r), flush=True)
    report()
    if a.clip:
        os.makedirs("clips", exist_ok=True)
        out = "clips/%s_%s_%s.gif" % (datetime.date.today().isoformat(), a.backend, pathlib.Path(a.clip).stem.replace(":", "_"))
        subprocess.run([sys.executable, "scripts/record_episode.py", "--task", "fight", "--agents", "1", "--policy", a.clip,
                        "--backend", a.backend, "--steps", str(a.steps), "--out", out])
        print("clip", out)


if __name__ == "__main__":
    main()
