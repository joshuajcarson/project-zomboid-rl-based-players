# Approach

## Goal

Agents that act as survivors, driven by an external RL policy (Python), running faster than a human-played session, and able to scale from 1 agent to 4 agents cooperating in the same world.

## Key finding: the game ships a headless player client

Build 42.21's `projectzomboid.jar` contains `zombie.network.FakeClientManager`, a standalone program (it has its own `main`) that The Indie Stone appears to use for multiplayer load testing. From inspecting its class signatures with `javap`:

- It is launched with `-scenarios=<file> -id=<n> [-loglevel=<n>]` and loads the non-Steam network library (`ZNetNoSteam64`), so it targets a server started without Steam.
- Each fake client goes through the real connection flow: `CONNECT → LOGIN → CHECKSUM → LOAD_PROFILE → CREATE_PLAYER → PLAYER_CONNECT → RUN`.
- Built-in behaviours include `Stay`, `Line`, `Circle`, `AIAttackZombies`, `AIRunAwayFromZombies`, `AIRunToAnotherPlayers` and `AINormal`, plus melee hits on zombies.
- It contains a `ZombieSimulator` that takes "authority" over nearby zombies, because in PZ multiplayer zombie AI is simulated by the nearest client, not the server.
- The scenario file is JSON-like with sections for `client` (server host/port, timeouts, checksums for lua/script/anim), `player` (fps, damage, speeds) and a list of `movements` (spawn, type, destination, delays, horde creation, sounds).

This means real, server-recognised players can exist with no rendered game client.

## Candidate architectures

### A. Fake clients driven by a policy (preferred first experiment)

1 headless server (`-nosteam`) + N fake-client processes. Replace or wrap the built-in behaviours so each fake client streams observations to Python and applies actions from it.

- Pros: truly headless, cheap per agent, natively multi-agent (4 agents = 4 connections), and the server stays authoritative.
- Cons: the fake client is a protocol-level puppet, not a full `IsoPlayer`. It moves and hits but likely does not do inventory, crafting, eating, or timed actions. Zombies near the agents are run by the fake client's simplified `ZombieSimulator`, not the real zombie AI, so fidelity is lower.
- Unknowns: whether 42.21 servers accept it without changes (checksums, auth), and how much of it can be extended without reimplementing it.

### B. Server-side NPCs via Java agent + Lua

A `-javaagent` on the server JVM spawns and drives player-like characters itself, keeps chunks loaded around them, and runs the real zombie AI on the server.

- Pros: full game fidelity, no clients at all.
- Cons: significant reverse-engineering; the engine assumes zombies are owned by clients and chunks are loaded by players.

### C. Rendered clients (fallback / ground truth)

One normal client per agent at minimum settings, with a Lua mod exposing state and actions over a file or socket bridge.

- Pros: full fidelity, lowest engineering risk, easy to debug visually.
- Cons: expensive per agent; four rendered clients on one PC is heavy.

## Plan

1. **Smoke test A.** Start a local `-nosteam` server, run one stock fake client with a minimal scenario, and confirm it logs in and appears in-world (verified by joining with a normal client).
2. **Measure.** Check what the fake client can and cannot do, how zombies behave around it, and the server tick rate with 1 and 4 fake clients.
3. **Bridge.** Build an observation/action bridge (Java side next to the fake client, Python side as a Gymnasium / PettingZoo environment for multi-agent).
4. **Decide** whether A's fidelity is enough, or whether to invest in B (or use C for evaluation runs).
