# CLAUDE.md

Context for Claude Code sessions working in this repo on Joshua's Windows PC.

**After a crash or session reset, read `docs/journal.md` first (task queue, how to resume, running log). Game mechanics, how they differ from our simulation and what to add: `docs/pz-mechanics.md`.**

## Goal

RL-driven survivors in Project Zomboid: start with 1 agent, grow to 4 agents cooperating on one server. Policies run in Python. See `docs/approach.md` for architectures considered.

## Environment

- Windows, PowerShell. Game: `C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid` (Steam, Build 42.21 at project start). User data: `C:\Users\joshu\Zomboid`.
- The game auto-updates. Run `python scripts/track_game_version.py` at the start of every session. Exit code 1 means a class we depend on changed: re-check the affected code before running experiments, record what changed in `docs/version-notes.md`, and commit the new snapshot in `versions/`.
- The user has approved running a local server with `-nosteam`. Server data goes in `.pzdata/` inside the repo (git-ignored), never the normal Zomboid folder. Don't touch the user's saves.

## Hard rules

- Never commit game files, `projectzomboid.jar`, decompiled source, or copied game/mod code. Snapshots in `versions/` hold hashes and class names only.
- Inspect game classes locally with `javap -p -c` (needs a JDK; the game's bundled JRE has no `javap`). Notes describing behaviour in our own words are fine.
- Bandits and other Workshop mods are dependencies to study, not code to copy (no license found).

## Current state (2026-10-25)

The smoke test passed and the Python bridge works end to end. Read `docs/approach.md` (the sections after "Option B findings") for evidence; this is the short version.

- **Architecture in use (option E):** fake clients provide the players (movement, melee), a Java agent (`agent/`, built with `scripts/build-agent.ps1`) adds a localhost control socket per fake client and an observation/command channel on the server, server Lua (`mods/RLBridge`) publishes observations and runs commands, and `pzrl/` is the Python environment (PettingZoo-style parallel env, 3 tasks: survive, rendezvous, fight). Option B (server-side NPCs) is parked: the world loads around them but zombie AI and NPC walking do not run.
- **Run it:** `python scripts/env_tasks_demo.py 4 4 120 survive,rendezvous,fight idle,random,scripted 1.0 6 12 Attack Base.BaseballBat 14` starts its own server and 4 fake clients at clock factor 4 and prints a table. `scripts/env_demo.py` is a random rollout against a running server. `pzrl.PZParallelEnv(...)` is the entry point; `env.close()` stops everything.
- **Time scaling:** `-TimeScale K` on `start-server.ps1` and `run-fake-client.ps1` (the env passes it). Verified up to 8x at the server level, 4x with the full env. Needs the agent jar; the jar is locked while any JVM uses it, so stop all java processes before rebuilding it.
- **Gotchas:** a fake client connects after `connection.interval x id` ms (the generated scenarios use 200 ms); a duplicate login kicks the new client; a leftover server holds port 16261 (`Connection Startup Failed. Code: 5`); a server boot takes about 5 minutes (iterate with a long-lived server: `Launcher.start_server(reuse=True)`, and `start-server.ps1 -Dev` plus `scripts/dev_eval.py` to run Lua or reflection live, never expose a dev server beyond localhost); fake clients need the admin role for teleports (`admin|Name`, done by the env); PowerShell array literals must not contain `+` expressions; keep `.ps1` paths free of backslash-r.
- **Rendered clients:** `PZParallelEnv(backend="rendered")` drives real graphical clients (1x only; about 4 GB and 1.4 cores each) through `RLBot.lua` (client Lua inside RLBridge) via `pzrl/rendered.py`; `scripts/env_rendered_demo.py` runs a baseline on it. Client Lua files must match the server's boot-time copy (restart the server after editing `mods/RLBridge/.../client/*.lua`; `rl_bot_dev.lua` plus the `reload` bot command allows iteration without restarts). Build the client agent jar separately: `RL_AGENT_OUT=agent
l-agent-client.jar scriptsuild-agent.ps1` (the server's jar is locked while it runs). Never stop java processes by memory size: the server is also large; match the command line.
- **Not real-game behaviour:** zombie damage is the synthetic bite rule in `RLBridge.lua` (the fake client's zombies do not hurt players), melee is the fake client's with an explicit attack action, and the hit damage config is cosmetic. Treat results as a training sandbox, not a measurement of the game.
- **Server data** in `.pzdata/` has `StarterKit = true` in its sandbox file (gives each new character a bag, bat and hammer in the bag, water and chips); characters and their kill counters persist across runs.
- Need `gymnasium`/`pettingzoo`/`stable-baselines3` for standard training libraries; they are not installed (ask before installing). A portable JDK 21 is at C:\bench\tools\jdk (not on PATH; reminder to set up environment variables is still open).

- **Cleanup:** run `python scripts/cleanup.py` at the end of every run/batch and whenever RAM or ports must be freed (stops clients, server, runs, wrappers; verifies processes, ports and the env lock; `--check` only reports, `--keep-server` keeps the server). Exit 0 = clean. Session monitors are not processes: stop those with TaskStop.

- **Latest (2026-10-30):** read the end of `docs/journal.md` (index + strategic read) and `docs/headless-client.md`. Headless/render-skip investigation: not a resource win (client ~1 core of frame-limiter spin and ~4.2 GB either way). Comparisons between runs are dominated by noise (per-episode damage sd ~27): use interleaved arms in one session (`rendered_fight_lab.py` accepts comma-separated policies; `scripts/compare_arms.py`), 30+ episodes per arm, report z. Keep the fight field's corpses cleared (client `arm|hour|r`), per-episode world snapshot is in the lab output. Strategy: fast fake backend for learning, real client for interleaved validation; next is the fake-vs-real fidelity check, then a PPO fighter.

## Next steps

1. Train a first policy (PPO with a shared policy across agents) on survive, then rendezvous, then fight, using the scripted baselines as reference scores.
2. Equivalence check against a rendered client for combat and zombie approach behaviour, then replace the synthetic bite rule if a better source of zombie damage is found.
3. Longer-run stability (hours), crash recovery in the launcher, and parallel servers for more throughput.
