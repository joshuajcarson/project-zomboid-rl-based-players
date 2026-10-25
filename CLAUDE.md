# CLAUDE.md

Context for Claude Code sessions working in this repo on Joshua's Windows PC.

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
- **Not real-game behaviour:** zombie damage is the synthetic bite rule in `RLBridge.lua` (the fake client's zombies do not hurt players), melee is the fake client's with an explicit attack action, and the hit damage config is cosmetic. Treat results as a training sandbox, not a measurement of the game.
- **Server data** in `.pzdata/` has `StarterKit = true` in its sandbox file (gives each new character a bag, bat and hammer in the bag, water and chips); characters and their kill counters persist across runs.
- Need `gymnasium`/`pettingzoo`/`stable-baselines3` for standard training libraries; they are not installed (ask before installing). A portable JDK 21 is at `C:ench	ools\jdk` (not on PATH; reminder to set up environment variables is still open).

## Next steps

1. Train a first policy (PPO with a shared policy across agents) on survive, then rendezvous, then fight, using the scripted baselines as reference scores.
2. Equivalence check against a rendered client for combat and zombie approach behaviour, then replace the synthetic bite rule if a better source of zombie damage is found.
3. Longer-run stability (hours), crash recovery in the launcher, and parallel servers for more throughput.
