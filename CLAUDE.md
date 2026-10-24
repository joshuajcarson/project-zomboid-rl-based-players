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

## Current step: smoke-test the built-in fake client

`zombie.network.FakeClientManager` (in `projectzomboid.jar`) is a headless test client with its own `main`. Args: `-scenarios=<json> -id=<movement id> [-loglevel=<n>]`. It loads `RakNet64` and `ZNetNoSteam64`, so it needs a `-nosteam` server. Default server port 16261; the client binds UDP 17500 locally (check whether multiple processes collide).

1. `.\scripts\start-server.ps1` and wait until the server reports it's ready.
2. In a second terminal: `.\scripts\run-fake-client.ps1 -Scenario scenarios\smoke-1.json -Id 1`.
3. Success = the log reaches the `RUN` state. Client state machine: `CONNECT → LOGIN → CHECKSUM → LOAD_PROFILE → CREATE_PLAYER → PLAYER_CONNECT → RUN`.
4. Ask the user to join `127.0.0.1` with the normal game (the client may also need `-nosteam`) and confirm the fake player is visible.

Likely problems:
- **Checksum rejection.** The scenario supports `config.client.checksum` with `lua`, `script` and optional `anim` strings. If the server rejects the client at `CHECKSUM`, find what the server expects (server log, or how `GameServer` validates checksums) and add it.
- **Spawn.** `movements[].spawn` is optional (random within a small range otherwise). The coordinates in `smoke-1.json` are a guess near Muldraugh.
- **Library path / FMOD init** errors: the client initialises FMOD and voice; run from the game directory (the scripts do).

### Scenario format (traced from the parser in 42.21)

Top level: `version` (string), `config`, `movements` (array).

- `config.client.connection`: `serverHost`?, `serverPort`?, `interval`, `timeout`, `delay` (ms)
- `config.client.statistics`: `period`, `id`
- `config.client.checksum`?: `lua`, `script`, `anim`?
- `config.zombies`?: `behaviour` (`Stay` | `Normal` | `Attack`), `maxZombiesPerUpdate`, `deleteZombieDistance`, `forgotZombieDistance`, `canSeeZombieDistance`, `seeZombieDistance`, `canChangeTarget`
- `config.player`: `fps`, `predict`, `damage`?, `voip`?, `movement.radius`, `movement.motion.{aim,sneak,sneakrun,walk,run,sprint}`, `movement.motion.pedestrian.{min,max}`, `movement.motion.vehicle.{min,max}`
- `movements[]`: `id`, `description`?, `spawn.{x,y}`?, `motion`? (`Aim` | `Sneak` | `Walk` | `SneakRun` | `Run` | `Sprint` | `Pedestrian` | `Vehicle`), `speed`?, `type`? (`Stay` | `Line` | `Circle` | `AIAttackZombies` | `AIRunAwayFromZombies` | `AIRunToAnotherPlayers` | `AINormal`), `radius`?, `direction`?, `ghost`?, `connect`?, `disconnect`?, `reconnect`?, `teleport`? (ms), `destination.{x,y}`?, `createHorde.{count,radius,interval}`?, `makeSound.{interval,radius,message}`?

`?` = optional. The fake client's weapon is hard-coded to `Base.Axe`.

## After the smoke test

Record in `docs/approach.md`: what the fake client can do, how zombies behave around it, server tick rate with 1 and 4 clients. Then design the observation/action bridge (likely: our own Java launcher that reuses the fake client's networking but replaces its movement logic with a socket to Python; multi-agent env via PettingZoo).
